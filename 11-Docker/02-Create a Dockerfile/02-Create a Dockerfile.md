## 1) Create a Dockerfile

With containers, the process will be:

1. Choose a base docker image with application dependencies and libraries (steps 1 and 2 for VMs).
2. Build the application.
3. Deploy the application into the image.

This process will be described into a file called *Dockerfile*. Let's see the following example:


```dockerfile
# Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:5.0-buster-slim AS build
WORKDIR /src
COPY "WebApp.csproj" .
RUN dotnet restore "WebApp.csproj"
COPY . .
RUN dotnet build "WebApp.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "WebApp.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "WebApp.dll"]
```

Note that in this Dockerfile, we are using 2 different docker images. One is used to build the application (sdk). And a second one is used to run the app (aspnet).

## 2) Build docker image

Run the same command and assign a name to the image:

```bash
$ docker build --rm -t webapp:1.0 .
```

Check the images exists:

```bash
$ docker images
```

## 3) Run a docker image

Let's run a container based on the image created earlier:

```bash
$ docker run --rm -d -p 5000:80/tcp webapp:1.0
```

Open web browser on *localhost:5000* to see the application running.

List the running docker containers:

```bash
$ docker ps
```

## 3) Run a command inside a docker container
Explore the command docker exec.
```bash
$ docker exec <CONTAINER_ID> -- ls
```

## 5) Stop a container

Explore the command docker stop.
```bash
$ docker stop <CONTAINER_ID>
```

## 6) Remove a container

Explore the command docker rm.
```bash
$ docker rm <CONTAINER_ID>
```

## 7) Remove an image

Explore the command docker rmi.
```bash
$ docker rmi <IMAGE_ID_OR_NAME>
```


## How to Write the Dockerfile

Go to the directory where you've cloned the project code. Inside there, go inside the notes-api/api directory, and create a new Dockerfile. Put the following code in the file:
```bash
# stage one
FROM node:lts-alpine as builder

# install dependencies for node-gyp
RUN apk add --no-cache python make g++

WORKDIR /app

COPY ./package.json .
RUN npm install --only=prod

# stage two
FROM node:lts-alpine

EXPOSE 3000
ENV NODE_ENV=production

USER node
RUN mkdir -p /home/node/app
WORKDIR /home/node/app

COPY . .
COPY --from=builder /app/node_modules  /home/node/app/node_modules

CMD [ "node", "bin/www" ]
```
This is a multi-staged build. The first stage is used for building and installing the dependencies using node-gyp and the second stage is for running the application. I'll go through the steps briefly:

Stage 1 uses node:lts-alpine as its base and uses builder as the stage name.

On line 5, we install python, make, and g++. The node-gyp tool requires these three packages to run.

On line 7, we set /app directory as the WORKDIR .

On line 9 and 10, we copy the package.json file to the WORKDIR and install all the dependencies.

Stage 2 also uses node-lts:alpine as the base.

On line 16, we set the NODE_ENV environment variable to production. This is important for the API to run properly.

From line 18 to line 20, we set the default user to node, create the /home/node/app directory, and set that as the WORKDIR.

On line 22, we copy all the project files and on line 23 we copy the node_modules directory from the builder stage. This directory contains all the built dependencies necessary for running the application.

On line 25, we set the default command.

To build an image from this Dockerfile, you can execute the following command:
```bash
docker image build --tag notes-api .
```


Before you run a container using this image, make sure the database container is running, and is attached to the notes-api-network.
```bash
docker container inspect notes-db
```



I've shortened the output for easy viewing here. On my system, the notes-db container is running, uses the notes-db-data volume, and is attached to the notes-api-network bridge.

Once you're assured that everything is in place, you can run a new container by executing the following command:
```bash
docker container run \
    --detach \
    --name=notes-api \
    --env DB_HOST=notes-db \
    --env DB_DATABASE=notesdb \
    --env DB_PASSWORD=secret \
    --publish=3000:3000 \
    --network=notes-api-network \
    notes-api
```


You should be able to understand this long command by yourself, so I'll go through the environment variables briefly.

The notes-api application requires three environment variables to be set. They are as follows:

DB_HOST - This is the host of the database server. Given that both the database server and the API are attached to the same user-defined bridge network, the database server can be refereed to using its container name which is notes-db in this case.

DB_DATABASE - The database that this API will use. On Running the Database Server we set the default database name to notesdb using the POSTGRES_DB environment variable. We'll use that here.

DB_PASSWORD - Password for connecting to the database. This was also set on Running the Database Server sub-section using the POSTGRES_PASSWORD environment variable.

To check if the container is running properly or not, you can use the container ls command:
```bash
docker container ls
```bash


The container is running now. You can visit http://127.0.0.1:3000/ to see the API in action.

The API has five routes in total that you can see inside the /notes-api/api/api/routes/notes.js file.

Although the container is running, there is one last thing that you'll have to do before you can start using it. You'll have to run the database migration necessary for setting up the database tables, and you can do that by executing npm run db:migrate command inside the container.