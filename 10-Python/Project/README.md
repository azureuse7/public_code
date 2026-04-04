# Microservices in Python

A walkthrough for building a microservices application using Python and Flask, containerized with Docker, and deployed with Kubernetes and Helm.

Reference: [DevOps Made Easy - Microservices in Python](https://www.youtube.com/watch?v=SdTzwYmsgoU&ab_channel=DevOpsMadeEasy)

## Install Sample Flask Application

Reference: [Flask Installation - Python Version](https://flask.palletsprojects.com/en/3.0.x/installation/#python-version)

## Create an Environment

Create a project folder and a `.venv` folder within it:

```bash
# macOS/Linux
mkdir myproject
cd myproject
python3 -m venv .venv
```

```bash
# Windows
mkdir myproject
cd myproject
python -m venv .venv
```

## Activate the Environment

Before you work on your project, activate the corresponding environment:

```bash
# macOS/Linux
. .venv/bin/activate
```

Your shell prompt will change to show the name of the activated environment.

## Install Flask

Reference: [Flask Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart/)

Within the activated environment, use the following command to install Flask:

```bash
pip install Flask
```

## Python Application

Create `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

Add a health check endpoint that returns JSON:

```python
@app.route("/health")
def health():
    return jsonify(
        status="UP"
    )
```

Reload and rerun the app, then navigate to `<IP>:5000/health` to verify.

## Jinja Templating for Dynamic Web Pages

Reference: [Flask - Rendering Templates](https://flask.palletsprojects.com/en/3.0.x/quickstart/#rendering-templates)

Add a new folder named `templates` and create a template file inside it.

## Function to Fetch Hostname and IP

```python
import socket  # add this at line 2

def fetchDetails():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    return str(hostname), str(host_ip)

@app.route("/details")
def details():
    hostname, ip = fetchDetails()
    return render_template('index.html', HOSTNAME=hostname, IP=ip)
```

## Using pip to Freeze Python Dependencies

Freeze the current dependencies into a `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

To install from this file later:

```bash
pip install -r requirements.txt
```

## Building the Docker Image Using a Dockerfile

Build the Docker image:

```bash
docker build -t webapp:1.0 .
```

Run the container, mapping port `80` on the host to port `5000` on the container:

```bash
docker run -d -p 80:5000 --name web webapp:1.0
```

Check running containers:

```bash
docker ps
```

Use the master IP and open it in a browser to verify.

## Writing a Docker Compose File

Common Docker Compose commands:

```bash
docker compose build
docker compose up -d
docker compose down
```

## Writing Kubernetes Manifest Files

Apply all manifest files in the current directory:

```bash
kubectl apply -f ./
```

Then navigate to `<IP>:<port>` in a browser.

## Creating a Helm Chart

Create and render a Helm chart:

```bash
helm create webapp
helm template webapp
```
