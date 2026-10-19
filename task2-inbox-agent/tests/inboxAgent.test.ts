import { describe, it, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { CustomerEmailSchema } from "../src/types.js";
import { emailClassifier } from "../src/classifier.js";
import { AutonomyEngine, autonomyEngine } from "../src/autonomyEngine.js";
import { draftEngine } from "../src/drafter.js";
import { SAMPLE_EMAILS } from "../src/dataset.js";
import { knowledgeClient } from "../src/knowledgeClient.js";
import { InboxStore } from "../src/store.js";

describe("Task 2: Customer Inbox Agent", () => {
  let autonomy: AutonomyEngine;

  beforeEach(() => {
    autonomy = new AutonomyEngine(20);
  });

  it("validates strict CustomerEmail schema with Zod", () => {
    const validEmail = {
      id: "email-test-01",
      from: "alice@example.com",
      customerName: "Alice",
      subject: "Refund query",
      body: "How do I process a refund?",
      receivedAt: new Date().toISOString()
    };
    const parsed = CustomerEmailSchema.safeParse(validEmail);
    assert.equal(parsed.success, true);

    const invalidEmail = {
      id: "email-test-02",
      from: "not-an-email",
      customerName: "Bob",
      subject: "Test",
      body: "Test",
      receivedAt: "invalid-date"
    };
    const invalidParsed = CustomerEmailSchema.safeParse(invalidEmail);
    assert.equal(invalidParsed.success, false);

    const invalidDate = CustomerEmailSchema.safeParse({ ...validEmail, receivedAt: "not-a-date" });
    assert.equal(invalidDate.success, false);
  });

  it("accurately classifies diverse customer email intents", () => {
    assert.equal(SAMPLE_EMAILS.length, 61);
    const billingEmail = SAMPLE_EMAILS.find(e => e.id === "email-011")!;
    const projectEmail = SAMPLE_EMAILS.find(e => e.id === "email-021")!;
    const quoteEmail = SAMPLE_EMAILS.find(e => e.id === "email-029")!;
    const complaintEmail = SAMPLE_EMAILS.find(e => e.id === "email-037")!;
    const followUpEmail = SAMPLE_EMAILS.find(e => e.id === "email-044")!;
    const howToEmail = SAMPLE_EMAILS.find(e => e.id === "email-002")!;

    assert.equal(emailClassifier.classify(billingEmail).category, "BILLING_REFUND");
    assert.equal(emailClassifier.classify(projectEmail).category, "PROJECT_REQUEST");
    assert.equal(emailClassifier.classify(quoteEmail).category, "QUOTE");
    assert.equal(emailClassifier.classify(complaintEmail).category, "COMPLAINT");
    assert.equal(emailClassifier.classify(followUpEmail).category, "FOLLOW_UP");
    assert.equal(emailClassifier.classify(howToEmail).category, "HOW_TO");
    const failedPaymentEmail = SAMPLE_EMAILS.find(e => e.id === "email-014")!;
    assert.equal(emailClassifier.classify(failedPaymentEmail).category, "BILLING_REFUND");
    const howToEmails = SAMPLE_EMAILS.filter(email => emailClassifier.classify(email).category === "HOW_TO");
    assert.ok(howToEmails.length >= 20, "The sample inbox must contain 20 distinct emails in a category to demonstrate the gate");
  });

  it("integrates with Task 1 Knowledge Brain HTTP API to ground drafts", async () => {
    // Health check on Task 1
    const health = await knowledgeClient.checkHealth();
    assert.equal(health.status, "healthy");

    // Ask how-to question
    const howToEmail = SAMPLE_EMAILS.find(e => e.id === "email-001")!; // Refund question
    const draft = await draftEngine.generateDraft(howToEmail);

    assert.equal(draft.emailId, howToEmail.id);
    assert.equal(draft.knowledgeFound, true);
    assert.ok(draft.groundingSources.length > 0);
    assert.ok(draft.draftBody.includes("Brilliant Directories"));
    assert.ok(draft.draftBody.includes("Finance > Transaction History") || draft.draftBody.toLowerCase().includes("refund"));
    assert.equal(draft.requiresHumanApproval, true); // Safe default
  });

  it("enforces strict 20 consecutive unchanged approval gate for progressive autonomy", () => {
    const category = "HOW_TO";

    // 1. Simulate 19 consecutive approvals
    for (let i = 1; i <= 19; i++) {
      const state = autonomy.recordAction(category, "APPROVED_UNCHANGED");
      assert.equal(state.consecutiveUnchangedCount, i);
      assert.equal(state.isAutonomous, false, `At run ${i}, autonomy should still be false`);
    }

    // 2. The 20th consecutive approval unlocks autonomy
    const unlockedState = autonomy.recordAction(category, "APPROVED_UNCHANGED");
    assert.equal(unlockedState.consecutiveUnchangedCount, 20);
    assert.equal(unlockedState.isAutonomous, true, "20th run MUST unlock autonomy for the category");

    // 3. Human edits a draft (EDITED_AND_APPROVED) -> autonomy must immediately be revoked and streak reset to 0
    const resetState = autonomy.recordAction(category, "EDITED_AND_APPROVED", "User adjusted phrasing");
    assert.equal(resetState.consecutiveUnchangedCount, 0, "Streak must reset to 0 on human edit");
    assert.equal(resetState.isAutonomous, false, "Autonomy must be revoked immediately upon human edit");
    assert.ok(resetState.lastResetReason?.includes("Autonomy revoked"));
  });

  it("resets streak to 0 immediately on draft rejection", () => {
    const category = "BILLING_REFUND";

    // Build up a 15-run streak
    for (let i = 1; i <= 15; i++) {
      autonomy.recordAction(category, "APPROVED_UNCHANGED");
    }
    assert.equal(autonomy.getState(category).consecutiveUnchangedCount, 15);

    // Human rejects the 16th draft
    const state = autonomy.recordAction(category, "REJECTED", "Wrong tone for enterprise account");
    assert.equal(state.consecutiveUnchangedCount, 0);
    assert.equal(state.isAutonomous, false);
    assert.ok(state.lastResetReason?.includes("rejected"));
  });

  it("only counts an unchanged approval for an existing, exactly unchanged draft and keeps review history", () => {
    const store = new InboxStore();
    const email = SAMPLE_EMAILS[0]!;
    const draft = {
      emailId: email.id,
      category: "HOW_TO" as const,
      confidence: 0.9,
      draftBody: "Verified reply",
      groundingSources: [],
      knowledgeFound: true,
      escalationId: null,
      requiresHumanApproval: true,
      canAutoSend: false
    };

    assert.throws(() => store.recordReview(email.id, "APPROVED_UNCHANGED", "Verified reply"), /Generate a draft/);
    store.setDraft(email.id, draft);
    assert.throws(() => store.recordReview(email.id, "APPROVED_UNCHANGED", "Changed reply"), /match exactly/);
    assert.equal(autonomyEngine.getState("HOW_TO").consecutiveUnchangedCount, 0);

    const audit = store.recordReview(email.id, "APPROVED_UNCHANGED", draft.draftBody);
    assert.equal(audit.originalDraft, draft.draftBody);
    assert.equal(audit.finalBody, draft.draftBody);
    assert.equal(store.getAuditLogs().length, 1);
    assert.equal(autonomyEngine.getState("HOW_TO").consecutiveUnchangedCount, 1);
    assert.throws(() => store.recordReview(email.id, "APPROVED_UNCHANGED", draft.draftBody), /only count once/);
    assert.equal(autonomyEngine.getState("HOW_TO").consecutiveUnchangedCount, 1);
  });

  it("rejects non-boolean autonomous-send authorization input", async () => {
    const previousNodeEnv = process.env.NODE_ENV;
    const previousAuthorization = autonomyEngine.allowAutonomousSend;
    process.env.NODE_ENV = "test";
    const { app } = await import("../src/server.js");
    const server = app.listen(0);
    try {
      await new Promise<void>(resolve => server.once("listening", resolve));
      const address = server.address();
      assert.ok(address && typeof address !== "string");
      const response = await fetch(`http://127.0.0.1:${address.port}/api/autonomy/toggle-safe-send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: "false" })
      });
      assert.equal(response.status, 400);
      assert.equal(autonomyEngine.allowAutonomousSend, previousAuthorization);
    } finally {
      await new Promise<void>((resolve, reject) => server.close(err => err ? reject(err) : resolve()));
      if (previousNodeEnv === undefined) delete process.env.NODE_ENV;
      else process.env.NODE_ENV = previousNodeEnv;
    }
  });

  it("renders autonomy status and a clear load error on the dashboard", async () => {
    const previousNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "test";
    const { app } = await import("../src/server.js");
    const server = app.listen(0);
    try {
      await new Promise<void>(resolve => server.once("listening", resolve));
      const address = server.address();
      assert.ok(address && typeof address !== "string");
      const response = await fetch(`http://127.0.0.1:${address.port}/`);
      assert.equal(response.status, 200);
      const html = await response.text();
      assert.match(html, /status\.innerText = data\.system_allow_auto_send/);
      assert.match(html, /Human review required/);
      assert.match(html, /Unable to load autonomy metrics/);
    } finally {
      await new Promise<void>((resolve, reject) => server.close(err => err ? reject(err) : resolve()));
      if (previousNodeEnv === undefined) delete process.env.NODE_ENV;
      else process.env.NODE_ENV = previousNodeEnv;
    }
  });

  it("safeguard: never auto-sends without both threshold reached AND explicit system authorization", () => {
    const category = "QUOTE";

    // Even if autonomy threshold is reached...
    for (let i = 1; i <= 20; i++) {
      autonomy.recordAction(category, "APPROVED_UNCHANGED");
    }
    assert.equal(autonomy.getState(category).isAutonomous, true);

    // Without explicit system authorization (allowAutonomousSend = false), canAutoSend MUST be false
    autonomy.allowAutonomousSend = false;
    assert.equal(autonomy.canAutoSend(category, 0.95), false);

    // Only when BOTH the category is autonomous AND system authorization is active, auto-send is allowed
    autonomy.allowAutonomousSend = true;
    assert.equal(autonomy.canAutoSend(category, 0.95), true);
  });

  it("evaluates at least 20 customer email benchmark cases and reports latency & accuracy", async () => {
    const testCases = SAMPLE_EMAILS.slice(0, 20);
    assert.equal(testCases.length, 20);

    let classifiedCorrectly = 0;
    let totalLatencyMs = 0;

    for (const email of testCases) {
      const expectedCategory = email.id === "email-001" || /^email-01[1-9]$/.test(email.id) || email.id === "email-020"
        ? "BILLING_REFUND"
        : "HOW_TO";
      const startTime = performance.now();
      const draft = await draftEngine.generateDraft(email);
      const latency = performance.now() - startTime;
      totalLatencyMs += latency;

      assert.ok(draft.draftBody.length > 50);
      assert.ok(draft.confidence > 0.7);
      assert.equal(draft.category, expectedCategory, `${email.id} should classify as ${expectedCategory}`);
      classifiedCorrectly += draft.category === expectedCategory ? 1 : 0;

      // Verify draft contains customer name
      assert.ok(draft.draftBody.includes(email.customerName));
    }

    const avgLatency = (totalLatencyMs / testCases.length).toFixed(2);
    const accuracy = classifiedCorrectly / testCases.length;
    console.log(`\n[Task 2 Benchmark] 20 Emails Evaluated: Accuracy = ${(accuracy * 100).toFixed(1)}%, Avg Latency = ${avgLatency}ms`);
    assert.ok(accuracy >= 0.90, `Expected >= 90% intent accuracy, got ${(accuracy * 100).toFixed(1)}%`);
  });
});
