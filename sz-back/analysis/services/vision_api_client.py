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
                        model: str = "gpt-4.1",
                        temperature: float = 0.1, 
                        max_tokens: int = 4090,
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

        # Configuration de la requête
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content_list}],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            logger.info(f"Envoi de la requête à l'API OpenAI (modèle: {model})...")
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
                except json.JSONDecodeError:
                    error_details = req_err.response.text
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
            raise

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