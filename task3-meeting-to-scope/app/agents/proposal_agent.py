import math
from typing import List
from app.models import MeetingTranscript, TaskEstimate, SOWProposal

HOURLY_RATE_USD = 75.0

class ProposalAgent:
    """Agent 4: Compiles native config tasks and custom engineering tasks into an executive SOW and client proposal."""

    def generate_sow(self, transcript: MeetingTranscript, tasks: List[TaskEstimate]) -> SOWProposal:
        native_tasks = [t for t in tasks if t.task_type == "NATIVE_CONFIG"]
        custom_tasks = [t for t in tasks if t.task_type == "CUSTOM_CODE"]

        total_hours = sum(t.expected_hours for t in tasks)
        total_budget = total_hours * HOURLY_RATE_USD
        timeline_weeks = max(1, math.ceil(total_hours / 25.0))

        hours_saved_by_native = len(native_tasks) * 14.0
        dollars_saved = hours_saved_by_native * HOURLY_RATE_USD

        summary = (
            f"Scope of Work for {transcript.client_name} prepared following '{transcript.title}'.\n\n"
            f"Key Architectural Finding:\n"
            f"Our technical audit identified {len(native_tasks)} core features that can be deployed immediately "
            f"using built-in platform settings, saving an estimated {hours_saved_by_native:.0f} developer hours "
            f"(${dollars_saved:,.0f} USD) compared to custom coding.\n\n"
            f"The remaining {len(custom_tasks)} complex integrations require bespoke software engineering. "
            f"Total estimated engagement is {total_hours:.1f} hours across {timeline_weeks} weeks."
        )

        return SOWProposal(
            sow_id=f"SOW-{transcript.id.upper()}",
            meeting_id=transcript.id,
            client_name=transcript.client_name,
            project_title=transcript.title,
            executive_summary=summary,
            native_config_tasks=native_tasks,
            custom_code_tasks=custom_tasks,
            total_expected_hours=total_hours,
            estimated_budget_usd=total_budget,
            estimated_timeline_weeks=timeline_weeks,
            human_approved=False
        )

proposal_agent = ProposalAgent()

