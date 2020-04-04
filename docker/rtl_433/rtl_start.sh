#!/bin/bash
rtl_433 -f 319500000 -R 100 -C si -M newmodel -F "mqtt://192.168.86.95:1883,user={broker}},pass={password}"