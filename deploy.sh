#!/bin/bash

# Script de déploiement pour Render

echo "🚀 Démarrage du déploiement..."

# Backend
cd sz-back

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

echo "✅ Backend prêt!"

# Lancer le serveur avec gunicorn
gunicorn salariz.wsgi:application --bind 0.0.0.0:$PORT
