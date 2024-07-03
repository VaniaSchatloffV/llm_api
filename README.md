# llm_api
Api para interactuar con llm en bedrock


docker build -t api_image .
docker run -p 8007:8007 -v $(pwd):/app --env-file .env --name api api_image
docker exec -it api bash
docker stop api
docker kill api
c.ContentsManager.allow_hidden = False