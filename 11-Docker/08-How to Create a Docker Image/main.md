# How to Create a Docker Image

This section covers creating a custom Docker image by writing a `Dockerfile` and building it with the `docker image build` command.

## Running the Default NGINX Container

Start by running the official NGINX image to verify it works:

```bash
docker container run --rm --detach --name default-nginx --publish 8080:80 nginx

docker container ls
```

Visit `http://127.0.0.1:8080` in the browser and you will see the default NGINX response page.

## Writing a Custom NGINX Dockerfile

To make a custom NGINX image, the image should:

- Have NGINX pre-installed (using a package manager).
- Start NGINX automatically upon running.

If you've cloned the project repository, go to the `custom-nginx` directory inside the project root. Create a new file named `Dockerfile` inside that directory with the following content:

```dockerfile
FROM ubuntu:latest

EXPOSE 80

RUN apt-get update && \
    apt-get install nginx -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["nginx", "-g", "daemon off;"]
```

### Explanation of Instructions

- **FROM** sets `ubuntu:latest` as the base image for the resulting image.
- **EXPOSE** indicates the port that needs to be published. Note that this instruction alone does not publish the port — you still need to use `--publish` explicitly when running the container. It acts as documentation and has some additional uses.
- **RUN** executes commands inside the container shell. `apt-get update && apt-get install nginx -y` installs NGINX, and `apt-get clean && rm -rf /var/lib/apt/lists/*` clears the package cache to keep the image lean.
- **CMD** sets the default command for the image. Running NGINX as a single process (`daemon off;`) inside containers is considered a best practice.

## Building the Image

```bash
docker image build .
```

## Running a Container from the Custom Image

Use the image ID from the build output (e.g., `3199372aa3fc`) to run a container:

```bash
docker container run --rm --detach --name custom-nginx-packaged --publish 8080:80 3199372aa3fc

docker container ls
```

Visit `http://127.0.0.1:8080` to verify the default NGINX response page is served.
