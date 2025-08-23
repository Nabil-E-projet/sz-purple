from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

def build_minimal_extract(text_pages: List[str]) -> Dict[str, Any]:
    """
    Extrait uniquement les champs nécessaires pour l'analyse, sans PII.
    
    Args:
        text_pages: Liste des textes par page (déjà pseudonymisés)
    
    Returns:
        Dictionnaire avec les champs métier essentiels
    """
    text = "\n".join(text_pages)
    logger.info(f"Extraction minimale sur {len(text)} caractères de texte pseudonymisé")
    
    def find_amount(pattern: str) -> str:
        """Trouve un montant avec un pattern regex."""
        match = re.search(pattern + r".{0,20}([\d\.,]+)", text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def find_text(pattern: str) -> str:
        """Trouve du texte avec un pattern regex."""
        match = re.search(pattern + r".{0,50}([A-Za-z0-9\s\-\.]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    # Heuristiques simples pour l'extraction de champs métier
    extract = {
        "version": "1.0.0",
        "extraction_date": None,  # Sera ajouté par le service appelant
        
        # Période de travail (sans identifier la personne)
        "periode": {
            "mois": find_text(r"(?:période|mois|du)\s+(\d{1,2}[/\-]\d{4}|\w+\s+\d{4})"),
            "annee": find_text(r"(\d{4})"),
        },
        
        # Temps de travail
        "heures": {
            "heures_base": find_amount(r"Heures?\s*(?:de\s*)?base|Base\s*heures?"),
            "heures_sup": find_amount(r"Heures?\s*suppl(?:émentaires?)?"),
            "heures_total": find_amount(r"Total\s*heures?"),
        },
        
        # Taux et coefficients (informations du contrat)
        "taux": {
            "taux_horaire": find_amount(r"Taux\s*h(?:oraire)?|SMIC\s*h(?:oraire)?"),
            "coefficient": find_amount(r"Coef(?:ficient)?|Niveau|Échelon"),
        },
        
        # Montants financiers (anonymisés)
        "remuneration": {
            "salaire_base": find_amount(r"Salaire\s*(?:de\s*)?base|Base\s*salaire"),
            "brut_total": find_amount(r"(?:Salaire\s*)?[Bb]rut(?:\s*total)?"),
            "net_imposable": find_amount(r"Net\s*impos(?:able)?"),
            "net_a_payer": find_amount(r"Net\s*(?:à|a)\s*payer"),
        },
        
        # Cotisations sociales (montants uniquement, pas les organismes identifiants)
        "cotisations": {
            "base_secu": find_amount(r"Base\s*(?:sécurité\s*sociale|S[ée]cu|SS)"),
            "total_cotisations_salariales": find_amount(r"Total\s*cotisations?\s*salariales?"),
            "total_cotisations_patronales": find_amount(r"Total\s*cotisations?\s*patronales?"),
        },
        
        # Informations sur la convention (sans identifier l'employeur)
        "convention": {
            "type_detecte": find_text(r"Convention\s*collective\s*([A-Z\s\-]+)"),
            "classification": find_text(r"(?:Cadre|ETAM|Ouvrier|Employé|Agent)"),
            "statut": find_text(r"(?:CDI|CDD|Intérimaire|Temps\s*partiel|Temps\s*plein)"),
        },
        
        # Primes et avantages (montants seulement)
        "primes": {
            "prime_anciennete": find_amount(r"Prime\s*(?:d')?ancienneté"),
            "prime_transport": find_amount(r"Prime\s*transport|Indemnité\s*transport"),
            "prime_repas": find_amount(r"Prime\s*repas|Tickets?\s*restaurant"),
            "autres_primes": [],  # Sera peuplé par une analyse plus fine si nécessaire
        }
    }
    
    # Nettoyer les valeurs None et vides
    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if v is not None and v != ""}
        return d
    
    cleaned_extract = clean_dict(extract)
    
    logger.info(f"Extraction terminée: {len(str(cleaned_extract))} caractères de métadonnées")
    return cleaned_extract
