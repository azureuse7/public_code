https://docs.docker.com/compose/gettingstarted/

## What is Docker Compose?

With Compose, you use a YAML file to configure your application’s services (containers). Then, with a single command, you can build, start or delete your application services.


# Why Docker Compose exists? 
Running multiple containers is a very common scenario.

Take for example a WordPress (WP) application. It consists of a WordPress service that talks to a MySQL database.


We could run both containers using two docker run commands with a bunch of cli arguments. The db container might be started like this:

```t
docker run -d \
  --name db \
  --restart always \
  -v db_data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=supersecret \
  -e MYSQL_DATABASE=exampledb \
  -e MYSQL_USER=exampleuser \
  -e MYSQL_PASSWORD=examplepass \
  mysql:5.7
```
We could create or remove networks with docker network commands, and modify docker run to take the network as an argument.

Typing out these verbose commands might be fine once or twice. But as the number of containers and configurations grows, they become increasingly harder to manage.

With Compose, we simply define the application’s configuration on a YAML file (named docker-compose.yml by default) like this:
```t
version: '3.9'
services:
  db:
    image: mysql:5.7
    restart: always
    environment:
      MYSQL_DATABASE: exampledb
      MYSQL_USER: exampleuser
      MYSQL_PASSWORD: examplepass
      MYSQL_ROOT_PASSWORD: supersecret
    volumes:
      - db_data:/var/lib/mysql
  wordpress:
    image: wordpress
    restart: always
    ports:
      - 8080:80
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: exampleuser
      WORDPRESS_DB_PASSWORD: examplepass
      WORDPRESS_DB_NAME: exampledb
    volumes:
      - wordpress_data:/var/www/html
volumes:
  wordpress_data:
  db_data:
  ```
This file defines 2 services, db and wordpress. It also specifies the configuration options for each - like the image, environment variables, published ports, volumes, etc.


After creating this file, we execute docker compose up, and Docker builds and runs our entire application in a new isolated environment (bridge network by default).

Similarly, we can use the docker compose down command to tear everything down (except volumes).


# How to use Docker Compose?
Source code for this demo: https://github.com/AluBhorta/docker-compose-demo

First of all, make sure you have installed:
```t
Docker
Docker Compose
```
NOTE: since Compose version 2, we use docker compose command instead of docker-compose. This tutorial uses version 2.

Step 2: Create a sample web application
Open up a terminal, create a new directory and switch into it:
```t
mkdir docker-compose-demo
cd docker-compose-demo
```
Add the code for a simple Python web app on a file named app.py:
```t
import time
import redis
from flask import Flask
app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
@app.route('/')
def hello():
    count = cache.incr('hits')
    return 'Hello World! I have been seen {} times.\n'.format(count)
```
This creates a Flask app with a single HTTP endpoint (/). This endpoint returns how many times it has been visited. The count is stored and incremented as an integer with a key named hits in a Redis host named redis.

Then we add the Python dependencies to a requirements.txt file:
```t
flask
redis
```
After that, we create a Dockerfile - to create a Docker image based on this application:
```t
FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]
```
# This tells Docker to:

1) Build an image starting with the Python 3.7 Alpine Linux image
2) Set the working directory to /code
3) Install gcc and other dependencies with the apk package manager
4) Copy requirements.txt from host to image
5) Install the Python dependencies with pip
6) Add metadata to the image to describe that the container is listening on port 5000
7) Copy the current directory . in the project to the workdir . in the image
8) Set environment variables used by the flask command
9) Set the default command for the container to flask run
1) Then we create a docker-compose.yml file for us to use Docker Compose:
```t
version: "3.9"
services:
  redis:
    image: "redis:alpine"
  web:
    build: .
    ports:
      - "8000:5000"
    depends_on:
      - redis
```
This Compose file defines two services: web and redis.
The redis service uses a public redis:alpine image pulled from the Docker Hub registry.

The web service uses an image that’s built from the Dockerfile in the current directory (.). It then maps port 8000 on the host to port 5000 on the container where the flask server will be running. 
It also specifies that web depends on redis so that Docker knows to start redis before web.

NOTE: since Compose creates a new bridge network on project startup, web can reach redis simply by using the service’s name ie. redis.

# Step 3: Run and test the application

```t
docker compose up
```
Docker will automatically pull the redis image, build our web image and start the containers.

Once deployed, we should now be able to reach the application at localhost:8000 on your browser.

Or alternatively, use curl on a separate terminal to reach the flask application like so:

```t
curl localhost:8000
```
You should see something like this:

Hello World! I have been seen 1 times.
The count is incremented every time we make a request.

