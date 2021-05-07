from kubernetes import client, config
import logging
from kubectl_launcher.exceptions import KubectlLauncherInvalidConfig, KubectlLauncherYamlException
from kubectl_launcher.config import Config
from kubectl_launcher.api import InitData
from urllib3.connectionpool import MaxRetryError
import yaml
import json

log = logging.getLogger(__name__)


class KubectlServer:
    def __init__(self, host, port, verify_ssl, ssl_ca_cet, name):
        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.ssl_ca_cert = ssl_ca_cet
        self.name = name

    @classmethod
    def parse(cls, server: dict):
        try:
            return cls(
                server['host'],
                server['port'],
                server['verify_ssl'],
                server['ssl_ca_cert'] if server['verify_ssl'] else None,
                server['name']
            )
        except KeyError as e:
            raise KubectlLauncherYamlException(f"A required key in server was not found in the config. {e}")


class KubectlWorker:
    def __init__(self, kubectl_server):
        try:
            self.kubectl_server = kubectl_server
            self.init_client()
        except config.ConfigException:
            raise KubectlLauncherInvalidConfig("Invalid kube-config file.")

    def init_client(self):
        aConfiguration = client.Configuration()
        aConfiguration.host = f"{self.kubectl_server.host}:{self.kubectl_server.port}"
        aConfiguration.verify_ssl = self.kubectl_server.verify_ssl
        if self.kubectl_server.verify_ssl:
            aConfiguration.ssl_ca_cert = self.kubectl_server.ssl_ca_cert
        self.aApiClient = client.ApiClient(aConfiguration)

    def create_service(self,service,namespace):
        k8s_apps_v1 = client.CoreV1Api(self.aApiClient)
        return k8s_apps_v1.create_namespaced_service(
            body=service, namespace=namespace)

    def create_deployment(self,deployment,namespace):
        k8s_apps_v1 = client.AppsV1Api(self.aApiClient)
        return k8s_apps_v1.create_namespaced_deployment(
            body=deployment, namespace=namespace)

    def create_pvc(self,pvc,namespace):
        k8s_apps_v1 = client.CoreV1Api(self.aApiClient)
        return k8s_apps_v1.create_namespaced_persistent_volume_claim(
            body=pvc, namespace=namespace)

    def create_kind(self, filename,kind_name,namespace="default"):
        results = []
        try:
            with open(filename) as f:
                kinds = yaml.safe_load_all(f)
                try:
                    for kind in kinds:
                        if kind_name == 'Service': resp = self.create_service(kind,namespace)
                        if kind_name == 'Deployment': resp = self.create_deployment(kind, namespace)
                        if kind_name == 'PersistentVolumes': resp = self.create_pvc(kind, namespace)
                        log.info("%s %s created" % (kind_name,resp.metadata.name))
                        results.append(KubectlResult.generate(filename, kind_name, namespace, self.kubectl_server, resp=resp))
                except MaxRetryError as e:
                    log.info(f"Connection to server {self.kubectl_server.host}:{self.kubectl_server.port} is bad.")
                    results.append(KubectlResult.generate(filename, kind_name, namespace, self.kubectl_server, max_retries=True))
        except client.exceptions.ApiException as e:
            resp = json.loads(e.body)
            results.append(KubectlResult.generate(filename, kind_name, namespace, self.kubectl_server, api_exception=True,resp=resp))
            log.info(f"Error connection with kubernetes API. Error: {resp['message']}")
        return results


class KubectlLauncher:
    def __init__(self, config: Config, data: InitData):
        self.config = config
        self.data = data
        self.__results = []

    def run(self):
        log.info("Starting the creation of kinds in kubectl")
        for server in self.config.kubectl_servers:
            kubectl_server = KubectlServer.parse(server)
            try:
                kw = KubectlWorker(kubectl_server)
                for deployment in self.config.deployments:
                    if {'name' : server['name']} in deployment['servers']:
                        result = kw.create_kind(deployment['filename'], 'Deployment' ,deployment['namespace'])
                        self.__result_append(result)
                for service in self.config.services:
                    if {'name': server['name']} in service['servers']:
                        result = kw.create_kind(service['filename'], 'Service' ,service['namespace'])
                        self.__result_append(result)
                for volume in self.config.persistentVolumes:
                    if {'name': server['name']} in volume['servers']:
                        result = kw.create_kind(volume['filename'], 'PersistentVolumes' ,volume['namespace'])
                        self.__result_append(result)
            except KeyError as e:
                raise KubectlLauncherYamlException(f"A required key in kind was not found in the config. {e}")
        log.info("Finish the creation of kinds in kubectl")

    def __result_append(self, results):
        for result in results:
            self.__results.append(result.__dict__['result'])

    @property
    def all_results(self):
        return self.__results

    @all_results.getter
    def all_results(self):
        return self.__results


class KubectlResult:
    def __init__(self, result):
        self.result = result

    @classmethod
    def generate(cls, filename, kind, namespace, server, *,
                 resp=None, max_retries=False, api_exception=False):
        result = {
            'kind': kind,
            'filename': filename,
            'namespace': namespace,
            'creation_timestamp': None,
            'cluster_name': None,
            'server_host': server.host,
            'server_port': server.port,
        }
        if api_exception:
            result.update({
                'status': resp['message'],
            })
        elif resp != None:
            result.update({
                'kind': resp.kind,
                'status': 'successful create',
                'name': resp.metadata.name,
                'namespace': resp.metadata.namespace,
                'creation_timestamp': str(resp.metadata.creation_timestamp),
                'cluster_name': resp.metadata.cluster_name
            })
        elif max_retries:
            result.update({
                'status': 'Failed to connect to Kubernetes.',
            })

        return cls(result)
