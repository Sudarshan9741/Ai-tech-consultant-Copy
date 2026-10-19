from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.storage import storage
from app.seed_data import SEED_ARTICLES, chunk_text
from app.vector_store import vector_store
from app.crawler import crawler
from app.rag_engine import rag_engine
from app.scheduler import DailySyncScheduler

sync_scheduler = DailySyncScheduler(
    sync=crawler.sync_sitemap,
    interval_seconds=settings.scheduled_sync_interval_seconds,
)

def ensure_seed_data():
    """Ensure seed articles are loaded into database and index."""
    active_urls = {a["url"] for a in storage.list_articles(limit=5000) if a["status"] == "active"}
    loaded_new = False
    for art in SEED_ARTICLES:
        if art["url"] not in active_urls:
            storage.save_article(
                url=art["url"],
                title=art["title"],
                category=art["category"],
                folder=art["folder"],
                content=art["content"],
                images=art.get("images", [])
            )
            chunks = chunk_text(art["content"])
            storage.save_chunks(art["url"], art["title"], chunks, art.get("images", []))
            loaded_new = True
    vector_store.reload()

# Ensure seed data is populated on module import
ensure_seed_data()

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_seed_data()
    if settings.scheduled_sync_enabled:
        sync_scheduler.start()
    try:
        yield
    finally:
        if settings.scheduled_sync_enabled:
            await sync_scheduler.stop()

app = FastAPI(
    title="Knowledge Brain API",
    description="Knowledge base and RAG chatbot API for Brilliant Directories help center.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Request / Response Models -----------------

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="The customer question")

class SourceCitation(BaseModel):
    title: str
    url: str
    snippet: str

class ImageCitation(BaseModel):
    url: str
    alt: str
    caption: str
    article_title: str
    article_url: str

class AskResponse(BaseModel):
    answered: bool
    answer: str
    confidence: float
    escalation_id: Optional[int] = None
    sources: List[SourceCitation]
    images: List[ImageCitation]

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=20)

class QueryResultItem(BaseModel):
    chunk_id: int
    article_url: str
    title: str
    chunk_index: int
    text: str
    images: List[Dict[str, Any]]
    score: float

class QueryResponse(BaseModel):
    total_results: int
    results: List[QueryResultItem]

class ResolveEscalationRequest(BaseModel):
    expert_response: str = Field(..., min_length=5, description="The expert's verified answer")

class SyncRequest(BaseModel):
    max_articles: int = Field(15, ge=1, le=100)
    force_resync: bool = False

# ----------------- API Routes -----------------

@app.get("/health", summary="Service Health and Index Statistics")
async def health():
    stats = storage.get_stats()
    return {
        "status": "healthy",
        "service": "task1-knowledge-brain",
        "llm_mode": "live_claude" if settings.has_live_llm else "offline_grounded_rag",
        "model": settings.claude_model if settings.has_live_llm else "deterministic_grounded_engine",
        "active_articles": stats["active_articles"],
        "total_chunks": stats["total_chunks"],
        "pending_escalations": stats["pending_escalations"],
        "total_escalations": stats["total_escalations"],
        "last_sync": stats["last_sync"]
    }

@app.post("/api/v1/ask", response_model=AskResponse, summary="Ask a question with evidence grounding")
async def ask_question(req: AskRequest):
    result = await rag_engine.answer_question(req.question)
    return result

@app.post("/api/v1/query", response_model=QueryResponse, summary="Semantic chunk retrieval")
async def semantic_query(req: QueryRequest):
    results = vector_store.search(req.query, top_k=req.top_k)
    return {
        "total_results": len(results),
        "results": results
    }

@app.get("/api/v1/articles", summary="List indexed knowledge base articles")
async def list_articles(limit: int = Query(50, ge=1, le=500)):
    articles = storage.list_articles(limit=limit)
    return {
        "count": len(articles),
        "articles": articles
    }

@app.get("/api/v1/escalations", summary="List human escalation tickets")
async def list_escalations(status: Optional[str] = Query(None, pattern="^(pending|resolved)$")):
    items = storage.list_escalations(status=status)
    return {
        "total": len(items),
        "escalations": items
    }

