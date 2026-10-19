import express, { Request, Response } from "express";
import { inboxStore } from "./store.js";
import { draftEngine } from "./drafter.js";
import { autonomyEngine } from "./autonomyEngine.js";
import { knowledgeClient } from "./knowledgeClient.js";
import { ApprovalActionSchema } from "./types.js";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

app.get("/health", async (_req: Request, res: Response) => {
  let task1Health: { status: string; active_articles: number } | null = null;
  let task1Connected = false;
  try {
    task1Health = await knowledgeClient.checkHealth();
    task1Connected = true;
  } catch {
    task1Connected = false;
  }

  res.json({
    status: "healthy",
    service: "task2-inbox-agent",
    emails_loaded: inboxStore.getAllEmails().length,
    task1_connected: task1Connected,
    task1_info: task1Health,
    auto_send_enabled: autonomyEngine.allowAutonomousSend
  });
});

app.get("/api/emails", async (_req: Request, res: Response) => {
  const emails = inboxStore.getAllEmails();
  const results = emails.map(email => ({
    ...email,
    draft: inboxStore.getDraft(email.id) || null,
    status: inboxStore.getStatus(email.id)
  }));
  res.json({ total: results.length, emails: results });
});

app.post("/api/emails/:id/draft", async (req: Request, res: Response) => {
  const email = inboxStore.getEmail(req.params.id);
  if (!email) {
    return res.status(404).json({ error: "Email not found" });
  }

  const draft = await draftEngine.generateDraft(email);
  inboxStore.setDraft(email.id, draft);
  return res.json(draft);
});

app.post("/api/emails/:id/review", async (req: Request, res: Response) => {
  const email = inboxStore.getEmail(req.params.id);
  if (!email) {
    return res.status(404).json({ error: "Email not found" });
  }

  const parseAction = ApprovalActionSchema.safeParse(req.body.action);
  if (!parseAction.success) {
    return res.status(400).json({ error: "Invalid action. Must be APPROVED_UNCHANGED, EDITED_AND_APPROVED, or REJECTED" });
  }

  const finalBody = typeof req.body.finalBody === "string" ? req.body.finalBody : "";
  const reason = typeof req.body.reason === "string" ? req.body.reason : undefined;
  let audit;
  try {
    audit = inboxStore.recordReview(email.id, parseAction.data, finalBody, "Admin User", reason);
  } catch (err) {
    return res.status(400).json({ error: err instanceof Error ? err.message : "Invalid review" });
  }
  const updatedState = autonomyEngine.getState(audit.category);

  return res.json({
    success: true,
    audit,
    category_state: updatedState
  });
});

app.get("/api/autonomy", (_req: Request, res: Response) => {
  const threshold = autonomyEngine.getState("HOW_TO").threshold;
  res.json({
    system_allow_auto_send: autonomyEngine.allowAutonomousSend,
    threshold,
    categories: autonomyEngine.getAllStates()
  });
});

app.post("/api/autonomy/toggle-safe-send", (req: Request, res: Response) => {
  if (typeof req.body?.enabled !== "boolean") {
    return res.status(400).json({ error: "enabled must be a boolean" });
  }
  const enable = req.body.enabled;
  autonomyEngine.allowAutonomousSend = enable;
  return res.json({
    system_allow_auto_send: autonomyEngine.allowAutonomousSend,
    message: enable ? "Automatic sending authorized" : "Automatic sending disabled (Safety Mode)"
  });
});

app.get("/api/audits", (_req: Request, res: Response) => {
  res.json({ audits: inboxStore.getAuditLogs() });
});

