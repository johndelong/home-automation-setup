# Common Useful Docker Commands

Start a docker container
```bash
docker start <containerID>
```

Stop a docker container
```bash
docker stop <containerID>
```

Remove a docker container
```bash
docker rm <containerID>
```

Run a command inside a docker container
```bash
docker exec -it <containerID> sh
```

Get logs for a docker container
```bash
docker logs <containerID>
```

List running docker containers
```bash
docker ps
```

List all docker containers
```bash
docker ps -a
```

Delete all unused images/containers
```bash
docker system prune -a
```

Build a docker image using the files in the local directory
```bash
docker build -t <imageName> .
```

## Common Arguments
???
```bash
-it
```

Run the container detached
```bash
-d
```