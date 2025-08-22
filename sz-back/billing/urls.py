from django.urls import path
from .views import CreateCheckoutSessionView, StripeWebhookView, MeCreditsView, BillingStatusView, CheckPaymentStatusView
from .simple_payments import PayPalExpressView, ManualPaymentView, FreeCreditsView

urlpatterns = [
    # Stripe (recommandé)
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='billing-create-checkout'),
    path('webhook/', StripeWebhookView.as_view(), name='billing-webhook'),
    path('check-payment-status/', CheckPaymentStatusView.as_view(), name='billing-check-payment'),
    
    # Alternatives simples
    path('paypal/', PayPalExpressView.as_view(), name='billing-paypal'),
    path('manual/', ManualPaymentView.as_view(), name='billing-manual'),
    path('free-credits/', FreeCreditsView.as_view(), name='billing-free'),
    
    # Info
    path('me/credits/', MeCreditsView.as_view(), name='billing-me-credits'),
    path('status/', BillingStatusView.as_view(), name='billing-status'),
]

