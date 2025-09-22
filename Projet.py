import paho.mqtt.client as mqtt
from pigpio_dht import DHT11
import pigpio
import time
import socket
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# Configuration
BROKER = "10.10.1.151"
PORT = 1883
BTN_PIN = 2
SENSOR_PIN = 4
LED_R = 27  
LED_B = 17  
LED_W = 22  

# Variables globales
envoi_donnees = True
derniere_temperature = 0
derniere_humidite = 0
hostname = socket.gethostname()
donnees_recue = {}
nom_courant = ""

TOPIC_TEMPERATURE = f"final/{hostname}/T"
TOPIC_HUMIDITY = f"final/{hostname}/H"
TOPIC_RECEIVER = "final/#"

# Initialisation GPIO
pi = pigpio.pi()
pi.set_mode(LED_R, pigpio.OUTPUT)
pi.set_mode(LED_B, pigpio.OUTPUT)
pi.set_mode(LED_W, pigpio.OUTPUT)
pi.set_mode(BTN_PIN, pigpio.INPUT)

# MQTT callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("MQTT connecté")
    else:
        print("Erreur MQTT:", rc)

def on_message(client, userdata, msg):
    global donnees_recue, nom_courant
    try:
        cle = msg.topic.split("/")[2]
        nom_courant = msg.topic.split("/")[1]
        donnees_recue[cle] = int(msg.payload.decode())
    except (IndexError, ValueError) as e:
        print(f"Erreur traitement message MQTT: {msg.topic} {msg.payload.decode()} - {e}")

# Lecture capteur DHT11
def lire_capteur():
    global derniere_temperature, derniere_humidite
    sensor = DHT11(SENSOR_PIN)
    sensor.timeout_secs = 1
    result = sensor.read()
    if result['valid']:
        t = result['temp_c']
        h = result['humidity']
        derniere_temperature = t
        derniere_humidite = h
        print(f"Lecture capteur: {t}°C / {h}%")
        return t, h
    else:
        print("Lecture capteur invalide.")
        return None, None

# Publication MQTT des données
def envoyer_donnees():
    t, h = lire_capteur()
    if t is None or h is None:
        return
    client.publish(TOPIC_TEMPERATURE, int(t))
    client.publish(TOPIC_HUMIDITY, int(h))

# API Flask routes
@app.route("/etat", methods=["POST"])
def api_etat():
    global envoi_donnees
    data = request.json
    if data and "etat" in data:
        envoi_donnees = bool(data["etat"])
        pi.write(LED_W, 1 if envoi_donnees else 0)
        return jsonify({"success": True, "envoi_donnees": envoi_donnees})
    return jsonify({"error": "etat manquant"}), 400

@app.route("/donnees", methods=["GET"])
def api_donnees():
    return jsonify({
        "temperature": int(derniere_temperature),
        "humidite": int(derniere_humidite)
    })

def demarrer_api():
    app.run(host="0.0.0.0", port=5000)

# Démarrage Flask dans un thread
Thread(target=demarrer_api, daemon=True).start()

# Programme principal
try:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC_RECEIVER)
    client.loop_start()

    dernier_envoi = 0

    while True:
        maintenant = time.time()

        if donnees_recue:
            maxi = max(donnees_recue, key=donnees_recue.get)
            print(f"Max: {nom_courant} ({donnees_recue[maxi]})")
            if nom_courant == "andy":
                if maxi == "H":
                    pi.write(LED_B, 1)
                    pi.write(LED_R, 0)
                elif maxi == "T":
                    pi.write(LED_R, 1)
                    pi.write(LED_B, 0)
            else:
                pi.write(LED_B, 0)
                pi.write(LED_R, 0)

        if envoi_donnees and maintenant - dernier_envoi >= 30:
            envoyer_donnees()
            pi.write(LED_W, 1)
            dernier_envoi = maintenant

        if pi.read(BTN_PIN) == 0:
            t0 = time.time()
            while pi.read(BTN_PIN) == 0:
                time.sleep(0.01)
            duree = time.time() - t0

            if duree > 1:
                envoi_donnees = not envoi_donnees
                pi.write(LED_W, 1 if envoi_donnees else 0)
                print("Envoi activé" if envoi_donnees else "Envoi désactivé")
            else:
                envoyer_donnees()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Arrêt du programme.")
finally:
    client.disconnect()
    client.loop_stop()
    pi.write(LED_R, 0)
    pi.write(LED_B, 0)
    pi.write(LED_W, 0)
    pi.stop()

