#!/bin/bash

docker run --name postgres_db --network aurelius_net -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=Aurelius -e POSTGRES_DB=AureliusDB  -d -v aurelius_pgdata:/var/lib/postgresql/data postgres:17.6
