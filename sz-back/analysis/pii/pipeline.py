from typing import Dict, Any, List
from .engine import build_analyzer
from .recognizers import register_custom_recognizers
from .masking import token_hex, mask_keep_edges
from django.conf import settings as dj
from presidio_analyzer import RecognizerResult
import logging

logger = logging.getLogger(__name__)

# Whitelist des termes à ne jamais masquer (contexte métier)
WHITELIST = {
    "Salaire de base", "Convention collective", "Cadre", "Prime", "Cotisation",
    "URSSAF", "POLE EMPLOI", "AGIRC", "ARRCO", "Sécurité Sociale", "Mutuelle",
    "Temps partiel", "Temps plein", "CDI", "CDD", "Intérimaire",
    "NET A PAYER", "Net payé", "Net imposable", "Brut", "SMIC", "Cumul"
}

def detect_pii(text: str) -> List[RecognizerResult]:
    """
    Détecte les données personnelles dans un texte.
    
    Args:
        text: Texte à analyser
    
    Returns:
        Liste des entités PII détectées avec positions et scores
    """
    logger.info(f"Détection PII sur {len(text)} caractères")
    
    analyzer = build_analyzer()
    register_custom_recognizers(analyzer)
    
    results = analyzer.analyze(
        text,
        language="fr",
        entities=["PERSON", "NIR_FR", "IBAN_FR", "SIRET_FR", "SIREN_FR", "PHONE_NUMBER", "EMAIL_ADDRESS"]
    )
    
    logger.info(f"Détectées {len(results)} entités PII potentielles")
    return results

def pseudonymize(text: str, results: List[RecognizerResult], doc_digest: str) -> str:
    """
    Pseudonymise un texte en remplaçant les PII détectées par des tokens ou masques.
    
    Args:
        text: Texte original
        results: Entités PII détectées
        doc_digest: Digest du document pour les tokens déterministes
    
    Returns:
        Texte pseudonymisé
    """
    logger.info(f"Pseudonymisation de {len(results)} entités")
    
    secret = getattr(dj, 'PII_SECRET', 'dev-fallback-secret').encode()
    salt = (doc_digest if getattr(dj, 'PII_PERSON_SCOPE', 'document') == "document" else "").encode()
    
    # Convertir le texte en liste pour modification en place
    out = list(text)
    
    # Traiter de droite à gauche pour conserver les indices
    for r in sorted(results, key=lambda x: x.start, reverse=True):
        value = text[r.start:r.end]
        
        # Vérifier la whitelist
        if value in WHITELIST: 
            logger.debug(f"Valeur '{value}' dans la whitelist, non masquée")
            continue
        
        # Génerer le remplacement selon le type d'entité
        if r.entity_type == "PERSON" and r.score >= 0.65:
            repl = f"[PERSON_{token_hex(value, secret, salt)}]"
            logger.debug(f"PERSON '{value}' -> {repl}")
            
        elif r.entity_type in {"NIR_FR", "IBAN_FR", "PHONE_NUMBER", "EMAIL_ADDRESS"} and r.score >= 0.85:
            repl = f"[{r.entity_type}:{mask_keep_edges(value)}]"
            logger.debug(f"{r.entity_type} '{value}' -> {repl}")
            
        elif r.entity_type in {"SIRET_FR", "SIREN_FR"} and r.score >= 0.85:
            repl = f"[{r.entity_type}:{mask_keep_edges(value)}]"
            logger.debug(f"{r.entity_type} '{value}' -> {repl}")
            
        else:
            # Score trop faible, on ignore
            logger.debug(f"Entité '{r.entity_type}' score {r.score} trop faible, ignorée")
            continue
        
        # Remplacer dans le texte
        out[r.start:r.end] = list(repl)
    
    pseudonymized_text = "".join(out)
    logger.info("Pseudonymisation terminée")
    return pseudonymized_text

def create_pii_report(results: List[RecognizerResult], pages_text: List[str]) -> List[Dict[str, Any]]:
    """
    Crée un rapport PII sans les valeurs sensibles.
    
    Args:
        results: Entités détectées
        pages_text: Textes par page (pour déterminer la page)
    
    Returns:
        Rapport PII avec types, scores et positions (sans valeurs)
    """
    report = []
    
    # Calculer les offsets de page pour déterminer sur quelle page est chaque entité
    page_offsets = [0]
    for page_text in pages_text:
        page_offsets.append(page_offsets[-1] + len(page_text) + 1)  # +1 pour le saut de ligne
    
    for r in results:
        # Déterminer la page
        page_index = 0
        for i, offset in enumerate(page_offsets[1:]):
            if r.start < offset:
                page_index = i
                break
        
        report.append({
            "type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": round(r.score, 3),
            "page": page_index,
            "length": r.end - r.start
        })
    
    return report
