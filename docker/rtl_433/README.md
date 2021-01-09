Based of [this repo](https://github.com/LinuxChristian/rtl_433-docker)

# Install Driver for RTL-SDR Dongle
https://tinjaw.com/2017/09/17/using-nooelec-nesdr-smart-on-a-raspberry-pi/


# Build Docker Image

```bash
docker build -t rtl_433 .
```

# Attaching the dongle

Find the RTL-SDR dongle usb bus address using `lsusb` in the host OS.

**Example output (System dependent)**

```bash
Bus 003 Device 006: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
```

# Build Docker Container

```bash
docker run -itd --name rtl_433 --device=/dev/bus/usb/001/006 -e MQTT_IP='192.168.86.95' -e MQTT_USER='user' -e MQTT_PASSWORD='password' rtl_433
```

With Docker Compose
```
docker-compose up -d
```

# Notes:

You may need to update the file permissions for the bash files

```bash
chmod +x {filename}.sh
```
