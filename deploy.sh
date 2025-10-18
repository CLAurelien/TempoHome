#!/bin/bash
set -e  # stop on error

cd ~/TempoHome

echo "Pulling latest version..."
git fetch origin
git reset --hard origin/main

echo "Installing dependencies..."
pip install -r requirements.txt

#echo "Restarting service..."
#sudo systemctl restart tempo.service

echo "✅ Deployment completed successfully!"