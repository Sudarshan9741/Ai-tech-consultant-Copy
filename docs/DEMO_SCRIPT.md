# 10-Minute Demo Video Script & Live Review Preparation Guide

This guide provides a minute-by-minute walkthrough to record your 10-minute capstone submission video, strictly following the evaluation rubric.

---

## 1. Video Structure & Timing (Max 10 Minutes)

| Timestamp | Section | Screen | What to Say / Show |
|---|---|---|---|
| **0:00 - 0:30** | **Face Introduction** | Webcam (Full screen with your face) | State your name, project title ("AI Tech Consultant for BusinessLabs"), problem summary (90% dev price drop requiring 10-20x throughput), and preview all 3 tasks. |
| **0:30 - 3:00** | **Task 1: The Knowledge Brain** | Browser: `http://127.0.0.1:8000` | 1. Ask in-domain question ("How do I process a refund?"). Show grounded answer, citations, and screenshot preview.<br>2. **Failure Case Demo**: Ask an out-of-domain question ("What is quantum physics?"). Show honest "insufficient information" response and automatic Ticket creation.<br>3. Go to "Escalation Queue", click "Provide Answer", resolve ticket, and re-ask the question to show memory self-evolution. |
| **3:00 - 6:00** | **Task 2: The Inbox Agent** | Browser: `http://127.0.0.1:3000` | 1. Show 50 realistic emails and intent classification.<br>2. Select an email; show draft grounded by calling Task 1's HTTP API with citations.<br>3. Show the **Progressive Autonomy Dashboard** (20-run streak). Click "Approve Unchanged" to show streak advancing.<br>4. Click "Edit & Approve" to demonstrate the safeguard: streak instantly resets to 0 and revokes autonomy if active.<br>5. Explain the safety kill switch: auto-send never dispatches real emails without explicit system authorization. |
| **6:00 - 8:30** | **Task 3: Meeting to Scope** | Browser: `http://127.0.0.1:8001` | 1. Select Meeting 1 (Discovery). Click "Run Multi-Agent Pipeline".<br>2. Show how Agent 2 queries Task 1 API to detect native settings (Radius search, Stripe, Membership tiers), saving \$3,150 in custom code!<br>3. Show custom code tasks (Telemedicine portal).<br>4. Click "Compare Meeting 1 vs Meeting 2" to show the Scope Delta Report: Unchanged, Modified, and brand-new AI Symptom Checker requiring a formal Change Order.<br>5. Click "Sign & Approve Scope of Work" to demonstrate the human gate. |
| **8:30 - 9:30** | **Automated Tests** | Terminal | Run `test_all.bat`. Show all 25 unit/integration tests and 60 benchmark evaluations passing with 100% precision. |
| **9:30 - 10:00** | **Conclusion & Architecture** | Codebase / IDE | Show clean folder structure, strict TypeScript types, decoupled REST API communication, and closing thoughts. |

---

## 2. Minute 0:00 - 0:30 Face Intro Script (Verbatim)

> *"Hi everyone, my name is [Your Name], and this is my submission for the BusinessLabs AI Tech Consultant Capstone. Over the last two years, generative AI coding tools have reduced custom software delivery costs by 90%—from $2,000 down to $200. For software agencies to survive and scale 10 to 20 times, they must automate the heavy operational bottlenecks surrounding code: finding product knowledge, triaging customer emails, and turning long client discovery meetings into accurate scopes of work without quoting custom code for features the platform already has. Today, I'll walk you through my three connected microservices: The Knowledge Brain in Python, the Progressive Autonomy Inbox Agent in strict TypeScript, and the Multi-Agent Meeting to Scope pipeline."*

---

## 3. 30-Minute Live Review Preparation

During your 30-minute live review with the evaluator, you must be ready to explain the architecture line-by-line and perform one small live code change. Here are the core concepts to explain:

### Architecture Explanations:
1. **Decoupled HTTP Communication**:
   - Task 1 runs on port 8000 (`FastAPI`).
   - Task 2 runs on port 3000 (`Node.js/Express + TypeScript`). It calls `http://127.0.0.1:8000/api/v1/ask` via `fetch()`.
   - Task 3 runs on port 8001 (`FastAPI`). It calls `http://127.0.0.1:8000/api/v1/ask` via `httpx.AsyncClient`.
   - **Why?** Zero tight-coupling. Any service can be rewritten or deployed as a cloud microservice without breaking others.

2. **Self-Evolving Knowledge Memory (Task 1)**:
   - When confidence is below threshold, `storage.create_escalation()` creates a pending ticket.
   - When an expert submits a verified answer, `resolve_escalation()` saves it as an active article in SQLite, chunks it, and calls `vector_store.reload()`. Subsequent identical queries immediately return the expert answer!

3. **Progressive Autonomy Safeguard (Task 2)**:
   - File: `task2-inbox-agent/src/autonomyEngine.ts`.
   - A category only unlocks autonomous sending after **20 consecutive unchanged approvals** (`APPROVED_UNCHANGED`).
   - Any edit (`EDITED_AND_APPROVED`) or rejection (`REJECTED`) resets `consecutiveUnchangedCount = 0` and sets `isAutonomous = false`.
   - `canAutoSend()` requires BOTH category autonomy AND system authorization (`allowAutonomousSend = true`).

4. **Platform Capability Cross-Examination (Task 3)**:
   - File: `task3-meeting-to-scope/app/agents/platform_checker.py`.
   - When a client asks for "zip code radius search", instead of quoting 16 hours of custom geospatial coding, Agent 2 queries Task 1's API. Task 1 returns the native Brilliant Directories documentation. Agent 3 estimates it at 1.0 hr (configuration), saving the client 14 hours and \$1,050.

### Likely Live Change Requests & How to Solve Them:
- **Change 1: "Change the autonomy threshold from 20 to 10."**
  - Go to `task2-inbox-agent/src/autonomyEngine.ts`: Change `const DEFAULT_THRESHOLD = 20;` to `10`.
- **Change 2: "Change the hourly rate in SOW proposals from \$75 to \$100."**
  - Go to `task3-meeting-to-scope/app/agents/proposal_agent.py` and `diff_agent.py`: Change `HOURLY_RATE_USD = 75.0` to `100.0`.
- **Change 3: "Add a new intent category to the Inbox Agent (e.g. PARTNERSHIP)."**
  - In `task2-inbox-agent/src/types.ts`: Add `"PARTNERSHIP"` to `EmailCategorySchema`.
  - In `task2-inbox-agent/src/classifier.ts`: Add keyword check for `"partner"` or `"collaboration"`.
