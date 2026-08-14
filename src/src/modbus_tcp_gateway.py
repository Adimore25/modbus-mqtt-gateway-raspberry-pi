"""
Modbus → MQTT Bridge (Corrected for Dashboard Compatibility)
------------------------------------------------------------
Publishes sensor data with correct field names so dashboard displays data.
"""

import time
import json
import logging
from pymodbus.client import ModbusTcpClient
from paho.mqtt import client as mqtt_client

# --- Configuration ------------------------------------------------------------
MODBUS_HOST = "localhost"
MODBUS_PORT = 1502
MODBUS_SLAVE_ID = 1
REGISTER_ADDRESS = 40001
REGISTER_COUNT = 10
POLLING_INTERVAL = 5

# MQTT Broker Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# FIXED: Dashboard expects these two topics
MQTT_TOPIC_SENSOR = "factory/sensor_data"
MQTT_TOPIC_MOTOR = "factory/motor_data"

CLIENT_ID = f"modbus-gateway-{int(time.time())}"

# --- Logging -----------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# --- Modbus Client -----------------------------------------------------------
modbus_client = ModbusTcpClient(
    host=MODBUS_HOST,
    port=MODBUS_PORT,
)

# --- MQTT Client --------------------------------------------------------------
def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            log.info("✅ Connected to MQTT Broker successfully!")
        else:
            log.error(f"❌ MQTT connection failed (code {reason_code})")

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
    except Exception as e:
        log.error(f"🚫 Could not connect to MQTT Broker: {e}")
        return None

    return client


def publish_data(mqttc, topic, data_payload):
    """Publish JSON payload to MQTT topic."""
    result = mqttc.publish(topic, data_payload, qos=0)
    if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
        log.info(f"📤 Published to '{topic}': {data_payload}")
    else:
        log.error(f"❌ MQTT publish failed (status={result.rc})")


# --- Main Loop ---------------------------------------------------------------
def main_loop():
    mqtt_client_instance = connect_mqtt()
    if not mqtt_client_instance:
        log.critical("Exiting: MQTT connection failed.")
        return

    mqtt_client_instance.loop_start()

    if not modbus_client.connect():
        log.critical(f"Exiting: Could not connect to Modbus at {MODBUS_HOST}:{MODBUS_PORT}")
        mqtt_client_instance.loop_stop()
        return

    log.info("🔌 Modbus Client connected to ModSim64.")

    while True:
        try:
            # ModSim addressing fix
            modbus_address = REGISTER_ADDRESS - 40001

            response = modbus_client.read_holding_registers(
                address=modbus_address,
                count=REGISTER_COUNT
            )

            if response.isError():
                log.error(f"⚠️ Modbus Read Error: {response}")
            else:
                raw_values = response.registers

                # FIX 1: Proper scaling of temperature & humidity
                temperature = raw_values[0] / 10.0 if len(raw_values) > 0 else None
                humidity = raw_values[1] / 10.0 if len(raw_values) > 1 else None

                # FIX 2: Fix invalid large motor_status values
                motor_raw = raw_values[2] if len(raw_values) > 2 else 0

                # Normalize motor value → 0–3000
                motor_status = motor_raw % 3000

                timestamp = int(time.time())

                # FIXED PAYLOAD FORMAT FOR DASHBOARD
                sensor_data = {
                    "timestamp": timestamp,
                    "temperature": temperature,   # FIXED FIELD NAME
                    "humidity": humidity,         # FIXED FIELD NAME
                    "raw_registers": raw_values[:2]
                }

                motor_data = {
                    "timestamp": timestamp,
                    "motor_status": motor_status,
                    "raw_registers": [motor_raw]
                }

                # Publish both topics
                publish_data(mqtt_client_instance, MQTT_TOPIC_SENSOR, json.dumps(sensor_data))
                publish_data(mqtt_client_instance, MQTT_TOPIC_MOTOR, json.dumps(motor_data))

        except Exception as e:
            log.exception(f"💥 Unexpected error: {e}")
            if not modbus_client.is_socket_open():
                log.warning("🔄 Reconnecting Modbus...")
                modbus_client.connect()

        time.sleep(POLLING_INTERVAL)


# --- Entry Point --------------------------------------------------------------
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log.info("\n🛑 Stopped by user.")
    finally:
        modbus_client.close()
        log.info("🔚 Modbus connection closed.")
