from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '.env')  # Chỉ định đường dẫn chính xác
        env_file_encoding = 'utf-8'

settings = Settings()
