# pip install kubernetes
from kubernetes import client, config
config.kube_config.load_kube_config(config_file="./kubernetes.yaml")
#获取API的CoreV1Api版本对象
v1 = client.CoreV1Api()

# 列出k8s集群中所有的名称空间
ret = v1.list_namespace()
for i in ret.items: 
    print(i.metadata.name) 

# 列出k8s集群中所有的service
ret = v1.list_service_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s 	%s 	%s 	%s 	%s" % (i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports ))

#列出所有的pod
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
