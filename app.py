from flask import Flask
import paho.mqtt.client as mqtt

app = Flask(__name__)

# debugging
conStat = "Gateway not connected to MQTT"
currError = ""

# when connecting, updates status
def onConnect(client, userdata, flags, rc, properites=None):
    global conStat, currError
    if rc == 0:
        conStat = "Gateway connected to MQTT"
        currError = ""
        print("Gateway connected to MQTT")
    else:
        conStat = "Gateway not connected to MQTT"
        currError = f"Connection failed. Error: {rc}"
        print(f"MQTT connection failed with code {rc}")
        
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mqtt_gateway")
mqtt_client.on_connect = onConnect

try:
    mqtt_client.connect("localhost", 1883)
    mqtt_client.loop_start()
    mqtt_client.subscribe("#")

except Exception as e:
    print(f"Connection to MQTT error: {e}")
    currError = str(e)
    
@app.route('/')
def index():
    return f"<h1>{conStat}</h1><p>Error log: {currError}</p>"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8080)