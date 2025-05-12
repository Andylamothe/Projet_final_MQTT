import paho.mqtt.client as pmc
import socket
import pigpio
import time
import busio
import board
import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.ads1115 import P0
from adafruit_ads1x15.analog_in import AnalogIn
from flask import Flask, jsonify, request
import pigpio
BROKER = "mqttbroker.lan"
PORT = 1883
BTN = 2
TOPIC_TEMPERATURE = "/final/andy@andy/T"
TOPIC_HUMIDITY = "/final/andy@andy/H"


# Initialisation de l'interface i2c
i2c = busio.I2C(board.SCL, board.SDA)
 
# Créer une instance de la classe ADS1115 
# et l'associer à l'interface i2c
ads = ADS1115(i2c)
 
# Créer une instance d'entrée analogique
# et l'associer à la broche 0 du module ADC
data = AnalogIn(ads, P0)
 

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

def messageH():

    moyenne = 0
    while True:
        
        result1 = " la luminosité : "+ str(int(data.value * 100 / 26767)) + "% , Le voltage : " + str(int(data.voltage * 100 / 3.3)) + "%"
        result =   int(data.voltage)
        client.publish(TOPIC_HUMIDITY,result)
        
        print(data.value, data.voltage)
        time.sleep(0.5)

def messageT():

    moyenne = 0
    while True:
        
        result1 = " la luminosité : "+ str(int(data.value * 100 / 26767)) + "% , Le voltage : " + str(int(data.voltage * 100 / 3.3)) + "%"
        result =   int(data.voltage)
        client.publish(TOPIC_TEMPERATURE,result)
        
        print(data.value, data.voltage)
        time.sleep(0.5)

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion


client.connect(BROKER,PORT)
messageH()
messageT()

client.disconnect()



app = Flask(__name__)
pi = pigpio.pi()
pi.set_mode(BTN,pigpio.INPUT)

valeur = 1
if pi.read(BTN) == 0:
        valeur == 0
        valLive = pi.read(BTN)
        if valeur == 0 and valLive == 0:
            valeur != valeur
            messageT()
            messageH()

@app.route('/donnees',methods=['GET'])
def get_donnees():
    d = {}
    d['etat'] = pi.read(BTN)
    messageH()
    messageT()
    time.sleep(30)

    
    
    return jsonify(d)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)