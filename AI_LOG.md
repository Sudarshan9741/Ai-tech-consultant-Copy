# AI Assistance & Decision Log (AI_LOG.md)

This log records the top 5 most useful prompts used during development, as well as an instance where an AI recommendation was explicitly rejected in favor of a superior engineering decision.

## 5 Most Useful Prompts

### Prompt 1: Polite Sitemap Crawler with Checkpointing
> *"Implement an async, polite sitemap crawler in Python for Brilliant Directories help center that reads https://support.brilliantdirectories.com/support/sitemap.xml with a token bucket rate limiter, checkpointing to crawl_state.json so it can resume after interruptions without hammering the server."*

### Prompt 2: Visual Grounding for Setting Screenshots
> *"Extract screenshot references from the help center articles and associate them with specific setting subheadings and UI navigation paths, so that answers can cite exact UI steps alongside image URLs."*

### Prompt 3: Progressive Autonomy Safeguard with 20-Run Streak
> *"Design a strict TypeScript state machine that tracks human approval history for customer email replies by category. The system must require 20 consecutive human approvals with zero edits for a specific category before offering an autonomous auto-send mode, and automatically revoke autonomy if an issue is flagged."*

### Prompt 4: Platform Setting vs. Custom Code Cross-Examination
> *"In the meeting-to-scope pipeline, implement an agent step that calls the Knowledge Brain API for every client feature request. If Brilliant Directories already provides a native setting for the feature, classify it as a Configuration Task (0.5 hrs) instead of a Custom Engineering Task (8-16 hrs)."*

### Prompt 5: Structured Scope Delta Between Discovery and Follow-Up Meetings
> *"Create a diffing algorithm that takes a baseline SOW and a follow-up meeting transcript, classifying items into Unchanged, Modified, Newly Added, and Out-of-Scope (requiring a change order quote)."*

---

## Rejected AI Suggestion

### Context
When designing the vector storage for Task 1, an AI tool initially suggested spinning up a multi-container Docker setup with Milvus, Redis, and Celery for distributed scraping and vector indexing.

### Why It Was Rejected
1. **Unnecessary Complexity & Single Point of Failure**: For an MVP of several hundred documentation articles, a full distributed cluster introduces severe setup friction, network dependencies, and orchestration fragility for the live evaluation.
2. **Explainability in 30-Minute Live Review**: During the live review, the candidate must explain every single line of code. A self-contained, lightweight, typed persistent vector store with cosine similarity and SQLite persistence is transparent, 100% testable, zero-external-dependency, and immediately verifiable.

