#!/bin/bash
set -e  # stop on error

cd ~/TempoHome

BRANCH=${1:-main}

# Vérifie que le webhook est bien passé
if [ -z "$DISCORD_WEBHOOK" ]; then
  echo "❌ Erreur : variable DISCORD_WEBHOOK non définie."
  exit 1
fi

# Crée le venv s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "📥 Pulling latest code from $BRANCH..."
git fetch origin
git reset --hard origin/$BRANCH

# 🔔 Notification Discord après pull
curl -H "Content-Type: application/json" \
     -d "{\"content\": \"📦 TempoHome : le code de la branche **$BRANCH** a été mis à jour avec succès sur le Raspberry Pi.\"}" \
     "$DISCORD_WEBHOOK"

# 🔁 Redémarrage du service
sudo systemctl restart tempo.service

# 🔔 Notification Discord finale
curl -H "Content-Type: application/json" \
     -d "{\"content\": \"✅ TempoHome : déploiement complet terminé sur la branche **$BRANCH**.\"}" \
     "$DISCORD_WEBHOOK"

echo "✅ Deployment completed successfully on branch $BRANCH!"
