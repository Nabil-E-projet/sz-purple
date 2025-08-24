# Guide de Déploiement Salariz

## Problèmes résolus

### 1. 404 sur `/api/resend-verification/` en production
**Cause**: Code non synchronisé sur Render
**Solution**: Redéployer le backend avec le code à jour

### 2. Page "NOT FOUND" sur les liens de vérification email
**Cause**: Render ne gère pas les routes React par défaut
**Solution**: Fichier `_redirects` ajouté dans `sz-front/front/public/`

### 3. Emails dans les spams
**Cause**: Headers email manquants et adresse expéditeur générique
**Solution**: Headers anti-spam ajoutés + adresse spécifique `verify@salariz.com`

## Configuration requise pour la production

### Backend (Render)
1. **Variables d'environnement** à configurer :
   ```bash
   FRONTEND_URL=https://sz-purple.onrender.com
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=verify@salariz.com
   EMAIL_HOST_PASSWORD=[mot_de_passe_app]
   DEFAULT_FROM_EMAIL=verify@salariz.com
   ```

2. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. **Start Command**: `python manage.py migrate && gunicorn salariz.wsgi:application`

### Frontend (Render)
1. **Build Command**: `npm install && npm run build`
2. **Publish Directory**: `dist`
3. **Variable d'environnement**:
   ```bash
   VITE_API_BASE_URL=https://backend-gijc.onrender.com
   ```

## Vérifications post-déploiement

### 1. Tester l'API resend-verification
```bash
curl -X POST https://backend-gijc.onrender.com/api/resend-verification/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### 2. Tester les routes frontend
- Aller sur `https://sz-purple.onrender.com/verify-email`
- Vérifier que ça ne montre pas "NOT FOUND"

### 3. Tester l'envoi d'emails
- Créer un compte de test
- Vérifier la réception de l'email (inbox, pas spam)
- Cliquer sur le lien de vérification

## Configuration DNS (pour éviter les spams)

Si vous possédez le domaine `salariz.com`, configurez :

### SPF Record
```
v=spf1 include:_spf.google.com ~all
```

### DKIM (dans Google Admin)
Activer DKIM pour le domaine

### DMARC Record
```
v=DMARC1; p=none; rua=mailto:admin@salariz.com
```

## Notes importantes

1. **Headers email** : Ajoutés pour éviter les filtres anti-spam
2. **Adresse expéditeur** : `verify@salariz.com` plus crédible que `noreply`
3. **Redirections React** : Fichier `_redirects` gère toutes les routes SPA
4. **Priorité email** : Définie comme "high" pour éviter les spams

## Troubleshooting

### Si les emails vont encore en spam :
1. Vérifier la configuration DNS
2. Utiliser un service comme SendGrid ou Mailgun
3. Éviter les mots-clés spam dans l'objet

### Si 404 persiste :
1. Vérifier les logs Render
2. Redéployer depuis GitHub
3. Vérifier que le code est bien poussé sur la branche principale
