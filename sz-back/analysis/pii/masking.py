import hmac
import hashlib
import re
from typing import Tuple

def token_hex(value: str, secret: bytes, salt: bytes) -> str:
    """
    Génère un token déterministe pour une valeur donnée.
    
    Args:
        value: Valeur à tokeniser
        secret: Clé secrète pour HMAC
        salt: Sel (peut être vide, doc_digest, etc.)
    
    Returns:
        Token hexadécimal sur 8 caractères
    """
    return hmac.new(secret, salt + value.encode(), hashlib.sha256).hexdigest()[:8].upper()

def mask_keep_edges(s: str, keep_first: int = 4, keep_last: int = 4, mask_char: str = "*") -> str:
    """
    Masque une chaîne en gardant les premiers et derniers caractères visibles.
    
    Args:
        s: Chaîne à masquer
        keep_first: Nombre de caractères à garder au début
        keep_last: Nombre de caractères à garder à la fin
        mask_char: Caractère de masquage
    
    Returns:
        Chaîne masquée format-preserving
    """
    # Supprime les espaces pour le masquage
    s2 = re.sub(r"\s", "", s)
    
    if len(s2) <= keep_first + keep_last:
        return mask_char * len(s2)
    
    return s2[:keep_first] + mask_char * (len(s2) - keep_first - keep_last) + s2[-keep_last:]
