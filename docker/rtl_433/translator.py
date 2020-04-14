
import paho.mqtt.client as mqtt

import time
import json

DISCOVERY_PREFIX = "homeassistant"
DISCOVERY_REFRESH_INTERVAL = 600  # Seconds before refreshing the discovery

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
}

def sanitize(text):
    """Sanitize a name for Graphite/MQTT use."""
    return (text
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("&", ""))

def publish_config(mqttc, topic, model, instance, mapping):
    now = time.time()

    # print("Model: " + model)
    # print("Instance: " + instance)
    # print("Mapping: " + json.dumps(mapping))    

    """Publish Home Assistant auto discovery data."""
    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = "-".join([model, instance, object_suffix])

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, "config"])

    # check timeout to see if we should home assistant another config message
    global discovery_timeouts
    if path in discovery_timeouts and discovery_timeouts[path] > now:
        return
        
    # update the refresh interval
    discovery_timeouts[path] = now + DISCOVERY_REFRESH_INTERVAL

    config = mapping["config"].copy()
    config["state_topic"] = topic

    print("\n=======================")
    print("Path: " + path)
    print("Config: " + json.dumps(config))
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
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("rtl_433/events/#")

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
    client.username_pw_set(username="ha_broker",password="C0nn3ctM3!")

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.86.95", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == '__main__':
    main()