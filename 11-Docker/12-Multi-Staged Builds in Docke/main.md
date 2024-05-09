# How to Perform Multi-Staged Builds in Docker

In development mode the npm run serve command starts a development server that serves the application to the user. That server not only serves the files but also provides the hot reload feature.

In production mode, the npm run build command compiles all your JavaScript code into some static HTML, CSS, and JavaScript files. To run these files you don't need node or any other runtime dependencies. All you need is a server like nginx for example.

To create an image where the application runs in production mode, you can take the following steps:

- Use node as the base image and build the application.

- Install nginx inside the node image and use that to serve the static files.

This approach is completely valid. But the problem is that the node image is big and most of the stuff it carries is unnecessary to serve your static files. A better approach to this scenario is as follows:

- Use node image as the base and build the application.

- Copy the files created using the node image to an nginx image.

- Create the final image based on nginx and discard all node related stuff.

This way your image only contains the files that are needed and becomes really handy.

This approach is a multi-staged build. To perform such a build, create a new Dockerfile inside your hello-dock project directory and put the following content in it:
```bash
FROM node:lts-alpine as builder

WORKDIR /app

COPY ./package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine

EXPOSE 80

COPY --from=builder /app/dist /usr/share/nginx/html
```
As you can see the Dockerfile looks a lot like your previous ones with a few oddities. The explanation for this file is as follows:

Line 1 starts the first stage of the build using node:lts-alpine as the base image. The as builder syntax assigns a name to this stage so that it can be referred to later on.

From line 3 to line 9, it's standard stuff that you've seen many times before. The RUN npm run build command actually compiles the entire application and tucks it inside /app/dist directory where /app is the working directory and /dist is the default output directory for vite applications.

Line 11 starts the second stage of the build using nginx:stable-alpine as the base image.

The NGINX server runs on port 80 by default so the line EXPOSE 80 is added.

The last line is a COPY instruction. The --from=builder part indicates that you want to copy some files from the builder stage. After that it's a standard copy instruction where /app/dist is the source and /usr/share/nginx/html is the destination. The destination used here is the default site path for NGINX so any static file you put inside there will be automatically served.

As you can see, the resulting image is a nginx base image containing only the files necessary for running the application. To build this image execute the following command:
```bash
docker image build --tag hello-dock:prod .
```


Once the image has been built, you may run a new container by executing the following command:
```bash
docker container run \
    --rm \
    --detach \
    --name hello-dock-prod \
    --publish 8080:80 \
    hello-dock:prod
```


The running application should be available on http://127.0.0.1:8080:

Here you can see my hello-dock application in all its glory. Multi-staged builds can be very useful if you're building large applications with a lot of dependencies. If configured properly, images built in multiple stages can be very optimized and compact.