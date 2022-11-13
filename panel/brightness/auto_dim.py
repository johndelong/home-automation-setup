from time import sleep
import os

min_brightness = 20
max_brightness = 100
prev_brightness = max_brightness

wait = 60 * 1000 # 1 min (Time in miliseconds)

# Open backlight control 'file' for writing
f = open('/sys/class/backlight/10-0045/brightness', 'w')

while True:
    idle = int(os.popen('DISPLAY=:0 xprintidle').read())

    brightness = max_brightness
    if idle > wait:
        brightness = min_brightness

    # Only write (change) backlight value if there's sensor level change
    if prev_brightness != brightness:
        prev_brightness = brightness

        f.seek(0)
        f.write(str(brightness))
        f.truncate()

    # Evaluate once a second
    sleep(1)