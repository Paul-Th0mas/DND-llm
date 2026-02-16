from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DnD API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./dnd.db"

    class Config:s
        env_file = ".env"


settings = Settings()
