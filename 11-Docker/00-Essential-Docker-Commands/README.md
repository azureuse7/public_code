Bash:

# Delete all containers including its volumes use,
```bash
docker rm -vf $(docker ps -aq)
```
# Delete all the images
```bash
docker rmi -f $(docker images -aq)
```

## Windows - Powershell
```bash
docker images -a -q | % { docker image rm $_ -f }
Windows - cmd.exe
```
for /F %i in ('docker images -a -q') do docker rmi -f %i

 
## List and Remove Docker Images


```bash
docker image rm <image identifier>

docker image rm custom-nginx:packaged
```
You can also use the image prune command to cleanup all un-tagged dangling images as follows:
```bash
docker image prune --force
```

## How to Access Logs from a Container in Docker
```bash
docker container logs <container identifier>
```
To access the logs from the notes-db container, you can execute the following command:
```bash
docker container logs notes-db
```


## Three very fundamental concepts of containerization in general:

- Container

- Image

- Registry


## What is a Container?

A container is an abstraction at the application layer that packages code and dependencies together. Instead of virtualizing the entire physical machine, containers virtualize the host operating system only.

Just like virtual machines, containers are completely isolated environments from the host system as well as from each other. 

Containers and virtual machines are actually different ways of virtualizing your physical hardware. 

Virtual machines are usually created and managed by a program known as a hypervisor, like Oracle VM VirtualBox, VMware Workstation, KVM, Microsoft Hyper-V and so on. This hypervisor program usually sits between the host operating system and the virtual machines to act as a medium of communication.

Each virtual machine comes with its own guest operating system which is just as heavy as the host operating system.

The application running inside a virtual machine communicates with the guest operating system, which talks to the hypervisor, which then in turn talks to the host operating system to allocate necessary resources from the physical infrastructure to the running application.

As you can see, there is a long chain of communication between applications running inside virtual machines and the physical infrastructure. The application running inside the virtual machine may take only a small amount of resources, but the guest operating system adds a noticeable overhead.

Unlike a virtual machine, a container does the job of virtualization in a smarter way. Instead of having a complete guest operating system inside a container, it just utilizes the host operating system via the container runtime while maintaining isolation – just like a traditional virtual machine.

The container runtime, that is Docker, sits between the containers and the host operating system instead of a hypervisor. The containers then communicate with the container runtime which then communicates with the host operating system to get necessary resources from the physical infrastructure.

As a result of eliminating the entire guest operating system layer, containers are much lighter and less resource-hogging than traditional virtual machines.

As a demonstration of the point, look at the following code block:
```bash
uname -a
# Linux alpha-centauri 5.8.0-22-generic #23-Ubuntu SMP Fri Oct 9 00:34:40 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux

docker run alpine uname -a
# Linux f08dbbe9199b 5.8.0-22-generic #23-Ubuntu SMP Fri Oct 9 00:34:40 UTC 2020 x86_64 Linux
```
In the code block above, I have executed the uname -a command on my host operating system to print out the kernel details. Then on the next line I've executed the same command inside a container running Alpine Linux.

As you can see in the output, the container is indeed using the kernel from my host operating system. This goes to prove the point that containers virtualize the host operating system instead of having an operating system of their own.

If you're on a Windows machine, you'll find out that all the containers use the WSL2 kernel. It happens because WSL2 acts as the back-end for Docker on Windows. On macOS the default back-end is a VM running on HyperKit hypervisor.

## What is a Docker Image?

Images are multi-layered self-contained files that act as the template for creating containers. They are like a frozen, read-only copy of a container. Images can be exchanged through registries.

In the past, different container engines had different image formats. But later on, the Open Container Initiative (OCI) defined a standard specification for container images which is complied by the major containerization engines out there. This means that an image built with Docker can be used with another runtime like Podman without any additional hassle.

Containers are just images in running state. When you obtain an image from the internet and run a container using that image, you essentially create another temporary writable layer on top of the previous read-only ones.

Docker Architecture Overview

The engine consists of three major components:

Docker Daemon: The daemon (dockerd) is a process that keeps running in the background and waits for commands from the client. The daemon is capable of managing various Docker objects.

Docker Client: The client  (docker) is a command-line interface program mostly responsible for transporting commands issued by users.

REST API: The REST API acts as a bridge between the daemon and the client. Any command issued using the client passes through the API to finally reach the daemon.

The Full Picture

This image is a slightly modified version of the one found in the official docs. The events that occur when you execute the command are as follows:

You execute docker run hello-world command where hello-world is the name of an image.

Docker client reaches out to the daemon, tells it to get the hello-world image and run a container from that.

Docker daemon looks for the image within your local repository and realizes that it's not there, resulting in the Unable to find image 'hello-world:latest' locally that's printed on your terminal.

The daemon then reaches out to the default public registry which is Docker Hub and pulls in the latest copy of the hello-world image, indicated by the latest: Pulling from library/hello-world line in your terminal.

Docker daemon then creates a new container from the freshly pulled image.

Finally Docker daemon runs the container created using the hello-world image outputting the wall of text on your terminal.

It's the default behavior of Docker daemon to look for images in the hub that are not present locally. But once an image has been fetched, it'll stay in the local cache. So if you execute the command again, you won't see the following lines in the output:

Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete
Digest: sha256:d58e752213a51785838f9eed2b7a498ffa1cb3aa7f946dda11af39286c3db9a9
Status: Downloaded newer image for hello-world:latest

