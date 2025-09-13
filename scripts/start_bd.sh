#!/bin/bash

docker run --name postgres_db --network aurelius_net --env-file .env  -d -v aurelius_pgdata:/var/lib/postgresql/data postgres:17.6
