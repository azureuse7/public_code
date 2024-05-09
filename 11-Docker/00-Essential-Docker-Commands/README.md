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

# Docker - Essential Commands
 

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
