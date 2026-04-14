from flask import Flask
import paho.mqtt.client as mqtt

app = Flask(__name__)

# debugging
conStat = "Gateway not connected to MQTT"
currError = ""
latestTemp = "Temperature not recieved"

# when connecting, updates status
def onConnect(client, userdata, flags, rc, properties=None):
    global conStat, currError, latestTemp
    if rc == 0:
        conStat = "Gateway connected to MQTT"
        currError = ""
        latestTemp = "Temperature not recieved"
        print("Gateway connected to MQTT")
    else:
        conStat = "Gateway not connected to MQTT"
        currError = f"Connection failed. Error: {rc}"
        latestTemp = "Temperature not recieved"
        print(f"MQTT connection failed with code {rc}")
        
# msg recieved updates temp if not logs
def onMsg(client, userdata, msg):
    global latestTemp
    if msg.topic == "device/1/temperature":
        latestTemp = msg.payload.decode()
    else:
        print(f"{msg.topic}: {msg.payload.decode()}")

# mqtt config
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="mqtt_gateway")
mqtt_client.on_connect = onConnect
mqtt_client.on_message = onMsg

# mqtt connection
try:
    mqtt_client.connect("localhost", 1883)
    mqtt_client.loop_start()
    mqtt_client.subscribe("#")

except Exception as e:
    print(f"Connection to MQTT error: {e}")
    currError = str(e)

# route for render and error logging
@app.route('/')
def index():
    return f"""
            <h1>CPAN 226 Final Project</h1>
            <h2>IoT Smart-Gateway</h2>
            <p>{conStat}</p>
            <p>Latest Temperature: {latestTemp}°C</p>
            <p>Error log: {currError}</p>
            """

# runs the app on port 8080 since mac uses 5000 for airplay
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8080)