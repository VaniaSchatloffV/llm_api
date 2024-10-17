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
    algorithm : str
    llm_identify_model : str
    llm_sql_model : str
    llm_recognize_model : str
    llm_fix_model : str
    llm_translate_model : str
    llm_sql_graph_model : str
    llm_graph_gen_model : str
    llm_temperature : float
    llm_top_p : float
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()