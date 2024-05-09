How to Use Detached Mode
Another very popular option of the run command is the --detach or -d option. In the example above, in order for the container to keep running, you had to keep the terminal window open. Closing the terminal window also stopped the running container.

This is because, by default, containers run in the foreground and attach themselves to the terminal like any other normal program invoked from the terminal.

In order to override this behavior and keep a container running in background, you can include the --detach option with the run command as follows:



docker container run --detach --publish 8080:80 fhsinchy/hello-dock

# 9f21cb77705810797c4b847dbd330d9c732ffddba14fb435470567a7a3f46cdc
Unlike the previous example, you won't get a wall of text thrown at you this time. Instead what you'll get is the ID of the newly created container.

The order of the options you provide doesn't really matter. If you put the --publish option before the --detach option, it'll work just the same. One thing that you have to keep in mind in case of the run command is that the image name must come last. If you put anything after the image name then that'll be passed as an argument to the container entry-point (explained in the Executing Commands Inside a Container sub-section) and may result in unexpected situations.

How to Work With Executable Images
 

Take for example my rmbyext project. This is a simple Python script capable of recursively deleting files of given extensions. To learn more about the project, you can checkout the repository:

fhsinchy/rmbyext

Recursively removes all files with given extension(s). - fhsinchy/rmbyext

favicon
fhsinchyGitHub

spare a ⭐ to keep me motivated

If you have both Git and Python installed, you can install this script by executing the following command:



pip install git+https://github.com/fhsinchy/rmbyext.git#egg=rmbyext
Assuming Python has been set up properly on your system, the script should be available anywhere through the terminal. The generic syntax for using this script is as follows:



rmbyext <file extension>
To test it out, open up your terminal inside an empty directory and create some files in it with different extensions. You can use the touch command to do so. Now, I have a directory on my computer with the following files:



touch a.pdf b.pdf c.txt d.pdf e.txt

ls

# a.pdf  b.pdf  c.txt  d.pdf  e.txt
To delete all the pdf files from this directory, you can execute the following command:



rmbyext pdf

# Removing: PDF
# b.pdf
# a.pdf
# d.pdf
An executable image for this program should be able to take extensions of files as arguments and delete them just like the rmbyext program did.

The fhsinchy/rmbyext image behaves in a similar manner. This image contains a copy of the rmbyext script and is configured to run the script on a directory /zone inside the container.

Now the problem is that containers are isolated from your local system, so the rmbyext program running inside the container doesn't have any access to your local file system. So, if somehow you can map the local directory containing the pdf files to the /zone directory inside the container, the files should be accessible to the container.

One way to grant a container direct access to your local file system is by using bind mounts.

A bind mount lets you form a two way data binding between the content of a local file system directory (source) and another directory inside a container (destination). This way any changes made in the destination directory will take effect on the source directory and vise versa.

Let's see a bind mount in action. To delete files using this image instead of the program itself, you can execute the following command:



docker container run --rm -v $(pwd):/zone fhsinchy/rmbyext pdf

# Removing: PDF
# b.pdf
# a.pdf
# d.pdf
As you may have already guessed by seeing the -v $(pwd):/zone part in the command, the  -v or --volume option is used for creating a bind mount for a container. This option can take three fields separated by colons (:). The generic syntax for the option is as follows:



--volume <local file system directory absolute path>:<container file system directory absolute path>:<read write access>
The third field is optional but you must pass the absolute path of your local directory and the absolute path of the directory inside the container.

The source directory in my case is /home/fhsinchy/the-zone. Given that my terminal is opened inside the directory, $(pwd) will be replaced with /home/fhsinchy/the-zone which contains the previously mentioned .pdf and .txt files.

You can learn more about command substitution here if you want to.

The --volume or -v option is valid for the container run as well as the container create commands. We'll explore volumes in greater detail in the upcoming sections so don't worry if you didn't understand them very well here.

The difference between a regular image and an executable one is that the entry-point for an executable image is set to a custom program instead of sh, in this case the rmbyext program. And as you've learned in the previous sub-section, anything you write after the image name in a container run command gets passed to the entry-point of the image.

