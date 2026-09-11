"""Central settings. Import `settings` from here; never read os.environ elsewhere."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = "sqlite:///./studyos.db"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-5"
    # Required only when the Anthropic key is org-level rather than workspace-scoped.
    anthropic_workspace_id: str = ""

    ai_mode: str = "auto"  # mock | live | auto
    cross_check: bool = False

    embedding_provider: str = "auto"  # auto | mock | openai
    openai_embedding_model: str = "text-embedding-3-small"

    search_provider: str = "mock"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    max_upload_mb: int = 25
    rate_limit_per_minute: int = 120
    request_timeout_s: float = 45.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def openai_live(self) -> bool:
        return self.ai_mode != "mock" and bool(self.openai_api_key)

    @property
    def anthropic_live(self) -> bool:
        return self.ai_mode != "mock" and bool(self.anthropic_api_key)

    @property
    def resolved_ai_mode(self) -> str:
        if self.ai_mode == "mock":
            return "mock"
        if self.ai_mode == "live":
            return "live"
        return "live" if (self.openai_api_key or self.anthropic_api_key) else "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
