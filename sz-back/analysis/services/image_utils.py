"""
Utilitaires pour la manipulation et la conversion d'images
"""
import base64
import io
import logging
from PIL import Image

logger = logging.getLogger('salariz.gpt_vision')

def pil_image_to_base64(image: Image.Image, format="JPEG") -> str:
    """
    Convertit une image PIL en chaîne base64.
    
    Args:
        image: L'image PIL à convertir
        format: Le format de sortie (JPEG par défaut)
        
    Returns:
        La chaîne base64 encodée de l'image
    """
    buffered = io.BytesIO()
    if image.mode == 'RGBA' or image.mode == 'P':  # Check for RGBA or P (paletted) mode
        image = image.convert('RGB')  # Convert to RGB to ensure JPEG compatibility
    image.save(buffered, format=format, quality=70)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def image_file_to_base64(image_path: str) -> str:
    """
    Charge une image depuis un fichier et la convertit en base64.
    
    Args:
        image_path: Chemin vers le fichier image
        
    Returns:
        La chaîne base64 encodée de l'image
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')