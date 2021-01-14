
# python操作k8s api
# pip install kubernetes
# kubectl describe secret/$(kubectl get secret -nkube-system |grep admin|awk '{print $1}') -nkube-system

from kubernetes import client, config
import os
import sys

class Helm_RollBack():
    """
        蓝鲸平台流程回滚阶段
    """
    def __init__(self, app_version):
        self.namespace_all = ['default', 'test', 'beat', 'rc', 'prod', 'monitoring']
        if app_version == "default":
            self.namespace = self.namespace_all[0]
        elif app_version == "test":
            self.namespace = self.namespace_all[1]
        elif app_version == "beta":
            self.namespace = self.namespace_all[2]
        elif app_version == "rc":
            self.namespace = self.namespace_all[3]
        elif app_version == "prod":
            self.namespace = self.namespace_all[4]
        else:
            self.namespace = self.namespace_all[5]

        # 列出Pod是记录信息
        self.applists = []

    def k8s_conn(self):
        # self.config_path = config.kube_config.load_kube_config(config_file=config_path)
        #获取API的CoreV1Api版本对象
        # self.v1 = client.CoreV1Api()
        Token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlRDM2hwNlM1ak1vUDZ2NjFtNDB4cEIzT0NlRDZzVmxPSFZiYzlqOEdXQzAifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLTV4bGtiIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI4NWZiMDMyZC05ZTI2LTRjMDgtOGY2Yi0yNDIwZGMxMTA5NDkiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.JqaGNnGflGQE7ENiXL9JFtwcBcS1PS3-JGmJX7bdStLm6fNENmtKXIa2L5RM8hzX3zwGZEkw3jKX1Ult6ug7e_EU5yXsP0BZ6lNhowfu6C0vYbEX4o-lJV2sX7DHFp9_-urmtjBeXHaf88J3vJ_Fbg8Yv_5Mfk3cCC0yiRZ7EAAUp7d8H2bjVPIvtGSkxFK4WrL0cj0lsrQZg7vgxDbclJJVCpWDDz8NLINjqURpqpfWGo0ABTwYQ_bV8tdXt9hTPAfVDXNTJYm4cHhP-fDQKjkUH-PGzmo56_e-aT24faIOQQEEefgQPw88ScUGY8UgXdfMXTv_tPJj-A588VSmMg"  
        APISERVER = 'https://127.0.0.1:6443'
        configuration = client.Configuration()
        configuration.host = APISERVER
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + Token}
        client.Configuration.set_default(configuration)
        conn = client.CoreV1Api()
        return conn
    
    # 列出所有的namespace
    def list_all_ns(self):
        conn = self.k8s_conn()
        for ns in conn.list_namespace().items:
            print(ns.metadata.name)

    # 列出所有的pod
    def list_allns_pods(self):
        conn = self.k8s_conn()    
        ret = conn.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    # 列出指定ns下的所有pod
    def list_ns_pods(self):
        conn = self.k8s_conn()  
        ret = conn.list_namespaced_pod(self.namespace)
        for i in ret.items:
            # print(ret)
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            # print({"ip":i.status.pod_ip, "namespace":i.metadata.namespace, "name":i.metadata.name})

    # 获取指定Pod中的日志
    # def list_pods_log(self):
    #     log_content = corev1api.read_namespaced_pod_log('redis-master-fsx46', 'default', pretty=True, tail_lines=200, container='redis-server')


    # 列出所有deployment
    def list_allns_deployment(self):
        config.kube_config.load_kube_config(config_file='./kubernetes.yaml')
        v1_deployment = client.AppsV1Api()
        ret = v1_deployment.list_deployment_for_all_namespaces(watch=False)
        # print(ret)
        for dep in ret.items:
            dep_info = {}
            dep_info['dep'] = dep.metadata.name
            dep_info['depns'] = dep.metadata.namespace
            dep_info['deprep'] = dep.spec.replicas
            self.applists.append(dep_info)
            print(self.applists)
    
    # 列出所有名称空间下的deployment
    def list_ns_deployment(self):
        config.kube_config.load_kube_config(config_file='./kubernetes.yaml')
        v1_deployment = client.AppsV1Api()
        ret = v1_deployment.list_namespaced_deployment(self.namespace)
        # print(ret)
        for dep in ret.items:
            dep_info = {}
            dep_info['dep'] = dep.metadata.name
            dep_info['depns'] = dep.metadata.namespace
            dep_info['deprep'] = dep.spec.replicas
            self.applists.append(dep_info)
            # print(self.applists)

    # 列出所有名称空间下的deployment
    def list_allns_deployment(self):
        config.kube_config.load_kube_config(config_file='./kubernetes.yaml')
        v1_deployment = client.AppsV1Api()
        ret = v1_deployment.list_deployment_for_all_namespaces(watch=False)
        # print(ret)
        for dep in ret.items:
            dep_info = {}
            dep_info['dep'] = dep.metadata.name
            dep_info['depns'] = dep.metadata.namespace
            dep_info['deprep'] = dep.spec.replicas
            self.applists.append(dep_info)
            # print(self.applists)
        # return dep_info['dep']

    # helm 回滚
    def helm_rollback(self, app_name):
        try:
            deployment_list = self.list_ns_deployment()
            # print('----' * 10)
            # print(self.applists)
            for i in self.applists:
                # app_name = self.applists[0]['dep']
                # print(i['dep'])
                if i['dep'] == str(app_name):
                    print("helm rollback {}".format(app_name))
                    break
            # print(deployment_list)
        except Exception as e:
            print('error info {}'.format(e))

if __name__ == "__main__":
    # 列出集群中所有的ns
    # Kubernetes.list_all_ns()

    # 列出所有名称空间下的pods
    # Kubernetes.list_allns_pods()

    # 列出指定ns下的所有pod
    # Kubernetes.list_ns_pods()

    # 列出所有deployment
    #  Kubernetes.list_allns_deployment()

    # 列出指定ns下的deployment
    # Kubernetes.list_ns_deployment()

    # 回滚
    # Kubernetes.helm_rollback(app_name=app_name)

    if sys.argv[1] == "rollback":
        # 所需要的变量
        app_stage = sys.argv[2]   # 1、名称空间 app_stage = "monitoring"
        app_name = sys.argv[3]    # 2、deployment部署名称 app_name = "kafka-exporter"
        print(app_stage, app_name)
        # config_path = os.path.join('./kubernetes.yaml')
        # Kubernetes = Helm_RollBack(app_stage)

        # 回滚操作
        # Kubernetes.helm_rollback(app_name=app_name)
    else:
        print("error")


