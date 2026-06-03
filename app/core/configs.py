from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Output
    output_dir: str = "outputs"

    # Model
    model_id: str = "g-group-ai-lab/gwen-tts-0.6B"

    # TTS
    chunk_max_chars: int = 200
    # Voices
    voices_dir: str = "app/voices"


settings = Settings()
