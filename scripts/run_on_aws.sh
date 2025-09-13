docker stop aurelius
docker rm aurelius

cd Aurelius
git pull

./scripts/build_bot_container.sh
./scripts/run_bot_container.sh