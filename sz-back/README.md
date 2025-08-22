# Salariz Backend
# salariz-backend

Billing/credits:
- New app `billing` with Stripe Checkout to buy credits.
- Env vars: STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET.
- Users have `credits` and get 1 free credit on signup.
- Upload triggers analysis only if a credit is available; otherwise `payment_required` status.
