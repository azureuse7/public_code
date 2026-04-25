# How to Use Detached Mode and Work with Executable Images

## How to Use Detached Mode

Another very popular option of the `run` command is `--detach` (or `-d`). By default, containers run in the foreground and attach themselves to the terminal like any other program invoked from the terminal. Closing the terminal window also stops the running container.

To override this behavior and keep a container running in the background, include the `--detach` option with the `run` command:

```bash
docker container run --detach --publish 8080:80 fhsinchy/hello-dock

# 9f21cb77705810797c4b847dbd330d9c732ffddba14fb435470567a7a3f46cdc
```

Instead of a wall of text, you'll get back the ID of the newly created container.

The order of the options you provide does not really matter. If you put the `--publish` option before the `--detach` option, it will work just the same. One important rule for the `run` command is that the **image name must come last**. Anything written after the image name is passed as an argument to the container entry-point, which may result in unexpected behavior.

## How to Work with Executable Images

Take the `rmbyext` project as an example. This is a simple Python script capable of recursively deleting files of given extensions. The project can be found at [fhsinchy/rmbyext](https://github.com/fhsinchy/rmbyext) on GitHub.

If you have both Git and Python installed, you can install this script by executing the following command:

```bash
pip install git+https://github.com/fhsinchy/rmbyext.git#egg=rmbyext
```

Assuming Python has been set up properly on your system, the script should be available anywhere through the terminal. The generic syntax for using the script is:

```bash
rmbyext <file extension>
```

To test it out, open your terminal inside an empty directory and create some files with different extensions:

```bash
touch a.pdf b.pdf c.txt d.pdf e.txt

ls

# a.pdf  b.pdf  c.txt  d.pdf  e.txt
```

To delete all the `pdf` files from this directory:

```bash
rmbyext pdf

# Removing: PDF
# b.pdf
# a.pdf
# d.pdf
```

An executable image for this program should be able to take file extensions as arguments and delete them just like the `rmbyext` program does.

The `fhsinchy/rmbyext` image behaves in the same manner. This image contains a copy of the `rmbyext` script and is configured to run the script on a directory `/zone` inside the container.

Since containers are isolated from your local system, the `rmbyext` program running inside the container does not have access to your local file system. To grant the container access to your local files, you can use a **bind mount**.

A bind mount creates a two-way data binding between a local file system directory (source) and a directory inside a container (destination). Any changes made in the destination directory are reflected in the source directory and vice versa.

To delete files using the image instead of the locally installed program:

```bash
docker container run --rm -v $(pwd):/zone fhsinchy/rmbyext pdf

# Removing: PDF
# b.pdf
# a.pdf
# d.pdf
```

The `-v $(pwd):/zone` part uses the `-v` or `--volume` option to create a bind mount. This option takes three fields separated by colons (`:`):

```bash
--volume <local file system directory absolute path>:<container file system directory absolute path>:<read write access>
```

The third field is optional, but you must pass absolute paths for both the local directory and the directory inside the container.

In this example, `$(pwd)` is replaced by the current working directory (e.g., `/home/fhsinchy/the-zone`), which contains the `.pdf` and `.txt` files. The `--volume` or `-v` option is valid for both `container run` and `container create` commands.

The difference between a regular image and an executable one is that the entry-point for an executable image is set to a custom program — in this case `rmbyext` — instead of `sh`. Anything you write after the image name in a `container run` command gets passed to the entry-point. So `docker container run --rm -v $(pwd):/zone fhsinchy/rmbyext pdf` effectively runs `rmbyext pdf` inside the container.

## How to Containerize a JavaScript Application

In this section, you'll work with the source code of the `fhsinchy/hello-dock` image.

### How to Write the Development Dockerfile

This is a simple JavaScript project powered by [vitejs/vite](https://vitejs.dev/). The plan for the development image is as follows:

1. Get a good base image for running JavaScript applications, like `node`.
2. Set the default working directory inside the image.
3. Copy the `package.json` file into the image.
4. Install necessary dependencies.
5. Copy the rest of the project files.
6. Start the Vite development server by running `npm run dev`.

Create a file named `Dockerfile.dev` with the following content:

```dockerfile
FROM node:lts-alpine

EXPOSE 3000

USER node

RUN mkdir -p /home/node/app

WORKDIR /home/node/app

COPY ./package.json .
RUN npm install

COPY . .

CMD [ "npm", "run", "dev" ]
```

### Explanation of Instructions

- **FROM** sets the official Node.js image as the base. The `lts-alpine` tag selects the Alpine variant of the long-term support version. Available tags and documentation can be found on the [node Docker Hub page](https://hub.docker.com/_/node).
- **USER** sets the default user to `node`. By default Docker runs containers as the root user, which can pose a security risk. The `node` image includes a non-root user named `node`.
- **RUN mkdir -p /home/node/app** creates an `app` directory inside the home directory of the `node` user. The home directory for any non-root user in Linux is `/home/<username>` by default.
- **WORKDIR** sets the default working directory to `/home/node/app`. This applies to any subsequent `COPY`, `ADD`, `RUN`, and `CMD` instructions.
- The first **COPY** copies `package.json` into the working directory. The **RUN** instruction runs `npm install` to install all dependencies.
- The second **COPY** copies the rest of the project files from the host into the image's working directory.
- **CMD** sets `npm run dev` as the default command in exec form.
- The Vite development server runs on port `3000` by default, so `EXPOSE 3000` is included.

### Building and Running the Development Image

Since the filename is `Dockerfile.dev` rather than `Dockerfile`, pass the filename explicitly using the `--file` option:

```bash
docker image build --file Dockerfile.dev --tag hello-dock:dev .
```

Run a container using this image:

```bash
docker container run \
    --rm \
    --detach \
    --publish 3000:3000 \
    --name hello-dock-dev \
    hello-dock:dev

# 21b9b1499d195d85e81f0e8bce08f43a64b63d589c5f15cbbd0b9c0cb07ae268
```

Visit `http://127.0.0.1:3000` to see the `hello-dock` application in action.

## How to Work with Anonymous Volumes in Docker

When using a bind mount for development (e.g., mounting the project directory), the `node_modules` folder inside the container can be overwritten by the empty `node_modules` from the host. An anonymous volume solves this problem.

An anonymous volume is identical to a bind mount except that you don't specify the source directory. The generic syntax is:

```bash
--volume <container file system directory absolute path>:<read write access>
```

The final command for starting the `hello-dock` container with both a bind mount and an anonymous volume:

```bash
docker container run \
    --rm \
    --detach \
    --publish 3000:3000 \
    --name hello-dock-dev \
    --volume $(pwd):/home/node/app \
    --volume /home/node/app/node_modules \
    hello-dock:dev

# 53d1cfdb3ef148eb6370e338749836160f75f076d0fbec3c2a9b059a8992de8b
```

Docker will take the entire `node_modules` directory from inside the container, store it in a location managed by the Docker daemon on the host, and mount it back as `node_modules` inside the container.

## How to Ignore Unnecessary Files

A `.dockerignore` file contains a list of files and directories to be excluded from image builds, similar to `.gitignore`. Place it in the same directory as your `Dockerfile` to prevent large or sensitive files from being copied into the image.

## How to Containerize a Multi-Container JavaScript Application

Now that you have learned about networks in Docker, this section covers containerizing a full-fledged multi-container project: a simple notes API powered by Express.js and PostgreSQL.

This project has two containers that need to communicate over a user-defined network. You will also use environment variables and named volumes.

### How to Run the Database Server

The database server uses the official `postgres` image. You must provide the `POSTGRES_PASSWORD` environment variable. A default database name is set with `POSTGRES_DB`, and port `5432` must be published.

Run the database server:

```bash
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
```

The `--env` option provides environment variables to a container. It can be used with both `container run` and `container create` commands.

Although the container is running, there is a potential problem: databases like PostgreSQL persist data in a directory (`/var/lib/postgresql/data` inside the container). If the container is destroyed, all data is lost. A named volume solves this problem.

### How to Work with Named Volumes in Docker

A named volume is similar to an anonymous volume but can be referenced by its name. Use the `volume create` command to create one:

```bash
docker volume create <volume name>
```

Create a volume named `notes-db-data`:

```bash
docker volume create notes-db-data

# notes-db-data

docker volume ls

# DRIVER    VOLUME NAME
# local     notes-db-data
```

Stop and remove the existing `notes-db` container:

```bash
docker container stop notes-db

# notes-db

docker container rm notes-db

# notes-db
```

Run a new container with the named volume mounted:

```bash
docker container run \
    --detach \
    --volume notes-db-data:/var/lib/postgresql/data \
    --name=notes-db \
    --env POSTGRES_DB=notesdb \
    --env POSTGRES_PASSWORD=secret \
    --network=notes-api-network \
    postgres:12

# 37755e86d62794ed3e67c19d0cd1eba431e26ab56099b92a3456908c1d346791
```

Verify the volume is mounted:

```bash
docker container inspect --format='{{range .Mounts}} {{ .Name }} {{end}}' notes-db

#  notes-db-data
```

Data is now safely stored in the `notes-db-data` volume and will persist across container restarts.

### How to Create a Network and Attach the Database Server

Containers must be attached to a user-defined bridge network in order to communicate with each other by container name. Create a network named `notes-api-network`:

```bash
docker network create notes-api-network
```

Attach the `notes-db` container to this network:

```bash
docker network connect notes-api-network notes-db
```