So in the end the docker container run --rm -v $(pwd):/zone fhsinchy/rmbyext pdf command translates to rmbyext pdf inside the container. Executable images are not that common in the wild but can be very useful in certain cases.

How to Containerize a JavaScript Application
In this sub-section, you'll be working with the source code of the fhsinchy/hello-dock image that you worked with on a previous section. 

How to Write the Development Dockerfile
To begin with, open up the directory where you've cloned the repository that came with this book. Code for the hello-dock application resides inside the sub-directory with the same name.

This is a very simple JavaScript project powered by the vitejs/vite project.  In my opinion, the plan should be as follows:

Get a good base image for running JavaScript applications, like node.

Set the default working directory inside the image.

Copy the package.json file into the image.

Install necessary dependencies.

Copy the rest of the project files.

Start the vite development server by executing npm run dev command.

 

Now if you put the above mentioned plan inside Dockerfile.dev, the file should look like as follows:



FROM node:lts-alpine

EXPOSE 3000

USER node

RUN mkdir -p /home/node/app

WORKDIR /home/node/app

COPY ./package.json .
RUN npm install

COPY . .

CMD [ "npm", "run", "dev" ]
The explanation for this code is as follows:

The FROM instruction here sets the official Node.js image as the base, giving you all the goodness of Node.js necessary to run any JavaScript application. The lts-alpine tag indicates that you want to use the Alpine variant, long term support version of the image. Available tags and necessary documentation for the image can be found on the node hub page.

The USER instruction sets the default user for the image to node. By default Docker runs containers as the root user. But according to Docker and Node.js Best Practices this can pose a security threat. So it's a better idea to run as a non-root user whenever possible. The node image comes with a non-root user named node which you can set as the default user using the USER instruction.

The RUN mkdir -p /home/node/app instruction creates a directory called app inside the home directory of the node user. The home directory for any non-root user in Linux is usually /home/<user name> by default.

Then the WORKDIR instruction sets the default working directory to the newly created /home/node/app directory. By default the working directory of any image is the root. You don't want any unnecessary files sprayed all over your root directory, do you? Hence you change the default working directory to something more sensible like /home/node/app or whatever you like. This working directory will be applicable to any subsequent COPY, ADD, RUN and CMD instructions.

The COPY instruction here copies the package.json file which contains information regarding all the necessary dependencies for this application. The RUN instruction executes the npm install command which is the default command for installing dependencies using a package.json file in Node.js projects. The . at the end represents the working directory.

The second COPY instruction copies the rest of the content from the current directory (.) of the host filesystem to the working directory (.) inside the image.

Finally, the CMD instruction here sets the default command for this image which is npm run dev written in exec form.

The vite development server by default runs on port 3000 , and adding an EXPOSE command seemed like a good idea, so there you go.

Now, to build an image from this Dockerfile.dev you can execute the following command:



docker image build --file Dockerfile.dev --tag hello-dock:dev .
Given the filename is not Dockerfile you have to explicitly pass the filename using the --file option. A container can be run using this image by executing the following command:



docker container run \
    --rm \
    --detach \
    --publish 3000:3000 \
    --name hello-dock-dev \
    hello-dock:dev

# 21b9b1499d195d85e81f0e8bce08f43a64b63d589c5f15cbbd0b9c0cb07ae268
Now visit http://127.0.0.1:3000 to see the hello-dock application in action.

Congratulations on running your first real-world application inside a container. 

 

How to Work With Anonymous Volumes in Docker
This problem can be solved using an anonymous volume. An anonymous volume is identical to a bind mount except that you don't need to specify the source directory here. The generic syntax for creating an anonymous volume is as follows:



--volume <container file system directory absolute path>:<read write access>
So the final command for starting the hello-dock container with both volumes should be as follows:



docker container run \
    --rm \
    --detach \
    --publish 3000:3000 \
    --name hello-dock-dev \
    --volume $(pwd):/home/node/app \
    --volume /home/node/app/node_modules \
    hello-dock:dev

