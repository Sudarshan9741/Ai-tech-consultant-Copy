import { CustomerEmail, EmailCategory } from "./types.js";

export interface ClassificationResult {
  category: EmailCategory;
  confidence: number;
  reason: string;
}

export class EmailClassifier {
  classify(email: CustomerEmail): ClassificationResult {
    const text = `${email.subject} ${email.body}`.toLowerCase();

    // 1. BILLING_REFUND
    if (
      text.includes("refund") ||
      text.includes("cancel subscription") ||
      text.includes("cancel my account") ||
      text.includes("double charge") ||
      text.includes("billing issue") ||
      text.includes("chargeback") ||
      text.includes("receipt") ||
      text.includes("invoice")
    ) {
      return {
        category: "BILLING_REFUND",
        confidence: 0.95,
        reason: "Matched billing, transaction, or refund keywords."
      };
    }

    // 2. COMPLAINT
    if (
      text.includes("urgent") ||
      text.includes("terrible") ||
      text.includes("not working at all") ||
      text.includes("down") ||
      text.includes("broken") ||
      text.includes("disappointed") ||
      text.includes("unacceptable") ||
      text.includes("lawsuit") ||
      text.includes("escalate")
    ) {
      return {
        category: "COMPLAINT",
        confidence: 0.90,
        reason: "Detected high-urgency complaint or dissatisfaction sentiment."
      };
    }

    // 3. QUOTE
    if (
      text.includes("how much") ||
      text.includes("price quote") ||
      text.includes("pricing") ||
      text.includes("estimate") ||
      text.includes("cost to build") ||
      text.includes("hourly rate") ||
      text.includes("budget")
    ) {
      return {
        category: "QUOTE",
        confidence: 0.92,
        reason: "Customer explicitly requested pricing, estimate, or project quote."
      };
    }

    // 4. FOLLOW_UP
    if (
      text.includes("any update") ||
      text.includes("following up") ||
      text.includes("checking in on") ||
      text.includes("status of") ||
      text.includes("previous email") ||
      text.includes("ticket #") ||
      text.includes("heard back")
    ) {
      return {
        category: "FOLLOW_UP",
        confidence: 0.88,
        reason: "Inquiry references prior communication or status follow-up."
      };
    }

    // 5. PROJECT_REQUEST
    if (
      text.includes("build a new") ||
      text.includes("custom feature") ||
      text.includes("redesign") ||
      text.includes("new website") ||
      text.includes("develop") ||
      text.includes("integrate custom") ||
      text.includes("hire your team") ||
      text.includes("scope of work")
    ) {
      return {
        category: "PROJECT_REQUEST",
        confidence: 0.89,
        reason: "Identified new project or custom development inquiry."
      };
    }

    // 6. HOW_TO (Default for knowledge queries)
    return {
      category: "HOW_TO",
      confidence: 0.85,
      reason: "General product how-to or configuration inquiry."
    };
  }
}

export const emailClassifier = new EmailClassifier();
