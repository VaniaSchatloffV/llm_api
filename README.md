# llm_api
Api para interactuar con llm en bedrock


docker build -t my-fastapi-app .
docker run -d -p 8007:8007 -v $(pwd):/app --name my-fastapi-container my-fastapi-app
docker stop my-fastapi-container
c.ContentsManager.allow_hidden = False