from queue import Queue
import logging
from docker_api import DockerApi


class DockerServiceMaintenance:

    def __init__(self, docker_api: DockerApi, task_queue: Queue):
        self.__docker_api = docker_api
        self.__task_queue = task_queue

    @staticmethod
    def __get_distinct_value_list(dictionary_list: list[dict], key) -> set:
        return {dictionary[key] for dictionary in dictionary_list if key in dictionary and dictionary[key]}

    def __process_service_container(self, container: dict, service_dict: dict):
        service: dict = service_dict[container["id_service"]]
        if service["image_digest_repo"] in container["image_digest_list"]:
            logging.info(f"Service {service['service_name']} is using up to date image")
        else:
            logging.info(f"Service {service['service_name']} is using outdated image. Update of service is in progress ...")
            if self.__docker_api.update_service_force(container["id_service"]):
                logging.info(f"Update of service {service['service_name']} successfully finished")
            else:
                logging.error(f"Update of service {service['service_name']} failed!")

    def __process_container_list(self, container_list: list[dict]):
        service_id_list = self.__get_distinct_value_list(container_list, "id_service")
        service_dict = self.__docker_api.get_service_list(service_id_list)
        for container in container_list:
            if container["id_service"]:
                self.__process_service_container(container, service_dict)

    def process_queue(self):
        if self.__task_queue.qsize() > 0:
            logging.info(f"Processing queue. Queue size: {self.__task_queue.qsize()}")
            self.__process_container_list(self.__task_queue.get())
            self.__task_queue.task_done()