# 53d1cfdb3ef148eb6370e338749836160f75f076d0fbec3c2a9b059a8992de8b
Here, Docker will take the entire node_modules directory from inside the container and tuck it away in some other directory managed by the Docker daemon on your host file system and will mount that directory as node_modules inside the container.

How to Ignore Unnecessary Files
.dockerignore file contains a list of files and directories to be excluded from image builds. 

 

How to Containerize a Multi-Container JavaScript Application
Now that you've learned enough about networks in Docker, in this section you'll learn to containerize a full-fledged multi-container project. The project you'll be working with is a simple notes-api powered by Express.js and PostgreSQL.

In this project there are two containers in total that you'll have to connect using a network. Apart from this, you'll also learn about concepts like environment variables and named volumes. So without further ado, let's jump right in.

How to Run the Database Server
The database server in this project is a simple PostgreSQL server and uses the official postgres image.

According to the official docs, in order to run a container with this image, you must provide the POSTGRES_PASSWORD environment variable. Apart from this one, I'll also provide a name for the default database using the POSTGRES_DB environment variable. PostgreSQL by default listens on port 5432, so you need to publish that as well.

To run the database server you can execute the following command:



docker container run \
    --detach \
    --name=notes-db \
    --env POSTGRES_DB=notesdb \
    --env POSTGRES_PASSWORD=secret \
    --network=notes-api-network \
    postgres:12

# a7b287d34d96c8e81a63949c57b83d7c1d71b5660c87f5172f074bd1606196dc

docker container ls

# CONTAINER ID   IMAGE         COMMAND                  CREATED              STATUS              PORTS      NAMES
# a7b287d34d96   postgres:12   "docker-entrypoint.s…"   About a minute ago   Up About a minute   5432/tcp   notes-db
The --env option for the container run and container create commands can be used for providing environment variables to a container. As you can see, the database container has been created successfully and is running now.

Although the container is running, there is a small problem. Databases like PostgreSQL, MongoDB, and MySQL persist their data in a directory. PostgreSQL uses the /var/lib/postgresql/data directory inside the container to persist data.

Now what if the container gets destroyed for some reason? You'll lose all your data. To solve this problem, a named volume can be used.

How to Work with Named Volumes in Docker
Previously you've worked with bind mounts and anonymous volumes. A named volume is very similar to an anonymous volume except that you can refer to a named volume using its name.

Volumes are also logical objects in Docker and can be manipulated using the command-line. The volume create command can be used for creating a named volume.

The generic syntax for the command is as follows:



docker volume create <volume name>
To create a volume named notes-db-data you can execute the following command:



docker volume create notes-db-data

# notes-db-data

docker volume ls

# DRIVER    VOLUME NAME
# local     notes-db-data
This volume can now be mounted to /var/lib/postgresql/data inside the notes-db container. To do so, stop and remove the notes-db container:



docker container stop notes-db

# notes-db

docker container rm notes-db

# notes-db
Now run a new container and assign the volume using the --volume or -v option.



docker container run \
    --detach \
    --volume notes-db-data:/var/lib/postgresql/data \
    --name=notes-db \
    --env POSTGRES_DB=notesdb \
    --env POSTGRES_PASSWORD=secret \
    --network=notes-api-network \
    postgres:12

# 37755e86d62794ed3e67c19d0cd1eba431e26ab56099b92a3456908c1d346791
Now inspect the notes-db container to make sure that the mounting was successful:



docker container inspect --format='{{range .Mounts}} {{ .Name }} {{end}}' notes-db

#  notes-db-data
Now the data will safely be stored inside the notes-db-data volume and can be reused in the future. A bind mount can also be used instead of a named volume here, but I prefer a named volume in such scenarios.

How to Create a Network and Attaching the Database Server in Docker
As you've learned in the previous section, the containers have to be attached to a user-defined bridge network in order to communicate with each other using container names. To do so, create a network named notes-api-network in your system:



docker network create notes-api-network
Now attach the notes-db container to this network by executing the following command:



docker network connect notes-api-network notes-db


