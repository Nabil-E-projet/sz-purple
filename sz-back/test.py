import os
from PIL import Image
import pytesseract
import io

# Testez avec un PDF existant dans votre container
# Note: Cette partie nécessitera une alternative si vous voulez toujours tester l'OCR
# sur des images extraites de PDF, par exemple en utilisant pdf2image ici aussi.
# Pour l'instant, le code dépendant de fitz (PyMuPDF) est retiré.

pdf_paths = [p for p in os.listdir('/app/media/payslips') if p.endswith('.pdf')]
if pdf_paths:
    pdf_path = os.path.join('/app/media/payslips', pdf_paths[0])
    print(f"Test avec le fichier: {pdf_path}")
    
    # La section suivante utilisant fitz.open() a été retirée.
    # Si vous avez besoin de tester l'OCR, vous devrez d'abord convertir le PDF en image
    # en utilisant une méthode compatible avec votre nouvelle configuration (ex: pdf2image).
    
    # Exemple de ce que vous pourriez faire si vous convertissiez avec pdf2image:
    # from pdf2image import convert_from_path
    # images = convert_from_path(pdf_path, dpi=300)
    # if images:
    #     image = images[0]
    #     text = pytesseract.image_to_string(image, lang="fra")
    #     print(f"Texte extrait (50 premiers caractères): {text[:50]}...")
    #     print("Test (modifié) réussi!")
    # else:
    #     print("Impossible d'extraire des images du PDF pour le test OCR.")
    print("Le code dépendant de PyMuPDF a été retiré de ce fichier de test.")
    print("Adaptez ce fichier si vous avez besoin de tester l'OCR sur des PDF.")

else:
    print("Aucun PDF trouvé dans /app/media/payslips")