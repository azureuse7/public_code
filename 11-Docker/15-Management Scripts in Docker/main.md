# How to Write Management Scripts in Docker

Managing a multi-container project along with the network and volumes and stuff means writing a lot of commands. To simplify the process, I usually have help from simple shell scripts and a Makefile.

You'll find four shell scripts in the notes-api directory. They are as follows:

boot.sh - Used for starting the containers if they already exist.

build.sh - Creates and runs the containers. It also creates the images, volumes, and networks if necessary.

destroy.sh - Removes all containers, volumes and networks associated with this project.

stop.sh - Stops all running containers.

There is also a Makefile that contains four targets named start, stop, build and destroy, each invoking the previously mentioned shell scripts.

If the container is in a running state in your system, executing make stop should stop all the containers. Executing make destroy should stop the containers and remove everything. Make sure you're running the scripts inside the notes-api directory:

make destroy

# ./shutdown.sh
# stopping api container --->
# notes-api
# api container stopped --->

# stopping db container --->
# notes-db
# db container stopped --->

# shutdown script finished

# ./destroy.sh
# removing api container --->
# notes-api
# api container removed --->

# removing db container --->
# notes-db
# db container removed --->

# removing db data volume --->
# notes-db-data
# db data volume removed --->

# removing network --->
# notes-api-network
# network removed --->

# destroy script finished

If you're getting a permission denied error, than execute chmod +x on the scripts:

chmod +x boot.sh build.sh destroy.sh shutdown.sh

I'm not going to explain these scripts because they're simple if-else statements along with some Docker commands that you've already seen many times. If you have some understanding of the Linux shell, you should be able to understand the scripts as well.

