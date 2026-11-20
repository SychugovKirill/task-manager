from typing import ClassVar
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    rabbitmq_default_user: str
    rabbitmq_default_pass: str

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
