from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):    
    bot_token: str

    class Config:
        env_file = 'envs/bot.env'
        env_file_encoding = 'utf-8'


config = BotSettings()

