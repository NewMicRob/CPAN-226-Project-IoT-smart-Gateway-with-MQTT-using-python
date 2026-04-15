import paho.mqtt.client as mqtt
import time 
import random
import json

class Devices:
    def __init__(self, broker="localhost", port=1883, deviceCount=20):
        self.broker = broker
        self.port = port
        self.deviceCount = deviceCount

        # starts mqtt to send data to all devices
        self.device_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="devsAdmin")
        
    def startDevices(self):
        print(f"Attempting to connect {self.deviceCount}")
        try: 
            self.device_client.connect(self.broker, self.port)
            self.transLoop() # starts transmitting data
        except Exception as e:
            print(f"Connection failed: {e}")
            
    def transLoop(self):
        try:
            while True:
                # loops devices to give temps
                for i in range(1, self.deviceCount + 1):
                    devId = f"device_{i}"
                    
                    # temp range between 5 - 50
                    temperature = round(random.uniform(5.0, 50.00), 2)
                    
                    # data sent to dictionaries
                    payload = {
                        "device_id" : devId,
                        "temperature": temperature
                    }
                    
                    # topic being sent to devices
                    topic = f"device/{devId}/temperature"
                    
                    # converts dictionary to json and sends to device to publish to mqtt
                    self.device_client.publish(topic, json.dumps(payload))
                    print(f"{devId} - {temperature}°C")
                
                # sends every 2 seconds
                time.sleep(2)
        except Exception as e:
            print("\n System Shutdown")
            self.device_client.disconnect()
if __name__ == "__main__":
    devices = Devices(deviceCount=20) # sets number of devices
    devices.startDevices()