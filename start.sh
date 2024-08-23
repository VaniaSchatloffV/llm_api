docker build -t api_image .
docker rm api
docker run -p 8007:8007 -v C:/Users/Cototo/Desktop/u/llm_api:/app --env-file .env --name api --network mynetwork api_image