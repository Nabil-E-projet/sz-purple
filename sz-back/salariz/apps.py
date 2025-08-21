from django.apps import AppConfig

class SalarizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'salariz'
    
    def ready(self):
        # Importer le thread de keep-alive
        from .keepalive import KeepAliveThread
        
        # Ne pas démarrer en mode development local
        import os
        if os.environ.get('RENDER_EXTERNAL_URL'):  # Cette variable n'existe que sur Render
            # Démarrer le thread pour Render uniquement
            keep_alive = KeepAliveThread()
            keep_alive.start()
            print("Thread de keep-alive démarré pour Render")