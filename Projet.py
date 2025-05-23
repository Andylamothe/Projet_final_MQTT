import paho.mqtt.client as pmc
from pigpio_dht import DHT11
import pigpio
import time
import socket
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

BROKER = "10.10.1.151"
PORT = 1883
BTN = 2
SENSOR_TH = 4
R = 27  
B = 17  
W = 22  
 
envoi_donnees = True
derniere_temperature = 0
derniere_humidite = 0
hostname = socket.gethostname()
donneRecu = {}
listNom = []
##Pour les globals on a appris de StackOverflow
 
TOPIC_TEMPERATURE = f"final/{hostname}/T"
TOPIC_HUMIDITY = f"final/{hostname}/H"
TOPIC_RECEVER = "final/#"
 ## Code fait par Jayden
# Initialisation 
pi = pigpio.pi()
pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)
pi.set_mode(W, pigpio.OUTPUT)
pi.set_mode(BTN, pigpio.INPUT)
 
# Connexion 
## Code fait par Jayden
def connexion(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("MQTT connecté")
    else:
        print("Erreur MQTT:", rc)
 
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.connect(BROKER, PORT)
client.loop_start()
## Code fait par Andy
# Lecture des données
def lire_capteur():
    global derniere_temperature, derniere_humidite
    sensor = DHT11(SENSOR_TH)
    sensor.timeout_secs = 1
    result = sensor.read()
    if result['valid']:
        t = result['temp_c']
        h = result['humidity']
        derniere_temperature = t
        derniere_humidite = h
        print(f"Lecture : {t}°C / {h}%")
        return t, h
    else:
        print("Lecture capteur invalide.")
        return None, None
## Code fait par Andy 
# Envoi des données
def envoyer_donnees():
    t, h = lire_capteur()
    if t is None or h is None:
        return
    valeurT = int(t)
    valeurH = int(h)
    client.publish(TOPIC_TEMPERATURE, valeurT)
    client.publish(TOPIC_HUMIDITY, valeurH)
 
    #LED TEMP
   # if t > h:
    #    pi.write(R, 1)
    #    pi.write(B, 0)
    #elif h > t:
    #    pi.write(R, 0)
    #    pi.write(B, 1)
  #  else:
    #    pi.write(R, 0)
     #   pi.write(B, 0)

## Code fait par Andy
def reception_msg(cl,userdata,msg):
    global donneRecu
    global names
    try:
        cle = msg.topic.split("/")[2]
        names = msg.topic.split("/")[1]
        donneRecu[cle] = int(msg.payload.decode())
    except IndexError:
        print(">>> ERREUR:",msg.topic,msg.payload.decode())
    except ValueError:
        print(">>> ERREUR:",msg.topic,msg.payload.decode())

    
## Code fait par Andy
# API Flask (Méthodes)
@app.route("/etat", methods=["POST"])
def api_etat():
    global envoi_donnees
    data = request.json
    if data and "etat" in data:
        envoi_donnees = bool(data["etat"])
        pi.write(W, 1 if envoi_donnees else 0)
        return jsonify({"success": True, "envoi_donnees": envoi_donnees})
    return jsonify({"error": "etat manquant"}), 400
## Code fait par Andy 
@app.route("/donnees", methods=["GET"])
def api_donnees():
    return jsonify({
        "T": int(derniere_temperature),
        "H": int(derniere_humidite)
    })
## Code fait par Andy 
# Démarrer Flask dans un thread
def demarrer_api():
    app.run(host="0.0.0.0", port=5000)
 
Thread(target=demarrer_api).start()
## Code fait par Andy 
# prog principal
try:
    client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
    client.on_connect = connexion
    client.on_message = reception_msg
    client.connect(BROKER,PORT)
    client.subscribe(TOPIC_RECEVER)
    client.loop_start()
    dernier_envoi = 0
    while True:
     ## Code fait par Andy 
        maintenant = time.time()
        if bool(donneRecu):
            nom = names
            maxi = max(donneRecu, key=donneRecu.get)
            print("Max:", names, "(" + str(donneRecu[maxi]) + ")")
            if names == "andy":
                if maxi == "H":      
                    pi.write(B,1)
                    pi.write(R,0)
                if maxi == "T":
                    pi.write(R,1)
                    pi.write(B,0)
            else:
                if maxi == "H":
                    pi.write(B,0)
                    pi.write(R,0)

                
           
        # Envoi automatique toutes les 30 secondes
        if envoi_donnees and maintenant - dernier_envoi >= 30:
            envoyer_donnees()
            pi.write(W,1)
            dernier_envoi = maintenant
 
        # Gestion du bouton
        if pi.read(BTN) == 0:
            t0 = time.time()
            while pi.read(BTN) == 0:
                time.sleep(0.01)
            t1 = time.time()
            duree = t1 - t0
            
 
            if duree > 1: ## 2 secondes moins 1 par soucis de calibrage 
                # Appui long 
                envoi_donnees = not envoi_donnees
                pi.write(W, 1 if envoi_donnees else 0)

                    
                print("Envoi activé" if envoi_donnees else "Envoi désactivé")
            else:
                # Appui court 
                envoyer_donnees()
        
 
        time.sleep(0.1)
 ## Code fait par Jayden
except KeyboardInterrupt:
    print("Arrêt du programme.")
    client.disconnect()
    client.loop_stop()
    pi.write(R, 0)
    pi.write(B, 0)
    pi.write(W, 0)
    pi.stop()
finally:
    pi.write(R, 0)
    pi.write(B, 0)
    pi.write(W, 0)
    pi.stop()
