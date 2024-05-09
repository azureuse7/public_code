# Network Manipulation Basics in Docker

consider a scenario where you have a notes-api application powered by Express.js and a PostgreSQL database server running in two separate containers.

These two containers are completely isolated from each other and are oblivious to each other's existence. So how do you connect the two? ‌

You may think of two possible solutions to this problem. They are as follows:

- Accessing the database server using an exposed port.

- Accessing the database server using its IP address and default port.

The first one involves exposing a port from the postgres container and the notes-api will connect through that. Assume that the exposed port from the postgres container is 5432. Now if you try to connect to 127.0.0.1:5432 from inside the notes-api container, you'll find that the notes-api can't find the database server at all.

The reason is that when you're saying 127.0.0.1 inside the notes-api container, you're simply referring to the localhost of that container and that container only. The postgres server simply doesn't exist there. As a result the notes-api application failed to connect.

The second solution you may think of is finding the exact IP address of the postgres container using the container inspect command and using that with the port. Assuming the name of the postgres container is notes-api-db-server you can easily get the IP address by executing the following command:
```bash
docker container inspect --format='{{range .NetworkSettings.Networks}} {{.IPAddress}} {{end}}' notes-api-db-server

#  172.17.0.2
```
Now given that the default port for postgres is 5432, you can very easily access the database server by connecting to 172.17.0.2:5432 from the notes-api container.

There are problems in this approach as well. Using IP addresses to refer to a container is not recommended. Also, if the container gets destroyed and recreated, the IP address may change. Keeping track of these changing IP addresses can be pretty hectic.

Now that I've dismissed the possible wrong answers to the original question, the correct answer is, you connect them by putting them under a user-defined bridge network.
```bash
Docker Network Basics
```
A network in Docker is another logical object like a container and image. Just like the other two, there is a plethora of commands under the docker network group for manipulating networks.

To list out the networks in your system, execute the following command:
```bash
docker network ls

# NETWORK ID     NAME      DRIVER    SCOPE
# c2e59f2b96bd   bridge    bridge    local
# 124dccee067f   host      host      local
# 506e3822bf1f   none      null      local
```
You should see three networks in your system. Now look at the DRIVER column of the table here. These drivers are can be treated as the type of network.

By default, Docker has five networking drivers. They are as follows:

- bridge - The default networking driver in Docker. This can be used when multiple containers are running in standard mode and need to communicate with each other.

- host - Removes the network isolation completely. Any container running under a host network is basically attached to the network of the host system.

- none - This driver disables networking for containers altogether. I haven't found any use-case for this yet.

- overlay - This is used for connecting multiple Docker daemons across computers and is out of the scope of this book.

- macvlan - Allows assignment of MAC addresses to containers, making them function like physical devices in a network.

There are also third-party plugins that allow you to integrate Docker with specialized network stacks. Out of the five mentioned above, you'll only work with the bridge networking driver in this book.

How to Create a User-Defined Bridge in Docker

. Let's begin by listing all the networks on your system:
```bash
docker network ls

# NETWORK ID     NAME      DRIVER    SCOPE
# c2e59f2b96bd   bridge    bridge    local
# 124dccee067f   host      host      local
# 506e3822bf1f   none      null      local
```
As you can see, Docker comes with a default bridge network named bridge. Any container you run will be automatically attached to this bridge network:
```bash
docker container run --rm --detach --name hello-dock --publish 8080:80 fhsinchy/hello-dock
# a37f723dad3ae793ce40f97eb6bb236761baa92d72a2c27c24fc7fda0756657d

docker network inspect --format='{{range .Containers}}{{.Name}}{{end}}' bridge
# hello-dock
```
Containers attached to the default bridge network can communicate with each others using IP addresses which I have already discouraged in the previous sub-section.

A user-defined bridge, however, has some extra features over the default one. According to the official docs on this topic, some notable extra features are as follows:

User-defined bridges provide automatic DNS resolution between containers: This means containers attached to the same network can communicate with each others using the container name. So if you have two containers named notes-api and notes-db the API container will be able to connect to the database container using the notes-db name.

User-defined bridges provide better isolation: All containers are attached to the default bridge network by default which can cause conflicts among them. Attaching containers to a user-defined bridge can ensure better isolation.

Containers can be attached and detached from user-defined networks on the fly: During a container’s lifetime, you can connect or disconnect it from user-defined networks on the fly. To remove a container from the default bridge network, you need to stop the container and recreate it with different network options.

Now that you've learned quite a lot about a user-defined network, it's time to create one for yourself. A network can be created using the network create command. The generic syntax for the command is as follows:
```bash
docker network create <network name>
```
To create a network with the name skynet execute the following command:
```bash
docker network create skynet

docker network ls

# NETWORK ID     NAME     DRIVER    SCOPE
# be0cab667c4b   bridge   bridge    local
# 124dccee067f   host     host      local
# 506e3822bf1f   none     null      local
# 7bd5f351aa89   skynet   bridge    local
```

As you can see a new network has been created with the given name. No container is currently attached to this network. In the next sub-section, you'll learn about attaching containers to a network.

# How to Attach a Container to a Network in Docker

There are mostly two ways of attaching a container to a network. First, you can use the network connect command to attach a container to a network. The generic syntax for the command is as follows:
```bash
docker network connect <network identifier> <container identifier>
```
To connect the hello-dock container to the skynet network, you can execute the following command:
```bash
docker network connect skynet hello-dock

docker network inspect --format='{{range .Containers}} {{.Name}} {{end}}' skynet

#  hello-dock

docker network inspect --format='{{range .Containers}} {{.Name}} {{end}}' bridge

#  hello-dock
```
As you can see from the outputs of the two network inspect commands, the hello-dock container is now attached to both the skynet and the default bridge network.

The second way of attaching a container to a network is by using the --network option for the container run or container create commands. The generic syntax for the option is as follows:

--network <network identifier>

To run another hello-dock container attached to the same network, you can execute the following command:
```bash
docker container run --network skynet --rm --name alpine-box -it alpine sh
```

--- hello-dock ping statistics ---
13 packets transmitted, 13 packets received, 0% packet loss
round-trip min/avg/max = 0.085/0.138/0.191 ms

As you can see, running ping hello-dock from inside the alpine-box container works because both of the containers are under the same user-defined bridge network and automatic DNS resolution is working.

Keep in mind, though, that in order for the automatic DNS resolution to work you must assign custom names to the containers. Using the randomly generated name will not work.

How to Detach Containers from a Network in Docker

In the previous sub-section you learned about attaching containers to a network. In this sub-section, you'll learn about how to detach them.

You can use the network disconnect command for this task. The generic syntax for the command is as follows:
```bash
docker network disconnect <network identifier> <container identifier>
```
To detach the hello-dock container from the skynet network, you can execute the following command:
```bash
docker network disconnect skynet hello-dock
```
Just like the network connect command, the network disconnect command doesn't give any output.

How to Get Rid of Networks in Docker

 Networks can be removed using the network rm command. The generic syntax for the command is as follows:
```bash
docker network rm <network identifier>
```
To remove the skynet network from your system, you can execute the following command:
```bash
docker network rm skynet
```
You can also use the network prune command to remove any unused networks from your system. The command also has the -f or --force and -a or --all options.