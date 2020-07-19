# Baseed on this repo
# https://github.com/LinuxChristian/rtl_433-docker/blob/master/Dockerfile

FROM debian:latest
MAINTAINER John DeLong <johnnydelong@gmail.com>

WORKDIR /tmp/

# Get the dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY discovery.py .

# Copy and execute the start script
COPY start.sh .
RUN chmod +x ./start.sh
CMD ./start.sh