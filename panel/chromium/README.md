Largly influenced by the work done [here](https://blog.r0b.io/post/minimal-rpi-kiosk/)

# Setup

Start with Raspbian Lite (not the desktop version). Then install the packages required to run chromium and set the pi to boot straight into to the console.

```bash
sudo apt-get update -qq

sudo apt-get install --no-install-recommends xserver-xorg-video-all \
  xserver-xorg-input-all xserver-xorg-core xinit x11-xserver-utils \
  chromium-browser unclutter

# Go to: Boot Options > Console Autologin
sudo raspi-config
```

Next edit `/home/pi/.bash_profile` to automatically start the gui. There's a check for the bash context first, so you don't accidentally start chromium whenever you ssh in.

```bash
if [ -z $DISPLAY ] && [ $(tty) = /dev/tty1 ]
then
  startx
fi
```

The last bit is to setup `/home/pi/.xinitrc` to run chromium whenever you run startx. Here's the full list of [chromium arguments](https://peter.sh/experiments/chromium-command-line-switches/).

```bash
#!/usr/bin/env sh
xset -dpms
xset s off      # disable screen saver
xset s noblank  # don't blank the video device

unclutter &
chromium-browser http://192.168.86.62:8123/ \
  --window-size=800,480 \
  --window-position=0,0 \
  --start-fullscreen \
  --kiosk \
  --incognito \
  --noerrdialogs \
  --disable-translate \
  --no-first-run \
  --fast \
  --fast-start \
  --disable-infobars \
  --disable-features=TranslateUI \
  --disk-cache-dir=/dev/null \
  --overscroll-history-navigation=0 \
  --disable-pinch
```

It disables the cursor and screensaver. Then runs chromium with *all* of the flags. Set `https://yourfancywebsite.com` to the website which you want to display. And set `--window-size` to the size of your display (it's horizontal first and vertical after the comma).

> You may also want to uncomment `disable_overscan=1` in `/boot/config.txt` so that the pi boots up using the full display.

Now whenever the pi boots up it'll go into the console then on into chromium. If you want to exit you can hit `Alt+F4`, then enter `startx` to start up the browser again.