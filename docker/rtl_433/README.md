Based of [this repo](https://github.com/LinuxChristian/rtl_433-docker)

# Install Driver for RTL-SDR Dongle
https://tinjaw.com/2017/09/17/using-nooelec-nesdr-smart-on-a-raspberry-pi/

See attached devices using the `lsusb` command. Verify you see a device named `Realtek Semiconductor Corp. RTL2838 DVB-T` attached.

By default, the OS loads an incorrect driver. To resolve this issue, we blacklist the driver the OS is trying to use with the following commands.
```bash
nano /etc/modprobe.d/blacklist-dvb.conf
```

And then add the following line to the file and then save and close.
```bash
blacklist dvb_usb_rtl28xxu
```
Next, install the actual driver we want to use.

```bash
sudo apt-get install rtl-sdr
```

Finally, we can test that everything is working by executing the following command:
```bash
rtl_test
```

**NOTE:**
For some reason i was running into an issue when i tried to find the attached usb dongle using the `lsusb` command. After some digging, i found [this issue](https://github.com/raspberrypi/linux/issues/3779) and resolved it be removing the problem package with the following command. 

```bash
sudo apt remove rpi.gpio-common
```

So long as you don't plan on using the GPIO pins, this is a sutable solution. Hopefully this issue is resolved soon.


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
