from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = ""
    tmdb_api_key: str = ""

    # Environment
    environment: str = "development"
    log_level: str = "info"

    # Database
    database_url: str = "postgresql+asyncpg://filmmatch:filmmatch@localhost:5432/filmmatch"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30
    magic_link_secret: str = "change-me"
    magic_link_expire_minutes: int = 15
    google_client_id: str = ""
    google_client_secret: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate Limiting
    rate_limit_per_minute: int = 30
    rate_limit_recommendations_per_minute: int = 10

    # Monitoring
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # TMDB
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
