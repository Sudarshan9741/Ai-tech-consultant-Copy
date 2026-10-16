import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    db_path: Path = DATA_DIR / "knowledge_brain.db"
    checkpoint_path: Path = DATA_DIR / "crawl_checkpoint.json"
    sitemap_url: str = "https://support.brilliantdirectories.com/support/sitemap.xml"
    crawl_delay_seconds: float = 0.5
    confidence_threshold: float = 0.20
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")

    @property
    def has_live_llm(self) -> bool:
        return bool(self.anthropic_api_key.strip())

settings = Settings()
