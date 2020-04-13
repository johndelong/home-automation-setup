Based of [this repo](https://github.com/LinuxChristian/rtl_433-docker)

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
docker run -itd --name rtl_433 --device=/dev/bus/usb/001/006 -e MQTT_IP='192.168.86.95' -e MPTT_USER='user' -e MQTT_PASSWORD='password' rtl_433
```

# Notes:

You may need to update the file permissions for the bash files

```bash
chmod +x {filename}.sh
```
