import docker
import logging

from docker.models.services import Service

from config.config import config


class DockerApi:

    def __init__(self):
        docker_base_url: str = config.get("DEFAULT", "docker_base_url")
        logging.info(f"Initialize docker client with base url: {docker_base_url}")
        self.__client = docker.DockerClient(base_url=docker_base_url)

    @staticmethod
    def __get_swarmkeeper_flag_from_label(service: Service) -> str:
        labels: dict = service.attrs.get("Spec")["Labels"]
        if "swarmkeeper.enable" in labels:
            if labels["swarmkeeper.enable"] == "true":
                return "Y"
            else:
                return "N"
        else:
            return "X"

    def get_image_digest_registry(self, image_tag: str) -> str:
        image_registry_data = self.__client.images.get_registry_data(image_tag)
        return image_registry_data.id

    def get_service_list(self) -> dict:
        logging.debug("Retrieve docker_service list")
        service_dict: dict = {}
        for service in self.__client.services.list():
            service_dict[service.id] = {"service_name": service.name,
                                        "image_tag": service.attrs.get("Spec")["Labels"]["com.docker.stack.image"],
                                        "image_digest": service.attrs.get("Spec")["TaskTemplate"]["ContainerSpec"]["Image"],
                                        "process_flag": self.__get_swarmkeeper_flag_from_label(service)}
        return service_dict

    def update_service_force(self, id_service: str):
        return self.__client.services.get(id_service).force_update()
