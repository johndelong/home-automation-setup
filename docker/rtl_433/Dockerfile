# Baseed on this repo
# https://github.com/LinuxChristian/rtl_433-docker/blob/master/Dockerfile

FROM debian:latest
MAINTAINER John DeLong <johnnydelong@gmail.com>

WORKDIR /tmp/

RUN apt-get update

RUN apt-get install -y git libtool libusb-1.0-0-dev librtlsdr-dev rtl-sdr build-essential autoconf cmake pkg-config

RUN git clone https://github.com/merbanan/rtl_433.git

COPY build.sh .
COPY rtl_start.sh .
# COPY rtl_433_events.py .
# COPY utils.py .

# Build rtl_433
RUN ./build.sh

RUN ./rtl_start.sh

# CMD python3 rtl_433_events.py