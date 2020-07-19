
import paho.mqtt.client as mqtt

import time
import json
import os

DISCOVERY_PREFIX = "homeassistant"
DEFAULT_TOPIC = "rtl_433/events/#"
DEFAULT_MQTT_PORT = 1883

# Seconds before refreshing the discovery
# Because HA needs to know of new devices that are discovered, we send out
# discovery messages every {DISCOVERY_INTERVAL} seconds to make sure HA
# knows about this device. This is especially useful for new instances
# of HA that are being started up for the first time.
DISCOVERY_INTERVAL = 600  
discovery_timeouts = {}

mappings = {
    "motion": {
        "device_type": "binary_sensor",
        "object_suffix": "M",
        "config": {
            "device_class": "motion",
            "name": "Motion",
            "off_delay": 60,
            "payload_on": "CLOSED",
            "value_template": "{{ value_json.switch1 }}"
        }
    },
    "contact": {
        "device_type": "binary_sensor",
        "object_suffix": "C",
        "config": {
            "device_class": "opening",
            "name": "Contact",
            "payload_off": "CLOSED",
            "payload_on": "OPEN",
            "value_template": "{{ value_json.switch1 }}"
        }
    },
     "battery_ok": {
        "device_type": "sensor",
        "object_suffix": "B",
        "config": {
            "device_class": "battery",
            "name": "Battery",
            "unit_of_measurement": "%",
            "value_template": "{{ float(value_json.battery_ok) * 99 + 1 }}"
        }
    },
}

def sanitize(text):
    """Sanitize a name for Graphite/MQTT use."""
    return (text
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("&", ""))

def publish_config(mqttc, topic, model, instance, mapping):
    """Publish Home Assistant auto discovery data."""
    global discovery_timeouts

    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = "-".join([model, instance, object_suffix])

    discoveryPrefix = os.getenv("HA_DISCOVERY_PREFIX", DISCOVERY_PREFIX)

    path = "/".join([discoveryPrefix, device_type, object_id, "config"])

    # check timeout
    now = time.time()
    if path in discovery_timeouts:
        if discovery_timeouts[path] > now:
            return

    discovery_timeouts[path] = now + DISCOVERY_INTERVAL

    config = mapping["config"].copy()
    config["state_topic"] = topic
    config["unique_id"] = object_id

    print("publishing config: " + json.dumps(config))
    mqttc.publish(path, json.dumps(config))
    
def bridge_event_to_hass(mqttc, topic, data):
    """Translate some rtl_433 sensor data to Home Assistant auto discovery."""

    if "model" not in data:
        # not a device event
        return
    model = sanitize(data["model"])

    if "channel" in data:
        channel = str(data["channel"])
        instance = channel
    elif "id" in data:
        device_id = str(data["id"])
        instance = device_id
    if not instance:
        print("No unique identifier found...")
        # no unique device identifier
        return

    # detect known attributes
    for key in data.keys():
        if key == "subtype":
            key = data[key]

        if key in mappings:
            # Found something we recognize and can parse
            publish_config(mqttc, topic, model, instance, mappings[key])

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

    topic = os.getenv('MQTT_SUB_TOPIC', DEFAULT_TOPIC)

    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received Message: " + msg.topic + " " + str(msg.payload))

    """Handle new MQTT messages."""
    # hass.states.set(entity_id, msg.payload)

    """Callback for MQTT message PUBLISH."""
    try:
        # Decode JSON payload
        data = json.loads(msg.payload)
        bridge_event_to_hass(client, msg.topic, data)

    except json.decoder.JSONDecodeError:
        print("JSON decode error: " + msg.payload)
        return


def main():
    client = mqtt.Client()
    client.username_pw_set(
        username=os.getenv('MQTT_USER'),
        password=os.getenv('MQTT_PASSWORD')
    )

    client.on_connect = on_connect
    client.on_message = on_message

    port = os.getenv('MQTT_PORT', DEFAULT_MQTT_PORT)
    ip = os.getenv('MQTT_IP')

    client.connect(ip, port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == '__main__':
    main()