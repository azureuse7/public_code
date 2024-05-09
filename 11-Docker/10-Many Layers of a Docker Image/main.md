# How to Understand the Many Layers of a Docker Image

For this demonstration, I'll be using the custom-nginx:packaged image from the previous sub-section.

# How to Build NGINX from Source

In order to build NGINX from source, you first need the source of NGINX. 

Get a good base image for building the application, like ubuntu.

Install necessary build dependencies on the base image.

Copy the nginx-1.19.2.tar.gz file inside the image.

Extract the contents of the archive and get rid of it.

Configure the build, compile and install the program using the make tool.

Get rid of the extracted source code.

Run nginx executable.

Now that you have a plan, let's begin by opening up old Dockerfile and updating its contents as follows:
```bash
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install build-essential\ 
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
As you can see, the code inside the Dockerfile reflects the seven steps I talked about above.

The FROM instruction sets Ubuntu as the base image making an ideal environment for building any application.

The RUN instruction installs standard packages necessary for building NGINX from source.

The COPY instruction here is something new. This instruction is responsible for copying the the nginx-1.19.2.tar.gz file inside the image. The generic syntax for the COPY instruction is COPY <source> <destination> where source is in your local filesystem and the destination is inside your image. The . as the destination means the working directory inside the image which is by default / unless set otherwise.

The second RUN instruction here extracts the contents from the archive using tar and gets rid of it afterwards.

The archive file contains a directory called nginx-1.19.2 containing the source code. So on the next step, you'll have to cd inside that directory and perform the build process. You can read the How to Install Software from Source Code… and Remove it Afterwards article to learn more on the topic.

Once the build and installation is complete, you remove the nginx-1.19.2 directory using rm command.

On the final step you start NGINX in single process mode just like you did before.

Now to build an image using this code, execute the following command:
```bash
docker image build --tag custom-nginx:built .
```


This code is alright but there are some places where we can make improvements.

Instead of hard coding the filename like nginx-1.19.2.tar.gz, you can create an argument using the ARG instruction. This way, you'll be able to change the version or filename by just changing the argument.

Instead of downloading the archive manually, you can let the daemon download the file during the build process. There is another instruction like COPY called the ADD instruction which is capable of adding files from the internet.

Open up the Dockerfile file and update its content as follows:
```bash
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install build-essential\ 
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

RUN rm -rf /${FILENAME}}

CMD ["nginx", "-g", "daemon off;"]
```
The code is almost identical to the previous code block except for a new instruction called ARG on line 13, 14 and the usage of the ADD instruction on line 16. Explanation for the updated code is as follows:

The ARG instruction lets you declare variables like in other languages. These variables or arguments can later be accessed using the ${argument name} syntax. Here, I've put the filename nginx-1.19.2 and the file extension tar.gz in two separate arguments. This way I can switch between newer versions of NGINX or the archive format by making a change in just one place. In the code above, I've added default values to the variables. Variable values can be passed as options of the image build command as well. You can consult the official reference for more details.

In the ADD instruction, I've formed the download URL dynamically using the arguments declared above. The https://nginx.org/download/${FILENAME}.${EXTENSION} line will result in something like https://nginx.org/download/nginx-1.19.2.tar.gz during the build process. You can change the file version or the extension by changing it in just one place thanks to the ARG instruction.

The ADD instruction doesn't extract files obtained from the internet by default, hence the usage of tar on line 18.

The rest of the code is almost unchanged. 
```bash
docker image build --tag custom-nginx:built .
```

Now you should be able to run a container using the custom-nginx:built image.
```bash
docker container run --rm --detach --name custom-nginx-built --publish 8080:80 custom-nginx:built


docker container ls
```

A container using the custom-nginx:built-v2 image has been successfully run. The container should be accessible at http://127.0.0.1:8080 now.

And here is the trusty default response page from NGINX. You can visit the official reference site to learn more about the available instructions.

# How to Optimize Docker Images

The image we built very unoptimized. To prove my point let's have a look at the size of the image using the image ls command:

docker image ls

# REPOSITORY         TAG       IMAGE ID       CREATED          SIZE
# custom-nginx       built     1f3aaf40bb54   16 minutes ago   343MB
```bash
docker image pull nginx:stable

docker image ls
```
In order to find out the root cause, let's have a look at the Dockerfile first:
```bash
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install build-essential\ 
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

RUN rm -rf /${FILENAME}}

CMD ["nginx", "-g", "daemon off;"]
```

As you can see on line 3, the RUN instruction installs a lot of stuff. Although these packages are necessary for building NGINX from source, they are not necessary for running it.

Out of the 6 packages that we installed, only two are necessary for running NGINX. These are libpcre3 and zlib1g. So a better idea would be to uninstall the other packages once the build process is done.

To do so, update your Dockerfile as follows:
```bash
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
As you can see, on line 10 a single RUN instruction is doing all the necessary heavy-lifting. The exact chain of events is as follows:

From line 10 to line 17, all the necessary packages are being installed.

On line 18, the source code is being extracted and the downloaded archive gets removed.

From line 19 to line 28, NGINX is configured, built, and installed on the system.

On line 29, the extracted files from the downloaded archive get removed.

From line 30 to line 36, all the unnecessary packages are being uninstalled and cache cleared. The libpcre3 and zlib1g packages are needed for running NGINX so we keep them.

You may ask why am I doing so much work in a single RUN instruction instead of nicely splitting them into multiple instructions like we did previously. Well, splitting them up would be a mistake.

If you install packages and then remove them in separate RUN instructions, they'll live in separate layers of the image. Although the final image will not have the removed packages, their size will still be added to the final image since they exist in one of the layers consisting the image. So make sure you make these kind of changes on a single layer.

Let's build an image using this Dockerfile and see the differences.
```bash
docker image build --tag custom-nginx:built .

docker image ls
```


As you can see, the image size has gone from being 343MB to 81.6MB. The official image is 133MB. This is a pretty optimized build, but we can go a bit further in the next sub-section.

Embracing Alpine Linux

If you've been fiddling around with containers for some time now, you may have heard about something called Alpine Linux. It's a full-featured Linux distribution like Ubuntu, Debian or Fedora.

Although not as user friendly as the other commercial distributions, the transition to Alpine is still very simple. In this sub-section you'll learn about recreating the custom-nginx image using the Alpine image as its base.

Open up your Dockerfile and update its content as follows:
```bash
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
The code is almost identical except for a few changes. I'll be listing the changes and explaining them as I go:

Instead of using apt-get install for installing packages, we use apk add. The --no-cache option means that the downloaded package won't be cached. Likewise we'll use apk del instead of apt-get remove to uninstall packages.

The --virtual option for the apk add command is used for bundling a bunch of packages into a single virtual package for easier management. Packages that are needed only for building the program are labeled as .build-deps which are then removed on line 29 by executing the apk del .build-deps command. You can learn more about virtuals in the official docs.

The package names are a bit different here. Usually every Linux distribution has its package repository available to everyone where you can search for packages. If you know the packages required for a certain task, then you can just head over to the designated repository for a distribution and search for it. You can look up Alpine Linux packages here.

Now build a new image using this Dockerfile and see the difference in file size:
```bash
docker image build --tag custom-nginx:built .
```
docker image ls
```


Where the ubuntu version was 81.6MB, the alpine one has come down to 12.8MB which is a massive gain. Apart from the apk package manager, there are some other things that differ in Alpine from Ubuntu but they're not that big a deal. You can just search the internet whenever you get stuck.
