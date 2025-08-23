from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import pdfplumber
import hashlib
from ..utils.types import PageToken

@dataclass
class IngestResult:
    doc_sha256: str
    pages: List[str]                # texte par page
    tokens: List[List[PageToken]]   # tokens avec bbox par page (x0,y0,x1,y1, page_index)

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def ingest_pdf(path: str, use_ocr: bool=False) -> IngestResult:
    """
    Ingère un PDF en extrayant le texte natif et les positions des mots.
    
    Args:
        path: Chemin vers le fichier PDF
        use_ocr: Si True, utilise l'OCR en fallback (pas implémenté dans ce POC)
    
    Returns:
        IngestResult avec texte par page et tokens positionnés
    """
    with open(path, "rb") as f:
        raw = f.read()
    digest = sha256_bytes(raw)
    
    pages_text: List[str] = []
    tokens: List[List[PageToken]] = []
    
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            if words:
                # Construire texte + offsets tokenisés précis
                page_text_parts = []
                page_tokens: list[PageToken] = []
                cursor = 0
                for idx, w in enumerate(words):
                    text = w["text"] or ""
                    start = cursor
                    end = start + len(text)
                    page_text_parts.append(text)
                    # Ajouter un espace entre mots sauf après le dernier
                    if idx < len(words) - 1:
                        page_text_parts.append(" ")
                        cursor = end + 1
                    else:
                        cursor = end
                    page_tokens.append(
                        PageToken(
                            text=text,
                            x0=w["x0"],
                            y0=w["top"],
                            x1=w["x1"],
                            y1=w["bottom"],
                            page_index=i,
                            start_offset=start,
                            end_offset=end,
                        )
                    )
                page_text = "".join(page_text_parts)
                pages_text.append(page_text)
                tokens.append(page_tokens)
            else:
                # Page vide ou sans texte extractible
                pages_text.append("")
                tokens.append([])
    
    # TODO: Si aucun texte et OCR autorisé → utiliser Tesseract
    # if not any(pages_text) and use_ocr:
    #     # Implémentation OCR Tesseract à ajouter si nécessaire
    #     pass
    
    return IngestResult(doc_sha256=digest, pages=pages_text, tokens=tokens)
