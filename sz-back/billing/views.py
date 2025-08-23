import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .models import Order, CreditTransaction


stripe.api_key = settings.STRIPE_SECRET_KEY or None


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY:
            return Response({"error": "Stripe non configuré"}, status=status.HTTP_400_BAD_REQUEST)

        # Détecter automatiquement l'URL frontend depuis le Referer
        referer = request.META.get('HTTP_REFERER')
        frontend_base = (referer or settings.FRONTEND_URL).split('?')[0].split('#')[0].rstrip('/')

        # Simple pricing: pack of 5 credits for 4.90€
        pack = request.data.get('pack', 'pack_5')
        if pack == 'pack_5':
            credits = 5
            amount_cents = 490
            name = 'Pack 5 crédits d\'analyse'
        elif pack == 'pack_20':
            credits = 20
            amount_cents = 1590
            name = 'Pack 20 crédits d\'analyse'
        else:
            credits = 1
            amount_cents = 199
            name = 'Crédit d\'analyse'

        order = Order.objects.create(
            user=request.user,
            credits=credits,
            amount_cents=amount_cents,
            currency='eur',
        )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': order.currency,
                        'product_data': {'name': name},
                        'unit_amount': order.amount_cents,
                    },
                    'quantity': 1,
                }],
                success_url=f'{frontend_base}/?payment=success',
                cancel_url=f'{frontend_base}/?payment=cancel',
                metadata={'order_id': str(order.id), 'user_id': str(request.user.id), 'credits': str(credits)},
            )
            order.stripe_session_id = session.id
            order.save(update_fields=['stripe_session_id'])
            return Response({'checkout_url': session.url})
        except Exception as e:
            import logging
            logger = logging.getLogger('salariz.billing')
            logger.error(f"Stripe checkout error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = None
        try:
            if endpoint_secret:
                event = stripe.Webhook.construct_event(
                    payload=payload, sig_header=sig_header, secret=endpoint_secret
                )
            else:
                import json
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )
        except Exception as e:
            import logging
            logger = logging.getLogger('salariz.billing')
            logger.error(f"Webhook error: {str(e)}")
            return Response({'error': str(e)}, status=400)

        if event and event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            user_id = session.get('metadata', {}).get('user_id')
            credits = int(session.get('metadata', {}).get('credits', '0') or '0')
            if order_id and user_id and credits > 0:
                order = get_object_or_404(Order, pk=order_id)
                if order.status != 'paid':
                    User = get_user_model()
                    user = get_object_or_404(User, pk=user_id)
                    # Mark paid
                    order.status = 'paid'
                    order.stripe_payment_intent = session.get('payment_intent')
                    order.save(update_fields=['status', 'stripe_payment_intent'])
                    # Add credits and transaction
                    try:
                        if hasattr(user, 'add_credits'):
                            user.add_credits(credits)
                        CreditTransaction.objects.create(
                            user=user,
                            type='purchase',
                            amount=credits,
                            description=f'Stripe purchase order #{order.id}',
                            stripe_payment_intent=order.stripe_payment_intent,
                        )
                    except Exception:
                        pass

        return Response({'received': True})


class MeCreditsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'credits': getattr(user, 'credits', 0)})


class CheckPaymentStatusView(APIView):
    """Vérifie et finalise automatiquement les paiements en attente"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Vérifie tous les paiements en attente de l'utilisateur"""
        user = request.user
        
        # Trouver les commandes en attente avec session Stripe
        pending_orders = Order.objects.filter(
            user=user, 
            status='created',
            stripe_session_id__isnull=False
        )
        
        processed_orders = []
        total_credits_added = 0
        
        for order in pending_orders:
            try:
                # Vérifier le statut de la session Stripe
                session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                
                if session.payment_status == 'paid':
                    # Marquer la commande comme payée
                    order.status = 'paid'
                    order.stripe_payment_intent = session.payment_intent
                    order.save(update_fields=['status', 'stripe_payment_intent'])
                    
                    # Ajouter les crédits
                    user.add_credits(order.credits)
                    total_credits_added += order.credits
                    
                    # Créer la transaction
                    CreditTransaction.objects.create(
                        user=user,
                        type='purchase',
                        amount=order.credits,
                        description=f'Auto-processing Stripe order #{order.id}',
                        stripe_payment_intent=order.stripe_payment_intent,
                    )
                    
                    processed_orders.append(order.id)
                    
            except Exception as e:
                import logging
                logger = logging.getLogger('salariz.billing')
                logger.error(f"Error processing order {order.id}: {str(e)}")
                continue
        
        return Response({
            'processed_orders': processed_orders,
            'credits_added': total_credits_added,
            'new_credit_total': user.credits
        })


class BillingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Vue de debug pour vérifier la configuration billing"""
        return Response({
            'stripe_configured': bool(settings.STRIPE_SECRET_KEY),
            'webhook_configured': bool(settings.STRIPE_WEBHOOK_SECRET),
            'user_credits': getattr(request.user, 'credits', 0),
            'stripe_key_prefix': settings.STRIPE_SECRET_KEY[:7] + '...' if settings.STRIPE_SECRET_KEY else None
        })

