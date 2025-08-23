# Configuration Gmail pour l'envoi d'emails

## 📧 Configuration terminée

✅ **Settings Django** : Paramètres SMTP configurés dans `settings.py`
✅ **Variables d'environnement** : Fichier `.env` créé avec les paramètres Gmail

## 🔑 Étapes suivantes pour activer l'envoi d'emails :

### 1. Générer un mot de passe d'application Gmail

1. **Connectez-vous à votre compte Gmail** : `tech.salariz@gmail.com`
2. **Allez dans les paramètres Google** : https://myaccount.google.com/
3. **Sécurité → Validation en 2 étapes** (obligatoire)
4. **Mots de passe des applications** : Générer un nouveau mot de passe
5. **Copiez le mot de passe généré** (16 caractères)

### 2. Mettre à jour le fichier .env

Éditez `sz-back/.env` et remplacez :
```bash
EMAIL_HOST_PASSWORD=
```

Par :
```bash
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application-gmail
```

### 3. Tester l'envoi d'email

```bash
cd sz-back
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Test d'envoi
send_mail(
    'Test Email Salariz',
    'Ceci est un test d\'envoi depuis Salariz',
    settings.DEFAULT_FROM_EMAIL,
    ['tech.salariz@gmail.com'],
    fail_silently=False,
)
```

## 📋 Configuration actuelle

- **SMTP Host** : `smtp.gmail.com`
- **Port** : `587`
- **TLS** : `Activé`
- **Email expéditeur** : `tech.salariz@gmail.com`
- **Backend** : `SMTP` (au lieu de `console`)

## 🔄 Processus d'inscription utilisateur

1. **Inscription** → Compte créé (inactif)
2. **Email envoyé** → Lien de validation
3. **Clic sur le lien** → Compte activé
4. **Connexion possible**

## ⚠️ Important

- Le mot de passe d'application Gmail est **différent** de votre mot de passe Gmail normal
- La validation en 2 étapes doit être **activée** sur le compte Gmail
- Gardez le mot de passe d'application **secret** et ne le partagez pas
