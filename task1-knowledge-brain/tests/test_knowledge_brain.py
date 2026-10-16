import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage
from app.vector_store import vector_store

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "task1-knowledge-brain"
    assert data["active_articles"] >= 10
    assert data["total_chunks"] >= 10

def test_ask_refund_question():
    payload = {"question": "How do I process a refund for a member?"}
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answered"] is True
    assert data["confidence"] > 0.25
    assert len(data["sources"]) > 0
    assert any("refund" in s["title"].lower() or "transaction" in s["title"].lower() for s in data["sources"])
    assert "Finance > Transaction History" in data["answer"] or "refund" in data["answer"].lower()

def test_ask_radius_search_question():
    payload = {"question": "Can I configure radius search and zip code filtering for member search?"}
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answered"] is True
    assert data["confidence"] > 0.25
    assert any("radius" in s["title"].lower() or "search" in s["title"].lower() for s in data["sources"])

def test_image_citations_included():
    payload = {"question": "Where is the payment gateway setup for Stripe?"}
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answered"] is True
    # Verify that image metadata is present
    assert len(data["images"]) > 0
    img = data["images"][0]
    assert "url" in img
    assert "caption" in img
    assert img["url"].startswith("http")

def test_unknown_question_triggers_escalation():
    payload = {"question": "What is the orbital trajectory of the James Webb telescope in astrophysics?"}
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answered"] is False
    assert data["escalation_id"] is not None
    assert "insufficient information" in data["answer"].lower()

    # Verify escalation was created in DB
    esc_id = data["escalation_id"]
    esc_response = client.get(f"/api/v1/escalations?status=pending")
    assert esc_response.status_code == 200
    esc_list = esc_response.json()["escalations"]
    assert any(e["id"] == esc_id for e in esc_list)

def test_resolve_escalation_flows_back_to_memory():
    # 1. Ask novel question that fails
    unique_token = int(time.time() * 1000)
    novel_q = f"QuestionNonce_{unique_token} AlphaToken_{unique_token} UnknownTerm_{unique_token}?"
    ask_resp = client.post("/api/v1/ask", json={"question": novel_q})
    assert ask_resp.status_code == 200
    esc_id = ask_resp.json()["escalation_id"]
    assert esc_id is not None

    # 2. Human expert resolves ticket
    expert_answer = f"The verified resolution for QuestionNonce_{unique_token} requires setting AlphaToken_{unique_token} to active."
    resolve_resp = client.post(
        f"/api/v1/escalations/{esc_id}/resolve",
        json={"expert_response": expert_answer}
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"

    # 3. Query again - brain should now know the answer!
    second_ask = client.post("/api/v1/ask", json={"question": novel_q})
    assert second_ask.status_code == 200
    sec_data = second_ask.json()
    assert sec_data["answered"] is True
    assert f"AlphaToken_{unique_token}" in sec_data["answer"]

def test_query_semantic_endpoint():
    response = client.post("/api/v1/query", json={"query": "newsletter mass email campaigns", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    first_result = data["results"][0]
    assert first_result["score"] > 0.0
    assert "email" in first_result["title"].lower()

def test_invalid_inputs():
    # Empty question
    resp = client.post("/api/v1/ask", json={"question": ""})
    assert resp.status_code == 422

    # Query with negative top_k
    resp = client.post("/api/v1/query", json={"query": "refund", "top_k": -1})
    assert resp.status_code == 422

    # Resolving non-existent escalation
    resp = client.post("/api/v1/escalations/999999/resolve", json={"expert_response": "dummy"})
    assert resp.status_code == 404

def test_deleted_article_purge():
    # Temporarily mark an article deleted
    test_url = "https://support.brilliantdirectories.com/support/solutions/articles/5000756720-member-reviews-and-rating-settings"
    storage.mark_article_deleted(test_url)
    vector_store.reload()

    # Query specifically for reviews - the deleted article chunks should not appear
    chunks = storage.get_all_active_chunks()
    assert not any(c["article_url"] == test_url for c in chunks)

    # Restore article for subsequent tests
    storage.save_article(
        url=test_url,
        title="Configuring Member Reviews, Star Ratings, and Moderation",
        category="Reviews",
        folder="Review Settings",
        content="Customer reviews and star ratings can be enabled or restricted on a per-membership plan basis in Settings > General Settings > Reviews.",
        images=[]
    )
    chunks_text = ["Customer reviews and star ratings can be enabled or restricted on a per-membership plan basis in Settings > General Settings > Reviews."]
    storage.save_chunks(test_url, "Configuring Member Reviews, Star Ratings, and Moderation", chunks_text, [])
    vector_store.reload()

def test_twenty_evaluation_benchmark_cases():
    """Run 20 discrete evaluation cases measuring accuracy, confidence, and latency."""
    eval_cases = [
        # In-domain questions (expected answered = True)
        ("How to process a refund for a member in Brilliant Directories?", True),
        ("Where can I configure Stripe API keys and webhooks?", True),
        ("How to set up radius search and zip code distance filtering?", True),
        ("Can I send a mass email campaign to my members?", True),
        ("How do I connect my custom domain name with an A record?", True),
        ("Where do I install the free SSL certificate in Domain Manager?", True),
        ("How to configure membership plan post publishing privileges?", True),
        ("How does automatic lead matching work by category and location?", True),
        ("Where can I set member reviews to require admin moderation?", True),
        ("How to generate REST API keys for external Zapier integration?", True),
        ("Can I cancel recurring subscriptions when refunding a transaction?", True),
        ("Where is the Default Website Email Address set in General Settings?", True),
        ("Can members post classifieds and events on free plans?", True),
        ("What payment gateways are natively supported besides Stripe?", True),
        ("How to prevent emails from going to spam using SPF and DKIM?", True),

        # Out-of-domain questions (expected answered = False, escalation created)
        ("How to configure Kubernetes ingress controller for Redis cluster?", False),
        ("What is the recipe for baking chocolate sourdough bread?", False),
        ("How to train a quantum neural network using Qiskit?", False),
        ("What are the torque specifications for a 2018 Honda Civic cylinder head?", False),
        ("How to write a compiler in Haskell using LLVM backend?", False),
    ]

    correct_predictions = 0
    total_latency_ms = 0.0

    for query, expected_answered in eval_cases:
        start_time = time.time()
        resp = client.post("/api/v1/ask", json={"question": query})
        latency = (time.time() - start_time) * 1000.0
        total_latency_ms += latency

        assert resp.status_code == 200
        data = resp.json()
        if data["answered"] == expected_answered:
            correct_predictions += 1

    accuracy = correct_predictions / len(eval_cases)
    avg_latency = total_latency_ms / len(eval_cases)

    # Must meet high accuracy benchmark (at least 90%)
    assert accuracy >= 0.90, f"Expected >= 90% accuracy, got {accuracy*100:.1f}%"
    print(f"\n[Task 1 Benchmark] 20 Cases: Accuracy = {accuracy*100:.1f}%, Avg Latency = {avg_latency:.1f}ms")