app.get("/", (_req: Request, res: Response) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Inbox Agent | AI Tech Consultant</title>
      <style>
        :root {
          --bg: #0f172a;
          --card: #1e293b;
          --border: #334155;
          --text: #f8fafc;
          --text-muted: #94a3b8;
          --primary: #2563eb;
          --success: #10b981;
          --warning: #f59e0b;
          --danger: #ef4444;
        }
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: var(--bg);
          color: var(--text);
          margin: 0;
          padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 380px 1fr; gap: 20px; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }
        .email-item { padding: 12px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s; }
        .email-item:hover, .email-item.active { background: #334155; }
        .badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; display: inline-block; }
        .badge-how_to { background: #1e3a8a; color: #93c5fd; }
        .badge-refund { background: #7c2d12; color: #fdba74; }
        .badge-project { background: #064e3b; color: #6ee7b7; }
        .badge-quote { background: #3b0764; color: #d8b4fe; }
        .badge-complaint { background: #7f1d1d; color: #fca5a5; }
        .badge-follow_up { background: #134e4a; color: #5eead4; }
        textarea { width: 100%; background: #0f172a; border: 1px solid var(--border); color: var(--text); border-radius: 6px; padding: 12px; font-size: 14px; box-sizing: border-box; resize: vertical; min-height: 180px; }
        .btn { padding: 8px 14px; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; margin-right: 8px; }
        .btn-success { background: var(--success); color: white; }
        .btn-warning { background: var(--warning); color: black; }
        .btn-danger { background: var(--danger); color: white; }
        .btn-primary { background: var(--primary); color: white; }
        .progress-bar-bg { background: #334155; border-radius: 999px; height: 8px; width: 100%; overflow: hidden; margin-top: 4px; }
        .progress-bar-fill { background: var(--success); height: 100%; width: 0%; transition: width 0.3s; }
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <div>
            <h1 style="margin: 0; font-size: 22px;">📬 Customer Inbox Agent</h1>
            <small style="color: var(--text-muted);">Progressive Autonomy with Strict 20-Run Unchanged Approval Gate</small>
          </div>
          <div id="autonomy-status" style="font-size: 13px;">Loading autonomy metrics...</div>
        </header>

        <!-- STREAK DASHBOARD -->
        <div class="card" style="margin-bottom: 20px;">
          <h4 style="margin: 0 0 12px 0;">🛡️ Progressive Autonomy Safeguard Tracker (Target: 20 Consecutive Unchanged Sends)</h4>
          <div id="streak-grid" style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; font-size: 12px;"></div>
        </div>

        <div class="grid">
          <!-- EMAIL LIST -->
          <div class="card" style="height: 600px; overflow-y: auto; padding: 0;">
            <div style="padding: 12px; border-bottom: 1px solid var(--border); background: #1e293b; position: sticky; top: 0;">
              <strong>Customer Inquiries (61 Realistic Scenarios)</strong>
            </div>
            <div id="email-list">Loading emails...</div>
          </div>

          <!-- DRAFT INSPECTION & REVIEW -->
          <div class="card" id="detail-panel">
            <p style="color: var(--text-muted); text-align: center; margin-top: 100px;">Select an email on the left to inspect or generate its grounded reply draft.</p>
          </div>
        </div>
      </div>

      <script>
        let emailsData = [];
        let selectedEmail = null;

        async function loadData() {
          const res = await fetch('/api/emails');
          const data = await res.json();
          emailsData = data.emails;
          renderEmailList();
          loadAutonomy();
        }

        async function loadAutonomy() {
          const status = document.getElementById('autonomy-status');
          const grid = document.getElementById('streak-grid');
          try {
          const res = await fetch('/api/autonomy');
          if (!res.ok) throw new Error('HTTP ' + res.status);
          const data = await res.json();
          status.innerText = data.system_allow_auto_send ? 'Auto-send authorization enabled' : 'Human review required';
          let html = '';
          for (const [cat, state] of Object.entries(data.categories)) {
            const percent = Math.min(100, (state.consecutiveUnchangedCount / data.threshold) * 100);
            html += '<div style="background: #0f172a; padding: 10px; border-radius: 6px; border: 1px solid #334155;">';
            html += '<strong>' + cat + '</strong><br>';
            html += '<small>' + state.consecutiveUnchangedCount + ' / ' + data.threshold + ' streak</small>';
            html += '<div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ' + percent + '%;"></div></div>';
            html += '<small style="color: ' + (state.isAutonomous ? '#10b981' : '#94a3b8') + '; font-weight: 600;">' + (state.isAutonomous ? '✅ AUTONOMOUS' : '🔒 Human Gate') + '</small>';
            html += '</div>';
          }
          grid.innerHTML = html;
          } catch (error) {
            status.innerText = 'Unable to load autonomy metrics';
            grid.innerHTML = '<p style="color: #fecaca;">Autonomy status could not be loaded. Refresh the page to retry.</p>';
          }
        }

        function renderEmailList() {
          const list = document.getElementById('email-list');
          let html = '';
          emailsData.forEach(e => {
            const isSel = selectedEmail && selectedEmail.id === e.id;
            html += '<div class="email-item ' + (isSel ? 'active' : '') + '" onclick="selectEmail(\\'' + e.id + '\\')">';
            html += '<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">';
            html += '<span style="font-weight: 600; font-size: 13px;">' + e.customerName + '</span>';
            html += '<span class="badge badge-how_to">' + (e.draft ? e.draft.category : 'NEW') + '</span>';
            html += '</div>';
            html += '<div style="font-size: 12px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">' + e.subject + '</div>';
            html += '</div>';
          });
          list.innerHTML = html;
        }

        async function selectEmail(id) {
          selectedEmail = emailsData.find(e => e.id === id);
          renderEmailList();
          const panel = document.getElementById('detail-panel');
          panel.innerHTML = '<p style="color: var(--text-muted);">Generating grounded draft via Task 1 Knowledge Brain...</p>';

          let draft = selectedEmail.draft;
          if (!draft) {
            const draftRes = await fetch('/api/emails/' + id + '/draft', { method: 'POST' });
            draft = await draftRes.json();
            selectedEmail.draft = draft;
          }

          let html = '<h3>' + selectedEmail.subject + '</h3>';
          html += '<p style="font-size: 13px; color: var(--text-muted);"><strong>From:</strong> ' + selectedEmail.customerName + ' &lt;' + selectedEmail.from + '&gt;</p>';
          html += '<div style="background: #0f172a; padding: 12px; border-radius: 6px; font-size: 13px; margin-bottom: 16px;">' + selectedEmail.body + '</div>';

          html += '<h4>Grounded Draft Reply:</h4>';
          html += '<textarea id="draftText">' + draft.draftBody + '</textarea>';

          if (draft.groundingSources && draft.groundingSources.length) {
            html += '<div style="margin-top: 10px; font-size: 12px;"><strong>Knowledge Citations from Task 1:</strong>';
            draft.groundingSources.forEach(s => {
              html += '<div style="color: #60a5fa; margin-top: 2px;">• ' + s.title + ' (' + s.url + ')</div>';
            });
            html += '</div>';
          }

          html += '<div style="margin-top: 16px;">';
          html += '<button class="btn btn-success" onclick="reviewDraft(\\'APPROVED_UNCHANGED\\')">1-Click Approve Unchanged</button>';
          html += '<button class="btn btn-warning" onclick="reviewDraft(\\'EDITED_AND_APPROVED\\')">Edit & Approve (Resets Streak)</button>';
          html += '<button class="btn btn-danger" onclick="reviewDraft(\\'REJECTED\\')">Reject Draft</button>';
          html += '</div>';

          panel.innerHTML = html;
        }

        async function reviewDraft(action) {
          const finalBody = document.getElementById('draftText').value;
          const res = await fetch('/api/emails/' + selectedEmail.id + '/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, finalBody })
          });
          const result = await res.json();
          alert('Action recorded: ' + action + '. Streak for ' + result.category_state.category + ': ' + result.category_state.consecutiveUnchangedCount + '/20');
          loadData();
        }

        loadData();
      </script>
    </body>
    </html>
  `);
});

export { app };

if (process.env.NODE_ENV !== "test") {
  app.listen(PORT, () => {
    console.log(`[Task 2] Customer Inbox Agent listening on http://127.0.0.1:${PORT}`);
  });
}

