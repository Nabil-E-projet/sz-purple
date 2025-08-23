class SecurityError(Exception):
    """
    Exception levée lors de tentatives d'envoi de données sensibles vers des services externes
    alors que le mode sécurisé est activé.
    """
    pass
