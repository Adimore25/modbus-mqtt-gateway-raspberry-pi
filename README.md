
# Modbus to MQTT Gateway using Raspberry Pi

A Python-based **Modbus RTU to MQTT Gateway** designed to bridge traditional industrial Modbus devices with modern Industrial Internet of Things (IIoT) applications using a Raspberry Pi.

## 📌 Overview

Traditional industrial devices commonly use **Modbus RTU over RS-485**, while modern IoT systems use lightweight protocols such as **MQTT**. This project provides a gateway between these two communication protocols.

The system runs on a **Raspberry Pi** and periodically reads data from a Modbus RTU sensor, converts the acquired values into JSON format, and publishes them to an MQTT broker. A Flask-based dashboard can then visualize the sensor data in real time.

The project was developed and tested using both a **Modbus simulation environment** and an **AirLab Temco Rev7 sensor**.

> This project is based on the research paper **"Development of MODBUS to MQTT Gateway using Raspberry Pi."**

## 🎯 Objectives

- Bridge Modbus RTU devices with MQTT-based IoT systems.
- Acquire industrial sensor data through RS-485.
- Convert Modbus register data into JSON.
- Publish sensor data to an MQTT broker.
- Provide real-time visualization through a web dashboard.
- Support bidirectional communication for monitoring and control.
- Implement communication error handling and reconnection mechanisms.
- Evaluate the gateway using both simulation and physical hardware.

## 🏗️ System Architecture

```text
┌──────────────────────┐
│  Modbus RTU Sensor   │
│  AirLab Temco Rev7   │
└──────────┬───────────┘
           │
         RS-485
           │
┌──────────▼───────────┐
│   USB-RS485 Adapter  │
└──────────┬───────────┘
           │
           │ USB
           ▼
┌──────────────────────┐
│     Raspberry Pi     │
│                      │
│  Python Gateway      │
│  ┌────────────────┐  │
│  │    pymodbus     │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │    paho-mqtt    │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
          MQTT
           │
           ▼
┌──────────────────────┐
│  Mosquitto Broker    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Flask Dashboard    │
│  Real-Time Monitoring│
└──────────────────────┘
```

The architecture consists of a Modbus RTU sensor, USB-RS485 converter, Raspberry Pi gateway, MQTT broker, and Flask dashboard.

## ⚙️ How It Works

1. The Modbus sensor measures environmental parameters.
2. The Raspberry Pi communicates with the sensor through RS-485.
3. Python uses `pymodbus` to read Modbus registers.
4. Raw register values are converted into appropriate engineering units.
5. The gateway packages the values into JSON.
6. The JSON data is published to the MQTT broker.
7. The Flask dashboard subscribes to the MQTT data.
8. Sensor values are displayed and plotted in real time.
9. MQTT control messages can be used to initiate Modbus write operations where supported.

## 📡 Communication

### Modbus RTU

Communication between the Raspberry Pi and industrial sensor uses:

- RS-485
- Modbus RTU
- Python `pymodbus`

### MQTT

The gateway publishes sensor data using MQTT.

**Default topic:**

```text
factory/sensor_data
```

Example message:

```json
{
    "temperature": 25.4,
    "humidity": 52.3,
    "co2": 620,
    "tvoc": 145
}
```

For bidirectional control, the architecture can use a control topic such as:

```text
factory/control/cmd
```

## 🧰 Technologies Used

| Technology | Purpose |
|---|---|
| Python | Gateway software |
| Raspberry Pi | Edge computing platform |
| Modbus RTU | Industrial communication |
| RS-485 | Physical communication interface |
| pymodbus | Modbus communication |
| MQTT | IoT messaging |
| Paho MQTT | MQTT client |
| Mosquitto | MQTT broker |
| Flask | Web dashboard |
| ModSim | Modbus simulation |

## 🔌 Hardware Requirements

- Raspberry Pi
- AirLab Temco Rev7 Modbus sensor or compatible Modbus RTU device
- USB-to-RS485 converter
- RS-485 communication wiring
- Regulated 24V DC power supply for the AirLab device
- Network connection

> The AirLab Temco Rev7 used in the project requires a stable 24V DC supply. Power instability was found to affect Modbus communication.

## 💻 Software Requirements

- Python 3.x
- Raspberry Pi OS
- Mosquitto MQTT Broker
- Flask
- pymodbus
- paho-mqtt

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/modbus-mqtt-gateway-raspberry-pi.git
cd modbus-mqtt-gateway-raspberry-pi
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Modbus connection

Configure the RS-485 serial parameters according to your Modbus device:

- Serial port
- Baud rate
- Parity
- Stop bits
- Timeout
- Slave ID

