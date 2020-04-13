import homeassistant.loader as loader

import time
import json

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "hello_mqtt"

# List of integration names (string) your integration depends upon.
DEPENDENCIES = ["mqtt"]

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "home-assistant/hello_mqtt"

MQTT_TOPIC = "rtl_433/+/events"
DISCOVERY_PREFIX = "homeassistant"

DISCOVERY_INTERVAL = 600  # Seconds before refreshing the discovery
discovery_timeouts = {}

mappings = {
    "temperature_C": {
        "device_type": "sensor",
        "object_suffix": "T",
        "config": {
            "device_class": "temperature",
            "name": "Temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{ value_json.temperature_C }}"
        }
    },
    "temperature_1_C": {
        "device_type": "sensor",
        "object_suffix": "T1",
        "config": {
            "device_class": "temperature",
            "name": "Temperature 1",
            "unit_of_measurement": "°C",
            "value_template": "{{ value_json.temperature_1_C }}"
        }
    },
    "temperature_2_C": {
        "device_type": "sensor",
        "object_suffix": "T2",
        "config": {
            "device_class": "temperature",
            "name": "Temperature 2",
            "unit_of_measurement": "°C",
            "value_template": "{{ value_json.temperature_2_C }}"
        }
    },
    "temperature_F": {
        "device_type": "sensor",
        "object_suffix": "F",
        "config": {
            "device_class": "temperature",
            "name": "Temperature",
            "unit_of_measurement": "°F",
            "value_template": "{{ value_json.temperature_F }}"
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

    "humidity": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
            "name": "Humidity",
            "unit_of_measurement": "%",
            "value_template": "{{ value_json.humidity }}"
        }
    },

    "moisture": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "moisture",
            "name": "Moisture",
            "unit_of_measurement": "%",
            "value_template": "{{ value_json.moisture }}"
        }
    },

    "pressure_hPa": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "name": "Pressure",
            "unit_of_measurement": "hPa",
            "value_template": "{{ value_json.pressure_hPa }}"
        }
    },

    "wind_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "weather",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value_json.wind_speed_km_h }}"
        }
    },

    "wind_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "weather",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value_json.wind_speed_m_s) * 3.6 }}"
        }
    },

    "gust_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "weather",
            "name": "Gust Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value_json.gust_speed_km_h }}"
        }
    },

    "gust_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "weather",
            "name": "Gust Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value_json.gust_speed_m_s) * 3.6 }}"
        }
    },

    "wind_dir_deg": {
        "device_type": "sensor",
        "object_suffix": "WD",
        "config": {
            "device_class": "weather",
            "name": "Wind Direction",
            "unit_of_measurement": "°",
            "value_template": "{{ value_json.wind_dir_deg }}"
        }
    },

    "rain_mm": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "device_class": "weather",
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ value_json.rain_mm }}"
        }
    },

    "rain_mm_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "device_class": "weather",
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ value_json.rain_mm_h }}"
        }
    },

    # motion...
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

    # switches...

    # binary sensors ...

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

    "depth_cm": {
        "device_type": "sensor",
        "object_suffix": "D",
        "config": {
            "device_class": "depth",
            "name": "Depth",
            "unit_of_measurement": "cm",
            "value_template": "{{ value_json.depth_cm }}"
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
    print("Model: " + model)
    print("Instance: " + instance)
    print("Mapping: " + json.dumps(mapping))    

    """Publish Home Assistant auto discovery data."""
    global discovery_timeouts

    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = "-".join([model, instance, object_suffix])

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, "config"])

    # check timeout
    now = time.time()
    if path in discovery_timeouts:
        if discovery_timeouts[path] > now:
            return

    discovery_timeouts[path] = now + DISCOVERY_INTERVAL

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
    entity_id = "hello_mqtt.last_message"

    # Listener to be called when we receive a message.
    # The msg parameter is a Message object with the following members:
    # - topic, payload, qos, retain
    def message_received(msg):
        print("Received Message: " + msg.payload)    

        """Handle new MQTT messages."""
        hass.states.set(entity_id, msg.payload)

        """Callback for MQTT message PUBLISH."""
        try:
            # Decode JSON payload
            data = json.loads(msg.payload)
            bridge_event_to_hass(mqtt, msg.topic, data)
    
        except json.decoder.JSONDecodeError:
            print("JSON decode error: " + msg.payload)
            return
        
    # Subscribe our listener to a topic.
    mqtt.subscribe(MQTT_TOPIC, message_received)
    print("Subscribed to actual topic: " + MQTT_TOPIC)
    print("Subscribed to topic: " + topic)

    # Set the initial state.
    hass.states.set(entity_id, "No messages")

    # Service to publish a message on MQTT.
    def set_state_service(call):
        """Service to send a message."""
        mqtt.publish(topic, call.data.get("new_state"))

    # Register our service with Home Assistant.
    hass.services.register(DOMAIN, "set_state", set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True
    

