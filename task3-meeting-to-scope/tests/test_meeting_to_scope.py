import asyncio
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.transcripts import SAMPLE_TRANSCRIPTS
from app.agents.clarifier_agent import clarifier_agent
from app.agents.platform_checker import platform_checker_agent
from app.agents.estimation_agent import estimation_agent
from app.agents.proposal_agent import proposal_agent
from app.agents.diff_agent import diff_agent
from app.knowledge_client import knowledge_client, KnowledgeBrainUnavailable
from app.models import Requirement

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "task3-meeting-to-scope"
    assert data["transcripts_available"] >= 3
    assert data["task1_connected"] is True

def test_clarifier_extracts_requirements():
    meeting1 = SAMPLE_TRANSCRIPTS[0]
    reqs = clarifier_agent.extract_requirements(meeting1)
    assert len(reqs) == 5
    assert len({r.title for r in reqs}) == len(reqs)
    
    titles = [r.title for r in reqs]
    assert any("Zip Code & Radius Search" in t for t in titles)
    assert any("Recurring Subscription Billing" in t for t in titles)
    assert any("Membership Privileges" in t for t in titles)
    assert any("Telemedicine" in t for t in titles)

    followup_titles = [r.title for r in clarifier_agent.extract_requirements(SAMPLE_TRANSCRIPTS[1])]
    assert "Automated Recurring Subscription Billing" in followup_titles
    assert "PayPal Payment Gateway Integration" in followup_titles
    assert "Google Calendar Appointment Booking Sync" in followup_titles
    assert not any("Epic EHR" in title for title in followup_titles)
    
    # Check that speaker references and quotes are preserved
    first_req = reqs[0]
    assert first_req.speaker in ["Jennifer (Client CEO)", "Alex (Client CTO)", "Participant"]
    assert len(first_req.transcript_quote) > 20
    assert first_req.line_reference > 0

def test_platform_checker_identifies_native_vs_custom():
    meeting1 = SAMPLE_TRANSCRIPTS[0]
    reqs = clarifier_agent.extract_requirements(meeting1)
    checks = asyncio.run(platform_checker_agent.check_requirements(reqs))

    # Search and Billing must be recognized as native settings
    search_req = next(r for r in reqs if "Radius" in r.title)
    billing_req = next(r for r in reqs if "Recurring" in r.title)
    telemed_req = next(r for r in reqs if "Telemedicine" in r.title)

    assert checks[search_req.id].is_native_setting is True
    assert "Settings > General Settings" in checks[search_req.id].setting_path
    assert checks[search_req.id].hours_saved >= 10.0

    assert checks[billing_req.id].is_native_setting is True
    assert "Payment Settings" in checks[billing_req.id].setting_path

    # Telemedicine is custom development
    assert checks[telemed_req.id].is_native_setting is False
    assert checks[telemed_req.id].setting_path is None

def test_estimation_and_proposal_pipeline():
    meeting1 = SAMPLE_TRANSCRIPTS[0]
    reqs = clarifier_agent.extract_requirements(meeting1)
    
    # Run pipeline via HTTP endpoint
    resp = client.post("/api/v1/pipeline/process", json={"meeting_id": "meeting-001"})
    assert resp.status_code == 200
    sow = resp.json()

    assert sow["sow_id"] == "SOW-MEETING-001"
    assert sow["client_name"] == "Apex Healthcare Network"
    assert len(sow["native_config_tasks"]) == 3
    assert len(sow["custom_code_tasks"]) == 2
    assert len(sow["native_config_tasks"]) + len(sow["custom_code_tasks"]) == 5
    assert sow["total_expected_hours"] > 20.0
    assert sow["estimated_budget_usd"] > 1000.0
    assert sow["human_approved"] is False  # Safe default

def test_human_approval_gate():
    # Process SOW
    client.post("/api/v1/pipeline/process", json={"meeting_id": "meeting-001"})

    # Approve SOW
    approve_resp = client.post(
        "/api/v1/proposals/SOW-MEETING-001/approve",
        json={"reviewer_name": "Dave (Senior Consultant)"}
    )
    assert approve_resp.status_code == 200
    data = approve_resp.json()
    assert data["status"] == "approved"
    assert data["approved_by"] == "Dave (Senior Consultant)"
    assert data["client_ready"] is True

