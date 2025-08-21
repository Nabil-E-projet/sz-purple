import logging
import os
import traceback
from typing import Dict, Any, List, Optional
import json

from django.conf import settings
from PIL import Image

from .image_utils import pil_image_to_base64, image_file_to_base64
from .pdf_converter import convert_pdf_to_images
from .vision_api_client import OpenAIVisionClient
# On importe seulement SMIC_DATA, SYNTEC_TEXT est maintenant géré dynamiquement
from .reference_data import SMIC_DATA

logger = logging.getLogger('salariz.gpt_vision')

class GPTVisionService:
    """
    Service d'analyse de fiches de paie avec GPT-4 Vision.
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("Clé API OpenAI non fournie. L'analyse GPT Vision sera désactivée.")
        
        # Le texte de la convention n'est plus chargé ici, il sera passé dynamiquement.
        # On réduit la taille du tableau SMIC pour limiter les tokens envoyés
        self.smic_data_for_prompt = self._prepare_smic_excerpt(SMIC_DATA)
        self.api_client = OpenAIVisionClient(self.api_key) if self.api_key else None

    def analyze_multiple_images(self, base64_images: List[str], additional_data: Dict = None) -> Dict[str, Any]:
        """
        Analyse plusieurs images de fiche de paie avec GPT Vision.
        """
        if not self.api_key:
            logger.error("Clé API OpenAI manquante.")
            return {"error": "Clé API OpenAI non configurée"}

        if not base64_images:
            return {"error": "Aucune image fournie pour l'analyse"}

        # Construction des informations contextuelles
        user_context_details = self._build_context_from_additional_data(additional_data)
        user_context_prompt = "\nCONTEXTE SUPPLÉMENTAIRE FOURNI PAR L'UTILISATEUR (À UTILISER POUR L'ANALYSE):\n" + "\n".join(user_context_details) if user_context_details else "\nAucun contexte utilisateur spécifique fourni."

        # Construction des guidelines pour la détection d'anomalies
        anomaly_detection_guidelines = self._build_anomaly_detection_guidelines(additional_data)

        # Construction du prompt principal
        prompt = self._build_analysis_prompt(user_context_prompt, anomaly_detection_guidelines, additional_data)

        # DEBUG: Log de ce qui est envoyé à GPT
        logger.info(f"=== DEBUG DONNEES ENVOYEES A GPT ===")
        logger.info(f"Nombre d'images: {len(base64_images)}")
        logger.info(f"Contexte utilisateur: {user_context_prompt}")
        logger.info(f"Données additionnelles reçues: {additional_data}")
        logger.info(f"Taille du prompt final: {len(prompt)} caractères")
        logger.info(f"Début du prompt: {prompt[:500]}...")
        logger.info(f"=== FIN DEBUG DONNEES GPT ===")

        try:
            # Appel à l'API Vision
            # Laisser le client choisir le modèle par défaut via settings (gpt-5-mini)
            return self.api_client.call_vision_api(prompt, base64_images)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des images: {str(e)}", exc_info=True)
            return {"error": f"Erreur interne: {str(e)}", "traceback": traceback.format_exc()}

    def analyze_pdf(self, pdf_path: str, max_pages: Optional[int] = None, additional_data: Dict = None) -> Dict[str, Any]:
        """
        Convertit un PDF en images et l'analyse avec GPT Vision.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
            return {"error": "Fichier PDF non trouvé"}

        try:
            # Conversion du PDF en images
            pages = convert_pdf_to_images(pdf_path, max_pages)
            
            if not pages:
                logger.warning(f"Aucune page extraite du PDF: {pdf_path}")
                return {"error": "Impossible d'extraire des images du PDF"}

            # Conversion des images en base64
            base64_images = [pil_image_to_base64(page) for page in pages]
            logger.info(f"Envoi de {len(base64_images)} page(s) à l'API pour analyse.")
            
            # Analyse des images
            return self.analyze_multiple_images(base64_images, additional_data)

        except ImportError:
            logger.error("Le module 'pdf2image' n'est pas installé ou Poppler non configuré.")
            return {"error": "Dépendance manquante: pdf2image ou Poppler non configuré"}
        except Exception as e:
            logger.error(f"Erreur lors de la conversion/analyse du PDF: {e}", exc_info=True)
            return {
                "error": f"Erreur de conversion/analyse PDF: {e}",
                "traceback": traceback.format_exc()
            }

    def analyze_document_image(self, image_path: str, additional_data: Dict = None) -> Dict[str, Any]:
        """
        Analyse une image de document (méthode rétrocompatible).
        """
        logger.warning("La méthode analyze_document_image est obsolète, veuillez utiliser analyze_pdf.")
        if not self.api_key:
            return {"error": "Clé API OpenAI non configurée"}
        
        try:
            base64_image = image_file_to_base64(image_path)
            return self.analyze_multiple_images([base64_image], additional_data)
        except FileNotFoundError:
            logger.error(f"Fichier image non trouvé: {image_path}")
            return {"error": "Fichier image non trouvé"}
        except Exception as e:
            logger.error(f"Erreur interne inattendue: {str(e)}", exc_info=True)
            return {"error": f"Erreur interne: {str(e)}", "traceback": traceback.format_exc()}

    def _build_context_from_additional_data(self, additional_data: Dict) -> List[str]:
        """Construit les éléments de contexte à partir des données supplémentaires"""
        user_context_details = []
        if not additional_data:
            return user_context_details
            
        if additional_data.get('contractual_salary'):
            user_context_details.append(f"- Salaire brut mensuel contractuel indiqué: {additional_data['contractual_salary']}€")
        
        if additional_data.get('additional_details'):
            user_context_details.append(f"- Détails supplémentaires fournis par l'utilisateur: {additional_data['additional_details']}")
        
        user_convention = additional_data.get('convention_collective')
        if user_convention:
            user_context_details.append(f"- Convention collective indiquée par l'utilisateur: {user_convention}")
        
        payment_date_str = additional_data.get('date_paiement')
        if payment_date_str:
            user_context_details.append(f"- Date de paiement indiquée (pour référence SMIC): {payment_date_str}")
            
        return user_context_details

    def _build_anomaly_detection_guidelines(self, additional_data: Dict) -> str:
        """Construit les directives de détection d'anomalies"""
        return f"""UTILISE IMPÉRATIVEMENT LES INFORMATIONS FOURNIES (CONTEXTE UTILISATEUR, TABLEAU SMIC, EXTRAITS DE CONVENTION) POUR AFFINER TON ANALYSE ET DÉTECTER LES ANOMALIES POTENTIELLES, notamment:
- Écart significatif (>2%) entre le salaire contractuel indiqué (si fourni) et le salaire de base brut extrait.
- Si une convention collective est spécifiée, confronter les informations extraites avec les extraits de la convention fournis.
- Vérifier si le taux horaire extrait est cohérent avec le salaire de base et les heures de base.
- Signaler si le taux horaire extrait est inférieur au SMIC de référence (consulter le tableau SMIC fourni et choisir la valeur la plus pertinente pour la période de la fiche de paie).
- Tiens compte des 'Détails supplémentaires fournis par l'utilisateur' pour interpréter les chiffres (ex: un temps partiel, un statut d'apprenti, une absence justifierait un salaire plus bas que le contractuel temps plein).
"""

    def _build_analysis_prompt(self, user_context_prompt: str, anomaly_detection_guidelines: str, additional_data: Dict) -> str:
        """Construit le prompt complet pour l'analyse"""
        contractual_salary_context = additional_data.get('contractual_salary', 'NON FOURNI')
        # On récupère dynamiquement le texte de la convention depuis les données additionnelles
        convention_collective_text = additional_data.get('convention_collective_text', 'Aucune convention collective spécifiée.')
        # On tronque le texte de la convention pour éviter les prompts trop volumineux
        try:
            from django.conf import settings as dj_settings
            max_chars = getattr(dj_settings, 'CONVENTION_TEXT_MAX_CHARS', 3000)
        except Exception:
            max_chars = 3000
        if convention_collective_text and len(convention_collective_text) > max_chars:
            convention_collective_text = convention_collective_text[:max_chars] + "\n[...]"

        return f"""
        Tu es un expert en analyse de fiches de paie françaises. Tu vas recevoir plusieurs images représentant les pages consécutives d'UNE SEULE fiche de paie. Analyse l'ensemble des pages.

        CONTEXTE IMPORTANT POUR L'ANALYSE (POC):
        {self.smic_data_for_prompt}
        
        CONTEXTE SPÉCIFIQUE À LA CONVENTION COLLECTIVE:
        {convention_collective_text}

        {user_context_prompt}

        TÂCHE:
        Extrait les informations clés de cette fiche de paie en te basant sur TOUTES les pages fournies et le contexte ci-dessus. Identifie les anomalies potentielles. Structure ta réponse au format JSON demandé.
        
        IMPORTANT: CALCULE ÉGALEMENT UN "MONTANT POTENTIELLEMENT DÛ AU SALARIÉ" si tu détectes des erreurs claires en sa défaveur.
        Pour ce calcul, suis CET ORDRE DE PRIORITÉ:
        1.  **ÉCART AU SALAIRE CONTRACTUEL (PRIORITAIRE SI CONTEXTE UTILISATEUR PERTINENT, EX: APPRENTI, TEMPS PARTIEL INDIQUÉ DANS LES DÉTAILS SUPPLÉMENTAIRES)**:
            Si un salaire brut mensuel contractuel attendu est fourni dans le CONTEXTE UTILISATEUR (par exemple, "{contractual_salary_context}€") et que le `salaire_de_base_brut` extrait de la fiche de paie est inférieur à ce montant contractuel (en tenant compte des `additional_details` qui pourraient justifier un montant inférieur, comme un temps partiel), alors le `montant_potentiel_du_salarie` principal est la différence: `salaire_contractuel_attendu_ajusté_si_nécessaire - salaire_de_base_brut_extrait`. L'explication doit clairement se baser sur cet écart par rapport au salaire contractuel attendu et aux détails fournis.
        2.  **ÉCART AU SMIC HORAIRE GÉNÉRAL (SUBSIDIAIRE)**:
            Si aucun salaire contractuel pertinent n'est fourni dans le contexte, OU si le salaire contractuel est respecté MAIS que le `taux_horaire` extrait semble incorrect par rapport au SMIC général:
            Si le `taux_horaire` extrait est inférieur au SMIC horaire applicable (voir tableau SMIC fourni), calcule le différentiel dû sur les `heures_travaillees_base` extraites. `montant_potentiel_du_salarie` = (`SMIC_horaire_applicable - taux_horaire_extrait`) * `heures_travaillees_base_extraites`.
        3.  **AJOUTS POUR HEURES SUPPLÉMENTAIRES / PRIMES**:
            Si des heures supplémentaires semblent non payées ou sous-payées, ajoute le montant estimé au montant calculé précédemment.
            Si une prime ou indemnité obligatoire (ex: prime de vacances Syntec si applicable et non versée) est absente, ajoute le montant estimé.
        
        - Fournis une explication concise et claire pour le `montant_potentiel_du_salarie` total calculé, en indiquant la base principale du calcul (écart au contractuel ou écart au SMIC général).
        - Si aucun montant n'est clairement dû, indique 0 ou null pour `montant_potentiel_du_salarie`.

        {anomaly_detection_guidelines}

        INSTRUCTIONS IMPORTANTES:
        1. Considère toutes les images comme un seul document. Synthétise les informations.
        2. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou après. Le JSON doit commencer par `{{` et finir par `}}`.
        3. Si une information n'est pas visible ou identifiable sur l'ensemble des pages, utilise la valeur `null`.
        4. Montants financiers: valeurs numériques (ex: 1500.50). Point comme séparateur décimal. N'inclus pas de symboles monétaires ou de séparateurs de milliers dans les valeurs numériques.
        5. Dates: format JJ/MM/AAAA si possible. Sinon, utilise le format tel qu'il apparaît.
        6. N'invente AUCUNE information. Base-toi strictement sur le contenu visible et le contexte fourni.
        7. Heures supplémentaires: extraire nombre d'heures et taux de majoration si possible.
        8. Anomalies: sois précis, justifie en te basant sur les règles fournies ou incohérences.

        FORMAT DE RÉPONSE JSON ATTENDU (NE PAS INCLURE LES COMMENTAIRES DANS LE JSON FINAL):
        ```json
        {{
            "informations_generales": {{
            "nom_salarie": string | null,
            "poste": string | null,
            "classification_conventionnelle": string | null,
            "nom_entreprise": string | null,
            "siret_entreprise": string | null,
            "convention_collective_applicable": string | null
            }},
            "periode": {{
            "periode_du": string | null,
            "periode_au": string | null,
            "date_paiement": string | null
            }},
            "remuneration": {{
            "salaire_de_base_brut": number | null,
            "salaire_brut_total": number | null,
            "total_cotisations_salariales": number | null,
            "net_imposable": number | null,
            "impot_preleve_a_la_source": number | null,
            "net_a_payer_avant_acomptes": number | null,
            "net_a_payer": number | null,
            "taux_horaire": number | null,
            "heures_travaillees_base": number | null,
            "heures_supplementaires_majorees": [ {{ "nombre": number, "taux_majoration_pourcent": number }} ] | null,
            "total_heures_travaillees_mois": number | null
            }},
            "conges_et_absences": {{
            "conges_payes_acquis": number | null,
            "conges_payes_pris": number | null,
            "solde_conges_payes": number | null,
            "rtt_acquis": number | null,
            "rtt_pris": number | null,
            "solde_rtt": number | null
            }},
            "anomalies_potentielles_observees": [
            {{ "type": string, "description": string, "level": "critical" | "warning" | "info" | "positive_check" }}
            ],
            "evaluation_financiere_salarie": {{
            "montant_potentiel_du_salarie": number | null,
            "explication_montant_du": string | null
            }}
        }}
        ```
        NOTE SUR LES ANOMALIES ET MONTANT DÛ (RAPPEL):
        - **Salaire de base / Taux horaire**: Si un salaire contractuel est fourni par l'utilisateur (ex: "{contractual_salary_context}€"), l'anomalie principale doit porter sur l'écart entre le `salaire_de_base_brut` extrait et ce salaire contractuel. Prends en compte les `additional_details` (ex: temps partiel, absence longue) pour évaluer si un salaire de base inférieur au contractuel est justifié. Le calcul du montant dû doit prioriser cet écart. La comparaison du `taux_horaire` au SMIC général devient alors une vérification secondaire.
        - **Cotisations Apprenti**: Si le statut d'apprenti est identifié (via le contexte utilisateur, les `additional_details` ou la fiche de paie) et que le `total_cotisations_salariales` est nul ou très faible, cela est généralement normal. Signale-le comme une "Observation" ou une caractéristique du statut plutôt qu'une "Anomalie" critique, sauf si d'autres éléments indiquent une erreur.
        - Calculs (brut/net, heures*taux): signaler si écart >5% ou >10€. Si en défaveur du salarié, estime le montant.
        - Heures supplémentaires: si des HS sont mentionnées mais non payées ou sous-payées, estime le dû.
        - Si aucune anomalie conduisant à un montant dû, renvoyer "montant_potentiel_du_salarie": 0 (ou null) et une explication comme "Aucun montant clairement dû détecté".
        """

    def _prepare_smic_excerpt(self, smic_csv: str, last_n: int = 18) -> str:
        """Retourne l'en-tête + les N dernières lignes du tableau SMIC pour limiter la taille du prompt."""
        if not smic_csv:
            return smic_csv
        lines = [ln for ln in smic_csv.splitlines() if ln.strip()]
        if not lines:
            return smic_csv
        header = lines[0]
        data = lines[1:]
        tail = data[-last_n:] if len(data) > last_n else data
        return "\n".join([header] + tail)