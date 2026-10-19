# AI Assistance & Decision Log

## Five prompt excerpts

These excerpts are from the available project conversation. They preserve the requests’ intent but are not a complete export of the original messages.

1. **Task 2 audit:** “Verify Task 2 against the assignment requirements: 50 realistic emails, classification, Knowledge Brain API integration, structured reply drafts, human review and feedback history, and the 20-consecutive-approval safeguard.”
2. **Task 3 debugging:** “Reproduce the failure with one request and identify the exact cause before editing. Apply the smallest necessary fix.”
3. **Capstone audit:** “Perform a complete final audit of my existing AI Tech Consultant capstone against the original Business Labs assignment requirements.”
4. **Task 1 scheduler:** “Add a configurable daily scheduler that invokes the existing incremental synchronization process automatically.”
5. **Model evaluation:** “Design a reproducible comparison using the same evaluation inputs for both models.”

## AI suggestion changed or rejected

**Suggestion:** Use a more complex setup with Docker, Milvus, Redis, and Celery.

**Decision:** Rejected that setup and kept the implementation simpler.

**Reason:** Prioritized a working, testable three-task MVP with limited time instead of introducing additional infrastructure and setup complexity.

## Final audit work (2026-10-19)

- Prompt: “Add sitemap-fetch retry behavior if missing. Do not run a live sync automatically during development or testing.”
- Tools used: VS Code workspace file inspection, PowerShell repository checks, `apply_patch`, pytest, and the TypeScript compiler. No live sitemap request or paid model request was made.
- Implemented: bounded sitemap retry/backoff, a mocked retry regression test, configurable Task 1 test database paths, isolated aggregate-test port selection, and safe startup defaults.
- Verification: Task 1 scheduler/retry tests passed 7/7; Task 2 `npm run lint` passed. The model comparison remains incomplete because no authorized second model endpoint or Anthropic credential was available.