def test_scope_diff_detects_meeting2_changes_and_change_orders():
    resp = client.post(
        "/api/v1/pipeline/diff",
        json={"baseline_meeting_id": "meeting-001", "followup_meeting_id": "meeting-002"}
    )
    assert resp.status_code == 200
    diff = resp.json()

    assert diff["baseline_meeting_id"] == "meeting-001"
    assert diff["followup_meeting_id"] == "meeting-002"
    assert len(diff["diff_items"]) >= 4

    statuses = [item["status"] for item in diff["diff_items"]]
    assert "UNCHANGED" in statuses
    assert "MODIFIED" in statuses
    assert "DEFERRED" in statuses
    assert "OUT_OF_SCOPE" in statuses

    # AI Symptom checker is brand new / out-of-scope and flags change order
    symptom_item = next(item for item in diff["diff_items"] if "symptom" in item["task_name"].lower())
    assert symptom_item["status"] == "OUT_OF_SCOPE"
    assert symptom_item["change_order_required"] is True
    calendar_item = next(item for item in diff["diff_items"] if "calendar" in item["task_name"].lower())
    assert calendar_item["status"] == "OUT_OF_SCOPE"
    assert calendar_item["change_order_required"] is True
    paypal_item = next(item for item in diff["diff_items"] if "paypal" in item["task_name"].lower())
    assert paypal_item["status"] == "OUT_OF_SCOPE"
    assert paypal_item["change_order_required"] is True
    epic_item = next(item for item in diff["diff_items"] if "epic" in item["task_name"].lower())
    assert epic_item["delta_hours"] < 0
    assert epic_item["status"] == "DEFERRED"
    assert "Deferred to Phase 2" in epic_item["explanation"]
    assert diff["change_order_required"] is True

def test_invalid_transcript_inputs():
    resp = client.post("/api/v1/pipeline/process", json={"meeting_id": "meeting-nonexistent"})
    assert resp.status_code == 404

    resp = client.post("/api/v1/pipeline/diff", json={"baseline_meeting_id": "invalid", "followup_meeting_id": "invalid2"})
    assert resp.status_code == 404

def test_pipeline_reports_task1_failure_instead_of_returning_unverified_sow(monkeypatch):
    async def fail_task1(_query):
        raise KnowledgeBrainUnavailable("Task 1 Knowledge Brain timed out after 10 seconds.")

    monkeypatch.setattr(knowledge_client, "check_platform_capability", fail_task1)
    resp = client.post("/api/v1/pipeline/process", json={"meeting_id": "meeting-001"})

    assert resp.status_code == 502
    assert resp.json()["detail"] == "Task 1 Knowledge Brain timed out after 10 seconds."

def test_twenty_evaluation_benchmark_cases():
    """Evaluate 20 requirements through the actual Task 1-backed platform checker."""
    eval_cases = [
        # (Feature title, expected is_native_setting)
        ("Zip code distance search and radius filtering", True),
        ("Stripe credit card recurring subscription billing", True),
        ("Membership plan post publishing permissions", True),
        ("Automatic buyer lead routing by category and location", True),
        ("Mass email newsletter campaign to directory members", True),
        ("Custom domain pointing with A record and DNS", True),
        ("Free SSL certificate installation via Let's Encrypt", True),
        ("Member review submission with admin moderation", True),
        ("REST API key generation for Zapier webhook trigger", True),
        ("Member refund and subscription cancellation workflow", True),
        ("PayPal secondary payment gateway connection", True),
        ("Default website administrative contact email", True),
        
        # Custom software engineering items
        ("HIPAA-compliant WebRTC video consultation microservice", False),
        ("Epic EHR HL7 FHIR hospital database automated credential sync", False),
        ("Homepage AI symptom checker and diagnosis assistant widget", False),
        ("IoT blood analyzer automated webhook ingestion pipeline", False),
        ("Custom 3D Mapbox interactive architectural portfolio viewer", False),
        ("Automated vehicle VIN decoder integration with NHTSA API", False),
        ("Multi-vendor calendar two-way sync with Google Calendar API", False),
        ("Custom biometric WebAuthn security hardware key authentication", False),
    ]

    requirements = [
        Requirement(
            id=f"BENCH-{idx:02d}",
            title=title,
            description=title,
            category="FUNCTIONAL",
            speaker="Benchmark",
            transcript_quote=title,
            line_reference=idx
        )
        for idx, (title, _) in enumerate(eval_cases, start=1)
    ]

    start_time = time.perf_counter()
    actual_checks = asyncio.run(platform_checker_agent.check_requirements(requirements))
    total_latency_ms = (time.perf_counter() - start_time) * 1000.0
    correct_classifications = sum(
        actual_checks[req.id].is_native_setting == expected_native
        for req, (_, expected_native) in zip(requirements, eval_cases)
    )
    mismatches = [
        (req.title, expected_native, actual_checks[req.id].is_native_setting, actual_checks[req.id].confidence)
        for req, (_, expected_native) in zip(requirements, eval_cases)
        if actual_checks[req.id].is_native_setting != expected_native
    ]

    accuracy = correct_classifications / len(eval_cases)
    avg_latency = total_latency_ms / len(eval_cases)

    print(f"\n[Task 3 Benchmark] 20 Requirements Evaluated: Accuracy = {accuracy*100:.1f}%, Avg Latency = {avg_latency:.2f}ms")
    assert accuracy == 1.0, f"Expected 100% accuracy, got {accuracy*100:.1f}%; mismatches: {mismatches}"
