import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import settings

class Storage:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT,
                    folder TEXT,
                    content TEXT NOT NULL,
                    images TEXT DEFAULT '[]',
                    last_updated TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    images TEXT DEFAULT '[]',
                    FOREIGN KEY (article_url) REFERENCES articles(url) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS escalations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    context_reason TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    expert_response TEXT,
                    resolved_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawler_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_article(self, url: str, title: str, category: str, folder: str, 
                     content: str, images: List[Dict[str, str]], last_updated: Optional[str] = None):
        with self._get_connection() as conn:
            now = last_updated or datetime.utcnow().isoformat()
            conn.execute("""
                INSERT INTO articles (url, title, category, folder, content, images, last_updated, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    category = excluded.category,
                    folder = excluded.folder,
                    content = excluded.content,
                    images = excluded.images,
                    last_updated = excluded.last_updated,
                    status = 'active'
            """, (url, title, category, folder, content, json.dumps(images), now))
            conn.commit()

    def mark_article_deleted(self, url: str):
        with self._get_connection() as conn:
            conn.execute("UPDATE articles SET status = 'deleted' WHERE url = ?", (url,))
            conn.execute("DELETE FROM chunks WHERE article_url = ?", (url,))
            conn.commit()

    def save_chunks(self, article_url: str, title: str, chunk_texts: List[str], images: List[Dict[str, str]]):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chunks WHERE article_url = ?", (article_url,))
            for idx, text in enumerate(chunk_texts):
                conn.execute("""
                    INSERT INTO chunks (article_url, title, chunk_index, chunk_text, images)
                    VALUES (?, ?, ?, ?, ?)
                """, (article_url, title, idx, text, json.dumps(images)))
            conn.commit()

    def get_all_active_chunks(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.article_url, c.title, c.chunk_index, c.chunk_text, c.images
                FROM chunks c
                JOIN articles a ON c.article_url = a.url
                WHERE a.status = 'active'
            """).fetchall()
            return [
                {
                    "id": r["id"],
                    "article_url": r["article_url"],
                    "title": r["title"],
                    "chunk_index": r["chunk_index"],
                    "chunk_text": r["chunk_text"],
                    "images": json.loads(r["images"]) if r["images"] else []
                }
                for r in rows
            ]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_articles = conn.execute("SELECT COUNT(*) FROM articles WHERE status = 'active'").fetchone()[0]
            deleted_articles = conn.execute("SELECT COUNT(*) FROM articles WHERE status = 'deleted'").fetchone()[0]
            total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            pending_escalations = conn.execute("SELECT COUNT(*) FROM escalations WHERE status = 'pending'").fetchone()[0]
            total_escalations = conn.execute("SELECT COUNT(*) FROM escalations").fetchone()[0]
            last_sync_row = conn.execute("SELECT value, updated_at FROM crawler_state WHERE key = 'last_sync'").fetchone()
            last_sync = last_sync_row["updated_at"] if last_sync_row else None
            return {
                "active_articles": total_articles,
                "deleted_articles": deleted_articles,
                "total_chunks": total_chunks,
                "pending_escalations": pending_escalations,
                "total_escalations": total_escalations,
                "last_sync": last_sync
            }

    def list_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT url, title, category, folder, last_updated, status, images
                FROM articles
                ORDER BY last_updated DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [
                {
                    "url": r["url"],
                    "title": r["title"],
                    "category": r["category"],
                    "folder": r["folder"],
                    "last_updated": r["last_updated"],
                    "status": r["status"],
                    "images_count": len(json.loads(r["images"])) if r["images"] else 0
                }
                for r in rows
            ]

    def create_escalation(self, query: str, context_reason: str) -> int:
        with self._get_connection() as conn:
            now = datetime.utcnow().isoformat()
            cursor = conn.execute("""
                INSERT INTO escalations (query, context_reason, created_at, status)
                VALUES (?, ?, ?, 'pending')
            """, (query, context_reason, now))
            conn.commit()
            return cursor.lastrowid

    def list_escalations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if status:
                rows = conn.execute("""
                    SELECT id, query, context_reason, created_at, status, expert_response, resolved_at
                    FROM escalations WHERE status = ?
                    ORDER BY id DESC
                """, (status,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT id, query, context_reason, created_at, status, expert_response, resolved_at
                    FROM escalations
                    ORDER BY id DESC
                """).fetchall()
            return [dict(r) for r in rows]

    def resolve_escalation(self, escalation_id: int, expert_response: str) -> bool:
        with self._get_connection() as conn:
            now = datetime.utcnow().isoformat()
            cursor = conn.execute("""
                UPDATE escalations
                SET status = 'resolved', expert_response = ?, resolved_at = ?
                WHERE id = ? AND status = 'pending'
            """, (expert_response, now, escalation_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_escalation(self, escalation_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT id, query, context_reason, created_at, status, expert_response, resolved_at
                FROM escalations WHERE id = ?
            """, (escalation_id,)).fetchone()
            return dict(row) if row else None

    def set_crawler_state(self, key: str, value: str):
        with self._get_connection() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute("""
                INSERT INTO crawler_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (key, value, now))
            conn.commit()

    def get_crawler_state(self, key: str) -> Optional[str]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM crawler_state WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

storage = Storage()

