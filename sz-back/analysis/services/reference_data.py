"""
Données de référence pour l'analyse des fiches de paie
"""
import os
from django.conf import settings

# Chemin vers le répertoire des données
DATA_DIR = os.path.join(settings.BASE_DIR, 'data')

def load_text_file(filename):
    """Charge le contenu d'un fichier texte depuis le répertoire data."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # En cas de fichier manquant, on retourne une chaîne vide pour ne pas bloquer l'analyse.
        return ""

def get_convention_collective_text(convention_code: str) -> str:
    """
    Récupère le texte de la convention collective basé sur son code.
    Le code doit correspondre au nom du fichier .txt en minuscules (ex: 'SYNTEC' -> 'syntec.txt').
    """
    if not convention_code or convention_code == 'AUTRE':
        return "Aucune convention collective spécifique n'a été sélectionnée pour cette analyse."
    
    filename = f"{convention_code.lower()}.txt"
    content = load_text_file(filename)
    
    if not content:
        return f"Les données pour la convention collective '{convention_code}' n'ont pas pu être chargées. L'analyse se fera sans ce contexte."
        
    return f"EXTRAITS PERTINENTS DE LA CONVENTION COLLECTIVE {convention_code.upper()} (À CONSIDÉRER POUR L'ANALYSE) :\n{content}"

# On charge les données SMIC qui sont toujours nécessaires
SMIC_DATA = load_text_file('smic.csv')

# Assure-toi de supprimer l'ancienne variable SYNTEC_TEXT si elle existe encore dans ce fichier.

# Tarifs par modèle (USD par 1000 tokens) avec les prix Batch API
MODEL_PRICING = {
    # GPT‑5 family
    "gpt-5":       {"prompt": 1.25,  "completion": 10.00},
    "gpt-5-mini":  {"prompt": 0.25,  "completion": 2.00},
    "gpt-5-nano":  {"prompt": 0.05,  "completion": 0.40},
    # Legacy/alternatives (conservés si besoin)
    "gpt-4.1":      {"prompt": 1.00,  "completion": 4.00},
    "gpt-4.1-mini": {"prompt": 0.20,  "completion": 0.80},
    "gpt-4.1-nano": {"prompt": 0.05,  "completion": 0.20},
    "gpt-4o":       {"prompt": 1.25,  "completion": 5.00},
    "gpt-4o-mini":  {"prompt": 0.075, "completion": 0.30},
    "o1-mini":      {"prompt": 0.55,  "completion": 2.20},
    "o3-mini":      {"prompt": 0.55,  "completion": 2.20},
    "o4-mini":      {"prompt": 0.55,  "completion": 2.20},
}