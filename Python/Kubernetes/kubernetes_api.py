# 
# pip install kubernetes
from kubernetes import client, config
config.kube_config.load_kube_config(config_file="./kubernetes.yaml")

#获取API的CoreV1Api版本对象
v1 = client.CoreV1Api()

#列出所有的pod
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
