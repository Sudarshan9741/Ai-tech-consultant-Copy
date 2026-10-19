import { z } from "zod";

export const EmailCategorySchema = z.enum([
  "HOW_TO",
  "PROJECT_REQUEST",
  "BILLING_REFUND",
  "COMPLAINT",
  "QUOTE",
  "FOLLOW_UP"
]);
export type EmailCategory = z.infer<typeof EmailCategorySchema>;

export const CustomerEmailSchema = z.object({
  id: z.string(),
  from: z.string().email(),
  customerName: z.string(),
  subject: z.string(),
  body: z.string(),
  receivedAt: z.string().datetime(),
  threadId: z.string().optional()
});
export type CustomerEmail = z.infer<typeof CustomerEmailSchema>;

export const GroundingSourceSchema = z.object({
  title: z.string(),
  url: z.string(),
  snippet: z.string()
});
export type GroundingSource = z.infer<typeof GroundingSourceSchema>;

export const DraftReplySchema = z.object({
  emailId: z.string(),
  category: EmailCategorySchema,
  confidence: z.number().min(0).max(1),
  draftBody: z.string(),
  groundingSources: z.array(GroundingSourceSchema),
  knowledgeFound: z.boolean(),
  escalationId: z.number().nullable(),
  requiresHumanApproval: z.boolean(),
  canAutoSend: z.boolean()
});
export type DraftReply = z.infer<typeof DraftReplySchema>;

export const ApprovalActionSchema = z.enum([
  "APPROVED_UNCHANGED",
  "EDITED_AND_APPROVED",
  "REJECTED"
]);
export type ApprovalAction = z.infer<typeof ApprovalActionSchema>;

export interface AuditRecord {
  id: string;
  emailId: string;
  category: EmailCategory;
  originalDraft: string;
  finalBody: string;
  action: ApprovalAction;
  timestamp: string;
  reviewedBy: string;
}

export interface CategoryAutonomyState {
  category: EmailCategory;
  consecutiveUnchangedCount: number;
  threshold: number;
  isAutonomous: boolean;
  totalApproved: number;
  totalEdited: number;
  totalRejected: number;
  lastActionAt: string | null;
  lastResetReason: string | null;
}

