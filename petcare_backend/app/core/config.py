from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "petcare_backend"
    environment: str = "local"

    database_url: str = "postgresql+asyncpg://user:password@db:5432/petcare"
    redis_url: str = "redis://redis:6379/0"

    access_token_exp_minutes: int = 60
    login_attempt_window_seconds: int = 900
    login_attempt_max: int = 5
    login_lockout_seconds: int = 900
    otp_request_cooldown_seconds: int = 60
    message_rate_limit_per_minute: int = 30


settings = Settings()
