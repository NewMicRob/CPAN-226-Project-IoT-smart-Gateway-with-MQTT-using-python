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
        
        self.lastRec = "Never"
        self.conStat = "Attempting to initialize"
        
        # client config
        clientId = f"gatewayId_{random.randint(1000, 9999)}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=clientId)

        self.client.on_connect = self.onCon
        self.client.on_message = self.onMsg
    
    # on connection starts when the client tries to connect to mqtt
    def onCon(self, client, userdata, flags, rc, properties=None):
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
            tempVal = int(payload.get("temperature", 0))
            curTime = datetime.now().strftime("%I:%M:%S %p")
            
            # if device is isolated sets temp, time isolated
            if devId in self.isoDevs:
                return

            self.lastRec = curTime
            
            # if device temp is over 45°C then gets put into isolated and delete from active, if under stays in active
            if tempVal > 45:
                self.isoDevs[devId] = {"temp": tempVal, "time": curTime}
                self.actDevs.pop(devId, None) # makes sure deivce is removed from active list
            else:
                # update the active devices temperatures
                self.actDevs[devId] = {"temp": tempVal, "time": curTime}
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
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <meta http-equiv="refresh" content="2">
    <style>
        html, body {
            height: 100%;
            display: flex;
            flex-direction: column;
            font-family: 'Roboto Mono', monospace;
            margin: 0;
            padding: 0;
            background-color: #06090f;
            color: #3fb950;
            text-shadow: 0 0 2px rgba(0, 255, 0, 0.3);
        }
        
        .mainCard {
            flex: 1 0 auto;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 40px 30px;
        }
        
        .cont {
            width: 100%;
            max-width: 960px;
            background: #0d1117;
            padding: 30px;
            border: 1px solid #238636;
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.05);
        }
        
        .headerCard {
            border-bottom: 1px solid #238636;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        h1 { 
            font-size: 1.8rem; 
            margin: 0; 
            text-align: center;
        }
        
        h2 { 
            font-size: 1.4rem;
            margin-top: 30px;
            padding-bottom: 5px;
            text-align: center;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            border: 1px solid #238636;
        }
        
        th {
            text-align: center; 
            padding: 12px; 
            color: #06090f;
        }
        
        td {
            text-align: center;
            padding: 12px; 
            border-bottom: 1px solid #238636;
        }
        
        .actHeader {
            background-color: #3fb950;
        }
        
        .isoHeader {
            background-color: #ff3e3e;
        }
        
        .actRow {
            color: #3fb950;
        }
        
        .isoRow {
            color: #ff3e3e;
            text-shadow: 0 0 5px rgba(255, 0, 0, 0.2);
        }
        
        .upTime {
            color: #fff;
            font-weight: bold;
        }

        footer {
            flex-shrink: 0;
            background: #0d1117;
            border-top: 1px solid #238636;
            padding: 15px 40px;
            display: flex;
            justify-content: center;
            font-size: 0.8rem;
            color: #238636;
        }
        
        .pulse {
            animation: pulse-animation 2s infinite ease-in-out; 
        }
        
        @keyframes 
        pulse-animation {
            0% {
                filter: brightness(0.7);
            }
            50% {
                filter: brightness(1.6);
            }
            100% {
                filter: brightness(0.7);
            }
        }
    </style>
    
    <script>
        function updateClock() {
            const clock = document.getElementById('clock');
            if (clock) {
                clock.innerText = new Date().toLocaleTimeString('en-US', {
                    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
                });
            }
            const year = document.getElementById('currentYear');
            if (year) year.innerText = new Date().getFullYear();
        }
        setInterval(updateClock, 1000);
    </script>

</head>
<body onload="updateClock()">
    <div class="mainCard">
        <div class="cont">
            <div class="headerCard">
                <h1>CPAN 226 Final Project</h1>
                <h2>IoT Smart-Gateway</h2>
            </div>

            <div style="display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px;">
                <p>MQTT Status: <span class="pulse" style="color:#fff;">{{ status }}</span></p>
                <p>System Condition: <span class="pulse" style="color: {{ health_col }}; font-weight: bold;">{{ health }}</span></p>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="display: flex; flex-direction: column;">
                    <span style="font-size: 0.8rem; color: #238636;">Current Time</span>
                    <span id="clock" class="upTime pulse" style="font-size: 1.2rem; animation: pulse-animation 2s infinite;">--:--:--</span>
                </div>

                <div style="display: flex; flex-direction: column; text-align: right;">
                    <span style="font-size: 0.8rem; color: #238636;">Last Update</span>
                    <span class="upTime pulse" style="font-size: 1.2rem; animation: pulse-animation 2s infinite;">{{ lastUpdated }}</span>
                </div>
            </div>

            <h2 style="color: #3fb950;">Active</h2>
            <table>
                <thead>
                    <tr class="actHeader">
                        <th>Device</th>
                        <th>Temperature</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {% if actList %}
                        {% for id, data in actList.items() %}
                            <tr class="pulse actRow">
                                <td class="upTime" style="color: inherit;">{{ id }}</td>
                                <td>{{ data.temp }}&deg;C</td>
                                <td>{{ data.time }}</td>
                            </tr>
                        {% endfor %}
                    {% else %}
                        <tr class="pulse"> 
                            <td colspan="3" style="text-align:center; color: #8b949e;">
                                All Devices Isolated
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>

            <h2 style="color: #ff3e3e">Isolated</h2>
            <table>
                <thead>
                    <tr class="isoHeader">
                        <th>Device</th>
                        <th>Temperature</th>
                        <th>Time Isolated</th>
                    </tr>
                </thead>
                <tbody>
                    {% if isoList %}
                        {% for id, data in isoList.items() %}
                            <tr class="pulse isoRow">
                                <td class="upTime iso" style="color: inherit;">{{ id }}</td>
                                <td>{{ data.temp }}&deg;C</td>
                                <td>{{ data.time }}</td>
                            </tr>
                        {% endfor %}
                    {% else %}
                        <tr class="pulse">
                            <td colspan="3" style="text-align:center; color: #3fb950;">No Devices Isolated</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>

    <footer>
        <span>
            &copy;<span id="currentYear"></span> Michael R Newman
        </span>
    </footer>

</body>
</html>
"""

@app.route('/')
def index():
    
    # sorts devices by number
    try:
        sortActList = dict(sorted(gateway.actDevs.items(), key=lambda x: int(x[0].split('_')[1])))
        sortIsoList = dict(sorted(gateway.isoDevs.items(), key=lambda x: int(x[0].split('_')[1])))
    except:
        sortActList, sortIsoList = gateway.actDevs, gateway.isoDevs

    # connection indicator
    hStatus, hColor = ("Receiving", "#3fb950") if gateway.actDevs else ("Idle", "#fff")
    if not gateway.actDevs and gateway.isoDevs: hStatus, hColor = ("Alert - All Devices Isolated", "#ff3e3e")
    
    return render_template_string(
        DashboardHTML,
        lastUpdated = gateway.lastRec,
        status = gateway.conStat,
        actList = sortActList,
        isoList = sortIsoList,
        health = hStatus,
        health_col = hColor
    )
    
if __name__ == '__main__':
    gateway.start() # starts mqtt listener
    app.run(use_reloader=False, port=8080, debug=True) # using 8080 because airplay uses 5000