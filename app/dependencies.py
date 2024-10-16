from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    environment : str
    host : str
    port : int
    aws_access_key_id : str
    aws_secret_access_key : str
    aws_default_region : str
    postgres_user : str
    postgres_password : str
    postgres_host : str
    postgres_port : int
    postgres_db : str
    temp_files : str
    postgres_schema : str
    file_expiration_time_delta: float
    auth0_domain : str
    api_identifier : str
    auth0_client_id : str
    auth0_client_secret : str
    identify : str
    sql : str
    recognize : str
    fix : str
    translate : str
    algorithm : str
    temp : float
    top_p : float
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()