###  Seccomp
With Seccomp, you can restrict container process calls made from pods to kernel.

Enable at Kubelet

- SECCOMP profile should be placed at /var/lib/kubelet/seccomp/profiles.json

- SECCOMP Profiles are 3 types

## Default Profile

- Audit -      audit.json.              → "defaultAction": "SCMP_ACT_LOG"--> Give me logs

- Violation-   violation.json.        → action": "SCMP_ACT_ERRNO"

- Custom -  fine-grained.json, ->  we can use both Allow and Error 

## SECCOMP profile action can be

- "action":        "SCMP_ACT_ALLOW"

- "action":        "SCMP_ACT_ERRNO"

- "defaultAction": "SCMP_ACT_LOG"


seccomp profile "/var/lib/kubelet/seccomp/profiles/violation.json

1)K get nodes

2)k get podes

3)ssh in node

4)sudo su 

5)system status kubelet 

6)Create a seccomp filter named /var/lib/kubelet/seccomp/profile

7)mkdir -p seccomp profile "/var/lib/kubelet/seccomp/profiles/

8)vim <profile.json>

ls 

 

Deploy a pod 

k apply -f main.yaml 


```t
apiVersion: v1
kind: Pod
metadata:
  name: violation-pod7
  labels:
    app: violation-pod3
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/violation.json
  containers:
  - name: test-container
    image: hashicorp/http-echo:0.2.3
    args:
    - "-text=just made some syscalls!"
    securityContext:
      allowPrivilegeEscalation: false
 ```

To test Audit 

Now this Pod is making audit call sing profile audit.json 

to view the, worker nodes: tail -f /var/log/syslog 

Create a service on that pod 

access the pod 

<IP>30040

curl 

you can see its made sys calls 
