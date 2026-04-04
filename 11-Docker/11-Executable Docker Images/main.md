# How to Create Executable Docker Images

An executable Docker image is one where the `ENTRYPOINT` is set to a custom program rather than a shell. This allows you to run the container like a command-line tool, passing arguments directly to the program.

## Design Plan for the Image

The image for the `rmbyext` script should be designed as follows:

- Have Python pre-installed.
- Contain a copy of the `rmbyext` script.
- Have a working directory set where the script will be executed.
- Have `rmbyext` set as the entry-point so the image can accept file extension names as arguments.

To build this image, take the following steps:

1. Get a good base image for running Python scripts, like `python`.
2. Set up the working directory to an easily accessible directory.
3. Install Git so the script can be installed from a GitHub repository.
4. Install the script using Git and `pip`.
5. Remove the build-only packages.
6. Set `rmbyext` as the entry-point for this image.

## Writing the Dockerfile

Create a new `Dockerfile` inside the `rmbyext` directory with the following content:

```dockerfile
FROM python:3-alpine

WORKDIR /zone

RUN apk add --no-cache git && \
    pip install git+https://github.com/fhsinchy/rmbyext.git#egg=rmbyext && \
    apk del git

ENTRYPOINT [ "rmbyext" ]
```

### Explanation of Instructions

- **FROM** sets `python:3-alpine` as the base image, providing an ideal environment for running Python scripts. The `3-alpine` tag indicates the Alpine variant of Python 3.
- **WORKDIR** sets the default working directory to `/zone`. The name of the working directory is arbitrary; `zone` is simply a fitting choice here.
- **RUN** installs `git` (needed to install the script from GitHub), installs `rmbyext` using `pip`, and then removes `git` to keep the image lean.
- **ENTRYPOINT** sets `rmbyext` as the entry-point for the image. This is what makes the image executable — anything written after the image name in a `docker container run` command gets passed as arguments to `rmbyext`.

## Building and Verifying the Image

Build the image:

```bash
docker image build --tag rmbyext .

docker image ls
```

No tag was provided after the image name, so the image is tagged as `latest` by default. You should now be able to run the image as described in the previous section. Remember to use the actual image name you set, instead of `fhsinchy/rmbyext`.
