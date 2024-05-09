How to Tag Docker Images
```bash
docker image build --tag custom-nginx:packaged .
```
you can now refer to your image as custom-nginx:packaged 

In cases where you forgot to tag an image during build time, or maybe you want to change the tag, you can use the image tag command to do that:
```bash
docker image tag <image id> <image repository>:<image tag>

## or ##

docker image tag <image repository>:<image tag> <new image repository>:<new image tag>
```