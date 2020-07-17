https://hub.docker.com/_/eclipse-mosquitto

Create directories and change the permission so docker can access them
```
chmod -R 0777 /home/pi/docker/mqtt/*
```

Without Docker Compose
```bash
docker run -it -d -p 1883:1883 -p 9001:9001 -v /home/pi/docker/mosquitto/:/mosquitto/ eclipse-mosquitto
```

With Docker Compose
```
docker-compose -f docker-compose.yml up -d
```


https://hometechhacker.com/mqtt-using-docker-and-home-assistant/

Adding security
As it is currently set up, any client can connect to your broker to publish and subscribe to any topic. You can add some security by requiring a username and password for clients to connect to the broker.

First, you’ll need to create a password file. The best way is to connect to your container and run mosquitto_passwd. In order to connect to your container’s console you need to find out its ID:

Shell
```
docker ps
```
This will give you a list of containers and their IDs. Using that ID you can then run:

Shell
```
docker exec -it <containerID> bash
```
Replacing <containerID> with the container of your Mosquitto container will give you a command line. Alternatively, you can use Portainer to connect directly to the console.

From the console run something similar to:

Shell
```
mosquitto_passwd -c /mqtt/config/credentials <username
```
With appropriate filename and username arguments, this command will ask for a password and then create a hashed password file. Then you need to update your Mosquitto config.

If you used a mosquitto.conf file similar to what I posted above you need to create a default.conf file in the conf.d subdirectory of your config directory with the following contents:

Shell
```
1 allow_anonymous false
2 password_file /mqtt/config/credentials
```
Remember to use the appropriate password_file path and filename. After restarting the container your publish and subscribe commands will need to have a username and password to work:

Shell
```
mosquitto_sub -h <brokerhost> -t "test" -u "<username>" -P "<password>"
mosquitto_pub -h <brokerhost> -t "test" -m "Hello World" -u "<username>" -P "<password>"
```
You can make your broker more secure by using web sockets or TLS. Digital Ocean has a great tutorial.