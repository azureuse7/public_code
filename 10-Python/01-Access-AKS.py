from kubernetes import client, config, utils
import os

config.load_kube_config()

v1 = client.CoreV1Api()

# List all pods across all namespaces with their IPs
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


# List pods in a specific namespace
def list_pods_in_namespace():
    result = v1.list_namespaced_pod(namespace="kube-system", watch=False)
    for i in result.items:
        print(i.metadata.name, i.status.pod_ip)

list_pods_in_namespace()


# Create resources from a YAML file
def apply_yaml():
    k8s_client = client.ApiClient()
    utils.create_from_yaml(k8s_client, "calico-test.yaml")

apply_yaml()


# Read an environment variable
key = 'HOME'
value = os.getenv(key)
print("Value of 'HOME' environment variable :", value)


# Create a service account
def create_service_account(namespace, service_account_name):
    try:
        body = client.V1ServiceAccount()
        body.metadata = client.V1ObjectMeta(name=service_account_name)
        v1.create_namespaced_service_account(namespace, body)
    except Exception as err:
        print(err)

create_service_account("default", "servicename1")
