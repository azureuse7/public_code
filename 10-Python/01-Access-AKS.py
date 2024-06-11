#You will need to have config locally 

# Listing pods with their IP
# Craete cluster 
from kubernetes import client, config
config.load_kube_config()
v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)



# Listing pods with their IP using the function
from kubernetes import client, config
config.load_kube_config()
def namespace():
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
namespace()



# Uisng utilis to create yaml file in python
from kubernetes import client, config, utils
def step_impl():
    """Step."""
    k8s_client = client.ApiClient()
    utils.create_from_yaml(k8s_client, "calico-test.yaml")
step_impl()



# Using  os to output value of home
import os
key = 'HOME'
value = os.getenv(key)
print("Value of 'HOME' environment variable :", value) 


# List pods in namespace examplekured
from kubernetes import config, client
config.load_kube_config()
def namespace():
    v1 = client.CoreV1Api()
    result = v1.list_namespaced_pod(namespace="kube-system",watch=False)
    for i in result.items:
        print(i.metadata.name, i.status.pod_ip )
        # print(result.items )
namespace()



# Create a service account
def create_service_account(namespace, service_account_name):
    """Create K8s Service Account."""
    try:
        body = client.V1ServiceAccount()
        body.metadata = client.V1ObjectMeta(name=service_account_name)
        v1.create_namespaced_service_account(namespace, body)
    except Exception as err:
        print(err)
create_service_account("default", "servicename1")