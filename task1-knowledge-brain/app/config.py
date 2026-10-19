import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    db_path: Path = Field(default_factory=lambda: Path(os.getenv("TASK1_DB_PATH", str(DATA_DIR / "knowledge_brain.db"))))
    checkpoint_path: Path = Field(default_factory=lambda: Path(os.getenv("TASK1_CHECKPOINT_PATH", str(DATA_DIR / "crawl_checkpoint.json"))))
    sitemap_url: str = "https://support.brilliantdirectories.com/support/sitemap.xml"
    crawl_delay_seconds: float = 0.5
    confidence_threshold: float = 0.20
    scheduled_sync_enabled: bool = Field(
        default_factory=lambda: os.getenv("TASK1_SCHEDULED_SYNC_ENABLED", "true").strip().lower()
        not in {"0", "false", "no", "off"}
    )
    scheduled_sync_interval_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TASK1_SCHEDULED_SYNC_INTERVAL_SECONDS", "86400")),
        gt=0,
    )
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")

    @property
    def has_live_llm(self) -> bool:
        return bool(self.anthropic_api_key.strip())

settings = Settings()
