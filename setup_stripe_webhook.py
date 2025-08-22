#!/usr/bin/env python3
"""
Script pour configurer automatiquement les webhooks Stripe
"""

import os
import sys
import subprocess


def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def check_stripe_cli():
    """Vérifie si Stripe CLI est installé"""
    stdout, stderr, code = run_command("stripe --version")
    if code == 0:
        print(f"✅ Stripe CLI trouvé: {stdout}")
        return True
    else:
        print("❌ Stripe CLI non trouvé")
        print("📥 Installez-le avec: brew install stripe/stripe-cli/stripe")
        return False


def setup_webhook():
    """Configure le webhook Stripe"""
    print("\n🔧 Configuration du webhook Stripe...")
    
    # Créer le webhook endpoint
    webhook_url = "http://localhost:8000/api/billing/webhook/"
    
    print(f"🌐 URL du webhook: {webhook_url}")
    print("\n📋 Étapes à suivre:")
    print("1. Ouvrez votre dashboard Stripe: https://dashboard.stripe.com/test/webhooks")
    print("2. Cliquez sur 'Add endpoint'")
    print(f"3. URL: {webhook_url}")
    print("4. Events: checkout.session.completed")
    print("5. Copiez le 'Signing secret' qui commence par 'whsec_'")
    print("6. Ajoutez-le à votre .env comme STRIPE_WEBHOOK_SECRET=whsec_...")
    
    print("\n🚀 Alternative avec Stripe CLI (recommandé pour les tests):")
    print("stripe listen --forward-to localhost:8000/api/billing/webhook/")
    print("(Copiez le webhook secret affiché)")


def update_env_file():
    """Met à jour le fichier .env"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print(f"\n📄 Création du fichier {env_path}")
        with open(env_path, "w") as f:
            f.write("# Configuration Stripe\n")
            f.write("STRIPE_SECRET_KEY=sk_test_...\n")
            f.write("STRIPE_PUBLISHABLE_KEY=pk_test_...\n")
            f.write("STRIPE_WEBHOOK_SECRET=whsec_...\n")
        print(f"✅ Fichier {env_path} créé")
    else:
        print(f"✅ Fichier {env_path} existant")
    
    print(f"\n📝 Éditez le fichier {env_path} avec vos clés Stripe")


def main():
    print("🎯 Configuration des webhooks Stripe pour Salariz")
    print("=" * 50)
    
    # Vérifier Stripe CLI
    if not check_stripe_cli():
        print("\n🔧 Vous pouvez aussi configurer manuellement via le dashboard Stripe")
    
    # Instructions pour les webhooks
    setup_webhook()
    
    # Configuration .env
    update_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Configuration terminée !")
    print("\n🔄 N'oubliez pas de redémarrer le serveur Django après avoir mis à jour .env")
    print("🧪 Testez avec: python test_webhook.py")


if __name__ == "__main__":
    main()
