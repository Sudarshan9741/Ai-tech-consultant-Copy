import { CustomerEmail, DraftReply, GroundingSource } from "./types.js";
import { emailClassifier } from "./classifier.js";
import { knowledgeClient } from "./knowledgeClient.js";
import { autonomyEngine } from "./autonomyEngine.js";

export class DraftEngine {
  async generateDraft(email: CustomerEmail): Promise<DraftReply> {
    const classification = emailClassifier.classify(email);
    const category = classification.category;

    let kbQuestion = email.subject;
    if (email.body.length > 10) {
      kbQuestion = `${email.subject} ${email.body.slice(0, 150)}`;
    }

    // Call Task 1 Knowledge Brain HTTP API
    const kbResult = await knowledgeClient.ask(kbQuestion);

    const sources: GroundingSource[] = kbResult.sources.map(s => ({
      title: s.title,
      url: s.url,
      snippet: s.snippet
    }));

    const draftBody = this.composeEmailBody(
      email.customerName,
      category,
      email.body,
      kbResult.answered,
      kbResult.answer,
      sources
    );

    const canAutoSend = autonomyEngine.canAutoSend(category, classification.confidence);

    return {
      emailId: email.id,
      category,
      confidence: classification.confidence,
      draftBody,
      groundingSources: sources,
      knowledgeFound: kbResult.answered,
      escalationId: kbResult.escalation_id,
      requiresHumanApproval: !canAutoSend,
      canAutoSend
    };
  }

  private composeEmailBody(
    name: string,
    category: string,
    inquiry: string,
    hasKbAnswer: boolean,
    kbAnswer: string,
    sources: GroundingSource[]
  ): string {
    const greeting = `Hi ${name || "there"},\n\nThank you for reaching out to our support team.`;
    const signoff = `\n\nBest regards,\nAI Tech Consultant Team\nBrilliant Directories Solutions`;

    if (hasKbAnswer) {
      let citations = "";
      if (sources.length > 0) {
        citations = "\n\nFor full step-by-step documentation, please refer to:\n" +
          sources.map(s => `• ${s.title}: ${s.url}`).join("\n");
      }
      return `${greeting}\n\n${kbAnswer}${citations}${signoff}`;
    }

    // If Knowledge Brain lacks direct answer or category requires consultation
    switch (category) {
      case "BILLING_REFUND":
        return `${greeting}\n\nWe have received your billing and refund request regarding:\n"${inquiry.slice(0, 100)}..."\n\nOur billing manager is reviewing your account transaction history and will process any eligible adjustment or cancellation within 1 business day.${signoff}`;

      case "PROJECT_REQUEST":
        return `${greeting}\n\nThank you for your project inquiry! Our technical consultants have logged your requirements:\n"${inquiry.slice(0, 120)}..."\n\nWe are currently evaluating whether this can be configured using built-in platform settings or requires a custom development scope. A senior consultant will share a breakdown and estimate shortly.${signoff}`;

      case "QUOTE":
        return `${greeting}\n\nThank you for requesting an estimate. We are reviewing the scope details to calculate a transparent quote and developer hour estimate. You will receive our formal proposal within 24 hours.${signoff}`;

      case "COMPLAINT":
        return `${greeting}\n\nWe sincerely apologize for any disruption or inconvenience you experienced. Your ticket has been marked URGENT and escalated directly to our senior engineering lead for immediate review.${signoff}`;

      case "FOLLOW_UP":
        return `${greeting}\n\nThank you for following up with us. We are currently actively progressing your request and will provide our next status update shortly.${signoff}`;

      default:
        return `${greeting}\n\nWe have received your technical inquiry. Our engineering team is reviewing the specifics and will follow up with verified instructions shortly.${signoff}`;
    }
  }
}

export const draftEngine = new DraftEngine();