We can list the containers of the Compose project with:

```t
docker compose ps
```
NOTE: docker compose up will by default attach to your terminal and print the logs from the services. We can use ctrl+c to detach that terminal, but it will stop the services.

To run the services in the background, use -d the flag:

```t
docker compose up -d
```
If you want to view the logs, use:
```t
docker compose logs -f
```
NOTE: -f will follow the log output as new logs are generated.

# Step 4: Modify the application

The web container is printing out a warning:

WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
In production, we definitely want to run a production-grade server like gunicorn instead of the development server, we get with flask run.

So, let’s first add gunicorn to requirements.txt:
```t
flask
redis
gunicorn
```
Then remove the last 3 instructions of Dockerfile and add a new CMD instruction:
```t
FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```
Images built from this Dockerfile will now run gunicorn instead of the flask dev server.

Once we’ve made the changes, we need to rebuild the web image:
```t
docker compose build
```
Then we restart the web service to use the new image:
```t
docker compose up web -d --no-deps -t 1
```
NOTE:

--no-deps tells Docker not to (re)start dependent services.
-t 1 specifies the container shutdown timeout of 1 second instead of the default 10s.
Try to reach web again:

curl localhost:8000
It should work as expected.

But if you check the logs:

docker compose logs web -f
You will notice we don’t have the warning anymore since we’re using gunicorn.

Step 5: Clean up
To remove all the services, we simply run:
```t
docker compose down
```
If we had defined volumes in the services (like in the WordPress example), the volumes wouldn’t be automatically removed with docker compose down. This is mainly to avoid accidental deletion of data.

To tear down everything including volumes, use the -v flag:
```t
docker compose down -v
```
Congratulations! You can now Compose! 🙌



## Docker Compose Basics

Go the directory where you've cloned the repository that came with this book. Go inside the notes-api/api directory and create a Dockerfile.dev file. Put the following code in it:
```bash
# stage one
FROM node:lts-alpine as builder

# install dependencies for node-gyp
RUN apk add --no-cache python make g++

WORKDIR /app

COPY ./package.json .
RUN npm install

# stage two
FROM node:lts-alpine

ENV NODE_ENV=development

USER node
RUN mkdir -p /home/node/app
WORKDIR /home/node/app

COPY . .
COPY --from=builder /app/node_modules /home/node/app/node_modules

CMD [ "./node_modules/.bin/nodemon", "--config", "nodemon.json", "bin/www" ]
```
The code is almost identical to the Dockerfile that you worked with in the previous section. The three differences in this file are as follows:

On line 10, we run npm install instead of npm run install --only=prod because we want the development dependencies also.

On line 15, we set the NODE_ENV environment variable to development instead of production.

On line 24, we use a tool called nodemon to get the hot-reload feature for the API.

You already know that this project has two containers:

notes-db - A database server powered by PostgreSQL.

notes-api - A REST API powered by Express.js

In the world of Compose, each container that makes up the application is known as a service. The first step in composing a multi-container project is to define these services.

Just like the Docker daemon uses a Dockerfile for building images, Docker Compose uses a docker-compose.yaml file to read service definitions from.

Head to the notes-api directory and create a new docker-compose.yaml file. Put the following code into the newly created file:
```bash
version: "3.8"

services: 
    db:
        image: postgres:12
        container_name: notes-db-dev
        volumes: 
            - notes-db-dev-data:/var/lib/postgresql/data
        environment:
            POSTGRES_DB: notesdb
            POSTGRES_PASSWORD: secret
    api:
        build:
            context: ./api
            dockerfile: Dockerfile.dev
        image: notes-api:dev
        container_name: notes-api-dev
        environment: 
            DB_HOST: db ## same as the database service name
            DB_DATABASE: notesdb
            DB_PASSWORD: secret
        volumes: 
            - /home/node/app/node_modules
            - ./api:/home/node/app
        ports: 
            - 3000:3000

volumes:
    notes-db-dev-data:
        name: notes-db-dev-data
```
Every valid docker-compose.yaml file starts by defining the file version. At the time of writing, 3.8 is the latest version. You can look up the latest version here.

Blocks in an YAML file are defined by indentation. I will go through each of the blocks and will explain what they do.

The services block holds the definitions for each of the services or containers in the application. db and api are the two services that comprise this project.

The db block defines a new service in the application and holds necessary information to start the container. Every service requires either a pre-built image or a Dockerfile to run a container. For the db service we're using the official PostgreSQL image.

Unlike the db service, a pre-built image for the api service doesn't exist. So we'll use the Dockerfile.dev file.

