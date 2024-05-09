# How to Create Executable Docker Images


To begin with, open up the directory where you've cloned the repository that came with this book. The code for the rmbyext application resides inside the sub-directory with the same name.

#  In my opinion it should be like something like this:

- The image should have Python pre-installed.

- It should contain a copy of my rmbyext script.

- A working directory should be set where the script will be executed.

- The rmbyext script should be set as the entry-point so the image can take extension names as arguments.

- To build the above mentioned image, take the following steps:

- Get a good base image for running Python scripts, like python.

- Set-up the working directory to an easily accessible directory.

- Install Git so that the script can be installed from my GitHub repository.

- Install the script using Git and pip.

- Get rid of the build's unnecessary packages.

- Set rmbyext as the entry-point for this image.

Now create a new Dockerfile inside the rmbyext directory and put the following code in it:
```bash
FROM python:3-alpine

WORKDIR /zone

RUN apk add --no-cache git && \
    pip install git+https://github.com/fhsinchy/rmbyext.git#egg=rmbyext && \
    apk del git

ENTRYPOINT [ "rmbyext" ]
```
The explanation for the instructions in this file is as follows:

The FROM instruction sets python as the base image, making an ideal environment for running Python scripts. The 3-alpine tag indicates that you want the Alpine variant of Python 3.

The WORKDIR instruction sets the default working directory to /zone here. The name of the working directory is completely random here. I found zone to be a fitting name, you may use anything you want.

Given the rmbyext script is installed from GitHub, git is an install time dependency. The RUN instruction on line 5 installs git then installs the rmbyext script using Git and pip. It also gets rid of git afterwards.

Finally on line 9, the ENTRYPOINT instruction sets the rmbyext script as the entry-point for this image.

In this entire file, line 9 is the magic that turns this seemingly normal image into an executable one. Now to build the image you can execute following command:
```bash
docker image build --tag rmbyext .

docker image ls
```


Here I haven't provided any tag after the image name, so the image has been tagged as latest by default. You should be able to run the image as you saw in the previous section. Remember to refer to the actual image name you've set, instead of fhsinchy/rmbyext here.