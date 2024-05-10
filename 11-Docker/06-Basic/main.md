## List and Remove Docker Images

You can use the image ls command to list all the images

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