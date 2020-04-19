#!/bin/bash
rtl_433 -f 319500000 -R 100 -C si -M newmodel -X "repeats>=4" -F "mqtt://${MQTT_IP}:1883,retain=1,events=rtl_433/events[/type][/model][/subtype][/channel][/id],user=${MQTT_USER},pass=${MQTT_PASSWORD}"
