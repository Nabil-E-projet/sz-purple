"""
Utilitaires de conversion PDF en images
"""
import os
import logging
import traceback
from typing import List, Optional, Dict, Any
from PIL import Image

logger = logging.getLogger('salariz.gpt_vision')

def convert_pdf_to_images(pdf_path: str, max_pages: Optional[int] = None, dpi: int = 150) -> List[Image.Image]:
    """
    Convertit un PDF en liste d'images PIL.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        max_pages: Nombre maximum de pages à convertir (None = toutes)
        dpi: Résolution des images en DPI
        
    Returns:
        Liste des images PIL correspondant aux pages du PDF
        
    Raises:
        FileNotFoundError: Si le fichier PDF n'existe pas
        ImportError: Si pdf2image n'est pas installé
        Exception: Pour les autres erreurs de conversion
    """
    if not os.path.exists(pdf_path):
        logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
        raise FileNotFoundError(f"Fichier PDF non trouvé: {pdf_path}")

    try:
        from pdf2image import convert_from_path # type: ignore
        
        # Prépare les arguments pour la conversion
        kwargs = {"dpi": dpi, "first_page": 1}
        if max_pages is not None:
            kwargs["last_page"] = max_pages

        # Conversion du PDF
        pages = convert_from_path(pdf_path, **kwargs)
        logger.info(f"Conversion réussie de {len(pages)} page(s) du PDF: {pdf_path}")
        
        return pages

    except ImportError:
        logger.error(
            "Le module 'pdf2image' n'est pas installé ou Poppler non configuré. "
            "Installez pdf2image et assurez-vous que Poppler est dans votre PATH."
        )
        raise ImportError("Dépendance manquante: pdf2image ou Poppler non configuré")
    except Exception as e:
        logger.error(f"Erreur lors de la conversion PDF de {pdf_path}: {e}", exc_info=True)
        raise