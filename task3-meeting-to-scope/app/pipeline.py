from datetime import datetime
from typing import Dict, List, Optional
from app.models import MeetingTranscript, SOWProposal, ScopeDiffReport
from app.agents.clarifier_agent import clarifier_agent
from app.agents.platform_checker import platform_checker_agent
from app.agents.estimation_agent import estimation_agent
from app.agents.proposal_agent import proposal_agent
from app.agents.diff_agent import diff_agent

class MeetingPipeline:
    def __init__(self):
        self.sow_cache: Dict[str, SOWProposal] = {}
        self.diff_cache: Dict[str, ScopeDiffReport] = {}

    async def generate_proposal(self, transcript: MeetingTranscript) -> SOWProposal:
        # Agent 1: Clarifier
        requirements = clarifier_agent.extract_requirements(transcript)

        # Agent 2: Platform Capability Checker (calls Task 1 API)
        checks = await platform_checker_agent.check_requirements(requirements)

        # Agent 3: Estimation Agent
        tasks = estimation_agent.estimate_tasks(requirements, checks)

        # Agent 4: Proposal & SOW Writer
        sow = proposal_agent.generate_sow(transcript, tasks)
        self.sow_cache[sow.sow_id] = sow
        return sow

    async def generate_scope_diff(
        self,
        followup_transcript: MeetingTranscript,
        baseline_sow: SOWProposal
    ) -> ScopeDiffReport:
        requirements = clarifier_agent.extract_requirements(followup_transcript)
        checks = await platform_checker_agent.check_requirements(requirements)
        followup_tasks = estimation_agent.estimate_tasks(requirements, checks)

        # Agent 5: Scope Diff & Change Order Agent
        diff_report = diff_agent.compute_diff(
            baseline_sow=baseline_sow,
            followup_meeting_id=followup_transcript.id,
            followup_tasks=followup_tasks
        )
        report_id = f"DIFF-{followup_transcript.id.upper()}"
        self.diff_cache[report_id] = diff_report
        return diff_report

    def approve_sow(self, sow_id: str, reviewer_name: str) -> Optional[SOWProposal]:
        sow = self.sow_cache.get(sow_id)
        if not sow:
            return None

        sow.human_approved = True
        sow.approved_by = reviewer_name
        sow.approved_at = datetime.utcnow().isoformat()
        return sow

pipeline = MeetingPipeline()
