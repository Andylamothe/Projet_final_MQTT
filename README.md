# 📡 MQTT-IoT-TempHumid
Un projet IoT Python pour lire les données du capteur DHT11, publier les valeurs température et humidité via MQTT, et exposer une API REST Flask pour consulter ces données et contrôler l'envoi automatique.

## Description
Ce projet utilise un capteur DHT11 connecté à un Raspberry Pi pour lire température et humidité. Ces données sont publiées périodiquement sur un broker MQTT local. Parallèlement, une API Flask permet d'activer/désactiver l'envoi automatique des données et de récupérer la dernière lecture.Le système utilise aussi des LEDs RGB pour indiquer l'état et un bouton pour contrôle manuel.

## Fonctionnalités

- Lecture du capteur DHT11 avec gestion de la validité des données
- Publication MQTT des données sous topics personnalisés par hostname
- Réception des messages MQTT pour contrôler le comportement et afficher des états LED
- API REST Flask pour activer/désactiver l'envoi automatique et récupérer la dernière température/humidité
- Gestion bouton physique pour activation/désactivation ou envoi manuel des données
- Indication visuelle par LEDs RGB selon les états

## Installation
```bash
git clone https://github.com/ton-utilisateur/MQTT-IoT-TempHumid.git
cd MQTT-IoT-TempHumid
pip install -r requirements.txt  # Assure-toi d'avoir un fichier requirements.txt adapté
python app.py
```

