from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    BOT_TOKEN: str
    ENV: Literal['dev', 'prod'] = 'dev'

settings = Settings() # type: ignore