from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # This now reads the single DATABASE_URL from the .env file
    DATABASE_URL: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()