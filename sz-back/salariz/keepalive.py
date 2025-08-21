import threading
import time
import requests
import logging

logger = logging.getLogger('salariz.keepalive')

class KeepAliveThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.interval = kwargs.pop('interval', 840)  # 14 minutes (en secondes)
        self.host = kwargs.pop('host', 'https://salariz-backend-1.onrender.com')
        super().__init__(*args, **kwargs)
        self.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête

    def run(self):
        """Exécute une requête HTTP vers notre propre serveur à intervalles réguliers."""
        # Attendre un peu au démarrage
        time.sleep(30)
            
        while True:
            try:
                url = f"{self.host}/health/"
                response = requests.get(url, timeout=10)
                logger.info(f"Keep-alive ping envoyé à {url} - Statut: {response.status_code}")
            except Exception as e:
                logger.error(f"Échec du ping keep-alive: {str(e)}")
            
            # Attendre l'intervalle spécifié avant le prochain ping
            time.sleep(self.interval)