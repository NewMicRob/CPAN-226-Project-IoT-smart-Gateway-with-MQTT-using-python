from flask import Flask, render_template_string
import paho.mqtt.client as mqtt
import json
import random
from datetime import datetime

class Gateway:
    def __init__(self, broker="localhost", port=1883):
        self.broker = broker
        self.port = port
        
        # maps the device id to the temp
        self.actDevs = {} # stores active temps
        self.isoDevs = {} # stores isolated temps
        
        self.latestTemp = "--:--:--"
        self.conStat = "Shutdown"
        
        # client config
        clientId = f"gatewayId_{random.randint(1000, 9999)}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=clientId)

        self.client.on_connect = self.onCon
        self.client.on_message = self.onMsg
    
    # on connection starts when the client tries to connect to mqtt
    def onCon(self, client, userdate, flags, rc, properties=None):
        if rc == 0:
            self.conStat = "Connected"
            self.client.subscribe("device/#")
            print("Gateway connected")
        else:
            self.conStat = f"Error: {rc}"
    
    # on message handles data recieved from mqttt
    def onMsg(self, client, userdata, msg):
        try:

            # decodes and parses json data
            payload = json.loads(msg.payload.decode())
            devId = payload.get("device_id")
            tempVal = float(payload.get("temperature", 0))

            # if device is isolated sets temp 
            if devId in self.isoDevs:
                self.isoDevs[devId] = tempVal
                return

            # if device temp is over 45°C then gets put into isolated and delete from active, if under stays in active
            if tempVal > 45.0:
                self.isoDevs[devId] = tempVal
                if devId in self.actDevs:
                    del self.actDevs[devId] # makes sure deivce is removed from active list
            else:
                # update the active devices temperatures
                self.actDevs[devId] = tempVal
                self.latestTemp = f"{tempVal}°C"
        except Exception as e:
            print(f"Mqtt Error: {e}")
    
    # connects mqtt to the port
    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()
        
gateway = Gateway()
app = Flask(__name__)

# html that is rendered when called
DashboardHTML = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="2">
    <script>
        function updateClock() {
            document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            }
        );
    }
    setInterval(updateClock, 1000);
</script>
</head>
<body onload="updateClock()">
    <h1>IoT Smart-Gateway</h1>
    <p>CPAN 226 Final Project</p>

    <p>System Time: <span id="clock"></span></p>
    <p>Last Update: {{ lastUpdated }}</p>
    <p>MQTT Status: {{ status }}</p>
    
    <h2>Active</h2>
    <p>{{ active }}</p>

    <h2>Isolated</h2>
    <p>{{ isolated }}</p>
</body>
</html>
"""

@app.route('/')
def index():
    
    # format data to strings from dictionaries
    actString = ", ".join([f"{id} ({temp}°C)" for id, temp in gateway.actDevs.items()])
    isoString = ", ".join([f"{k} ({v}°C)" for k, v in gateway.isoDevs.items()])
    
    return render_template_string(
        DashboardHTML, # renders dashboard
        lastUpdated = datetime.now().strftime("%I:%M:%S %p"), # renders time formatted for last updated
        status=gateway.conStat, # updates the status of the connection
        curTemp=gateway.latestTemp,
        active = actString if actString else "No Devices Connected",
        isolated = isoString if isoString else "No Devices Isolated"
    )
    
if __name__ == '__main__':
    gateway.start() # starts mqtt listener
    app.run(use_reloader=False, port=8080, debug=True) # using 8080 because airplay uses 5000