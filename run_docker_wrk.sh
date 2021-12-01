echo killing old docker processes
docker-compose rm -fs

echo building docker containers
docker-compose -f docker-compose-wrk.yml up --build -d