@app.post("/api/v1/escalations/{escalation_id}/resolve", summary="Resolve escalation and feed answer back into memory")
async def resolve_escalation(escalation_id: int, req: ResolveEscalationRequest):
    escalation = storage.get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation ticket not found")

    success = storage.resolve_escalation(escalation_id, req.expert_response)
    if not success:
        raise HTTPException(status_code=400, detail="Ticket is already resolved or could not be updated")

    # Flow expert answer back into knowledge brain as an active article
    kb_url = f"https://support.brilliantdirectories.com/internal/escalation/{escalation_id}"
    kb_title = f"Expert Resolution: {escalation['query'][:60]}"
    storage.save_article(
        url=kb_url,
        title=kb_title,
        category="Expert Solutions",
        folder="Escalations",
        content=f"Question: {escalation['query']}\nVerified Solution: {req.expert_response}",
        images=[]
    )
    chunks = chunk_text(f"Question: {escalation['query']}\nVerified Solution: {req.expert_response}")
    storage.save_chunks(kb_url, kb_title, chunks, [])
    vector_store.reload()

    return {
        "status": "resolved",
        "escalation_id": escalation_id,
        "message": "Answer verified and re-indexed into Knowledge Brain memory.",
        "reindexed_url": kb_url
    }

@app.post("/api/v1/sync", summary="Trigger polite crawl and sync with sitemap")
async def sync_sitemap(req: SyncRequest):
    result = await crawler.sync_sitemap(max_articles=req.max_articles, force_resync=req.force_resync)
    return {
        "status": "completed",
        "details": result
    }

# ----------------- Visual Web Dashboard -----------------

