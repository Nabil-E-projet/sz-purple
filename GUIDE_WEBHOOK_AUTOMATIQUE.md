# 🔧 Guide pour automatiser les paiements Stripe

## 🎯 Problème actuel
- Les paiements Stripe réussissent mais les crédits ne sont pas ajoutés automatiquement
- Cause : `STRIPE_WEBHOOK_SECRET` manquant

## ✅ Solution complète

### Étape 1 : Configurer le webhook Stripe

1. **Ouvrez votre dashboard Stripe** : https://dashboard.stripe.com/test/webhooks
2. **Cliquez sur "Add endpoint"**
3. **URL de l'endpoint** : `http://localhost:8000/api/billing/webhook/`
4. **Événements à écouter** : Sélectionnez `checkout.session.completed`
5. **Cliquez sur "Add endpoint"**

### Étape 2 : Récupérer le secret du webhook

1. **Cliquez sur votre webhook** nouvellement créé
2. **Dans la section "Signing secret"**, cliquez sur "Reveal"
3. **Copiez la clé** qui commence par `whsec_...`

### Étape 3 : Ajouter la clé à votre .env

Éditez le fichier `.env` dans `sz-back/` et ajoutez :

```bash
STRIPE_WEBHOOK_SECRET=whsec_votre_cle_ici
```

### Étape 4 : Redémarrer le serveur

```bash
cd sz-back
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## 🧪 Test automatique

Une fois configuré, testez en :
1. Achetant des crédits via Stripe
2. Les crédits devraient être ajoutés automatiquement !

## 🔧 Alternative pour les tests : Stripe CLI

Si vous voulez tester en local :

```bash
# Installer Stripe CLI
brew install stripe/stripe-cli/stripe

# Connecter à votre compte
stripe login

# Écouter les événements et les rediriger
stripe listen --forward-to localhost:8000/api/billing/webhook/
```

Le webhook secret sera affiché dans la console.

## ❗ Important

- Le webhook ne fonctionne qu'avec un serveur accessible depuis l'extérieur
- Pour la production, utilisez ngrok ou déployez sur un serveur public
- En local, utilisez Stripe CLI pour les tests
