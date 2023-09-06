from typing import Optional
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):    
    bot_token: str
    postgres_dsn: str
    postgres_password: str
    postgres_user: Optional[str] = "postgres"
    postgres_db: Optional[str] = "postgres"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = ProjectSettings()
