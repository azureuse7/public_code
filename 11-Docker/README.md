# Docker: Containerisation

> Practical Docker guides covering essential commands, Dockerfile authoring, image building, volumes, networking, Docker Compose, multi-stage builds, and real-world project examples.

---

## Contents

| Directory | Topic |
|-----------|-------|
| [00-Essential-Docker-Commands/](00-Essential-Docker-Commands/) | Must-know Docker CLI commands — run, stop, rm, ps, exec, logs |
| [000-Docker-Tag-and-Push/](000-Docker-Tag-and-Push/) | Tagging images and pushing to a registry (Docker Hub / ACR) |
| [01-Mount docker volume to the conatiner/](01-Mount%20docker%20volume%20to%20the%20conatiner/) | Bind mounts and named volumes |
| [02-Create a Dockerfile/](02-Create%20a%20Dockerfile/) | Writing a Dockerfile from scratch |
| [03-Docker-Compose/](03-Docker-Compose/) | Docker Compose — multi-container applications |
| [07-How to Publish a Port/](07-How%20to%20Publish%20a%20Port/) | `-p` flag — mapping container ports to host ports |
| [08-How to Create a Docker Image/](08-How%20to%20Create%20a%20Docker%20Image/) | `docker build` workflow |
| [09-How to Tag Docker Images/](09-How%20to%20Tag%20Docker%20Images/) | Image tagging conventions and strategies |
| [10-Many Layers of a Docker Image/](10-Many%20Layers%20of%20a%20Docker%20Image/) | Understanding image layers and caching |
| [11-Executable Docker Images/](11-Executable%20Docker%20Images/) | `ENTRYPOINT` vs `CMD` — making images executable |
| [12-Multi-Staged Builds in Docke/](12-Multi-Staged%20Builds%20in%20Docke/) | Multi-stage builds — smaller production images |
| [13-Network Manipulationr/](13-Network%20Manipulationr/) | Docker networks — bridge, host, custom networks |
| [14-Execute Commands in a Running Container/](14-Execute%20Commands%20in%20a%20Running%20Container/) | `docker exec` — run commands inside a live container |
| [00-GIT-Repo/docker-handbook-projects/](00-GIT-Repo/docker-handbook-projects/) | Full-stack application examples from the Docker Handbook |

---

## Essential Commands

### Container lifecycle
```bash
# Run a container interactively
docker run -it ubuntu /bin/bash

# Run detached with port mapping and name
docker run -d -p 8080:80 --name my-app nginx

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop and remove a container
docker stop my-app && docker rm my-app

# Stream logs
docker logs -f my-app

# Execute a command in a running container
docker exec -it my-app /bin/sh
```

### Images
```bash
# Build an image from a Dockerfile
docker build -t my-image:1.0 .

# Tag an image for a registry
docker tag my-image:1.0 myregistry.azurecr.io/my-image:1.0

# Push to a registry
docker push myregistry.azurecr.io/my-image:1.0

# Pull an image
docker pull nginx:latest

# List local images
docker images

# Remove an image
docker rmi my-image:1.0
```

### Volumes
```bash
# Named volume
docker run -v my-volume:/app/data my-image

# Bind mount (host path)
docker run -v $(pwd)/data:/app/data my-image
```

---

## Dockerfile Best Practices

```dockerfile
# Use a specific tag, not 'latest'
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy dependency files first (layer caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

## Multi-Stage Build Example

```dockerfile
# Stage 1: build
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o app

# Stage 2: minimal runtime image
FROM alpine:3.18
COPY --from=builder /app/app /app
CMD ["/app"]
```
