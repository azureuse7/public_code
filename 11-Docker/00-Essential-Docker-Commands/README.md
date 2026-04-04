# Essential Docker Commands

This file covers the fundamental concepts of Docker — containers, images, and the Docker architecture — along with the most commonly used Docker commands.

## Core Concepts

### Three Fundamental Concepts of Containerization

- **Container**
- **Image**
- **Registry**

### What is a Container?

- A container is an abstraction at the application layer that packages code and dependencies together.
- Instead of virtualizing the entire physical machine, containers virtualize the host operating system only.
- Just like virtual machines, containers are completely isolated environments from the host system as well as from each other.
- Containers and virtual machines are actually different ways of virtualizing your physical hardware.
- Virtual machines are usually created and managed by a program known as a hypervisor, like Oracle VM VirtualBox, VMware Workstation, KVM, Microsoft Hyper-V, and so on. This hypervisor program usually sits between the host operating system and the virtual machines to act as a medium of communication.
- Each virtual machine comes with its own guest operating system which is just as heavy as the host operating system.
- The application running inside a virtual machine communicates with the guest operating system, which talks to the hypervisor, which then in turn talks to the host operating system to allocate necessary resources from the physical infrastructure to the running application.
- As you can see, there is a long chain of communication between applications running inside virtual machines and the physical infrastructure. The application running inside the virtual machine may take only a small amount of resources, but the guest operating system adds a noticeable overhead.
- Unlike a virtual machine, a container does the job of virtualization in a smarter way. Instead of having a complete guest operating system inside a container, it just utilizes the host operating system via the container runtime while maintaining isolation — just like a traditional virtual machine.
- The container runtime (Docker) sits between the containers and the host operating system instead of a hypervisor. The containers then communicate with the container runtime which then communicates with the host operating system to get necessary resources from the physical infrastructure.
- As a result of eliminating the entire guest operating system layer, containers are much lighter and less resource-intensive than traditional virtual machines.

As a demonstration, look at the following code block:

```bash
uname -a
# Linux alpha-centauri 5.8.0-22-generic #23-Ubuntu SMP Fri Oct 9 00:34:40 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux

docker run alpine uname -a
# Linux f08dbbe9199b 5.8.0-22-generic #23-Ubuntu SMP Fri Oct 9 00:34:40 UTC 2020 x86_64 Linux
```

In the code block above, the `uname -a` command is executed on the host operating system to print out the kernel details. Then the same command is executed inside a container running Alpine Linux. As you can see in the output, the container is using the kernel from the host operating system. This proves that containers virtualize the host operating system instead of having an operating system of their own.

If you're on a Windows machine, you'll find that all containers use the WSL2 kernel. This happens because WSL2 acts as the back-end for Docker on Windows. On macOS the default back-end is a VM running on the HyperKit hypervisor.

### What is a Docker Image?

- Images are multi-layered, self-contained files that act as the template for creating containers. They are like a frozen, read-only copy of a container. Images can be exchanged through registries.
- In the past, different container engines had different image formats. Later on, the Open Container Initiative (OCI) defined a standard specification for container images which is followed by the major containerization engines. This means that an image built with Docker can be used with another runtime like Podman without any additional hassle.
- Containers are just images in a running state. When you obtain an image and run a container from it, you essentially create another temporary writable layer on top of the previous read-only ones.

## Docker Architecture Overview

The Docker engine consists of three major components:

- **Docker Daemon**: The daemon (`dockerd`) is a process that keeps running in the background and waits for commands from the client. The daemon is capable of managing various Docker objects.
- **Docker Client**: The client (`docker`) is a command-line interface program mostly responsible for transporting commands issued by users.
- **REST API**: The REST API acts as a bridge between the daemon and the client. Any command issued using the client passes through the API to finally reach the daemon.

### The Full Picture

Here is what happens when you run `docker run hello-world`:

1. The **Docker client** reaches out to the daemon and tells it to get the `hello-world` image and run a container from it.
2. The **Docker daemon** looks for the image within your local repository and, if it's not found, prints `Unable to find image 'hello-world:latest' locally`.
3. The daemon then reaches out to the default public registry (Docker Hub) and pulls in the latest copy of the `hello-world` image.
4. The **Docker daemon** creates a new container from the freshly pulled image and runs it.

