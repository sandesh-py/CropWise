from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "CropWise API"
    api_prefix: str = "/api"
    openweather_api_key: str | None = os.getenv("OPENWEATHER_API_KEY")
    sentinelhub_client_id: str | None = os.getenv("SENTINELHUB_CLIENT_ID")
    sentinelhub_client_secret: str | None = os.getenv("SENTINELHUB_CLIENT_SECRET")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")


def get_settings() -> Settings:
    return Settings()


