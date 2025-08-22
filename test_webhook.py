#!/usr/bin/env python3
"""
Script pour tester les webhooks Stripe
"""

import os
import sys
import django
import json
import requests

# Configuration Django
sys.path.append('./sz-back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salariz.settings')
django.setup()

from billing.models import Order, CreditTransaction
from users.models import CustomUser


def test_webhook_endpoint():
    """Teste si l'endpoint webhook est accessible"""
    webhook_url = "http://localhost:8000/api/billing/webhook/"
    
    print(f"🧪 Test de l'endpoint webhook: {webhook_url}")
    
    # Payload de test simple
    test_payload = {
        "id": "evt_test",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test",
                "payment_intent": "pi_test",
                "metadata": {
                    "order_id": "999",
                    "user_id": "1",
                    "credits": "5"
                }
            }
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Endpoint webhook accessible")
            return True
        else:
            print(f"❌ Erreur webhook: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("🔧 Assurez-vous que le serveur tourne sur localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def check_database_state():
    """Vérifie l'état de la base de données"""
    print("\n📊 État actuel de la base de données:")
    
    print("\n=== UTILISATEURS ===")
    for user in CustomUser.objects.all()[:5]:
        print(f"User #{user.id} ({user.email}): {user.credits} crédits")
    
    print("\n=== COMMANDES RÉCENTES ===")
    for order in Order.objects.order_by('-created_at')[:5]:
        print(f"Commande #{order.id}: {order.credits} crédits, {order.status}")
    
    print("\n=== TRANSACTIONS RÉCENTES ===")
    for tx in CreditTransaction.objects.order_by('-created_at')[:5]:
        print(f"Transaction #{tx.id}: {tx.type} {tx.amount} crédits pour user {tx.user.id}")


def check_stripe_config():
    """Vérifie la configuration Stripe"""
    from django.conf import settings
    
    print("\n🔧 Configuration Stripe:")
    print(f"STRIPE_SECRET_KEY: {'✅ Configuré' if settings.STRIPE_SECRET_KEY else '❌ Manquant'}")
    print(f"STRIPE_PUBLISHABLE_KEY: {'✅ Configuré' if settings.STRIPE_PUBLISHABLE_KEY else '❌ Manquant'}")
    print(f"STRIPE_WEBHOOK_SECRET: {'✅ Configuré' if settings.STRIPE_WEBHOOK_SECRET else '❌ Manquant'}")
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        print("\n⚠️  STRIPE_WEBHOOK_SECRET manquant !")
        print("🔧 Configurez-le avec: python setup_stripe_webhook.py")


def main():
    print("🧪 Test des webhooks Stripe pour Salariz")
    print("=" * 50)
    
    # Vérifier la configuration
    check_stripe_config()
    
    # Tester l'endpoint
    webhook_ok = test_webhook_endpoint()
    
    # État de la DB
    check_database_state()
    
    print("\n" + "=" * 50)
    if webhook_ok:
        print("✅ Tests passés ! Le système webhook semble fonctionnel")
    else:
        print("❌ Problèmes détectés avec les webhooks")
        print("🔧 Exécutez: python setup_stripe_webhook.py")


if __name__ == "__main__":
    main()
