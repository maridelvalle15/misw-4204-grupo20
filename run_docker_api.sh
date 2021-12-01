echo killing old docker processes
docker-compose rm -fs

echo building docker containers
docker-compose -f docker-compose-api.yml up --build -d