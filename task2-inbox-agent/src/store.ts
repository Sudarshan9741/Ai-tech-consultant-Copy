import { AuditRecord, CustomerEmail, DraftReply, ApprovalAction } from "./types.js";
import { SAMPLE_EMAILS } from "./dataset.js";
import { autonomyEngine } from "./autonomyEngine.js";

export interface EmailStatusRecord {
  status: "UNREVIEWED" | "APPROVED_UNCHANGED" | "EDITED_AND_APPROVED" | "REJECTED";
  finalBody?: string;
  reviewedAt?: string;
  reviewedBy?: string;
}

export class InboxStore {
  private emails: Map<string, CustomerEmail> = new Map();
  private drafts: Map<string, DraftReply> = new Map();
  private statuses: Map<string, EmailStatusRecord> = new Map();
  private auditLogs: AuditRecord[] = [];

  constructor() {
    this.reset();
  }

  reset() {
    this.emails.clear();
    this.drafts.clear();
    this.statuses.clear();
    this.auditLogs = [];

    for (const email of SAMPLE_EMAILS) {
      this.emails.set(email.id, email);
      this.statuses.set(email.id, { status: "UNREVIEWED" });
    }
    autonomyEngine.resetAll();
  }

  getAllEmails(): CustomerEmail[] {
    return Array.from(this.emails.values());
  }

  getEmail(id: string): CustomerEmail | undefined {
    return this.emails.get(id);
  }

  setDraft(emailId: string, draft: DraftReply) {
    this.drafts.set(emailId, draft);
  }

  getDraft(emailId: string): DraftReply | undefined {
    return this.drafts.get(emailId);
  }

  getStatus(emailId: string): EmailStatusRecord {
    return this.statuses.get(emailId) || { status: "UNREVIEWED" };
  }

  recordReview(
    emailId: string,
    action: ApprovalAction,
    finalBody: string,
    reviewedBy = "Human Reviewer",
    reason?: string
  ): AuditRecord {
    const email = this.emails.get(emailId);
    if (!email) {
      throw new Error(`Email ${emailId} not found`);
    }

    const draft = this.drafts.get(emailId);
    const category = draft ? draft.category : "HOW_TO";
    const originalDraft = draft ? draft.draftBody : "";

    // 1. Update autonomy streak state
    autonomyEngine.recordAction(category, action, reason);

    // 2. Update status record
    this.statuses.set(emailId, {
      status: action,
      finalBody,
      reviewedAt: new Date().toISOString(),
      reviewedBy
    });

    // 3. Create audit record
    const record: AuditRecord = {
      id: `audit-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      emailId,
      category,
      originalDraft,
      finalBody,
      action,
      timestamp: new Date().toISOString(),
      reviewedBy
    };
    this.auditLogs.unshift(record);

    return record;
  }

  getAuditLogs(): AuditRecord[] {
    return [...this.auditLogs];
  }
}

export const inboxStore = new InboxStore();
