Largly influenced by the work done [here](https://github.com/dandydanny/PiAutoDim)

### Software Setup
#### Edit the backlight permissions file to allow read and write permissions to all users:

`sudo nano /etc/udev/rules.d/backlight-permissions.rules`

Insert:

`SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"`

#### Put `autobrightness.py` on your pi, in a directory called `PiAutoDim`:

`mkdir /home/pi/PiAutoDim`

#### Enable autorun of `autobrightness.py` on boot, by making it a `systemd` service

In `/etc/systemd/system/`, make a `autobrightness.service` file.

`touch autobrightness.service`

Open this file in an editor:

`sudo nano autobrightness.service`

Put in following:
```
[Unit]
Description=Get auto brightness service running at boot

[Service]
ExecStart=/usr/bin/python3 /home/pi/PiAutoDim/auto_dim.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=autobrightness
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

Press `CTRL-O` to save, and `CTRL-X` to exit nano editor.

Enable service to run on startup:

`sudo systemctl enable autobrightness.service`

Start autobrightness service (for current boot):

`sudo systemctl start autobrightness.service`

Check if it's running:

`systemctl status autobrightness.service`
