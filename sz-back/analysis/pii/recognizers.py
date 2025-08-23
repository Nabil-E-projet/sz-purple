import re
from presidio_analyzer import PatternRecognizer, Pattern
import logging

logger = logging.getLogger(__name__)

# Expressions régulières pour les données françaises
NIR_RE = r"\b[12]\s?\d{2}\s?(?:0[1-9]|1[0-2]|20|[3-9]\d)\s?(?:\d{2}|2A|2B|97[1-6]|98[0-8])\s?\d{3}\s?\d{3}\s?\d{2}\b"
IBAN_FR_RE = r"\bFR\d{2}\s?\d{5}\s?\d{5}\s?[A-Z0-9]{11}\s?\d{2}\b"
SIREN_RE = r"\b\d{9}\b"
SIRET_RE = r"\b\d{14}\b"
PHONE_FR_RE = r"\b(?:(?:\+33|0)\s?[1-9](?:[\s\.-]?\d{2}){4})\b"
ADDRESS_FR_RE = r"\b(\d{1,4}\s+(?:rue|avenue|av\.|bd|boulevard|impasse|chemin|all[eé]e|quai|place|faubourg|route)\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-\s]+(?:\s\d{5}\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-\s]+)?)\b"

def register_custom_recognizers(analyzer):
    """
    Enregistre les recognizers personnalisés pour les données françaises.
    
    Args:
        analyzer: AnalyzerEngine de Presidio
    """
    logger.info("Enregistrement des recognizers personnalisés français")
    
    # NIR (Numéro de Sécurité Sociale)
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="NIR_FR",
        patterns=[Pattern("nir", NIR_RE, 0.9)],
        supported_language="fr"
    ))
    
    # IBAN français
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="IBAN_FR",
        patterns=[Pattern("iban_fr", IBAN_FR_RE, 0.9)],
        supported_language="fr"
    ))
    
    # SIREN (9 chiffres)
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="SIREN_FR",
        patterns=[Pattern("siren", SIREN_RE, 0.7)],
        supported_language="fr"
    ))
    
    # SIRET (14 chiffres)  
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="SIRET_FR",
        patterns=[Pattern("siret", SIRET_RE, 0.85)],
        supported_language="fr"
    ))
    
    # Téléphone français
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        patterns=[Pattern("phone_fr", PHONE_FR_RE, 0.85)],
        supported_language="fr"
    ))
    # Adresse postale (heuristique)
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="ADDRESS_FR",
        patterns=[Pattern("address_fr", ADDRESS_FR_RE, 0.5)],
        supported_language="fr"
    ))
    
    logger.info("Recognizers personnalisés enregistrés avec succès")

# Validation NIR (clé 97 + Corse)
NIR_RE_COMPILED = re.compile(NIR_RE)

def nir_to_int(nir: str) -> int:
    """Convertit un NIR en entier pour validation."""
    s = re.sub(r"\s", "", nir).upper().replace("2A", "19").replace("2B", "18")
    return int(s[:-2])

def nir_key(nir: str) -> int:
    """Extrait la clé de contrôle d'un NIR."""
    return int(re.sub(r"\s", "", nir)[-2:])

def nir_valid(nir: str) -> bool:
    """Valide un NIR avec sa clé de contrôle."""
    try:
        return (97 - (nir_to_int(nir) % 97)) == nir_key(nir)
    except (ValueError, IndexError):
        return False
