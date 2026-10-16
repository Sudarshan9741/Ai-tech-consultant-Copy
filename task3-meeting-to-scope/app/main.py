from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.models import SOWProposal, ScopeDiffReport
from app.transcripts import SAMPLE_TRANSCRIPTS
from app.pipeline import pipeline
from app.knowledge_client import knowledge_client

app = FastAPI(
    title="Meeting to Scope of Work Multi-Agent API",
    description="Multi-agent team turning client meeting transcripts into SOWs, estimates, proposals, and scope deltas.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessMeetingRequest(BaseModel):
    meeting_id: str

class DiffRequest(BaseModel):
    followup_meeting_id: str
    baseline_meeting_id: str

class ApproveRequest(BaseModel):
    reviewer_name: str = "Lead Tech Consultant"

@app.get("/health")
async def health():
    kb_test = await knowledge_client.check_platform_capability("Can Brilliant Directories configure radius search?")
    return {
        "status": "healthy",
        "service": "task3-meeting-to-scope",
        "transcripts_available": len(SAMPLE_TRANSCRIPTS),
        "task1_connected": kb_test.get("answered", False)
    }

@app.get("/api/v1/transcripts")
async def list_transcripts():
    return {
        "transcripts": [
            {
                "id": t.id,
                "title": t.title,
                "client_name": t.client_name,
                "speakers": t.speakers,
                "is_followup": t.is_followup,
                "baseline_meeting_id": t.baseline_meeting_id
            }
            for t in SAMPLE_TRANSCRIPTS
        ]
    }

@app.post("/api/v1/pipeline/process", response_model=SOWProposal)
async def process_meeting(req: ProcessMeetingRequest):
    transcript = next((t for t in SAMPLE_TRANSCRIPTS if t.id == req.meeting_id), None)
    if not transcript:
        raise HTTPException(status_code=404, detail="Meeting transcript not found")

    sow = await pipeline.generate_proposal(transcript)
    return sow

@app.post("/api/v1/pipeline/diff", response_model=ScopeDiffReport)
async def process_scope_diff(req: DiffRequest):
    base_transcript = next((t for t in SAMPLE_TRANSCRIPTS if t.id == req.baseline_meeting_id), None)
    followup_transcript = next((t for t in SAMPLE_TRANSCRIPTS if t.id == req.followup_meeting_id), None)

    if not base_transcript or not followup_transcript:
        raise HTTPException(status_code=404, detail="One or both meeting transcripts not found")

    base_sow = await pipeline.generate_proposal(base_transcript)
    diff_report = await pipeline.generate_scope_diff(followup_transcript, base_sow)
    return diff_report

@app.post("/api/v1/proposals/{sow_id}/approve")
async def approve_proposal(sow_id: str, req: ApproveRequest):
    approved = pipeline.approve_sow(sow_id, req.reviewer_name)
    if not approved:
        raise HTTPException(status_code=404, detail="SOW Proposal not found. Process meeting first.")
    return {
        "status": "approved",
        "sow_id": sow_id,
        "approved_by": approved.approved_by,
        "approved_at": approved.approved_at,
        "client_ready": True
    }

@app.get("/", response_class=HTMLResponse)
async def web_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meeting to Scope | AI Tech Consultant</title>
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
            .container { max-width: 1100px; margin: 0 auto; }
            header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            select, button { padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; }
            select { background: #0f172a; border: 1px solid var(--border); color: var(--text); }
            button.btn-primary { background: var(--primary); border: none; color: white; }
            button.btn-success { background: var(--success); border: none; color: white; }
            table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid var(--border); }
            th { color: var(--text-muted); }
            .badge-native { background: #064e3b; color: #6ee7b7; padding: 3px 8px; border-radius: 4px; font-size: 11px; }
            .badge-custom { background: #7c2d12; color: #fdba74; padding: 3px 8px; border-radius: 4px; font-size: 11px; }
            .stat-box { background: #0f172a; padding: 14px; border-radius: 6px; border: 1px solid var(--border); text-align: center; }
            .stat-val { font-size: 22px; font-weight: 700; color: var(--success); }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1 style="margin: 0; font-size: 22px;">🤝 Meeting to Scope of Work</h1>
                    <small style="color: var(--text-muted);">Multi-Agent Team: Clarifier → Platform Capability Checker → Estimator → Proposal & Diff Writer</small>
                </div>
                <div id="service-badge" style="font-size: 12px; color: var(--text-muted);">Connected</div>
            </header>

            <div class="card">
                <h3>Select Discovery Meeting Transcript</h3>
                <div style="display: flex; gap: 12px; align-items: center; margin-top: 12px;">
                    <select id="meetingSelect" style="flex: 1;">
                        <option value="meeting-001">Meeting 1: Apex Healthcare Network - Initial Discovery (5 Requirements)</option>
                        <option value="meeting-002">Meeting 2: Apex Healthcare Network - Scope Shift & Follow-up (Diff / Change Order)</option>
                        <option value="meeting-003">Meeting 3: BioHealth Diagnostics - Initial Discovery & IoT Sync</option>
                    </select>
                    <button class="btn-primary" onclick="runPipeline()">Run Multi-Agent Pipeline</button>
                    <button class="btn-primary" style="background: #4f46e5;" onclick="runDiff()">Compare Meeting 1 vs Meeting 2</button>
                </div>
            </div>

            <div id="resultsArea"></div>
        </div>

        <script>
            async function runPipeline() {
                const meetingId = document.getElementById('meetingSelect').value;
                const container = document.getElementById('resultsArea');
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 40px;">Executing multi-agent team (calling Task 1 Knowledge Brain API)...</p>';

                const res = await fetch('/api/v1/pipeline/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ meeting_id: meetingId })
                });
                const sow = await res.json();

                let html = '<div class="card">';
                html += '<div style="display: flex; justify-content: space-between; align-items: center;">';
                html += '<h2>' + sow.project_title + '</h2>';
                html += '<span style="font-size: 12px; background: #1e3a8a; padding: 4px 10px; border-radius: 4px;">' + sow.sow_id + '</span>';
                html += '</div>';

                html += '<div class="grid" style="margin: 16px 0;">';
                html += '<div class="stat-box"><small style="color: var(--text-muted);">Total Expected Hours</small><div class="stat-val">' + sow.total_expected_hours + ' hrs</div></div>';
                html += '<div class="stat-box"><small style="color: var(--text-muted);">Estimated Client Budget</small><div class="stat-val">$' + Number(sow.estimated_budget_usd).toLocaleString() + ' USD</div></div>';
                html += '</div>';

                html += '<div style="background: #0f172a; padding: 14px; border-radius: 6px; margin-bottom: 20px; white-space: pre-line; font-size: 13px;">' + sow.executive_summary + '</div>';

                html += '<h4>1. Native Platform Settings (Zero-Code Solutions - Verified via Task 1 API):</h4>';
                html += '<table><thead><tr><th>Task</th><th>Setting Path</th><th>Estimated Effort</th><th>Risk</th></tr></thead><tbody>';
                sow.native_config_tasks.forEach(t => {
                    html += '<tr><td><strong>' + t.task_name + '</strong></td><td style="color: #60a5fa;">' + t.setting_reference + '</td><td>' + t.expected_hours + ' hr</td><td><span class="badge-native">' + t.risk_level + '</span></td></tr>';
                });
                html += '</tbody></table>';

                html += '<h4 style="margin-top: 24px;">2. Custom Engineering Deliverables:</h4>';
                html += '<table><thead><tr><th>Task</th><th>Deliverable</th><th>Hours (Best / Exp / Worst)</th><th>Risk</th></tr></thead><tbody>';
                sow.custom_code_tasks.forEach(t => {
                    html += '<tr><td><strong>' + t.task_name + '</strong></td><td>' + t.deliverable + '</td><td>' + t.best_case_hours + ' / ' + t.expected_hours + ' / ' + t.worst_case_hours + ' hrs</td><td><span class="badge-custom">' + t.risk_level + '</span></td></tr>';
                });
                html += '</tbody></table>';

                html += '<div style="margin-top: 24px; text-align: right;">';
                if (!sow.human_approved) {
                    html += '<button class="btn-success" onclick="approveSow(\\'' + sow.sow_id + '\\')">✍️ Sign & Approve Scope of Work (Human Gate)</button>';
                } else {
                    html += '<span style="color: #10b981; font-weight: 700;">✅ Approved by ' + sow.approved_by + '</span>';
                }
                html += '</div>';

                html += '</div>';
                container.innerHTML = html;
            }

            async function runDiff() {
                const container = document.getElementById('resultsArea');
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 40px;">Computing scope shift deltas between Meeting 1 and Meeting 2...</p>';

                const res = await fetch('/api/v1/pipeline/diff', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ baseline_meeting_id: 'meeting-001', followup_meeting_id: 'meeting-002' })
                });
                const diff = await res.json();

                let html = '<div class="card">';
                html += '<h2>📊 Meeting 1 vs Meeting 2 Scope Delta Report</h2>';
                html += '<div style="background: #0f172a; padding: 14px; border-radius: 6px; margin: 16px 0; white-space: pre-line; font-size: 13px;">' + diff.summary_of_changes + '</div>';

                html += '<table><thead><tr><th>Item</th><th>Status</th><th>Prev Hours</th><th>New Hours</th><th>Delta</th><th>Explanation</th><th>Change Order?</th></tr></thead><tbody>';
                diff.diff_items.forEach(item => {
                    const statusColor = item.status === 'UNCHANGED' ? '#94a3b8' : (item.status === 'MODIFIED' ? '#f59e0b' : '#ef4444');
                    html += '<tr>';
                    html += '<td><strong>' + item.task_name + '</strong></td>';
                    html += '<td><span style="color: ' + statusColor + '; font-weight: 700;">' + item.status + '</span></td>';
                    html += '<td>' + item.previous_hours + 'h</td>';
                    html += '<td>' + item.new_hours + 'h</td>';
                    html += '<td style="font-weight: 700;">' + (item.delta_hours > 0 ? '+' : '') + item.delta_hours + 'h</td>';
                    html += '<td>' + item.explanation + '</td>';
                    html += '<td>' + (item.change_order_required ? '<span style="color: #ef4444; font-weight: 700;">YES</span>' : 'No') + '</td>';
                    html += '</tr>';
                });
                html += '</tbody></table>';
                html += '</div>';
                container.innerHTML = html;
            }

            async function approveSow(sowId) {
                const res = await fetch('/api/v1/proposals/' + sowId + '/approve', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ reviewer_name: 'Alex Turner (Lead Tech Consultant)' })
                });
                const data = await res.json();
                alert('SOW Approved! Ready for client presentation.');
                runPipeline();
            }
        </script>
    </body>
    </html>
    """
