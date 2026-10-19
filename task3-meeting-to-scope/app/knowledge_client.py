import os
import httpx
from typing import Dict, Any, Optional

class KnowledgeBrainUnavailable(RuntimeError):
    """Task 1 could not provide a trustworthy capability check."""

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
                resp.raise_for_status()
                data = resp.json()
                if (
                    not isinstance(data, dict)
                    or not isinstance(data.get("answered"), bool)
                    or not isinstance(data.get("answer"), str)
                    or isinstance(data.get("confidence"), bool)
                    or not isinstance(data.get("confidence"), (int, float))
                    or not isinstance(data.get("sources"), list)
                ):
                    raise KnowledgeBrainUnavailable("Task 1 returned an unexpected response.")
                return data
        except KnowledgeBrainUnavailable:
            raise
        except httpx.TimeoutException as exc:
            raise KnowledgeBrainUnavailable("Task 1 Knowledge Brain timed out after 10 seconds.") from exc
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            raise KnowledgeBrainUnavailable(f"Task 1 Knowledge Brain request failed: {exc}") from exc

knowledge_client = KnowledgeBrainClient()

