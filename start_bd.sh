
docker run --name postgres_bd -e POSTGRES_PASSWORD=mysecretpassword -d -v aurelius_pgdata:/var/lib/postgresql/data postgres:17.6
