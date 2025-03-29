from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Univercity Scheduler"
    database_url: str = "sqlite:///./shop.db"
    jwt_secret: str = "aae#g$1y7mb-i#4xrtc^p5zs9!056382u**7nl9i*_o#by9&lv"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int | None = None  # None means no expiration (infinite)
    MAX_FILE_SIZE: int = 2 * 1024 * 1024  # 2 MB in bytes
    ALLOWED_CONTENT_TYPES: set[str] = {"image/jpeg", "image/png"}
    ALLOWED_EXTENSIONS: set[str] = {'.jpg', '.jpeg', '.png'}

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")



settings = Settings()
