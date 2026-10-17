import os
import httpx
from typing import Dict, Any, Optional

class KnowledgeBrainClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("TASK1_API_URL", "http://127.0.0.1:8000")).rstrip("/")

    async def check_platform_capability(self, query: str) -> Dict[str, Any]:
        """Query Task 1 Knowledge Brain API to check if a feature is native vs custom."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/v1/ask",
                    json={"question": query}
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass

        return {
            "answered": False,
            "answer": "Unable to verify native platform settings via Task 1 API.",
            "confidence": 0.0,
            "sources": [],
            "images": []
        }

knowledge_client = KnowledgeBrainClient()

