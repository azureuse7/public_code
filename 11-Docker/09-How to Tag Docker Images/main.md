# How to Tag Docker Images

Tags make it easy to identify and manage specific versions of a Docker image. You can assign a tag at build time or add/change a tag afterwards.

## Tagging an Image at Build Time

Use the `--tag` option with `docker image build` to assign a name and tag in one step:

```bash
docker image build --tag custom-nginx:packaged .
```

You can now refer to your image as `custom-nginx:packaged`.

## Tagging an Existing Image

If you forgot to tag an image during the build, or want to change the tag, use the `docker image tag` command:

```bash
docker image tag <image id> <image repository>:<image tag>

## or ##

docker image tag <image repository>:<image tag> <new image repository>:<new image tag>
```
