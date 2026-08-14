#!/usr/bin/env python3
import time
import json
import datetime
from pymodbus.client.sync import ModbusSerialClient
import paho.mqtt.client as mqtt

# ------------------------
# Modbus / AirLab config
# ------------------------
PORT      = "COM9"        # <-- UPDATE THIS
BAUD      = 9600
PARITY    = "N"
STOPBITS  = 1
BYTESIZE  = 8
SLAVE_ID  = 2
INTERVAL  = 1.0           # seconds

# ------------------------
# MQTT config
# ------------------------
BROKER       = "localhost"
BROKER_PORT  = 1883
TOPIC        = "factory/sensor_data"

# ------------------------
# MQTT setup
# ------------------------
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, BROKER_PORT, 60)
mqtt_client.loop_start()

# ------------------------
# Modbus setup (pymodbus 2.5.3)
# ------------------------
client = ModbusSerialClient(
    method="rtu",
    port=PORT,
    baudrate=BAUD,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=1,
)

if not client.connect():
    print(f"❌ Could not open {PORT}. Check the COM port or wiring.")
    raise SystemExit

print(f"✅ Connected to {PORT}, reading AirLab registers...")

def read_reg(addr: int):
    try:
        result = client.read_holding_registers(address=addr, count=1, unit=SLAVE_ID)
        if result.isError():
            print(f"⚠️ Modbus error at addr {addr}: {result}")
            return None
        return result.registers[0]
    except Exception as e:
        print(f"💥 Exception reading addr {addr}: {e}")
        return None


# ------------------------
# Main Loop
# ------------------------
try:
    while True:
        temp_raw = read_reg(121)   # Temperature * 10
        co2_raw  = read_reg(139)   # CO2 ppm
        hum_raw  = read_reg(140)   # Humidity %
        voc_raw  = read_reg(988)   # TVOC ppb

        if None in (temp_raw, co2_raw, hum_raw, voc_raw):
            print("⚠️ Read error — skipping cycle")
            time.sleep(INTERVAL)
            continue

        timestamp = int(time.time())
        temperature = temp_raw / 10.0
        hum_raw = hum_raw / 10.0

        payload = {
            "timestamp": timestamp,
            "temperature": temperature,
            "co2": co2_raw,
            "humidity": hum_raw,
            "tvoc": voc_raw
        }

        mqtt_client.publish(TOPIC, json.dumps(payload))

        print(f"[{datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}] ✅ {payload}")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n⛔ Stopped by user")

finally:
    client.close()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("🟢 Clean exit")
