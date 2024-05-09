# microservices-in-python
https://www.youtube.com/watch?v=SdTzwYmsgoU&ab_channel=DevOpsMadeEasy


- Install Sample Flask Application --> https://flask.palletsprojects.com/en/3.0.x/installation/#python-version
# Create an environment

Create a project folder and a .venv folder within:
```t
macOS/LinuxWindows
$ mkdir myproject
$ cd myproject
$ python3 -m venv .venv
```
# Activate the environment
Before you work on your project, activate the corresponding environment:
```t
macOS/LinuxWindows
$ . .venv/bin/activate
```
Your shell prompt will change to show the name of the activated environment.

# Install Flask
https://flask.palletsprojects.com/en/3.0.x/quickstart/
Within the activated environment, use the following command to install Flask:
```t
$ pip install Flask
```
# Python Application
Create app.py
```t
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

Add health check and return as josn 
```t
@app.route("/health")
def health():
    return jsonify(
        status="UP"
    )
```
Reload and rerun and now try <IP>:5000/health

# Jinja templating for Dynamic Web Pages
- https://flask.palletsprojects.com/en/3.0.x/quickstart/#rendering-templates
- Add a new folder as temples and create a file
# Function to fetch hostname and ip 
```t
# import socket (line 2)

def fetchDetails():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    return str(hostname), str(host_ip)

@app.route("/details")
def details():
    hostname, ip = fetchDetails()
    return render_template('index.html', HOSTNAME=hostname, IP=ip)
```

# Using Pip to Freeze Python Dependencies
- pip freeze > requirements.txt
- let move it out side in the folder
- To use it pip install -r requirements.txt
 
# Building the docker image using Dockerfile
  
# Writing Docker Compose file
- Install a cluster
- Write docker file 
- docker build -t webapp:1.0 .
- then run 
- docker run -d -p 80:5000 --name web webapp:1:0
- -p port mapping on host 80 to port on conatine that is 5000 and name it as web and the image name is  webapp:1.0
- docker ps
- use master ip and try on browser 

# docker compose
Docker compose build 
docker compose up -d 
docker compose down

# Writing Kubernetes Manifest files for the application
k apply -f ./
<ip>port number

# Creating Helm Chart
helm ceate webapp--> This creates helm files
helm template webapp --> rende it 