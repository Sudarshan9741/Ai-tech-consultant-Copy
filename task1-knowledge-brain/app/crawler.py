import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.storage import storage
from app.seed_data import chunk_text
from app.vector_store import vector_store

logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)

class PoliteCrawler:
    def __init__(self):
        self.sitemap_url = settings.sitemap_url
        self.delay = settings.crawl_delay_seconds
        self.headers = {
            "User-Agent": "AI-Tech-Consultant-Bot/1.0 (Polite-Research-Crawler; +https://github.com/ai-tech-consultant)"
        }

    async def fetch_sitemap_urls(self) -> Dict[str, Optional[str]]:
        """Fetch and parse sitemap.xml, returning a mapping of {url: lastmod}."""
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=self.headers) as client:
            resp = await client.get(self.sitemap_url)
            resp.raise_for_status()

        root = ET.fromstring(resp.content)
        urls: Dict[str, Optional[str]] = {}
        for url_elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            lastmod_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            if loc_elem is not None and loc_elem.text:
                url = loc_elem.text.strip()
                if "/support/solutions/articles/" in url:
                    lastmod = lastmod_elem.text.strip() if lastmod_elem is not None and lastmod_elem.text else None
                    urls[url] = lastmod
        return urls

    async def parse_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Politely fetch and parse a single article with retry mechanism."""
        retries = 3
        backoff = 1.0
        html = ""

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=self.headers) as client:
            for attempt in range(retries):
                try:
                    resp = await client.get(url)
                    if resp.status_code == 404:
                        logger.warning(f"Article not found (404): {url}")
                        return None
                    resp.raise_for_status()
                    html = resp.text
                    break
                except (httpx.HTTPError, httpx.TimeoutException) as e:
                    if attempt == retries - 1:
                        logger.error(f"Failed to fetch {url} after {retries} attempts: {e}")
                        return None
                    await asyncio.sleep(backoff)
                    backoff *= 2.0

        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Title
        h1 = soup.find("h1")
        title = h1.text.strip() if h1 else (soup.title.string.strip() if soup.title else url)
        # Clean title suffix if present
        title = title.split(" | ")[0].strip()

        # 2. Category & Folder from solution links
        category = "General"
        folder = "General"
        sol_links = [
            a.text.strip() for a in soup.find_all("a")
            if "/support/solutions/" in a.get("href", "") and a.text.strip()
        ]
        for link_text in sol_links:
            if link_text.startswith("Section:"):
                category = link_text.replace("Section:", "").strip()
            elif link_text != title and category != link_text:
                folder = link_text

        # 3. Content body
        body_elem = soup.find("div", class_="article-body") or soup.find("article") or soup.find("div", class_="content")
        if body_elem:
            content = body_elem.get_text(separator=" ", strip=True)
        else:
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            content = " ".join([p for p in paragraphs if len(p) > 20])

        if not content or len(content) < 40:
            content = f"{title}. Please refer to the official documentation page for complete visual instructions."

        # 4. Screenshot Images
        images: List[Dict[str, str]] = []
        img_tags = body_elem.find_all("img") if body_elem else soup.find_all("img")
        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if src and not src.endswith(".svg") and "logo" not in src.lower():
                alt = img.get("alt", "").strip() or f"Screenshot for {title}"
                images.append({
                    "url": src,
                    "alt": alt,
                    "caption": f"Visual guide: {alt}"
                })

        return {
            "url": url,
            "title": title,
            "category": category,
            "folder": folder,
            "content": content,
            "images": images
        }

    async def sync_sitemap(self, max_articles: int = 20, force_resync: bool = False) -> Dict[str, Any]:
        """
        Check the sitemap daily/on-demand.
        Find pages that were added, updated, or removed, and update only what changed.
        Respects polite delays and updates the search index incrementally.
        """
        sitemap_urls = await self.fetch_sitemap_urls()
        existing_articles = {a["url"]: a for a in storage.list_articles(limit=5000)}
        
        # Check checkpoint
        checkpoint_data = storage.get_crawler_state("sitemap_checkpoint")
        processed_set = set(json.loads(checkpoint_data)) if checkpoint_data else set()

        added_urls = []
        updated_urls = []
        deleted_urls = []

        # Find added or updated
        for url, lastmod in sitemap_urls.items():
            if url not in existing_articles:
                added_urls.append((url, lastmod))
            elif force_resync:
                updated_urls.append((url, lastmod))

        # Find removed articles (present in DB as active, but missing in sitemap)
        for url, art in existing_articles.items():
            if art["status"] == "active" and url not in sitemap_urls:
                deleted_urls.append(url)

        # Handle removals immediately
        for del_url in deleted_urls:
            storage.mark_article_deleted(del_url)
            logger.info(f"Purged deleted article: {del_url}")

        queue = (added_urls + updated_urls)[:max_articles]
        success_count = 0
        failed_count = 0

        for url, lastmod in queue:
            try:
                parsed = await self.parse_article(url)
                if parsed:
                    storage.save_article(
                        url=parsed["url"],
                        title=parsed["title"],
                        category=parsed["category"],
                        folder=parsed["folder"],
                        content=parsed["content"],
                        images=parsed["images"],
                        last_updated=lastmod or datetime.utcnow().isoformat()
                    )
                    # Create and store chunks
                    chunks = chunk_text(parsed["content"])
                    storage.save_chunks(parsed["url"], parsed["title"], chunks, parsed["images"])
                    processed_set.add(url)
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                failed_count += 1

            # Polite delay between requests
            await asyncio.sleep(self.delay)

        # Update checkpoint and vector index
        storage.set_crawler_state("sitemap_checkpoint", json.dumps(list(processed_set)))
        storage.set_crawler_state("last_sync", datetime.utcnow().isoformat())
        vector_store.reload()

        return {
            "sitemap_total": len(sitemap_urls),
            "added_found": len(added_urls),
            "updated_found": len(updated_urls),
            "deleted_removed": len(deleted_urls),
            "articles_processed_in_batch": success_count,
            "articles_failed": failed_count,
            "resumed_checkpoint_count": len(processed_set)
        }

crawler = PoliteCrawler()
