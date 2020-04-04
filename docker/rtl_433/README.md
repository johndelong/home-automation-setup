Based of [this repo](https://github.com/LinuxChristian/rtl_433-docker)

# Attaching the dongle

- Find the RTL-SDR dongle usb bus address using lsusb in the host OS,

  # Example output (System dependent)

  Bus 003 Device 006: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T

- Attach the usb device to the container

  docker run -d --name rtl_433 --device=/dev/bus/usb/003/006 -e MQTT_IP='10.0.0.1' rtl_433

# Build Docker Container

You may need to update the file permissions for the bash files

```bash
chmod +x {filename}.sh
```

Run

```bash
docker build -t rtl_433 .
```
