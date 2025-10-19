# TempoHome
Un projet RaspberryPi afin d'afficher les leds correspondantes aux couleurs des jours de l'offre d'électricité Tempo.

Tempo Service (Raspberry ou égal) : 
<p>sudo nano /etc/systemd/system/tempo.service</p>

Inside :
[Unit]
Description=TempoHome Automation Service
After=network.target

[Service]
User=aurel
WorkingDirectory=/home/aurel/TempoHome
ExecStart=/usr/bin/python3 /home/aurel/TempoHome/src/main.py
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target

Save it

sudo systemctl daemon-reload
sudo systemctl enable tempo.service
sudo systemctl start tempo.service

Verif : sudo systemctl status tempo.service

<H1> Pi Runner (Si self-hosted)</H1>

Voir Runner GitHub Action :
Créer un self-hosted runner

mkdir ~/actions-runner && cd ~/actions-runner

Prendre la dernière version : https://github.com/actions/runner/releases

Version 2.329.0 : curl -L -o actions-runner-linux-arm-2.329.0.tar.gz https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-arm-2.329.0.tar.gz

./config.sh --url https://github.com/CLAurelien/TempoHome --token <TON_TOKEN>

./run.sh

<H3> Démarrage au boot </H3>

sudo ./svc.sh install

sudo ./svc.sh start
