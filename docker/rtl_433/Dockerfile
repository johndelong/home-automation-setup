# Baseed on this repo
# https://github.com/LinuxChristian/rtl_433-docker/blob/master/Dockerfile

FROM debian:latest
MAINTAINER John DeLong <johnnydelong@gmail.com>

WORKDIR /tmp/

# Get the dependencies
RUN apt-get update
RUN apt-get install -y git libtool libusb-1.0-0-dev librtlsdr-dev rtl-sdr build-essential autoconf cmake pkg-config python3 python3-pip
RUN git clone https://github.com/merbanan/rtl_433.git

# Copy Resources
COPY build.sh .

# Build rtl_433
RUN ./build.sh

COPY ha_discovery.py .

COPY rtl_start.sh .
CMD ./rtl_start.sh