import fitz  # PyMuPDF
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def redact_pdf(input_path: str, output_path: str, spans: List[Dict[str, Any]]) -> None:
    """
    Redacte (masque) des zones dans un PDF en dessinant des rectangles noirs.
    
    Args:
        input_path: Chemin du PDF source
        output_path: Chemin du PDF masqué de sortie
        spans: Liste des zones à masquer [{page:int, x0:float, y0:float, x1:float, y1:float}]
    """
    logger.info(f"Redaction PDF: {len(spans)} zones à masquer")
    
    doc = fitz.open(input_path)
    
    try:
        for span in spans:
            page_num = span["page"]
            
            # Vérifier que la page existe
            if page_num >= len(doc):
                logger.warning(f"Page {page_num} n'existe pas dans le PDF (total: {len(doc)})")
                continue
                
            page = doc[page_num]
            rect = fitz.Rect(span["x0"], span["y0"], span["x1"], span["y1"])
            
            # Ajouter une annotation de redaction (rectangle noir)
            page.add_redact_annot(rect, fill=(0, 0, 0))
        
        # Appliquer les redactions sur toutes les pages
        for page in doc:
            page.apply_redactions()
        
        # Sauvegarder le PDF masqué
        doc.save(output_path)
        logger.info(f"PDF redacté sauvegardé: {output_path}")
        
    finally:
        doc.close()

def results_to_spans(tokens_pages: List[List], results: List, pages_text: List[str]) -> List[Dict[str, Any]]:
    """
    Convertit les résultats PII en spans de coordonnées PDF pour redaction.
    
    Args:
        tokens_pages: Tokens avec positions par page
        results: Résultats de détection PII
        pages_text: Texte par page pour mapper les offsets
    
    Returns:
        Liste de spans avec coordonnées PDF
    """
    spans = []
    
    # Calculer les offsets de texte par page
    page_offsets = [0]
    for page_text in pages_text:
        page_offsets.append(page_offsets[-1] + len(page_text) + 1)  # +1 pour newline

    PADDING = 1.5  # points PDF

    for result in results:
        # Déterminer la page de ce résultat
        page_index = 0
        for i, offset in enumerate(page_offsets[1:]):
            if result.start < offset:
                page_index = i
                break

        # Offset relatif dans la page
        page_start_offset = page_offsets[page_index]
        relative_start = result.start - page_start_offset
        relative_end = result.end - page_start_offset

        # Trouver les tokens correspondants précis dans cette page
        if page_index < len(tokens_pages):
            page_tokens = tokens_pages[page_index]

            min_x0, min_y0 = float('inf'), float('inf')
            max_x1, max_y1 = 0, 0

            for token in page_tokens:
                # chevauchement exact via offsets tokenisés
                if token.end_offset > relative_start and token.start_offset < relative_end:
                    min_x0 = min(min_x0, token.x0)
                    min_y0 = min(min_y0, token.y0)
                    max_x1 = max(max_x1, token.x1)
                    max_y1 = max(max_y1, token.y1)

            if min_x0 != float('inf'):
                spans.append({
                    "page": page_index,
                    "x0": min_x0 - PADDING,
                    "y0": min_y0 - PADDING,
                    "x1": max_x1 + PADDING,
                    "y1": max_y1 + PADDING,
                })
    
    logger.info(f"Générés {len(spans)} spans de redaction")
    return spans
