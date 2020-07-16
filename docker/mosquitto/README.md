https://hub.docker.com/_/eclipse-mosquitto

docker run -it -d -p 1883:1883 -p 9001:9001 -v /home/pi/docker/mosquitto/:/mosquitto/ eclipse-mosquitto
