# How to Understand the Many Layers of a Docker Image

Docker images are composed of multiple read-only layers, each representing an instruction in the `Dockerfile`. Understanding layers helps you optimize image size and build speed.

## How to Build NGINX from Source

To build NGINX from source, the following steps are needed:

1. Get a good base image for building the application, like `ubuntu`.
2. Install necessary build dependencies on the base image.
3. Copy the `nginx-1.19.2.tar.gz` file inside the image.
4. Extract the contents of the archive and remove it.
5. Configure the build, compile, and install the program using the `make` tool.
6. Remove the extracted source code.
7. Run the NGINX executable.

Open the `Dockerfile` and update its contents as follows:

```dockerfile
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install build-essential \
                    libpcre3 \
                    libpcre3-dev \
                    zlib1g \
                    zlib1g-dev \
                    libssl1.1 \
                    libssl-dev \
                    -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY nginx-1.19.2.tar.gz .

RUN tar -xvf nginx-1.19.2.tar.gz && rm nginx-1.19.2.tar.gz

RUN cd nginx-1.19.2 && \
    ./configure \
        --sbin-path=/usr/bin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --http-log-path=/var/log/nginx/access.log \
        --with-pcre \
        --pid-path=/var/run/nginx.pid \
        --with-http_ssl_module && \
    make && make install

RUN rm -rf /nginx-1.19.2

CMD ["nginx", "-g", "daemon off;"]
```

The code inside the `Dockerfile` reflects the seven steps above:

- **FROM** sets Ubuntu as the base image, providing an ideal environment for building any application.
- The first **RUN** installs the standard packages necessary for building NGINX from source.
- **COPY** copies the `nginx-1.19.2.tar.gz` file inside the image. The generic syntax is `COPY <source> <destination>`, where `source` is in your local filesystem and `destination` is inside your image. The `.` as the destination means the working directory inside the image, which is `/` by default unless set otherwise.
- The second **RUN** extracts the contents from the archive using `tar` and removes the archive file.
- The third **RUN** enters the `nginx-1.19.2` directory and performs the build and installation.
- The fourth **RUN** removes the `nginx-1.19.2` directory using `rm`.
- **CMD** starts NGINX in single-process mode.

Build the image:

```bash
docker image build --tag custom-nginx:built .
```

## Improving the Dockerfile with ARG and ADD

Instead of hard-coding the filename `nginx-1.19.2.tar.gz`, you can use the `ARG` instruction to declare a variable. You can also let the daemon download the archive during the build process using the `ADD` instruction.

Update your `Dockerfile` as follows:

```dockerfile
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install build-essential \
                    libpcre3 \
                    libpcre3-dev \
                    zlib1g \
                    zlib1g-dev \
                    libssl1.1 \
                    libssl-dev \
                    -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG FILENAME="nginx-1.19.2"
ARG EXTENSION="tar.gz"

ADD https://nginx.org/download/${FILENAME}.${EXTENSION} .

RUN tar -xvf ${FILENAME}.${EXTENSION} && rm ${FILENAME}.${EXTENSION}

RUN cd ${FILENAME} && \
    ./configure \
        --sbin-path=/usr/bin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --http-log-path=/var/log/nginx/access.log \
        --with-pcre \
        --pid-path=/var/run/nginx.pid \
        --with-http_ssl_module && \
    make && make install

RUN rm -rf /${FILENAME}

CMD ["nginx", "-g", "daemon off;"]
```

The key updates are:

- The `ARG` instruction declares variables (`FILENAME` and `EXTENSION`) with default values. These can be overridden at build time. Variable values can be passed as options of the `docker image build` command.
- The `ADD` instruction dynamically forms the download URL using the declared arguments. The URL `https://nginx.org/download/${FILENAME}.${EXTENSION}` resolves to something like `https://nginx.org/download/nginx-1.19.2.tar.gz` during the build.
- The `ADD` instruction does not extract files obtained from the internet by default, so `tar` is still needed.

Build the image:

```bash
docker image build --tag custom-nginx:built .
```

Run a container from the built image:

```bash
docker container run --rm --detach --name custom-nginx-built --publish 8080:80 custom-nginx:built

docker container ls
```

The container should be accessible at `http://127.0.0.1:8080`.

## How to Optimize Docker Images

The image built above is not optimized. Check its size:

```bash
docker image ls
```

Example output:

