from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class MeetingTranscript(BaseModel):
    id: str
    title: str
    date: str
    client_name: str
    speakers: List[str]
    raw_text: str
    is_followup: bool = False
    baseline_meeting_id: Optional[str] = None

class Requirement(BaseModel):
    id: str
    title: str
    description: str
    category: Literal["FUNCTIONAL", "NON_FUNCTIONAL", "INTEGRATION", "DESIGN"]
    speaker: str
    transcript_quote: str
    line_reference: int

class PlatformCheckResult(BaseModel):
    req_id: str
    is_native_setting: bool
    setting_path: Optional[str] = None
    article_title: Optional[str] = None
    article_url: Optional[str] = None
    confidence: float
    rationale: str
    hours_saved: float = 0.0

class TaskEstimate(BaseModel):
    task_id: str
    req_id: str
    task_name: str
    task_type: Literal["NATIVE_CONFIG", "CUSTOM_CODE"]
    best_case_hours: float
    expected_hours: float
    worst_case_hours: float
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    setting_reference: Optional[str] = None
    deliverable: str

class SOWProposal(BaseModel):
    sow_id: str
    meeting_id: str
    client_name: str
    project_title: str
    executive_summary: str
    native_config_tasks: List[TaskEstimate]
    custom_code_tasks: List[TaskEstimate]
    total_expected_hours: float
    estimated_budget_usd: float
    estimated_timeline_weeks: int
    human_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None

class ScopeDiffItem(BaseModel):
    req_id: str
    task_name: str
    status: Literal["UNCHANGED", "MODIFIED", "NEWLY_ADDED", "OUT_OF_SCOPE"]
    previous_hours: float
    new_hours: float
    delta_hours: float
    explanation: str
    change_order_required: bool

class ScopeDiffReport(BaseModel):
    baseline_meeting_id: str
    followup_meeting_id: str
    client_name: str
    diff_items: List[ScopeDiffItem]
    net_hours_delta: float
    net_cost_delta: float
    change_order_required: bool
    summary_of_changes: str
    human_approved: bool = False