@app.get("/", response_class=HTMLResponse, summary="Interactive Web Dashboard")
async def web_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Knowledge Brain | AI Tech Consultant</title>
        <style>
            :root {
                --primary: #2563eb;
                --primary-hover: #1d4ed8;
                --bg: #0f172a;
                --card: #1e293b;
                --border: #334155;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 24px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border);
                padding-bottom: 16px;
                margin-bottom: 24px;
            }
            h1 { margin: 0; font-size: 24px; }
            .badge {
                padding: 4px 10px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 600;
                background: #1e3a8a;
                color: #93c5fd;
            }
            .tabs {
                display: flex;
                gap: 8px;
                margin-bottom: 20px;
            }
            .tab-btn {
                background: var(--card);
                border: 1px solid var(--border);
                color: var(--text-muted);
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
            }
            .tab-btn.active {
                background: var(--primary);
                color: #fff;
                border-color: var(--primary);
            }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }
            input, textarea {
                width: 100%;
                background: #0f172a;
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 10px;
                color: var(--text);
                font-size: 14px;
                box-sizing: border-box;
                margin-bottom: 12px;
            }
            button.btn-primary {
                background: var(--primary);
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            button.btn-primary:hover { background: var(--primary-hover); }
            .result-box {
                margin-top: 16px;
                padding: 16px;
                border-radius: 6px;
                background: #0f172a;
                border-left: 4px solid var(--primary);
            }
            .result-box.escalation { border-left-color: var(--warning); }
            .citation-card {
                background: #1e293b;
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 10px;
                margin-top: 8px;
            }
            .citation-card a { color: #60a5fa; text-decoration: none; }
            .citation-card a:hover { text-decoration: underline; }
            .img-preview {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
                margin-top: 8px;
                border: 1px solid var(--border);
            }
            table { width: 100%; border-collapse: collapse; margin-top: 12px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid var(--border); font-size: 13px; }
            th { color: var(--text-muted); }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>🧠 Knowledge Brain</h1>
                    <small style="color: var(--text-muted);">Brilliant Directories Self-Evolving Help Center Memory</small>
                </div>
                <div id="stats-badge" class="badge">Loading stats...</div>
            </header>

            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('chat')">Ask Chatbot</button>
                <button class="tab-btn" onclick="switchTab('escalations')">Human Escalation Queue</button>
                <button class="tab-btn" onclick="switchTab('articles')">Indexed Articles</button>
            </div>

            <!-- CHAT TAB -->
            <div id="tab-chat" class="tab-content active">
                <div class="card">
                    <h3>Ask the Product Knowledge Brain</h3>
                    <p style="color: var(--text-muted); font-size: 14px;">
                        Try: "How do I process a refund?", "Can I configure zip code radius search?", or "What is quantum computing?"
                    </p>
                    <input type="text" id="questionInput" placeholder="Enter question..." onkeydown="if(event.key==='Enter') askQuestion()">
                    <button class="btn-primary" onclick="askQuestion()">Ask Brain</button>
                    <div id="chatResult"></div>
                </div>
            </div>

            <!-- ESCALATION TAB -->
            <div id="tab-escalations" class="tab-content">
                <div class="card">
                    <h3>Human Expert Escalation Queue</h3>
                    <p style="color: var(--text-muted); font-size: 14px;">
                        Questions the Knowledge Brain could not answer are routed here. Expert resolutions automatically feed back into memory.
                    </p>
                    <button class="btn-primary" onclick="loadEscalations()">Refresh Tickets</button>
                    <div id="escalationList"></div>
                </div>
            </div>

            <!-- ARTICLES TAB -->
            <div id="tab-articles" class="tab-content">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Active Knowledge Base Articles</h3>
                        <button class="btn-primary" onclick="triggerSync()">Sync with Live Sitemap</button>
                    </div>
                    <div id="syncStatus" style="margin-top: 8px; font-size: 13px; color: var(--text-muted);"></div>
                    <div id="articleList"></div>
                </div>
            </div>
        </div>

        <script>
            async function fetchStats() {
                try {
                    const res = await fetch('/health');
                    const data = await res.json();
                    document.getElementById('stats-badge').innerText = 
                        `${data.active_articles} Articles | ${data.total_chunks} Chunks | ${data.pending_escalations} Pending Tickets`;
                } catch (e) {
                    document.getElementById('stats-badge').innerText = 'Offline';
                }
            }

            function switchTab(tab) {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                if (tab === 'chat') {
                    document.querySelector("button[onclick*='chat']").classList.add('active');
                    document.getElementById('tab-chat').classList.add('active');
                } else if (tab === 'escalations') {
                    document.querySelector("button[onclick*='escalations']").classList.add('active');
                    document.getElementById('tab-escalations').classList.add('active');
                    loadEscalations();
                } else if (tab === 'articles') {
                    document.querySelector("button[onclick*='articles']").classList.add('active');
                    document.getElementById('tab-articles').classList.add('active');
                    loadArticles();
                }
            }

            async function askQuestion() {
                const q = document.getElementById('questionInput').value.trim();
                if (!q) return;
                const container = document.getElementById('chatResult');
                container.innerHTML = '<p style="color: var(--text-muted);">Consulting Knowledge Brain...</p>';

                try {
                    const res = await fetch('/api/v1/ask', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({question: q})
                    });
                    const data = await res.json();
                    
                    let html = '';
                    if (data.answered) {
                        html += `<div class="result-box">`;
                        html += `<h4>Answer (Confidence: ${(data.confidence * 100).toFixed(1)}%):</h4>`;
                        html += `<p style="white-space: pre-line;">${renderAnswerMarkdown(data.answer)}</p>`;
                        
                        if (data.sources && data.sources.length) {
                            html += `<h5>Sources & Evidence:</h5>`;
                            data.sources.forEach(s => {
                                html += `<div class="citation-card"><a href="${s.url}" target="_blank">📄 ${s.title}</a><br><small style="color: #94a3b8;">${s.snippet}</small></div>`;
                            });
                        }

                        if (data.images && data.images.length) {
                            html += `<h5>Referenced Screenshots:</h5>`;
                            data.images.forEach(img => {
                                html += `<div style="margin-top: 8px;"><small>🖼️ ${img.caption}</small><br><img class="img-preview" src="${img.url}" alt="${img.alt}" onerror="this.style.display='none'"></div>`;
                            });
                        }
                        html += `</div>`;
                    } else {
                        html += `<div class="result-box escalation">`;
                        html += `<h4>⚠️ Insufficient Knowledge</h4>`;
                        html += `<p>${data.answer}</p>`;
                        html += `<p><strong>Escalation Ticket ID:</strong> #${data.escalation_id}</p>`;
                        html += `</div>`;
                    }
                    container.innerHTML = html;
                    fetchStats();
                } catch (err) {
                    container.innerHTML = `<div class="result-box escalation"><p style="color: var(--danger);">Error communicating with Knowledge Brain.</p></div>`;
                }
            }

            function renderAnswerMarkdown(markdown) {
                const escaped = String(markdown).replace(/[&<>"']/g, character => ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[character]);
                return escaped
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/^[ \t]*- (.+)$/gm, '&bull; $1');
            }

            async function loadEscalations() {
                const list = document.getElementById('escalationList');
                list.innerHTML = 'Loading tickets...';
                try {
                    const res = await fetch('/api/v1/escalations');
                    const data = await res.json();
                    if (!data.escalations.length) {
                        list.innerHTML = '<p style="color: var(--text-muted); margin-top: 12px;">No escalation tickets found.</p>';
                        return;
                    }
                    let html = '<table><thead><tr><th>ID</th><th>Query</th><th>Status</th><th>Created</th><th>Action</th></tr></thead><tbody>';
                    data.escalations.forEach(e => {
                        html += `<tr>
                            <td>#${e.id}</td>
                            <td>${e.query}</td>
                            <td><span style="color: ${e.status === 'pending' ? '#f59e0b' : '#10b981'}; font-weight: 600;">${e.status.toUpperCase()}</span></td>
                            <td>${new Date(e.created_at).toLocaleTimeString()}</td>
                            <td>
                                ${e.status === 'pending' ? 
                                `<button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="resolveTicket(${e.id})">Provide Answer</button>` : 
                                `<small style="color: #94a3b8;">Resolved</small>`}
                            </td>
                        </tr>`;
                    });
                    html += '</tbody></table>';
                    list.innerHTML = html;
                } catch (e) {
                    list.innerHTML = 'Failed to load tickets.';
                }
            }

            async function resolveTicket(id) {
                const answer = prompt(`Enter verified expert answer for Ticket #${id}:`);
                if (!answer) return;
                try {
                    const res = await fetch(`/api/v1/escalations/${id}/resolve`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({expert_response: answer})
                    });
                    const data = await res.json();
                    alert(data.message);
                    loadEscalations();
                    fetchStats();
                } catch (e) {
                    alert('Failed to resolve ticket.');
                }
            }

            async function loadArticles() {
                const list = document.getElementById('articleList');
                list.innerHTML = 'Loading articles...';
                try {
                    const res = await fetch('/api/v1/articles');
                    const data = await res.json();
                    let html = '<table><thead><tr><th>Title</th><th>Category</th><th>Screenshots</th><th>Status</th></tr></thead><tbody>';
                    data.articles.forEach(a => {
                        html += `<tr>
                            <td><a href="${a.url}" target="_blank" style="color: #60a5fa; text-decoration: none;">${a.title}</a></td>
                            <td>${a.category || 'General'}</td>
                            <td>${a.images_count}</td>
                            <td><span style="color: #10b981;">ACTIVE</span></td>
                        </tr>`;
                    });
                    html += '</tbody></table>';
                    list.innerHTML = html;
                } catch (e) {
                    list.innerHTML = 'Failed to load articles.';
                }
            }

            async function triggerSync() {
                const statusElem = document.getElementById('syncStatus');
                statusElem.innerText = 'Syncing polite crawl with sitemap... please wait.';
                try {
                    const res = await fetch('/api/v1/sync', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({max_articles: 5})
                    });
                    const data = await res.json();
                    statusElem.innerText = `Sync complete: Processed ${data.details.articles_processed_in_batch} new/updated articles. Total sitemap: ${data.details.sitemap_total}.`;
                    loadArticles();
                    fetchStats();
                } catch (e) {
                    statusElem.innerText = 'Sync failed.';
                }
            }

            fetchStats();
        </script>
    </body>
    </html>
    """