### 5. Start the MQTT broker

If Mosquitto is installed:

```bash
sudo systemctl start mosquitto
```

Check its status:

```bash
sudo systemctl status mosquitto
```

### 6. Run the gateway

```bash
python src/gateway.py
```

### 7. Run the dashboard

```bash
python dashboard/app.py
```

Open the dashboard in a web browser using the Raspberry Pi's IP address.

## 📊 Sensor Register Mapping

The AirLab Temco Rev7 was used as the physical test device.

| Parameter | Register | Scaling | Unit |
|---|---:|---:|---|
| Temperature | 121 | ÷10 | °C |
| Humidity | 140 | ÷10 | %RH |
| CO₂ | 139 | Raw | ppm |
| PM2.5 | 766 | Raw | µg/m³ |

> Verify the register addresses against the documentation of your specific Modbus device before deployment.

## 🧪 Testing

The gateway was tested in two stages.

### Simulation Testing

A Modbus simulator was used to verify:

- Modbus register polling
- JSON formatting
- MQTT publishing
- MQTT topic handling
- Dashboard updates
- Error detection
- Recovery and reconnection behavior

### Hardware Testing

The system was subsequently tested using an AirLab Temco Rev7 Modbus sensor connected through RS-485.

The hardware testing focused on:

- Reliable Modbus communication
- Correct sensor register mapping
- MQTT message transmission
- Real-time dashboard visualization
- Long-duration stability

## 📈 Performance

The system achieved an average end-to-end latency of approximately:

```text
~1 second
```

from sensor acquisition to dashboard presentation.

During testing, the system demonstrated stable Modbus polling and smooth dashboard updates. The paper also reports that communication became more reliable after providing a regulated 24V supply to the sensor.

## 🛡️ Error Handling

The gateway includes mechanisms for handling communication failures, including:

- Modbus timeout detection
- Modbus retry behavior
- MQTT reconnection
- Invalid-value checking
- Continuous polling
- Communication recovery

These mechanisms improve the reliability of the gateway during network or device communication problems.

## 🔄 Bidirectional Communication

The project is designed to support two-way communication:

```text
             Monitoring
Modbus ───────────────────► MQTT
  ▲                           │
  │                           │
  └──────── Control ◄─────────┘
```

### Modbus → MQTT

Sensor values are read from Modbus registers and published to MQTT.

### MQTT → Modbus

MQTT control commands can trigger Modbus write operations for supported devices.

This allows the gateway to move beyond simple monitoring toward industrial control applications.

## 📁 Project Structure

```text
modbus-mqtt-gateway-raspberry-pi/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── src/
│   ├── gateway.py
│   ├── modbus_client.py
│   ├── mqtt_client.py
│   └── config.py
│
├── dashboard/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│
├── simulation/
│   └── modbus_simulator.py
│
├── config/
│   └── config.example.json
│
├── docs/
│   ├── architecture.md
│   ├── register-mapping.md
│   └── setup-raspberry-pi.md
│
├── images/
│   ├── system-architecture.png
│   ├── flowchart.png
│   └── dashboard.png
│
└── tests/
    ├── test_modbus.py
    └── test_mqtt.py
```

## 🔮 Future Scope

Possible future improvements include:

- MQTT authentication
- MQTT SSL/TLS security
- Support for multiple Modbus devices
- Cloud integration with AWS IoT or Azure
- Long-term sensor data storage
- Predictive maintenance
- Anomaly detection
- Dynamic gateway configuration
- Watchdog and health monitoring
- Support for additional industrial protocols
- FPGA-based gateway implementation

## 👨‍💻 Authors

**Ashwinee Barbadekar**  
**Aditya More**  
**Sarvesh More**  
**Shrut Mude**  
**Nandini Yelgulwar**  
**Isha Yerme**  
**Asmita Yadav**

Vishwakarma Institute of Technology, Pune, India.

## 📄 Research Paper

This repository is based on the project presented in:

**"Development of MODBUS to MQTT Gateway using Raspberry Pi"**

The paper describes the architecture, implementation, simulation, hardware testing, performance evaluation, and future scope of the gateway.

## ⭐ Project Highlights

- 🔌 Modbus RTU / RS-485
- 🍓 Raspberry Pi Edge Gateway
- 📡 MQTT Communication
- 🔄 Bidirectional Communication
- 📊 Real-Time Dashboard
- 🐍 Python Implementation
- 🧪 Simulation + Hardware Testing
- ⚡ ~1 Second Average Latency
- 🛡️ Error Handling & Reconnection
- 🏭 Industrial IoT / Industry 4.0

## 📜 License

This project is intended for educational, research, and prototyping purposes.
