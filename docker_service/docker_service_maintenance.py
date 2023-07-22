from queue import Queue
import logging
from docker_service.docker_api import DockerApi
from config.config import config


class DockerServiceMaintenance:

    def __init__(self, docker_api: DockerApi, task_queue: Queue):
        self.__docker_api: DockerApi = docker_api
        self.__task_queue: Queue = task_queue
        self.__service_ignore_list: list = config.get("DEFAULT", "service_ignore_list").split(" ")

    def __can_process_service_container(self, container: dict, service: dict) -> bool:
        if service["process_flag"] == "N":
            logging.info(f"Skip processing of container {container['name']} [Service {container['service_name']}], because it was disabled by service label")
            return False
        elif self.__service_ignore_list and container["service_name"] in self.__service_ignore_list:
            logging.info(f"Skip processing of container {container['name']} [Service {container['service_name']}], because it belongs to ignored service")
            return False
        else:
            return True

    def __process_service_container(self, container: dict, service: dict):
        if self.__can_process_service_container(container, service):
            image_digest_repository: str = self.__docker_api.get_image_digest_registry(service["image_tag"])
            if image_digest_repository in container["image_digest_list"]:
                logging.info(f"Container {container['name']} [{container['service_name']}] is using up to date image")
            else:
                logging.info(f"Container {container['name']} [{container['service_name']}] is using outdated image. Update of service is in progress ...")
                if self.__docker_api.update_service_force(container["id_service"]):
                    logging.info(f"Update of service {service['service_name']} successfully finished")
                else:
                    logging.error(f"Update of service {service['service_name']} failed!")

    def __process_service_container_list(self, service_container_list: list[dict]):
        service_dict = self.__docker_api.get_service_list()
        for service_container in service_container_list:
            self.__process_service_container(service_container, service_dict[service_container["id_service"]])

    def process_queue(self):
        if self.__task_queue.qsize() > 0:
            logging.info(f"Processing queue. Queue size: {self.__task_queue.qsize()}")
            self.__process_service_container_list(self.__task_queue.get())
            self.__task_queue.task_done()
