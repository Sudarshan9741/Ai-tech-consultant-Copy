# 10-Minute Demo Video Script & Live Review Preparation Guide

This guide provides a minute-by-minute walkthrough to record your 10-minute capstone submission video, strictly following the evaluation rubric.

---

## 1. Video Structure & Timing (Max 10 Minutes)

| Timestamp | Section | Screen | What to Say / Show |
|---|---|---|---|
| **0:00 - 0:30** | **Face Introduction** | Webcam (Full screen with your face) | State your name, project title ("AI Tech Consultant for BusinessLabs"), describe the agency workflow problem in your own words, and preview all three tasks. Avoid unsupported market-size or cost claims. |
| **0:30 - 3:00** | **Task 1: The Knowledge Brain** | Browser: `http://127.0.0.1:8000` | 1. Show captured output for a known in-domain refund question, or ask it only in an isolated database copy.<br>2. For the failure case, show captured output or use an isolated copy to demonstrate an out-of-domain escalation.<br>3. Show captured expert-resolution/retrieval output or demonstrate it only in the isolated copy. Do not submit questions that could create escalations in the live database. |
| **3:00 - 6:00** | **Task 2: The Inbox Agent** | Browser: `http://127.0.0.1:3000` | 1. Show the 61 sample emails and intent classification.<br>2. Show captured grounded-draft output or generate it only in an isolated copy.<br>3. Demonstrate review and streak reset only in an isolated copy or with captured output; do not send email or enable auto-send.<br>4. Explain that audit and approval state is process-local. |
| **6:00 - 8:30** | **Task 3: Meeting to Scope** | Browser: `http://127.0.0.1:8001` | 1. Show captured Meeting 1 SOW output or generate it in an isolated copy, including native/custom tasks, estimate ranges, and risks.<br>2. If you mention the 42-hour / $3,150 figure, label it a modeled estimate: three native settings × assumed 14 hours each × $75/hour. It is not measured client savings.<br>3. Show captured Meeting 1 vs Meeting 2 diff and change-order output, or generate it in the isolated copy.<br>4. Demonstrate approval only in an isolated copy or with captured output; approvals are process-local. |
| **8:30 - 9:30** | **Verified Checks** | Terminal | Show the actual 18 October 2026 Task 2 results: `npm run lint` passed and eight filtered local unit tests passed. These exclude Task 1 integration and the 20-email benchmark. Do not run `test_all.bat` against the live project; the full suite has not been verified in one run. The 20-case task evaluations are not a two-model comparison. |
| **9:30 - 10:00** | **Conclusion & Architecture** | Codebase / IDE | Show Task 2 and Task 3 HTTP clients calling Task 1 `/api/v1/ask`, then explain the handoff from knowledge retrieval to grounded drafts and scope decisions. State that Task 1 live sitemap connectivity and the two-model comparison remain unverified. |

## Evidence Preparation and Safe Rehearsal

No saved workflow screenshots or output captures are currently included in the repository. Prepare genuine captures by using a disposable copy of the project, with its own copy of the Task 1 database. `run.bat` sets `TASK1_SCHEDULED_SYNC_ENABLED=false` for a safe demo start. Keep the live project's database and services separate. Start the copied services only when ports 8000, 3000, and 8001 are free; do not run the copied `run.bat` alongside the live services. The current machine's Node.js compatibility check succeeds, so no preload shim is required. Task 2 drafts and reviews, Task 3 pipeline/diff/approval actions, and Task 1 questions that may escalate should be demonstrated only in the disposable copy or with captured output. The tests are not ready-made screenshots; use `test_all.bat`, which creates a temporary database and Task 1 integration port.

For a 10-minute rehearsal, keep the three workflow demonstrations to captured or isolated-copy outputs. Show the Task 1 refusal/escalation as the failure case. To demonstrate end-to-end integration, show the Task 2 and Task 3 HTTP client code and a captured response containing Task 1 evidence. Do not use Task 3 `/health` against the live system: it also calls Task 1.

---

## 2. Minute 0:00 - 0:30 Face Intro Script (Verbatim)

> *"Hi everyone, my name is [Your Name], and this is my submission for the BusinessLabs AI Tech Consultant Capstone. I built this project around three operational problems for a software agency: finding reliable product knowledge, reviewing repetitive customer email, and turning discovery conversations into accurate scopes of work. Today, I'll walk through my three connected services: the Knowledge Brain in Python, the Inbox Agent in strict TypeScript, and the Meeting to Scope pipeline."*

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

