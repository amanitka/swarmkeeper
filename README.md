# Swarmkeeper
Simple application for maintenance of docker services in docker swarm mode. In order to work it needs to receive information from all the nodes in the swarm, for that purpose it is using "sidekick"
service [Swarmkeeper Agent](https://github.com/amanitka/swarmkeeper-agent).

Swarmkeeper Agent periodically reports container status to Swarmkeeper. Base on provided data, swarmkeeper checks whether the service container is using up-to-date image, if not it will update it.

If enabled Swarmkeeper Agent also can clean up stopped containers and unused images.

#### Example of usage
```
version: "3.8"

services:

  # Swarmkeeper agent
  swarmkeeper_agent:
    image: amanitka/swarmkeeper-agent:latest
    user: worker:${DOCKER_GROUP}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TZ=${TIMEZONE}
      - SWARMKEEPER_URL=http://swarmkeeper:5090
      - "REPORT_CRON_SCHEDULE=0 0 4 * * *"
      - "CLEANUP_CRON_SCHEDULE=0 0 6 * * *"
      - CONTAINER_CLEANUP=True
      - IMAGE_CLEANUP=True
    networks:
      - mon_network
    deploy:
      mode: global
      placement:
        constraints: 
          - node.platform.os == linux
  
  # Swarmkeeper
  swarmkeeper:
    image: amanitka/swarmkeeper:latest
    user: worker:${DOCKER_GROUP}
    ports:
      - 5090:5090
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TZ=${TIMEZONE} 
      - "NAMESPACE_IGNORE_LIST=proxy mon"
    networks:
      - mon_network
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: 
          - node.role == manager  
```