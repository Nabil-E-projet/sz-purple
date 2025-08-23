from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine
import logging

logger = logging.getLogger(__name__)

def build_analyzer(lang="fr") -> AnalyzerEngine:
    """
    Construit un moteur d'analyse PII avec spaCy pour le français.
    """
    try:
        # Configuration explicite: liste de modèles avec lang_code requis par Presidio
        nlp = SpacyNlpEngine(models=[{"lang_code": lang, "model_name": "fr_core_news_lg"}])
        return AnalyzerEngine(nlp_engine=nlp, supported_languages=[lang])
    except OSError as e:
        logger.error(f"Erreur lors du chargement du modèle spaCy français: {e}")
        logger.error("Veuillez installer le modèle avec: python -m spacy download fr_core_news_lg")
        raise

def build_anonymizer() -> AnonymizerEngine:
    """
    Construit un moteur d'anonymisation PII.
    """
    return AnonymizerEngine()