The volumes block defines any name volume needed by any of the services. At the time it only enlists notes-db-dev-data volume used by the db service.

Now that have a high level overview of the docker-compose.yaml file, let's have a closer look at the individual services.

The definition code for the db service is as follows:
```bash
db:
    image: postgres:12
    container_name: notes-db-dev
    volumes: 
        - db-data:/var/lib/postgresql/data
    environment:
        POSTGRES_DB: notesdb
        POSTGRES_PASSWORD: secret
```
The image key holds the image repository and tag used for this container. We're using the postgres:12 image for running the database container.

The container_name indicates the name of the container. By default containers are named following <project directory name>_<service name> syntax. You can override that using container_name.

The volumes array holds the volume mappings for the service and supports named volumes, anonymous volumes, and bind mounts. The syntax <source>:<destination> is identical to what you've seen before.

The environment map holds the values of the various environment variables needed for the service.

Definition code for the api service is as follows:
```
api:
    build:
        context: ./api
        dockerfile: Dockerfile.dev
    image: notes-api:dev
    container_name: notes-api-dev
    environment: 
        DB_HOST: db ## same as the database service name
        DB_DATABASE: notesdb
        DB_PASSWORD: secret
    volumes: 
        - /home/node/app/node_modules
        - ./api:/home/node/app
    ports: 
        - 3000:3000
```
The api service doesn't come with a pre-built image. Instead it has a build configuration. Under the build block we define the context and the name of the Dockerfile for building an image. You should have an understanding of context and Dockerfile by now so I won't spend time explaining those.

The image key holds the name of the image to be built. If not assigned, the image will be named following the <project directory name>_<service name> syntax.

Inside the environment map, the DB_HOST variable demonstrates a feature of Compose. That is, you can refer to another service in the same application by using its name. So the db here, will be replaced by the IP address of the api service container. The DB_DATABASE and DB_PASSWORD variables have to match up with POSTGRES_DB and POSTGRES_PASSWORD respectively from the db service definition.

In the volumes map, you can see an anonymous volume and a bind mount described. The syntax is identical to what you've seen in previous sections.

The ports map defines any port mapping. The syntax, <host port>:<container port> is identical to the --publish option you used before.

Finally, the code for the volumes is as follows:
```
volumes:
    db-data:
        name: notes-db-dev-data
```
Any named volume used in any of the services has to be defined here. If you don't define a name, the volume will be named following the <project directory name>_<volume key> and the key here is db-data.

You can learn about the different options for volume configuration in the official docs.

How to Start Services in Docker Compose

There are a few ways of starting services defined in a YAML file. The first command that you'll learn about is the up command. The up command builds any missing images, creates containers, and starts them in one go.

Before you execute the command, though, make sure you've opened your terminal in the same directory where the docker-compose.yaml file is. This is very important for every docker-compose command you execute.
```bash
docker-compose --file docker-compose.yaml up --detach
```


The --detach or -d option here functions the same as the one you've seen before. The --file or -f option is only needed if the YAML file is not named docker-compose.yaml (but I've used here for demonstration purposes).

Apart from the the up command there is the start command. The main difference between these two is that the start command doesn't create missing containers, only starts existing containers. It's basically the same as the container start command.

The --build option for the up command forces a rebuild of the images. There are some other options for the up command that you can see in the official docs.

How to List Services in Docker Compose

Although service containers started by Compose can be listed using the container ls command, there is the ps command for listing containers defined in the YAML only.
```bash
docker-compose ps
```


It's not as informative as the container ls output, but it's useful when you have tons of containers running simultaneously.

How to Execute Commands Inside a Running Service in Docker Compose

I hope you remember from the previous section that you have to run some migration scripts to create the database tables for this API.

Just like the container exec command, there is an exec command for docker-compose. Generic syntax for the command is as follows:
```bash
docker-compose exec <service name> <command>
```
To execute the npm run db:migrate command inside the api service, you can execute the following command:
```bash
docker-compose exec api npm run db:migrate
```


Unlike the container exec command, you don't need to pass the -it flag for interactive sessions. docker-compose does that automatically.

How to Access Logs from a Running Service in Docker Compose

You can also use the logs command to retrieve logs from a running service. The generic syntax for the command is as follows:

docker-compose logs <service name>

To access the logs from the api service, execute the following command:
```bash
docker-compose logs api
```

This is just a portion from the log output. You can kind of hook into the output stream of the service and get the logs in real-time by using the -f or --follow option. Any later log will show up instantly in the terminal as long as you don't exit by pressing ctrl + c or closing the window. The container will keep running even if you exit out of the log window.

How to Stop Services in Docker Compose

