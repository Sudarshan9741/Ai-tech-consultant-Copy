import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.storage import storage
from app.vector_store import vector_store

logger = logging.getLogger("rag_engine")

class RAGEngine:
    def __init__(self):
        pass

    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer question using retrieved evidence.
        If evidence is insufficient, state unknown and trigger human escalation.
        Returns citations and relevant screenshots.
        """
        query = question.strip()
        if not query:
            return {
                "answered": False,
                "answer": "Please provide a valid question.",
                "confidence": 0.0,
                "escalation_id": None,
                "sources": [],
                "images": []
            }

        # 1. Retrieve top chunks
        results = vector_store.search(query, top_k=5)
        top_score = results[0]["score"] if results else 0.0

        # 2. Check confidence against threshold
        if not results or top_score < settings.confidence_threshold:
            # Create human escalation record
            reason = (
                f"Query confidence {top_score:.3f} is below minimum threshold "
                f"({settings.confidence_threshold}) or no relevant articles found."
            )
            escalation_id = storage.create_escalation(query, context_reason=reason)
            logger.info(f"Escalation #{escalation_id} created for query: '{query}' (score: {top_score:.3f})")

            return {
                "answered": False,
                "answer": (
                    "I do not have sufficient information in the Brilliant Directories help center "
                    "to answer this question accurately (insufficient information). A ticket has been created for a human expert."
                ),
                "confidence": round(top_score, 4),
                "escalation_id": escalation_id,
                "sources": [],
                "images": []
            }

        # 3. Filter retrieved chunks to only relevant evidence
        # Chunks from the primary matched article are relevant.
        # Chunks from secondary articles are only included if their score is strong (>= 80% of top_score)
        # and above the confidence threshold.
        primary_url = results[0]["article_url"]
        relevant_chunks = []
        for c in results:
            if c["article_url"] == primary_url:
                # Keep lower-scoring chunks from the primary article so answers
                # are not cut off at a chunk boundary.
                relevant_chunks.append(c)
            elif c["score"] >= settings.confidence_threshold and c["score"] >= top_score * 0.80:
                relevant_chunks.append(c)

        if not relevant_chunks:
            relevant_chunks = [results[0]]

        # 4. Aggregate citations and screenshots from relevant chunks only
        sources = []
        seen_urls = set()
        all_images = []
        seen_images = set()

        for chunk in relevant_chunks:
            if chunk["article_url"] not in seen_urls:
                seen_urls.add(chunk["article_url"])
                sources.append({
                    "title": chunk["title"],
                    "url": chunk["article_url"],
                    "snippet": chunk["text"][:250] + "..." if len(chunk["text"]) > 250 else chunk["text"]
                })
            
            for img in chunk.get("images", []):
                img_url = img.get("url")
                if img_url and img_url not in seen_images:
                    seen_images.add(img_url)
                    all_images.append({
                        "url": img_url,
                        "alt": img.get("alt", ""),
                        "caption": img.get("caption", ""),
                        "article_title": chunk["title"],
                        "article_url": chunk["article_url"]
                    })

        # 5. Generate answer via Claude or Deterministic Grounded Engine
        answer_text = await self._generate_answer(query, relevant_chunks, all_images)

        return {
            "answered": True,
            "answer": answer_text,
            "confidence": round(top_score, 4),
            "escalation_id": None,
            "sources": sources,
            "images": all_images
        }

    async def _generate_answer(self, query: str, context_chunks: List[Dict[str, Any]], images: List[Dict[str, Any]]) -> str:
        """Call Claude if key is available, else use deterministic grounded synthesis."""
        if settings.has_live_llm:
            try:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
                context_str = "\n\n".join([
                    f"Article: {c['title']} ({c['article_url']})\nContent: {c['text']}"
                    for c in context_chunks
                ])
                image_notes = "\n".join([
                    f"- Screenshot: {img['caption']} from {img['article_title']}"
                    for img in images
                ])
                
                prompt = (
                    "You are the Brilliant Directories AI Tech Consultant. Answer the customer's question "
                    "using ONLY the documentation provided below. Mention exact navigation paths and settings. "
                    "Ensure every claim is directly supported by the documentation. Do not include unrelated topics. "
                    "If a screenshot explains the setting, mention it clearly.\n\n"
                    f"Documentation Context:\n{context_str}\n\n"
                    f"Visual Guide Screenshots:\n{image_notes}\n\n"
                    f"User Question: {query}\n\nAnswer:"
                )
                
                response = await client.messages.create(
                    model=settings.claude_model,
                    max_tokens=600,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Live Claude API error: {e}, falling back to grounded synthesis.")

        # Deterministic Grounded Synthesis (Transparent & Offline-Ready)
        # Group chunks by article and order by chunk_index to maintain coherent, supported claims
        primary_chunks = [c for c in context_chunks if c["article_url"] == context_chunks[0]["article_url"]]
        primary_chunks.sort(key=lambda c: c.get("chunk_index", 0))
        
        primary_title = primary_chunks[0]["title"]
        primary_text = "\n\n".join([c["text"] for c in primary_chunks])
        
        answer_lines = [
            f"Based on the Brilliant Directories documentation in **{primary_title}**:",
            "",
            primary_text
        ]
        
        # Only add secondary details if secondary article meets strict relevance threshold
        secondary_chunks = [c for c in context_chunks if c["article_url"] != context_chunks[0]["article_url"]]
        if secondary_chunks:
            sec_title = secondary_chunks[0]["title"]
            sec_text = secondary_chunks[0]["text"]
            answer_lines.append("")
            answer_lines.append(f"Related documentation from **{sec_title}**: {sec_text}")

        if images:
            answer_lines.append("")
            answer_lines.append("**Visual Guide:**")
            for img in images[:2]:
                caption = img.get("caption") or img.get("alt")
                answer_lines.append(f"- Refer to {caption} ({img['url']})")

        return "\n".join(answer_lines)

rag_engine = RAGEngine()
