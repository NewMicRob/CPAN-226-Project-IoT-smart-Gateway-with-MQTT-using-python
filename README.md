# IoT Smart-Gateway with MQTT Project

**Developed by:** Michael R. Newman  
**Course:** CPAN-226  Network & Telecomm. Programming

---

## Project Summary
This project implements a **Smart-Gateway system**. It simulates 20 independent devices that publish temperature to a **Mosquitto Broker**. A central **Gateway** subscribes to these topics, processes the incoming JSON data, and updates a **Flask dashboard** in real-time.

---

## The Three Pillars
I built this project based on three main goals:

* **Sustainability:** I used **Object-Oriented Programming (OOP)**. This makes the code clean and easy to grow. Because of the "Wildcard" setup, you can add 100 more devices without changing a single line of code.
* **Quality:** I used **Asynchronous Threading**. This ensures the website dashboard stays fast and smooth, even when all 20 devices are sending data at the same time.
* **Security:** I built an **Automation Guard**. If a device gets too hot (over 45°C), the gateway automatically "freezes" it. It stops listening to that device to keep the rest of the network safe.

---

## Links
* **Project Report:** [Report here](./Network%20Programming%20and%20Telecomm%20Final%20Project%20Report.pdf)
* **Demo Video:** [Demo here](https://youtu.be/sUkILawJK74)

---

## How to Run
To run this project on your machine, follow these steps:

1. **Set up the Environment:**
   ```bash
   # Create a fresh virtual environment
   python3 -m venv iot_env
   
   # Activate the environment
   source iot_env/bin/activate
   
   # Install the library versions from the requirements file
   pip install -r requirements.txt
   ```
2.  **Start the MQTT Broker:**
    Make sure `mosquitto` is running on your computer.
3.  **Run the Gateway:**
    ```bash
    python3 gateway.py
    ```
4.  **Run the Devices:**
    ```bash
    python3 devices.py
    ```

---

## Tech Stack
* **Language:** Python
* **Data Format:** JSON Serialization
* **Networking Protocol:** MQTT (Paho-MQTT 2.1.0)
* **Web Framework:** Flask (Dashboard)
* **Message Broker:** Mosquitto
* **Editor:** VS Code
