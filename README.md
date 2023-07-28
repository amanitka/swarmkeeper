# Swarmkeeper
Simple application for maintenance of docker services in docker swarm mode. In order to work it needs to receive information from all the nodes in the swarm, for that purpose it is using "sidekick"
service [Swarmkeeper Agent](https://github.com/amanitka/swarmkeeper-agent).

Swarmkeeper Agent periodically reports container status to Swarmkeeper. Base on provided data, swarmkeeper checks whether the service container is using up-to-date image, if not it will update it.

If enabled Swarmkeeper Agent can clean up stopped containers and unused images.

## Usage
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
      labels:
        - "swarmkeeper.enable=false"
        
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
    networks:
      - mon_network
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: 
          - node.role == manager  
      labels:
        - "swarmkeeper.enable=false"
```

## Configuration
### Swarmkeeper
#### Environment variables:
- `DOCKER_BASE_URL` - by default it is using docker sock *unix://var/run/docker.sock*, but it can be overwritten to use SSH or TCP access to docker
- `SERVICE_IGNORE_LIST` - list of docker service divided by space which should be ignored, for example *"SERVICE_IGNORE_LIST=service1 service2"*

#### Labels
It is also possible to exclude services from processing via lables. Just include label `"swarmkeeper.enable=false"` on service level.

### Swarmkeeper Agent
Environment variables:
- `DOCKER_BASE_URL` - by default it is using docker sock *unix://var/run/docker.sock*, but it can be overwritten to use SSH or TCP access to docker
- `SWARMKEEPER_URL` - http://service-name:5090 -> http://swarmkeeper:5090
- `REPORT_CRON_SCHEDULE` - schedule for reporting of service container status to swarmkeeper. It is defined as cron schedule, for example 0 0 4 * * *
- `CLEANUP_CRON_SCHEDULE` - schedule for cleanup of stopped containers or unused images. It is defined as cron schedule, for example 0 0 6 * * *
- `CONTAINER_CLEANUP` - True - enable container cleanup, False - disable container cleanup
- `IMAGE_CLEANUP` - True - enable image cleanup, False - disable image cleanup
