# Create a Dockerfile

This guide walks through creating a `Dockerfile`, building a Docker image, and running containers. It also covers writing a multi-stage Dockerfile for a Node.js API.

## 1. Create a Dockerfile

With containers, the build and deploy process is as follows:

1. Choose a base Docker image with the required application dependencies and libraries.
2. Build the application.
3. Deploy the application into the image.

This process is described in a file called `Dockerfile`. See the following example for a .NET web application:

```dockerfile
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

Note that this `Dockerfile` uses two different Docker images: one for building the application (`sdk`) and a second one for running it (`aspnet`).

## 2. Build the Docker Image

Build the image and assign a name and tag to it:

```bash
docker build --rm -t webapp:1.0 .
```

Verify the image exists:

```bash
docker images
```

## 3. Run the Docker Image

Run a container based on the image created earlier:

```bash
docker run --rm -d -p 5000:80/tcp webapp:1.0
```

Open a web browser at `localhost:5000` to see the application running.

List the running Docker containers:

```bash
docker ps
```

## 4. Run a Command Inside a Docker Container

Use `docker exec` to run commands inside a running container:

```bash
docker exec <CONTAINER_ID> -- ls
```

## 5. Stop a Container

Use `docker stop` to gracefully stop a running container:

```bash
docker stop <CONTAINER_ID>
```

## 6. Remove a Container

Use `docker rm` to remove a stopped container:

```bash
docker rm <CONTAINER_ID>
```

## 7. Remove an Image

Use `docker rmi` to remove an image by ID or name:

```bash
docker rmi <IMAGE_ID_OR_NAME>
```

## How to Write a Multi-Stage Dockerfile for a Node.js API

Navigate to your project's `notes-api/api` directory and create a new `Dockerfile` with the following content:

```dockerfile
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

This is a multi-staged build. The first stage builds and installs the dependencies using `node-gyp`; the second stage runs the application. Here is a brief explanation:

- **Stage 1** uses `node:lts-alpine` as its base and is named `builder`.
- `python`, `make`, and `g++` are installed because `node-gyp` requires them.
- `/app` is set as the `WORKDIR`.
- `package.json` is copied to the `WORKDIR` and all dependencies are installed.
- **Stage 2** also uses `node:lts-alpine` as the base.
- The `NODE_ENV` environment variable is set to `production`, which is important for the API to run properly.
- The default user is set to `node`, the `/home/node/app` directory is created, and it is set as the `WORKDIR`.
- All project files are copied, and then the `node_modules` directory is copied from the `builder` stage. This directory contains all the built dependencies needed to run the application.
- The default command is set with `CMD`.

Build the image from this `Dockerfile`:

```bash
docker image build --tag notes-api .
```

Before running a container using this image, make sure the database container is running and attached to the `notes-api-network`:

```bash
docker container inspect notes-db
```

Once you have confirmed everything is in place, run a new container:

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

The `notes-api` application requires three environment variables:

- `DB_HOST` — The hostname of the database server. Since both the database server and the API are on the same user-defined bridge network, the database can be referenced by its container name (`notes-db`).
- `DB_DATABASE` — The database this API will use. The default database name was set to `notesdb` using the `POSTGRES_DB` environment variable when the database server was started.
- `DB_PASSWORD` — The password for connecting to the database. This was set using the `POSTGRES_PASSWORD` environment variable when the database server was started.

Verify the container is running:

```bash
docker container ls
```

The container is now running. You can visit `http://127.0.0.1:3000/` to see the API in action.

The API has five routes in total, which you can find in the `/notes-api/api/api/routes/notes.js` file.

Although the container is running, you'll also need to run the database migration to set up the database tables by executing `npm run db:migrate` inside the container.
