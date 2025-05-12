import paho.mqtt.client as pmc
from pigpio_dht import DHT11, DHT22
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
BROKER = "10.10.1.151"
PORT = 1883
BTN = 2
SENSOR_TH = 4
R = 27
B = 17
W = 22
TOPIC_TEMPERATURE = "/final/andy@andy/T"
TOPIC_HUMIDITY = "/final/andy@andy/H"
app = Flask(__name__)
pi = pigpio.pi()
pi.set_mode(R,pigpio.INPUT)
pi.set_mode(B,pigpio.INPUT)
pi.set_mode(W,pigpio.INPUT)
pi.set_mode(BTN,pigpio.INPUT)

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)


client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.connect(BROKER,PORT)

try:
    while True:

        sensor = DHT11(SENSOR_TH)
        result = sensor.read()
        
        print(result)
        x = result["temp_c"]
        y = result["humidity"]
        print(x,y)
        if x > y:
            # Température supérieur
            pi.write(R,1)
            pi.write(B,0)
            pi.write(W,0)

        if y > x:
            # Humidité supérieur
            pi.write(R,0)
            pi.write(B,1)
            pi.write(W,0)
        valeurH = str(y) + "%" 
        valeurT = str(x) + "°C"
        print(valeurH +" "+ valeurT)
        client.publish(TOPIC_HUMIDITY,valeurH)
        client.publish(TOPIC_TEMPERATURE,valeurT)
        time.sleep(1)
        valeur = 1
        if pi.read(BTN) == 0:
                valeur == 0
                valLive = pi.read(BTN)
                if valeur == 0 and valLive == 0:
                    valeur != valeur

except KeyboardInterrupt:
    client.disconnect()
    pi.write(R,0)
    pi.write(B,0)
    pi.write(W,0)
    pi.stop()

