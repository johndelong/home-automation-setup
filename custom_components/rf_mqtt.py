# Built from the following example:
# https://github.com/merbanan/rtl_433/blob/e9fbb92c2ee4948814c6fbdfb18902dcf3cd90df/examples/rtl_433_mqtt_hass.py

import json
import logging
import time

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "rf_mqtt"

# List of integration names (string) your integration depends upon.
DEPENDENCIES = ["mqtt"]

CONF_SUB_TOPIC = "sub_topic"
CONF_PUB_TOPIC = "pub_topic"
CONF_DEBOUNCE = "debounce"

DISCOVERY_PREFIX = "homeassistant"

_LOGGER = logging.getLogger(__name__)

g_sub_topic = ""
g_pub_topic = ""

# Devices already "discovered" and sent to HA
g_discovered_devices = {}

# Devices that should be debounced
g_debounce_devices = {}
g_debounced_messages = {}

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
    global g_discovered_devices

    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = "-".join([model, instance, object_suffix])

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, "config"])

    # Check if we've already configured this device
    if g_discovered_devices.get(path) != None:
        return

    g_discovered_devices[path] = True

    config = mapping["config"].copy()
    config["state_topic"] = "/".join([g_pub_topic, topic])
    config["unique_id"] = object_id

    _LOGGER.info("publishing config: " + json.dumps(config))
    mqttc.publish(path, json.dumps(config))

def debounce(mqttc, topic, debounce_count, data):
    global g_debounced_messages

    _LOGGER.info("Data:" + json.dumps(data))
    _LOGGER.info("Topic: " + topic)

    device_id = data["id"]
    raw_msg = data["raw_message"]

    now = time.time()
    blank = {"raw_msg": raw_msg, "count": 0, "updated": now}

    message = g_debounced_messages.get(device_id, blank)

    if message["updated"] - now > 5:
        _LOGGER.info("Message too old. Resetting debounce count.")
        g_debounced_messages[device_id] = blank

    # Increment the number of times we've seen this message
    if message["raw_msg"] == raw_msg:
        message["count"] += 1
        _LOGGER.info("We've seen this message before %s of %s", message["count"], debounce_count)
    else:
        # There is a new message we should start debouncing
        message["raw_msg"] = raw_msg
        message["count"] = 1
        _LOGGER.info("This is the first time we've seen this message")

    # Save this entry so we can refer to it later
    message["updated"] = now
    g_debounced_messages[device_id] = message

    if message["count"] >= debounce_count:
        _LOGGER.info("Successfully debounced - Sending message!")
        mqttc.publish(topic, json.dumps(data))
    else:
        _LOGGER.info("Messaged is being held. Nothing sent.")
    
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
        _LOGGER.info("No unique identifier found...")
        # no unique device identifier
        return

    # detect known attributes
    for key in data.keys():
        if key == "subtype":
            key = data[key]

        if key in mappings:
            publish_config(mqttc, topic, model, instance, mappings[key])

        pub_topic = "/".join([g_pub_topic, topic])

        if key in g_debounce_devices:
            # Debounce this message
            debounce_count = g_debounce_devices[key]
            debounce(mqttc, pub_topic, debounce_count, data)
        else:
            # Just send the message on the alterted topic
            mqttc.publish(pub_topic, json.dumps(data))

def setup(hass, config):
    """Set up the Hello MQTT component."""
    mqtt = hass.components.mqtt

    global g_debounce_devices
    g_debounce_devices = config[DOMAIN].get(CONF_DEBOUNCE)

    global g_sub_topic, g_pub_topic
    g_sub_topic = config[DOMAIN].get(CONF_SUB_TOPIC)
    g_pub_topic = config[DOMAIN].get(CONF_PUB_TOPIC)

    if g_sub_topic == None:
        _LOGGER.error("No subscription topic specified for mqtt!")
        return False

    if g_pub_topic == None:
        _LOGGER.error("No publish topic specified for mqtt!")

    # Listener to be called when we receive a message.
    # The msg parameter is a Message object with the following members:
    # - topic, payload, qos, retain
    def message_received(msg):
        _LOGGER.info("Received Message: " + msg.payload)    

        """Callback for MQTT message PUBLISH."""
        try:
            # Decode JSON payload
            data = json.loads(msg.payload)
            bridge_event_to_hass(mqtt, msg.topic, data)

        except json.decoder.JSONDecodeError:
            _LOGGER.info("JSON decode error: " + msg.payload)
            return
        
    # Subscribe our listener to a topic.
    mqtt.subscribe(g_sub_topic, message_received)

    # Return boolean to indicate that initialization was successfully.
    return True
    

