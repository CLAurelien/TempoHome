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