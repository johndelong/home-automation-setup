# home-assistant-config

# ZWave Controller Setup

Get info on the attached devices:

```bash
udevadm info -a -p $(udevadm info -q path -n /dev/ttyUSB0)
```

Edit file: `/etc/udev/rules.d/99-usb-serial.rules`

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="0658", ATTRS{idProduct}=="0200", SYMLINK+="ttyUSB-ZStick-5G"
SUBSYSTEM=="tty", ATTRS{interface}=="HubZ Z-Wave Com Port", SYMLINK+="ttyUSB-zwave"
SUBSYSTEM=="tty", ATTRS{interface}=="HubZ ZigBee Com Port", SYMLINK+="ttyUSB-zigbee"
```

After updating this file, run the following command to refresh

```bash
sudo udevadm trigger
```

Tell the docker container about our devices by using the symlink

```
sudo docker run --restart=always -d --name="home-assistant" -v /volume1/docker/home_assistant:/config --device=/dev/ttyUSB-zigbee:/dev/ttyUSB-zigbee --device=/dev/ttyUSB-zwave:/dev/ttyUSB-zwave -e TZ=America/Detroit --net=host homeassistant/home-assistant
```

Add the following configurations to Home assistant `configuration.yaml` file

```yaml
zwave:
  usb_path: /dev/ttyUSB-zwave
zigbee:
  device: /dev/ttyUSB-zigbee
```
