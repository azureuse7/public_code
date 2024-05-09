https://www.youtube.com/watch?v=MDVEoGLDOh8&list=WL&index=35&t=4s

1) Fisrt we create a pod and test it 


apiVersion: v1
kind: Pod
metadata:
  name: demo-sidecar
  containers:
  - name: main-container
    image: iam7hills/dockerdemo:nginxdemos
    ports:
      - containerPort: 8080

1) Add the rest of code and now it could ick file from side container 

Create another conatiner 



apiVersion: v1
kind: Pod
metadata:
  name: demo-sidecar
  containers:
  - name: main-container
    image: iam7hills/dockerdemo:nginxdemos
    ports:
      - containerPort: 8080
  - name: sidecar-container
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo 'index.html generated from sidecar' > /usr/share/nginx/html/index.html; sleep 30; done"]


But nothing work, bevuas we need to mount a vilume
at prset we onlu jhae two conatine in a pod


k exec -it <pod> --conatiner<name>
/bin/sh

look for the file ls -lrt //usr/share/nginx/html/index.html
cat /proc/mount
cat /proc/mount | nginix
its not there becuase we need to mount a vilume

  volumes:
  - name: shared-html name of volume
    emptyDir: {}  This is the deafult volume by kubnernest


now e need to attcah them to the conatiners
    volumeMounts:
    - name: shared-html
      mountPath: /usr/share/nginx/html


apply and try now 
tyhe hmt should be different 