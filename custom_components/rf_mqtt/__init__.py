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

recognized_devices = {
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

def publish_config(hass, mqttc, topic, model, instance, mapping):
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
    config["state_topic"] = topic
    config["unique_id"] = object_id

    _LOGGER.info("Publishing config: " + json.dumps(config))
    mqttc.publish(hass, path, json.dumps(config))

def debounce(hass, mqttc, topic, debounce_count, data):
    global g_debounced_messages

    device_id = data["id"]
    raw_msg = data["raw_message"]

    now = time.time()
    blank = {"raw_msg": raw_msg, "count": 0, "updated": now}

    msg_count = g_debounced_messages.get(device_id, blank)

    # If message is older than 2 seconds, restart the debounce
    if now - msg_count["updated"] > 2:
        g_debounced_messages[device_id] = blank

    # Increment the number of times we've seen this message
    if msg_count["raw_msg"] == raw_msg:
        msg_count["count"] += 1
    else:
        # There is a new message we should start debouncing
        msg_count["raw_msg"] = raw_msg
        msg_count["count"] = 1

    # Save this entry so we can refer to it later
    g_debounced_messages[device_id] = msg_count

    _LOGGER.info("Debouncing message (" + str(msg_count["count"]) + " of " + str(debounce_count) + ") to topic: " + topic)

    if msg_count["count"] >= debounce_count:
        message = json.dumps(data)
        _LOGGER.info("Publishing (debounced) message to topic: " + topic + "\n" + message)
        mqttc.publish(hass, topic, message)
    
def bridge_event_to_hass(hass, mqttc, original_topic, data):
    """Translate some rtl_433 sensor data to Home Assistant auto discovery."""

    if "model" not in data:
        # not a device event
        return

    model = sanitize(data["model"])
    topic = "/".join([g_pub_topic, original_topic])

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

    # Look for known attributes in this message and configure devices
    for key in data.keys():
        if key == "subtype":
            key = data[key]

        if key in recognized_devices:
            publish_config(hass, mqttc, topic, model, instance, recognized_devices[key])

    # Check if this message should be debounced
    did_debounce = False
    for key in data.keys():
        if key == "subtype":
            key = data[key]

        if key in g_debounce_devices:
            # Debounce this message
            debounce(hass, mqttc, topic, g_debounce_devices[key], data)
            did_debounce = True
            break
    
    if did_debounce == False:
        # Just send the message on the alterted topic
        message = json.dumps(data)
        _LOGGER.info("Publishing (non-debounced) message to topic: " + topic + "\n" + message)
        mqttc.publish(hass, topic, message)

def setup(hass, config):
    """Set up the Hello MQTT component."""
    mqtt = hass.components.mqtt

    global g_debounce_devices
    g_debounce_devices = config[DOMAIN].get(CONF_DEBOUNCE)

    _LOGGER.info("Loaded devices to be debounced: " + str(g_debounce_devices))

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
        _LOGGER.info("Received message on topic: " + msg.topic + "\n" + msg.payload)    

        """Callback for MQTT message PUBLISH."""
        try:
            # Decode JSON payload
            data = json.loads(msg.payload)
            bridge_event_to_hass(hass, mqtt, msg.topic, data)

        except json.decoder.JSONDecodeError:
            _LOGGER.info("JSON decode error: " + msg.payload)
            return
        
    # Subscribe our listener to a topic.
    mqtt.subscribe(g_sub_topic, message_received)

    # Return boolean to indicate that initialization was successfully.
    return True
