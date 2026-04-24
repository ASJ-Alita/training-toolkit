"""
应用配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Training Toolkit API"
    VERSION: str = "0.2.0"
    DEBUG: bool = True

    # JWT 认证
    SECRET_KEY: str = "training-toolkit-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
