import { ApprovalAction, CategoryAutonomyState, EmailCategory } from "./types.js";

const DEFAULT_THRESHOLD = 20;

export class AutonomyEngine {
  private states: Map<EmailCategory, CategoryAutonomyState> = new Map();
  // Safe default: system never sends real emails without explicit configuration
  public allowAutonomousSend: boolean = process.env.SYSTEM_ALLOW_AUTONOMOUS_SEND === "true";

  constructor(threshold = DEFAULT_THRESHOLD) {
    const categories: EmailCategory[] = [
      "HOW_TO",
      "PROJECT_REQUEST",
      "BILLING_REFUND",
      "COMPLAINT",
      "QUOTE",
      "FOLLOW_UP"
    ];

    for (const cat of categories) {
      this.states.set(cat, {
        category: cat,
        consecutiveUnchangedCount: 0,
        threshold,
        isAutonomous: false,
        totalApproved: 0,
        totalEdited: 0,
        totalRejected: 0,
        lastActionAt: null,
        lastResetReason: null
      });
    }
  }

  getState(category: EmailCategory): CategoryAutonomyState {
    const state = this.states.get(category);
    if (!state) {
      throw new Error(`Invalid category: ${category}`);
    }
    return { ...state };
  }

  getAllStates(): Record<EmailCategory, CategoryAutonomyState> {
    const result = {} as Record<EmailCategory, CategoryAutonomyState>;
    for (const [cat, state] of this.states.entries()) {
      result[cat] = { ...state };
    }
    return result;
  }

  recordAction(category: EmailCategory, action: ApprovalAction, reason?: string): CategoryAutonomyState {
    const state = this.states.get(category);
    if (!state) {
      throw new Error(`Category ${category} not found`);
    }

    const now = new Date().toISOString();
    state.lastActionAt = now;

    if (action === "APPROVED_UNCHANGED") {
      state.totalApproved += 1;
      state.consecutiveUnchangedCount += 1;

      if (state.consecutiveUnchangedCount >= state.threshold) {
        state.isAutonomous = true;
      }
    } else if (action === "EDITED_AND_APPROVED") {
      state.totalEdited += 1;
      const wasAutonomous = state.isAutonomous;
      state.consecutiveUnchangedCount = 0;
      state.isAutonomous = false;
      state.lastResetReason = wasAutonomous
        ? `Autonomy revoked: human modified draft (Reason: ${reason || "content adjusted"})`
        : `Streak reset: human modified draft (Reason: ${reason || "content adjusted"})`;
    } else if (action === "REJECTED") {
      state.totalRejected += 1;
      state.consecutiveUnchangedCount = 0;
      state.isAutonomous = false;
      state.lastResetReason = `Streak reset: draft rejected by human (${reason || "unspecified reason"})`;
    }

    return { ...state };
  }

  canAutoSend(category: EmailCategory, confidence: number): boolean {
    const state = this.states.get(category);
    if (!state) return false;

    // Safety checks:
    // 1. Explicit environment permission
    // 2. Category has achieved >= 20 consecutive unchanged approvals
    // 3. Model confidence is above safe threshold
    return (
      this.allowAutonomousSend &&
      state.isAutonomous &&
      confidence >= 0.85
    );
  }

  revokeAutonomy(category: EmailCategory, reason: string): void {
    const state = this.states.get(category);
    if (state) {
      state.isAutonomous = false;
      state.consecutiveUnchangedCount = 0;
      state.lastResetReason = `Manual revocation: ${reason}`;
    }
  }

  resetAll(): void {
    for (const state of this.states.values()) {
      state.consecutiveUnchangedCount = 0;
      state.isAutonomous = false;
      state.totalApproved = 0;
      state.totalEdited = 0;
      state.totalRejected = 0;
      state.lastActionAt = null;
      state.lastResetReason = "Full reset";
    }
  }
}

export const autonomyEngine = new AutonomyEngine();

