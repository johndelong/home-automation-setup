import homeassistant.loader as loader

import json

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "rf_mqtt"

# List of integration names (string) your integration depends upon.
DEPENDENCIES = ["mqtt"]

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "home-assistant/rf_mqtt"

DISCOVERY_PREFIX = "homeassistant"

discovered_devices = {}

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
    """Publish Home Assistant auto discovery data."""
    global discovered_devices

    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = "-".join([model, instance, object_suffix])

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, "config"])

    # Check if we've already configured this device
    if discovered_devices.get(path) != None:
        return

    discovered_devices[path] = True

    config = mapping["config"].copy()
    config["state_topic"] = topic

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
            publish_config(mqttc, topic, model, instance, mappings[key])

def setup(hass, config):
    """Set up the Hello MQTT component."""
    mqtt = hass.components.mqtt
    topic = config[DOMAIN].get(CONF_TOPIC, DEFAULT_TOPIC)

    # Listener to be called when we receive a message.
    # The msg parameter is a Message object with the following members:
    # - topic, payload, qos, retain
    def message_received(msg):
        print("Received Message: " + msg.payload)    

        """Callback for MQTT message PUBLISH."""
        try:
            # Decode JSON payload
            data = json.loads(msg.payload)
            bridge_event_to_hass(mqtt, msg.topic, data)
    
        except json.decoder.JSONDecodeError:
            print("JSON decode error: " + msg.payload)
            return
        
    # Subscribe our listener to a topic.
    mqtt.subscribe(topic, message_received)

    # Return boolean to indicate that initialization was successfully.
    return True
    

