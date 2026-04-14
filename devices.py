import paho.mqtt.client as mqtt
import time 
import random

# device config
device_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="device_1")

# device connect
print("Attempting to connect devices to mqtt")
device_client.connect("localhost", 1883)

# device loop to send random tempsevery 5 seconds
try:
    while True:
        temperature = round(random.uniform(5.0, 50.0), 2)
        tempFormat = "{:.2f}".format(temperature)

        
        # confirmation of data sent
        print(f"Sending: {tempFormat}°C -- topic: device/1/temperature")
        device_client.publish("device/1/temperature", tempFormat)
        
        time.sleep(5)

# shutdown
except KeyboardInterrupt:
    print("Device disconnected")
    device_client.disconnect()