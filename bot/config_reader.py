from typing import Optional

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str

    postgres_user: Optional[str] = "postgres"
    postgres_password: Optional[str] = "postgres"
    postgres_db: Optional[str] = "postgres"
    postgres_port: Optional[int] = 5432

    @property
    def postgres_dsn(self):
        # The database host is 'db' (the name of the service) due to the common service network in docker
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@db:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = 'envs/bot.env'
        env_file_encoding = 'utf-8'


config = BotSettings()
