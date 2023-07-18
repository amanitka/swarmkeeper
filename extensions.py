import configparser
import os
from queue import Queue

from docker_api import DockerApi
from docker_service_maintenance import DockerServiceMaintenance

# Initiate config parser
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
# Initiate DockerApi
docker_api = DockerApi(config.get("DEFAULT", "docker_base_url", fallback="unix://var/run/docker.sock", vars=os.environ))
# Initiate work queue
task_queue = Queue()
# Initialize docker service maintenance
docker_service_maintenance = DockerServiceMaintenance(docker_api, task_queue)
