from typing import Optional
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):    
    bot_token: str
    postgres_dsn: str
    superuser_password: str
    superuser_user: Optional[str] = "admin"
    redis_dsn: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = ProjectSettings()
