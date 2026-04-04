# How to Perform Multi-Staged Builds in Docker

A multi-staged build uses multiple `FROM` instructions in a single `Dockerfile`, allowing you to copy artifacts from one build stage into another. This keeps the final image small by discarding everything that was only needed during the build.

## Why Use Multi-Stage Builds?

To create an image where a JavaScript application runs in production mode, you could:

- Use `node` as the base image and build the application.
- Install NGINX inside the `node` image and use it to serve the static files.

This approach is valid, but the `node` image is large and most of its contents are unnecessary just to serve static files. A better approach is:

1. Use the `node` image as the base and build the application.
2. Copy the built files from the `node` stage into an `nginx` image.
3. Create the final image based on `nginx` and discard all Node.js-related content.

This results in a much smaller and more focused image.

## Writing the Multi-Stage Dockerfile

Create a new `Dockerfile` inside your `hello-dock` project directory with the following content:

```dockerfile
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

### Explanation

- **Line 1** starts the first build stage using `node:lts-alpine` as the base image. The `as builder` syntax assigns a name to this stage so it can be referenced later.
- **Lines 3–9** are standard setup steps. The `RUN npm run build` command compiles the entire application and outputs it to the `/app/dist` directory (the default output directory for Vite applications).
- **Line 11** starts the second build stage using `nginx:stable-alpine` as the base image.
- **`EXPOSE 80`** documents the port the NGINX server listens on.
- The final **COPY** instruction uses `--from=builder` to copy files from the first stage. `/app/dist` is the source and `/usr/share/nginx/html` is the destination — the default site path for NGINX, so any static files placed there are automatically served.

## Building the Production Image

```bash
docker image build --tag hello-dock:prod .
```

## Running the Production Container

```bash
docker container run \
    --rm \
    --detach \
    --name hello-dock-prod \
    --publish 8080:80 \
    hello-dock:prod
```

The running application should be available at `http://127.0.0.1:8080`.

Multi-staged builds are very useful when building large applications with many dependencies. When configured properly, the resulting image contains only what is needed to run the application, making it compact and efficient.
