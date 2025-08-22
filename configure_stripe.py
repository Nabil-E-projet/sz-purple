#!/usr/bin/env python3
"""
Script de configuration automatique pour Stripe
"""

import os

def create_env_file():
    """Crée le fichier .env avec la configuration Stripe"""
    
    print("🔧 Configuration de Stripe pour Salariz")
    print("=" * 50)
    
    # Demander les clés Stripe
    print("\n1. Récupérez vos clés depuis https://dashboard.stripe.com/test/apikeys")
    stripe_secret = input("Clé secrète Stripe (sk_test_...): ").strip()
    stripe_public = input("Clé publique Stripe (pk_test_...): ").strip()
    
    # Webhook secret (optionnel pour les tests locaux)
    print("\n2. Configuration webhook (optionnel pour les tests)")
    print("URL webhook: http://localhost:8000/api/billing/webhook/")
    webhook_secret = input("Secret webhook (whsec_... ou laissez vide): ").strip()
    
    # Autres configurations
    django_secret = input("\nClé secrète Django (ou laissez vide pour auto-génération): ").strip()
    if not django_secret:
        import secrets
        django_secret = secrets.token_urlsafe(50)
    
    openai_key = input("Clé OpenAI (optionnel): ").strip()
    
    # Créer le contenu du fichier .env
    env_content = f"""# Django Configuration
DEBUG=True
DJANGO_SECRET_KEY={django_secret}
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI
OPENAI_API_KEY={openai_key}

# Stripe Configuration
STRIPE_SECRET_KEY={stripe_secret}
STRIPE_PUBLISHABLE_KEY={stripe_public}
STRIPE_WEBHOOK_SECRET={webhook_secret}

# Database (SQLite par défaut)
# DATABASE_URL=postgresql://user:password@localhost:5432/salariz
"""
    
    # Écrire le fichier
    env_path = os.path.join(os.path.dirname(__file__), 'sz-back', '.env')
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ Fichier .env créé : {env_path}")
        return True
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du fichier .env : {e}")
        return False

def create_stripe_webhook():
    """Instructions pour créer le webhook Stripe"""
    print("\n🔗 Configuration du webhook Stripe:")
    print("=" * 40)
    print("1. Allez sur https://dashboard.stripe.com/test/webhooks")
    print("2. Cliquez sur 'Ajouter un endpoint'")
    print("3. URL de l'endpoint: http://localhost:8000/api/billing/webhook/")
    print("4. Événements à écouter: checkout.session.completed")
    print("5. Copiez le 'Secret de signature' dans votre fichier .env")

def test_configuration():
    """Teste la configuration"""
    print("\n🧪 Test de la configuration:")
    print("=" * 30)
    print("1. Redémarrez le serveur Django:")
    print("   cd sz-back && python manage.py runserver")
    print("2. Allez sur http://localhost:8081/buy-credits")
    print("3. La page devrait afficher 'Paiements activés ✅'")
    print("4. Testez avec une carte test: 4242 4242 4242 4242")

if __name__ == "__main__":
    if create_env_file():
        create_stripe_webhook()
        test_configuration()
        print("\n🎉 Configuration terminée ! Redémarrez le serveur pour appliquer les changements.")
    else:
        print("\n💡 Créez manuellement un fichier sz-back/.env avec votre configuration Stripe")
