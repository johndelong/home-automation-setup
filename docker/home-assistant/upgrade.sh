#!/bin/bash

# Stop Docker
docker stop home-assistant

# Remove the docker container
docker rm home-assistant

# Retrieve the new image
docker pull homeassistant/home-assistant:latest

# Create the container
docker-compose up -d
