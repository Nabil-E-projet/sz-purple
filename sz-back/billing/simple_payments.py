"""
Alternatives simples à Stripe pour les paiements
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Order, CreditTransaction
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class PayPalExpressView(APIView):
    """Alternative PayPal plus simple que Stripe"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        pack = request.data.get('pack', 'pack_5')
        
        # Configuration des packs (même que Stripe)
        if pack == 'pack_5':
            credits = 5
            amount = "4.90"
        elif pack == 'pack_20':
            credits = 20
            amount = "15.90"
        else:
            credits = 1
            amount = "1.99"
        
        # Créer une commande
        order = Order.objects.create(
            user=request.user,
            credits=credits,
            amount_cents=int(float(amount.replace(',', '.')) * 100),
            currency='eur',
        )
        
        # URL PayPal simple (sandbox)
        paypal_url = f"https://www.sandbox.paypal.com/cgi-bin/webscr"
        paypal_params = {
            'cmd': '_xclick',
            'business': 'sb-c9o1b31470229@business.example.com',  # Votre email PayPal
            'item_name': f'Salariz - {credits} crédit(s)',
            'amount': amount,
            'currency_code': 'EUR',
            'return': 'http://localhost:8080/?payment=success',
            'cancel_return': 'http://localhost:8080/?payment=cancel',
            'notify_url': request.build_absolute_uri('/api/billing/paypal-ipn/'),
            'custom': str(order.id),
        }
        
        # Construire l'URL
        params_str = '&'.join([f"{k}={v}" for k, v in paypal_params.items()])
        checkout_url = f"{paypal_url}?{params_str}"
        
        return Response({'checkout_url': checkout_url})


class ManualPaymentView(APIView):
    """Paiement manuel pour tests/démo"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        pack = request.data.get('pack', 'pack_5')
        simulate_success = request.data.get('simulate_success', True)
        
        if pack == 'pack_5':
            credits = 5
        elif pack == 'pack_20':
            credits = 20
        else:
            credits = 1
            
        if simulate_success:
            # Ajouter directement les crédits (pour les tests)
            user = request.user
            user.add_credits(credits)
            
            # Créer une transaction
            CreditTransaction.objects.create(
                user=user,
                type='purchase',
                amount=credits,
                description=f'Paiement manuel - {pack}',
            )
            
            return Response({
                'success': True, 
                'message': f'{credits} crédits ajoutés !',
                'new_credits': user.credits
            })
        else:
            return Response({'success': False, 'message': 'Paiement simulé échoué'})


class CryptoPaymentView(APIView):
    """Paiement crypto simple avec CoinGate ou similaire"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Placeholder pour l'intégration crypto
        return Response({
            'error': 'Paiements crypto pas encore implémentés',
            'alternatives': [
                'Utilisez le paiement manuel pour les tests',
                'Configurez Stripe pour les vrais paiements',
                'Intégrez PayPal pour plus de simplicité'
            ]
        })


class FreeCreditsView(APIView):
    """Donner des crédits gratuits (pour les tests/promotions)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        credits_to_add = request.data.get('credits', 1)
        reason = request.data.get('reason', 'Crédits gratuits')
        
        # Limite pour éviter les abus
        if credits_to_add > 10:
            return Response({'error': 'Maximum 10 crédits gratuits'}, status=400)
            
        # Vérifier si l'utilisateur a déjà reçu des crédits gratuits aujourd'hui
        from django.utils import timezone
        today = timezone.now().date()
        
        existing_free_credits = CreditTransaction.objects.filter(
            user=user,
            type='grant',
            created_at__date=today
        ).exists()
        
        if existing_free_credits:
            return Response({'error': 'Vous avez déjà reçu des crédits gratuits aujourd\'hui'}, status=400)
        
        # Ajouter les crédits
        user.add_credits(credits_to_add)
        
        # Créer la transaction
        CreditTransaction.objects.create(
            user=user,
            type='grant',
            amount=credits_to_add,
            description=reason,
        )
        
        return Response({
            'success': True,
            'message': f'{credits_to_add} crédits gratuits ajoutés !',
            'new_credits': user.credits
        })