```
REPOSITORY     TAG     IMAGE ID       CREATED          SIZE
custom-nginx   built   1f3aaf40bb54   16 minutes ago   343MB
```

Pull the official NGINX image for comparison:

```bash
docker image pull nginx:stable

docker image ls
```

### Reducing Size by Combining RUN Instructions

The build packages installed by `apt-get` are only needed during the build, not for running NGINX. Out of the 6 packages installed, only `libpcre3` and `zlib1g` are required at runtime. Combine all installation, build, and cleanup steps into a single `RUN` instruction so that unnecessary packages do not persist in any layer.

Update your `Dockerfile` as follows:

```dockerfile
FROM ubuntu:latest

EXPOSE 80

ARG FILENAME="nginx-1.19.2"
ARG EXTENSION="tar.gz"

ADD https://nginx.org/download/${FILENAME}.${EXTENSION} .

RUN apt-get update && \
    apt-get install build-essential \
                    libpcre3 \
                    libpcre3-dev \
                    zlib1g \
                    zlib1g-dev \
                    libssl1.1 \
                    libssl-dev \
                    -y && \
    tar -xvf ${FILENAME}.${EXTENSION} && rm ${FILENAME}.${EXTENSION} && \
    cd ${FILENAME} && \
    ./configure \
        --sbin-path=/usr/bin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --http-log-path=/var/log/nginx/access.log \
        --with-pcre \
        --pid-path=/var/run/nginx.pid \
        --with-http_ssl_module && \
    make && make install && \
    cd / && rm -rfv /${FILENAME} && \
    apt-get remove build-essential \
                    libpcre3-dev \
                    zlib1g-dev \
                    libssl-dev \
                    -y && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["nginx", "-g", "daemon off;"]
```

The single `RUN` instruction:

1. Installs all necessary packages.
2. Extracts the source code and removes the archive.
3. Configures, builds, and installs NGINX.
4. Removes the extracted source files.
5. Uninstalls all build-only packages and clears the cache. The `libpcre3` and `zlib1g` packages are kept since they are needed at runtime.

> **Important:** If you install packages in one `RUN` instruction and remove them in a separate `RUN` instruction, they will live in separate image layers. Although the final image will not show the removed packages, their size is still counted because they exist in an earlier layer. Always combine install and cleanup steps into a single `RUN` instruction.

Build the optimized image:

```bash
docker image build --tag custom-nginx:built .

docker image ls
```

The image size drops from 343MB to approximately 81.6MB.

## Embracing Alpine Linux

Alpine Linux is a full-featured, minimal Linux distribution. Switching to Alpine as the base image can dramatically reduce image size further.

Update your `Dockerfile` to use Alpine:

```dockerfile
FROM alpine:latest

EXPOSE 80

ARG FILENAME="nginx-1.19.2"
ARG EXTENSION="tar.gz"

ADD https://nginx.org/download/${FILENAME}.${EXTENSION} .

RUN apk add --no-cache pcre zlib && \
    apk add --no-cache \
            --virtual .build-deps \
            build-base \
            pcre-dev \
            zlib-dev \
            openssl-dev && \
    tar -xvf ${FILENAME}.${EXTENSION} && rm ${FILENAME}.${EXTENSION} && \
    cd ${FILENAME} && \
    ./configure \
        --sbin-path=/usr/bin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --http-log-path=/var/log/nginx/access.log \
        --with-pcre \
        --pid-path=/var/run/nginx.pid \
        --with-http_ssl_module && \
    make && make install && \
    cd / && rm -rfv /${FILENAME} && \
    apk del .build-deps

CMD ["nginx", "-g", "daemon off;"]
```

Notable differences from the Ubuntu version:

- `apk add` replaces `apt-get install`. The `--no-cache` option prevents the downloaded package from being cached.
- `apk del` replaces `apt-get remove` to uninstall packages.
- The `--virtual` option for `apk add` bundles a group of packages into a single virtual package named `.build-deps` for easier management. These are removed in one step with `apk del .build-deps`.
- Package names differ slightly on Alpine. You can search for Alpine packages at [pkgs.alpinelinux.org](https://pkgs.alpinelinux.org/packages).

Build the Alpine-based image:

```bash
docker image build --tag custom-nginx:built .

docker image ls
```

The Alpine-based image comes in at approximately 12.8MB, compared to 81.6MB for the Ubuntu version — a massive reduction.