It's the default behavior of the Docker daemon to look for images on Docker Hub when they are not present locally. But once an image has been fetched, it'll stay in the local cache. So if you run the command again, you won't see the following lines:

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete
Digest: sha256:d58e752213a51785838f9eed2b7a498ffa1cb3aa7f946dda11af39286c3db9a9
Status: Downloaded newer image for hello-world:latest
```

If there is a newer version of the image available on the public registry, the daemon will fetch the image again. The `:latest` portion is a tag. Images usually have meaningful tags to indicate versions or builds.

## How to Run a Container

```bash
docker run <image name>
```

A better way of dispatching commands to the Docker daemon uses this syntax:

```bash
docker <object> <command> <options>
```

In this syntax:

- **object** indicates the type of Docker object you'll be manipulating. This can be a `container`, `image`, `network`, or `volume` object.
- **command** indicates the task to be carried out by the daemon, such as the `run` command.
- **options** can be any valid parameter that overrides the default behavior of the command, like the `--publish` option for port mapping.

The `run` command can also be written as:

```bash
docker container run <image name>
```

To run a container using a specific image, execute the following command:

```bash
docker container run --publish 8080:80 fhsinchy/hello-dock
```

## Container Management Commands

### List Containers

List containers currently running:

```bash
docker container ls
```

List all containers including stopped ones:

```bash
docker container ls --all
```

Shorthand equivalent:

```bash
docker ps -a
```

### Name or Rename a Container

By default, every container has two identifiers:

- **CONTAINER ID** — a random 64-character string.
- **NAME** — a combination of two random words joined with an underscore.

Naming a container is achieved using the `--name` option:

```bash
docker container run --detach --publish 8888:80 --name hello-dock-container fhsinchy/hello-dock
```

Rename an existing container:

```bash
docker container rename <container identifier> <new name>
```

### Stop or Kill a Running Container

Containers running in the foreground can be stopped by closing the terminal window or pressing `Ctrl+C`. Containers running in the background must be stopped with a command.

Stop a container gracefully (sends `SIGTERM`):

```bash
docker container stop <container identifier>
```

Example:

```bash
docker container stop hello-dock-container
```

Kill a container immediately (sends `SIGKILL`):

```bash
docker container kill hello-dock-container-2
```

### Restart a Container

```bash
docker container start <container identifier>
```

Example:

```bash
docker container start hello-dock-container

docker container restart hello-dock-container-2
```

### Create a Container Without Running

```bash
docker container create --publish 8080:80 fhsinchy/hello-dock

docker container ls --all

docker container start hello-dock

docker container ls
```

### Remove Dangling Containers

Containers that have been stopped or killed remain in the system until explicitly removed.

```bash
docker container rm <container identifier>
```

Example:

```bash
docker container rm 6cf52771dde1
```

Verify removal:

```bash
docker container ls --all
```

### Run a Container in Interactive Mode

```bash
docker container run --rm -it ubuntu
```

The `-it` option sets the stage for you to interact with any interactive program inside a container. It is made up of two separate options:

- `-i` or `--interactive` — connects you to the input stream of the container so you can send input to bash.
- `-t` or `--tty` — allocates a pseudo-TTY for proper formatting and a native terminal-like experience.

Use `-it` whenever you want to run a container in interactive mode. Another example:

```bash
docker container run -it node
```

### Execute Commands Inside a Container

Pass a command to a running container:

```bash
docker run alpine uname -a
```

Generic syntax for passing a command to a container:

```bash
docker container run <image name> <command>
```

Example with shell command substitution:

```bash
docker container run --rm busybox sh -c "echo -n my-secret | base64"
```

## Image Management Commands

### List and Remove Docker Images

Remove a specific image:

```bash
docker image rm <image identifier>

docker image rm custom-nginx:packaged
```

Remove all untagged (dangling) images:

```bash
docker image prune --force
```

### How to Access Logs from a Container

```bash
docker container logs <container identifier>
```

Example:

```bash
docker container logs notes-db
```

### Delete All Containers Including Volumes

```bash
docker rm -vf $(docker ps -aq)
```

### Delete All Images

```bash
docker rmi -f $(docker images -aq)
```

#### Windows — PowerShell

```bash
docker images -a -q | % { docker image rm $_ -f }
```

#### Windows — cmd.exe

```
for /F %i in ('docker images -a -q') do docker rmi -f %i
```

## Quick Reference Table

The following table summarizes the most commonly used Docker commands:

| Command | Description |
| ------- | ----------- |
| `docker ps` | List all running containers |
| `docker ps -a` | List all containers (stopped and running) |
| `docker stop <container-id>` | Stop the container that is running |
| `docker start <container-id>` | Start a container that is stopped |
| `docker restart <container-id>` | Restart the container that is running |
| `docker port <container-id>` | List port mappings of a specific container |
| `docker rm <container-id or name>` | Remove a stopped container |
| `docker rm -f <container-id or name>` | Remove a running container forcefully |
| `docker pull <image-info>` | Pull the image from Docker Hub repository |
| `docker exec -it <container-name> /bin/sh` | Connect to a Linux container and execute commands |
| `docker rmi <image-id>` | Remove a Docker image |
| `docker logout` | Log out from Docker Hub |
| `docker login -u <username> -p <password>` | Log in to Docker Hub |
| `docker stats` | Display a live stream of container resource usage statistics |
| `docker top <container-id or name>` | Display the running processes of a container |
| `docker version` | Show the Docker version information |
| `docker system prune` | Remove unused images |
| `docker system prune -a` | Remove all unused images |

## Further Reading

- [How to Remove Docker Images, Containers, and Volumes](https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes)