If there is a newer version of the image available on the public registry, the daemon will fetch the image again. That :latest is a tag. Images usually have meaningful tags to indicate versions or builds. You'll learn about this in greater detail later on.

How to Run a Container

docker run <image name> 

|     Commands                 |    Description                                  |
| ------------------------------- | --------------------------------------------- |
| docker ps | List all running containers |
| docker ps -a | List all containers stopped, running |
| docker stop container-id | Stop the container which is running |
| docker start container-id | Start the container which is stopped |
| docker restart container-id | Restart the container which is running |
| docker port container-id | List port mappings of a specific container |
| docker rm container-id or name | Remove the stopped container |
| docker rm -f container-id or name| Remove the running container forcefully |
| docker pull image-info | Pull the image from docker hub repository |
| docker pull stacksimplify/springboot-helloworld-rest-api:2.0.0-RELEASE | Pull the image from docker hub repository |
| docker exec -it container-name /bin/sh | Connect to linux container and execute commands in container |
| docker rmi image-id | Remove the docker image |
| docker logout | Logout from docker hub |
| docker login -u username -p password | Login to docker hub |
| docker stats | Display a live stream of container(s) resource usage statistics |
| docker top container-id or name | Display the running processes of a container |
| docker version | Show the Docker version information |
| docker system prune | pune images 
| docker system prune -a | prune all images
| 


https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes


# List Containers that are currently running or have run in the past:
```bash
docker ps -a
```
# How to Run a Container
```bash
docker run <image name>
```
Better way of dispatching commands to the docker daemon.
```bash
docker <object> <command> <options>
```
In this syntax:

- object indicates the type of Docker object you'll be manipulating. This can be a container, image, network or volume object.

- command indicates the task to be carried out by the daemon, that is the run command.

- options can be any valid parameter that can override the default behavior of the command, like the --publish option for port mapping.

Run command can be written as follows:
```bash
# docker container run <image name>
```
The image name can be of any image from an online registry or your local system. 

To run a container using this image, execute following command on your terminal:
```bash
docker container run --publish 8080:80 fhsinchy/hello-dock
```

The command is pretty self-explanatory. The only portion that may require some explanation is the --publish 8080:80 portion which will be explained in the next sub-section.

# List Containers
```bash
docker container ls
```

The container ls command only lists the containers that are currently running on your system. In order to list out the containers that have run in the past you can use the --all or -a option.
```bash
docker container ls --all
```

# Name or Rename a Container

By default, every container has two identifiers. They are as follows:

- CONTAINER ID - a random 64 character-long string.

- NAME - combination of two random words, joined with an underscore.

Naming a container can be achieved using the --name option. To run another container using the fhsinchy/hello-dock image with the name hello-dock-container you can execute the following command:
```bash
docker container run --detach --publish 8888:80 --name hello-dock-container fhsinchy/hello-dock
```


The 8080 port on local network is occupied by the gifted_sammet container (the container created in the previous sub-section). That's why you'll have to use a different port number, like 8888. Now to verify, run the container ls command:
```bash
docker container ls
```

# Rename old containers

```bash
docker container rename <container identifier> <new name>
```

# Stop or Kill a Running Container

Containers running in the foreground can be stopped by simply closing the terminal window or hitting ctrl + c. Containers running in the background, however, can not be stopped in the same way.

There are two commands that deal with this task. 
```bash
docker container stop <container identifier>
```

I hope that you remember the container you started in the previous section. It's still running in the background. Get the identifier for that container using docker container ls (I'll be using hello-dock-container container for this demo). Now execute the following command to stop the container:
```bash
docker container stop hello-dock-container
```


In cases where you want to send a SIGKILL signal instead of a SIGTERM signal, you may use the container kill command instead. The container kill command follows the same syntax as the stop command.
```bash
docker container kill hello-dock-container-2
```

# Restart a Container
```bash
docker container start <container identifier>
```

Now to restart the hello-dock-container container, you may execute the following command:
```bash
docker container start hello-dock-container


docker container restart hello-dock-container-2
```

# Create a Container Without Running

```bash
docker container create --publish 8080:80 fhsinchy/hello-dock

docker container ls --all

docker container start hello-dock

docker container ls
```
              

# Remove Dangling Containers

As you've already seen, containers that have been stopped or killed remain in the system. 

In order to remove a stopped container you can use the container rm command. 
```bash
docker container rm <container identifier>

docker container ls --all
```
To remove the 6cf52771dde1 you can execute the following command:

```bash
docker container rm 6cf52771dde1
```


You can check the container list using the container ls --all command to make sure that the dangling containers have been removed:
```bash
docker container ls --all
```

# Run a Container in Interactive Mode
```bash
docker container run --rm -it ubuntu
```

The -it option sets the stage for you to interact with any interactive program inside a container. This option is actually two separate options mashed together.

The -i or --interactive option connects you to the input stream of the container, so that you can send inputs to bash.

The -t or --tty option makes sure that you get some good formatting and a native terminal-like experience by allocating a pseudo-tty.

You need to use the -it option whenever you want to run a container in interactive mode. Another example can be running the node image as follows:
```bash
docker container run -it node
```

How to Execute Commands Inside a Container

```bash
docker run alpine uname -a
```


And the generic syntax for passing a command to a container that is not running is as follows:
```bash
docker container run <image name> <command>

docker container run --rm busybox sh -c "echo -n my-secret | base64
```
