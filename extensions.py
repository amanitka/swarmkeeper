from queue import Queue

from docker_api import DockerApi
from docker_service_maintenance import DockerServiceMaintenance

# Initiate DockerApi
docker_api = DockerApi()
# Initiate work queue
task_queue = Queue()
# Initialize docker service maintenance
docker_service_maintenance = DockerServiceMaintenance(docker_api, task_queue)