To stop services, there are two approaches that you can take. The first one is the down command. The down command stops all running containers and removes them from the system. It also removes any networks:
```bash
docker-compose down --volumes
```


The --volumes option indicates that you want to remove any named volume(s) defined in the volumes block. You can learn about the additional options for the down command in the official docs.

Another command for stopping services is the stop command which functions identically to the container stop command. It stops all the containers for the application and keeps them. These containers can later be started with the start or up command.

How to Compose a Full-stack Application in Docker Compose

In this sub-section, we'll be adding a front-end to our notes API and turning it into a complete full-stack application. I won't be explaining any of the Dockerfile.dev files in this sub-section (except the one for the nginx service) as they are identical to some of the others you've already seen in previous sub-sections.‌

If you've cloned the project code repository, then go inside the fullstack-notes-application directory. Each directory inside the project root contains the code for each service and the corresponding Dockerfile.‌

Before we start with the docker-compose.yaml file let's look at a diagram of how the application is going to work:

Instead of accepting requests directly like we previously did, in this application all the requests will be first received by an NGINX (lets call it router) service.

The router will then see if the requested end-point has /api in it. If yes, the router will route the request to the back-end or if not, the router will route the request to the front-end.

You do this because when you run a front-end application it doesn't run inside a container. It runs on the browser, served from a container. As a result, Compose networking doesn't work as expected and the front-end application fails to find the api service.

NGINX, on the other hand, runs inside a container and can communicate with the different services across the entire application.

I will not get into the configuration of NGINX here. That topic is kinda out of the scope of this book. But if you want to have a look at it, go ahead and check out the /notes-api/nginx/development.conf and /notes-api/nginx/production.conf files. Code for the /notes-api/nginx/Dockerfile.dev is as follows:
```bash
FROM nginx:stable-alpine

COPY ./development.conf /etc/nginx/conf.d/default.conf
```
All it does is copy the configuration file to /etc/nginx/conf.d/default.conf inside the container.

Let's start writing the docker-compose.yaml file. Apart from the api and db services there will be the client and nginx services. There will also be some network definitions that I'll get into shortly.
```bash
version: "3.8"

services: 
    db:
        image: postgres:12
        container_name: notes-db-dev
        volumes: 
            - db-data:/var/lib/postgresql/data
        environment:
            POSTGRES_DB: notesdb
            POSTGRES_PASSWORD: secret
        networks:
            - backend
    api:
        build: 
            context: ./api
            dockerfile: Dockerfile.dev
        image: notes-api:dev
        container_name: notes-api-dev
        volumes: 
            - /home/node/app/node_modules
            - ./api:/home/node/app
        environment: 
            DB_HOST: db ## same as the database service name
            DB_PORT: 5432
            DB_USER: postgres
            DB_DATABASE: notesdb
            DB_PASSWORD: secret
        networks:
            - backend
    client:
        build:
            context: ./client
            dockerfile: Dockerfile.dev
        image: notes-client:dev
        container_name: notes-client-dev
        volumes: 
            - /home/node/app/node_modules
            - ./client:/home/node/app
        networks:
            - frontend
    nginx:
        build:
            context: ./nginx
            dockerfile: Dockerfile.dev
        image: notes-router:dev
        container_name: notes-router-dev
        restart: unless-stopped
        ports: 
            - 8080:80
        networks:
            - backend
            - frontend

volumes:
    db-data:
        name: notes-db-dev-data

networks: 
    frontend:
        name: fullstack-notes-application-network-frontend
        driver: bridge
    backend:
        name: fullstack-notes-application-network-backend
        driver: bridge

```
The file is almost identical to the previous one you worked with. The only thing that needs some explanation is the network configuration. The code for the networks block is as follows:
```bash
networks: 
    frontend:
        name: fullstack-notes-application-network-frontend
        driver: bridge
    backend:
        name: fullstack-notes-application-network-backend
        driver: bridge
```
I've defined two bridge networks. By default, Compose creates a bridge network and attaches all containers to that. In this project, however, I wanted proper network isolation. So I defined two networks, one for the front-end services and one for the back-end  services.

I've also added networks block in each of the service definitions. This way the the api and db service will be attached to one network and the client service will be attached to a separate network. But the nginx service will be attached to both the networks so that it can perform as router between the front-end and back-end services.

Start all the services by executing the following command:
```bash
docker-compose --file docker-compose.yaml up --detach
```


Now visit http://localhost:8080 and voilà!

Try adding and deleting notes to see if the application works properly. The project also comes with shell scripts and a Makefile. Explore them to see how you can run this project without the help of docker-compose like you did in the previous section.