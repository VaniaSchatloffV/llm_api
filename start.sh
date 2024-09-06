docker build -t api_image .
docker rm api
docker run -p 8007:8007 -v $(pwd):/app --env-file .env --name api --network mynetwork api_image