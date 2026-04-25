# Mount a Docker Volume to a Container

This guide demonstrates how to mount a local file or directory into a running Docker container using volumes and bind mounts.

Reference video: [TechnoPanti — Docker Volumes](https://www.youtube.com/watch?v=B9uaQcc2dLs&list=WL&index=4&ab_channel=TechnoPanti)

## Basic Example: Mounting a Single File

The following steps show how to create a file on the host and access it from inside a container.

1. Create a file on the host:

```bash
touch abc.txt
```

2. Create some content in it (optional):

```bash
vim abc.txt
```

3. Confirm the file location:

```bash
ls
# Location of the file: /home/gagan/abc.txt
```

4. Run a container with the file mounted to `/temp` inside the container:

```bash
docker run -d --volume /home/gagan/abc.txt:/temp <image-id> sleep infinity
```

`/temp` is the folder inside the container where the file will be accessible.

5. Access the file from inside the container:

```bash
docker exec -it <container-id> sh
cd /temp
cat abc.txt
```

## Bind Mounting a Project Directory

To mount an entire project directory (useful for live development), use `$(pwd)` to refer to the current working directory:

```bash
docker container run \
    --rm \
    --publish 3000:3000 \
    --name hello-dock-dev \
    --volume $(pwd):/home/node/app \
    hello-dock:dev
```

## Using Volumes in a Docker Compose File

The equivalent configuration in a `docker-compose.yml` file looks like this:

```yaml
python:
  container_name: python
  image: aimvector/python:1.0.0
  build:
    context: ./python
    target: debug
  # working_dir: /work      # comment out for build.target:prod
  # entrypoint: /bin/sh     # comment out for build.target:prod
  # stdin_open: true        # comment out for build.target:prod
  # tty: true               # comment out for build.target:prod
  volumes:
    - ./11-Docker/01_docker_dotnet/:/work  # local source directory
  ports:
    - 5003:5000
    - 5678:5678
```

## Running and Connecting to the Compose Service

Build and start the service in the background:

```bash
docker-compose up -d
```

Verify the running containers:

```bash
docker ps
```

Connect to the `python` container interactively:

```bash
docker exec -it python sh
```
