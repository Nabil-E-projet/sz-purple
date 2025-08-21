"""
Client pour l'API Vision d'OpenAI
"""
import json
import logging
import traceback
import requests
from typing import Dict, Any, List

from .reference_data import MODEL_PRICING

logger = logging.getLogger('salariz.gpt_vision')

class OpenAIVisionClient:
    """Client pour communiquer avec l'API Vision d'OpenAI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def call_vision_api(self, 
                        prompt: str, 
                        base64_images: List[str], 
                        model: str = None,
                        temperature: float = None, 
                        max_tokens: int = None,
                        timeout: int = 180) -> Dict[str, Any]:
        """
        Appelle l'API Vision d'OpenAI pour analyser des images.
        
        Args:
            prompt: Le texte du prompt d'instruction
            base64_images: Liste d'images encodées en base64
            model: Le modèle OpenAI à utiliser
            temperature: Température pour la génération (0.0-1.0)
            max_tokens: Nombre max de tokens pour la réponse
            timeout: Délai d'attente en secondes
            
        Returns:
            Dict contenant la réponse analysée, les données brutes et les métriques d'usage
            
        Raises:
            requests.exceptions.RequestException: Pour les erreurs de communication API
            json.JSONDecodeError: Si la réponse n'est pas au format JSON
            Exception: Pour les autres erreurs
        """
        # Préparation du contenu de la requête
        content_list = [{"type": "text", "text": prompt}]
        for b64_img in base64_images:
            content_list.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_img}", "detail": "high"}
            })

        # Valeurs par défaut depuis les settings (permet override par argument)
        try:
            from django.conf import settings
            default_model = getattr(settings, 'OPENAI_VISION_MODEL', 'gpt-5-mini')
            default_temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.1)
            default_max_tokens = getattr(settings, 'OPENAI_MAX_OUTPUT_TOKENS', 8192)  # Plus de tokens pour GPT-5
        except Exception:
            default_model, default_temperature, default_max_tokens = 'gpt-5-mini', 0.1, 8192

        model = model or default_model
        temperature = default_temperature if temperature is None else temperature
        max_tokens = default_max_tokens if max_tokens is None else max_tokens

        # Configuration de la requête (support GPT-4 et GPT-5)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content_list}],
            "response_format": {"type": "json_object"},
            "temperature": temperature
        }
        
        # GPT-5 utilise 'max_completion_tokens', GPT-4 utilise 'max_tokens'
        if model.startswith('gpt-5'):
            payload["max_completion_tokens"] = max_tokens
            # GPT-5 ne supporte que temperature=1 par défaut
            if temperature != 1.0:
                logger.warning(f"GPT-5 ne supporte que temperature=1, ignoré temperature={temperature}")
                payload.pop("temperature", None)
        else:
            payload["max_tokens"] = max_tokens
        
        # DEBUG: Log de la configuration de la requête
        logger.info(f"Configuration requête API:")
        logger.info(f"  Modèle: {model}")
        logger.info(f"  Max tokens: {max_tokens}")
        logger.info(f"  Temperature: {temperature}")
        logger.info(f"  Nombre d'images: {len(base64_images)}")
        logger.info(f"  Taille du prompt: {len(prompt)} caractères")

        try:
            logger.info(f"Envoi de la requête à l'API OpenAI (modèle: {model})...")
            
            # GPT-5 utilise l'API responses, GPT-4 utilise chat/completions
            if model.startswith('gpt-5'):
                return self._call_responses_api(prompt, base64_images, model, max_tokens, timeout)
            else:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=payload,
                    timeout=timeout
                )
            
            # Gestion des erreurs HTTP
            response.raise_for_status()
            logger.info(f"Réponse reçue de l'API OpenAI (status {response.status_code}).")
            result = response.json()

            # Vérification de la structure de la réponse
            if not (result.get("choices") and
                   isinstance(result["choices"], list) and
                   len(result["choices"]) > 0 and
                   result["choices"][0].get("message") and
                   result["choices"][0]["message"].get("content")):
                logger.error(f"Réponse inattendue ou malformée de l'API OpenAI: {result}")
                return {
                    "error": "Réponse API OpenAI malformée", 
                    "details": result
                }

            # Extraction du contenu et calcul du coût
            content_str = result["choices"][0]["message"]["content"].strip()
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            # Calcul du coût estimé
            estimated_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

            # Tentative de parser la réponse JSON
            try:
                json_result = json.loads(content_str)
                logger.info("Analyse JSON extraite avec succès.")
                
                # DEBUG: Log détaillé de ce que retourne GPT
                logger.info(f"=== DEBUG REPONSE GPT BRUTE ===")
                logger.info(f"Réponse JSON parsée: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
                anomalies = json_result.get('anomalies_potentielles_observees', [])
                logger.info(f"Anomalies détectées par GPT: {len(anomalies)}")
                for i, anomalie in enumerate(anomalies):
                    logger.info(f"  Anomalie GPT {i+1}: {anomalie}")
                logger.info(f"Note conformité GPT: {json_result.get('note_conformite_legale', 'ABSENTE')}")
                logger.info(f"Note globale GPT: {json_result.get('note_globale', 'ABSENTE')}")
                logger.info(f"=== FIN DEBUG GPT ===")
                
                return {
                    "gpt_analysis": json_result,  # JSON parsé
                    "raw": content_str,          # Contenu brut
                    "usage": usage,              # Métriques d'utilisation
                    "estimated_cost": estimated_cost  # Coût estimé
                }
            except json.JSONDecodeError as json_err:
                logger.error(f"Réponse non JSON malgré la demande: {content_str[:200]}... Erreur: {json_err}")
                return {
                    "error": "Réponse GPT non au format JSON valide",
                    "raw_analysis": content_str,
                    "details": str(json_err),
                    "usage": usage,
                    "estimated_cost": estimated_cost
                }

        except requests.exceptions.Timeout:
            logger.error("Timeout lors de l'appel à l'API OpenAI.")
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Erreur de requête vers l'API OpenAI: {req_err}", exc_info=True)
            error_details = str(req_err)
            if req_err.response is not None:
                try:
                    error_details = req_err.response.json()
                    logger.error(f"Détails de l'erreur API: {json.dumps(error_details, indent=2)}")
                except json.JSONDecodeError:
                    error_details = req_err.response.text
                    logger.error(f"Réponse d'erreur brute: {error_details}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
            raise

    def _call_responses_api(self, prompt: str, base64_images: List[str], model: str, max_tokens: int, timeout: int) -> Dict[str, Any]:
        """
        Appelle l'API Responses d'OpenAI pour GPT-5 avec support des images.
        """
        # Construction du contenu avec images pour l'API responses
        content_list = []
        
        # Ajouter le texte en premier
        content_list.append({
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": prompt}]
        })
        
        # Ajouter les images
        for b64_img in base64_images:
            content_list.append({
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{b64_img}"
                }]
            })
        
        # Format pour l'API responses
        payload = {
            "model": model,
            "input": content_list,  # 'input' au lieu de 'messages'
            "max_output_tokens": max_tokens,  # API Responses utilise max_output_tokens
            "reasoning": {"effort": "minimal"},  # Pour plus de rapidité
            "text": {
                "verbosity": "low",
                "format": {"type": "json_object"}
            },
            "store": False
        }
        
        logger.info(f"Utilisation de l'API Responses pour GPT-5")
        
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json=payload,
            timeout=timeout
        )
        
        response.raise_for_status()
        logger.info(f"Réponse reçue de l'API Responses (status {response.status_code}).")
        result = response.json()
        
        # Adapter la réponse au format attendu (supporte différents formats de Responses)
        content_str = None
        usage = result.get("usage", {})
        # Nouveau format: tableau 'output' avec un bloc 'message' contenant 'output_text'
        output_blocks = result.get("output")
        if isinstance(output_blocks, list):
            for block in output_blocks:
                if block.get("type") == "message":
                    for piece in block.get("content", []):
                        if piece.get("type") == "output_text":
                            content_str = (piece.get("text") or "").strip()
                            break
                if content_str:
                    break
        # Ancien format: champ top-level 'output_text'
        if not content_str and "output_text" in result:
            content_str = (result["output_text"] or "").strip()

        # Extraction des métriques d'usage selon les clés présentes
        prompt_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
        completion_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))

        if content_str:
            # Calcul du coût estimé
            estimated_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
            # Parser la réponse JSON
            try:
                json_result = json.loads(content_str)
                logger.info("Analyse JSON extraite avec succès via API Responses.")
                logger.info(f"=== DEBUG REPONSE GPT-5 BRUTE ===")
                logger.info(f"Réponse JSON parsée: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
                anomalies = json_result.get('anomalies_potentielles_observees', [])
                logger.info(f"Anomalies détectées par GPT-5: {len(anomalies)}")
                for i, anomalie in enumerate(anomalies):
                    logger.info(f"  Anomalie GPT-5 {i+1}: {anomalie}")
                logger.info(f"Note conformité GPT-5: {json_result.get('note_conformite_legale', 'ABSENTE')}")
                logger.info(f"Note globale GPT-5: {json_result.get('note_globale', 'ABSENTE')}")
                logger.info(f"=== FIN DEBUG GPT-5 ===")
                return {
                    "gpt_analysis": json_result,
                    "raw": content_str,
                    "usage": usage,
                    "estimated_cost": estimated_cost
                }
            except json.JSONDecodeError as json_err:
                logger.error(f"Réponse GPT-5 non JSON: {content_str[:200]}... Erreur: {json_err}")
                estimated_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
                return {
                    "error": "Réponse GPT-5 non au format JSON valide",
                    "raw_analysis": content_str,
                    "details": str(json_err),
                    "usage": usage,
                    "estimated_cost": estimated_cost
                }

        logger.error(f"Format de réponse inattendu de l'API Responses: {result}")
        return {
            "error": "Format de réponse API Responses inattendu",
            "details": result
        }

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calcule le coût estimé d'une requête API"""
        pricing = MODEL_PRICING.get(model)
        if pricing:
            cost = (prompt_tokens/1000000)*pricing["prompt"] + (completion_tokens/1000000)*pricing["completion"]
            logger.info(
                f"Coût estimé pour {model}: ${cost:.4f} "
                f"({prompt_tokens}p @${pricing['prompt']}/M, {completion_tokens}c @${pricing['completion']}/M)"
            )
            return cost
        else:
            logger.info(f"Aucun tarif défini pour le modèle {model}. Tokens: prompt={prompt_tokens}, completion={completion_tokens}")
            return None