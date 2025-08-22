# 💳 Guide des Paiements - Salariz

## 🚀 Options disponibles (du plus simple au plus complexe)

### 1. **MODE TEST/DÉMO** ⚡ (Le plus simple)
**Parfait pour tester l'application sans configuration**

- ✅ **Aucune configuration requise**
- ✅ **Crédits gratuits quotidiens**
- ✅ **Simulation de paiements**
- ❌ Pas de vrais paiements

**Comment utiliser :**
1. Allez sur `/buy-credits`
2. Cliquez sur "Réclamer" pour 1 crédit gratuit/jour
3. Utilisez les boutons "🧪 Test (Mode démo)" pour simuler des achats

---

### 2. **STRIPE** 💪 (Recommandé pour la production)
**Solution complète et professionnelle**

- ✅ **Paiements par carte sécurisés**
- ✅ **Gestion automatique des webhooks**
- ✅ **Interface moderne**
- ❌ Requires configuration initiale

**Configuration rapide :**
```bash
# 1. Exécutez le script de configuration
python configure_stripe.py

# 2. Récupérez vos clés sur https://dashboard.stripe.com/test/apikeys
# 3. Redémarrez le serveur
cd sz-back && python manage.py runserver
```

**Cartes de test :**
- ✅ Succès : `4242 4242 4242 4242`
- ❌ Échec : `4000 0000 0000 0002`
- 🔄 3D Secure : `4000 0025 0000 3155`

---

### 3. **PAYPAL EXPRESS** 🌐 (Alternative simple)
**Plus familier pour certains utilisateurs**

- ✅ **Configuration simple**
- ✅ **Connu des utilisateurs**
- ❌ Interface moins moderne
- ❌ Pas encore implémenté côté frontend

**Configuration :**
1. Créez un compte PayPal Business
2. Récupérez votre email PayPal
3. Modifiez `billing/simple_payments.py` ligne 45

---

## 🛠️ Configuration actuelle

### Vérifier le statut
```bash
curl http://localhost:8000/api/billing/status/
```

### Fichier .env requis
```env
# Dans sz-back/.env
STRIPE_SECRET_KEY=sk_test_votre_cle_secrete
STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle_publique
STRIPE_WEBHOOK_SECRET=whsec_votre_secret_webhook
```

---

## 🧪 Tests rapides

### 1. Test des crédits gratuits
```bash
curl -X POST http://localhost:8000/api/billing/free-credits/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"credits": 1, "reason": "Test"}'
```

### 2. Test de simulation de paiement
```bash
curl -X POST http://localhost:8000/api/billing/manual/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pack": "pack_5", "simulate_success": true}'
```

---

## 🚨 Résolution des problèmes courants

### Problème : "Stripe non configuré"
**Solution :** Vérifiez votre fichier `.env` et redémarrez le serveur

### Problème : "Webhook failed"
**Solutions :**
1. Vérifiez l'URL webhook dans Stripe Dashboard
2. Exposez votre localhost avec ngrok : `ngrok http 8000`
3. Laissez `STRIPE_WEBHOOK_SECRET` vide pour les tests

### Problème : "Payment failed"
**Solutions :**
1. Utilisez les cartes de test Stripe
2. Vérifiez les logs du serveur Django
3. Essayez le mode simulation en attendant

---

## 📊 Tableau de comparaison

| Solution | Facilité | Sécurité | Coût | Production Ready |
|----------|----------|----------|------|------------------|
| Mode Test | ⭐⭐⭐⭐⭐ | ⭐⭐ | Gratuit | ❌ |
| Stripe | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2.9% + 0.25€ | ✅ |
| PayPal | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 3.4% + 0.35€ | ✅ |

---

## 🎯 Recommandations

### Pour le développement :
1. **Utilisez le mode test** pour commencer
2. **Configurez Stripe** quand vous êtes prêt

### Pour la production :
1. **Stripe** pour une expérience moderne
2. **PayPal** si vos utilisateurs le préfèrent
3. **Les deux** pour maximiser les conversions

---

## 📞 Support

En cas de problème :
1. Vérifiez les logs Django
2. Testez les endpoints avec curl
3. Consultez la documentation Stripe
4. Utilisez le mode démo en attendant
