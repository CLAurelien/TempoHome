#!/bin/bash
set -e  # stop on error

cd ~/TempoHome

BRANCH=${1:-main}  # si aucun argument, default = main
cd ~/TempoHome

# Crée le venv s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

git fetch origin
git reset --hard origin/$BRANCH

sudo systemctl restart tempo.service

echo "✅ Deployment completed successfully on branch $BRANCH!"
