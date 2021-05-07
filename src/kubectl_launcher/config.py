import yaml
import logging
from kubectl_launcher.exceptions import KubectlLauncherYamlException

log = logging.getLogger(__name__)

class Config:
    kubectl_servers = []
    servers = []
    deployments = []
    services = []
    persistentVolumes = []

    def __init__(self,file_yaml):
        try:
            config_yaml = yaml.safe_load(file_yaml)
            self.__dict__.update(config_yaml)
            log.info(f"Config {file_yaml.name} successful download")
        except yaml.YAMLError as e:
            raise KubectlLauncherYamlException("YAMLError bad parse  file.")