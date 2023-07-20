from queue import Queue
import logging
from docker_service.docker_api import DockerApi
from config.config import config


class DockerServiceMaintenance:

    def __init__(self, docker_api: DockerApi, task_queue: Queue):
        self.__docker_api: DockerApi = docker_api
        self.__task_queue: Queue = task_queue
        self.__service_ignore_list: list = config.get("DEFAULT", "service_ignore_list").split(" ")
        self.__namespace_ignore_list: list = config.get("DEFAULT", "namespace_ignore_list").split(" ")

    @staticmethod
    def __get_distinct_value_list(dictionary_list: list[dict], key) -> set:
        return {dictionary[key] for dictionary in dictionary_list if key in dictionary and dictionary[key]}

    def __process_service_container(self, container: dict, service: dict):
        image_digest_repository: str = self.__docker_api.get_image_digest_registry(service["image_tag"])
        if image_digest_repository in container["image_digest_list"]:
            logging.info(f"Container {container['name']} [{container['service_name']}] is using up to date image")
        else:
            logging.info(f"Container {container['name']} [{container['service_name']}] is using outdated image. Update of service is in progress ...")
            if self.__docker_api.update_service_force(container["id_service"]):
                logging.info(f"Update of service {service['service_name']} successfully finished")
            else:
                logging.error(f"Update of service {service['service_name']} failed!")

    def __process_container_list(self, container_list: list[dict]):
        service_id_list = self.__get_distinct_value_list(container_list, "id_service")
        service_dict = self.__docker_api.get_service_list(service_id_list)
        for container in container_list:
            if container["id_service"]:
                if self.__service_ignore_list and container["service_name"] in self.__service_ignore_list:
                    logging.info(f"Skip processing of container {container['name']} [{container['service_name']}], because it belongs to ignored service")
                elif self.__namespace_ignore_list and container["stack_namespace"] in self.__namespace_ignore_list:
                    logging.info(f"Skip processing of container {container['name']} [{container['service_name']}], because it belongs to ignored stack namespace {container['stack_namespace']}")
                else:
                    self.__process_service_container(container, service_dict[container["id_service"]])

    def process_queue(self):
        if self.__task_queue.qsize() > 0:
            logging.info(f"Processing queue. Queue size: {self.__task_queue.qsize()}")
            self.__process_container_list(self.__task_queue.get())
            self.__task_queue.task_done()
