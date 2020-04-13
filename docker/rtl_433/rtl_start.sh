#!/bin/bash
rtl_433 -f 319500000 -R 100 -C si -M newmodel -F "mqtt://${MQTT_IP}:1883,user=${MQTT_USER},pass=${MQTT_PASSWORD}"