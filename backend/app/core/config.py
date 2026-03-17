from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DnD API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/dnd_db"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Required — GeminiNarrator is used for world/dungeon generation.
    # Set this in .env. The app will refuse to start if it is missing.
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
