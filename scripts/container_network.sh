#Need so the container with the bot can run and connect to the database container
#!/bin/bash

docker network create aurelius_net
docker network connect aurelius_net postgres_db
docker network connect aurelius_net aurelius-devcontainer
