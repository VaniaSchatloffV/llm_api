import uvicorn
from app.dependencies import get_settings
from app.models import initialize_models

settings = get_settings()

if __name__ == "__main__":
    host = settings.host
    port = settings.port
    initialize_models()
    if settings.environment == 'dev':
        uvicorn.run("app:app", host=host, port=port, reload=True)
    elif settings.environment == 'prod':
        uvicorn.run("app:app", host=host, port=port)