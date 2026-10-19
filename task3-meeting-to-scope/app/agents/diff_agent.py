from typing import List, Optional, Set
from app.models import SOWProposal, TaskEstimate, ScopeDiffItem, ScopeDiffReport

HOURLY_RATE_USD = 75.0

class DiffAgent:
    """Agent 5: Detects scope shifts between discovery meetings and calculates formal Change Order deltas."""

    def compute_diff(
        self,
        baseline_sow: SOWProposal,
        followup_meeting_id: str,
        followup_tasks: List[TaskEstimate],
        deferred_task_names: Optional[Set[str]] = None,
    ) -> ScopeDiffReport:
        baseline_tasks_map = {
            t.task_name.lower(): t
            for t in (baseline_sow.native_config_tasks + baseline_sow.custom_code_tasks)
        }
        followup_tasks_map = {
            t.task_name.lower(): t
            for t in followup_tasks
        }

        diff_items: List[ScopeDiffItem] = []
        change_order_needed = False
        deferred_keys = {name.lower() for name in (deferred_task_names or set())}

        # 1. Check existing baseline tasks against followup
        for base_key, base_task in baseline_tasks_map.items():
            matching_followup = None
            for f_key, f_task in followup_tasks_map.items():
                # Fuzzy matching by core topic
                if self._are_tasks_matching(base_key, f_key):
                    matching_followup = f_task
                    break

            if matching_followup:
                delta = matching_followup.expected_hours - base_task.expected_hours
                if delta == 0:
                    status = "UNCHANGED"
                    explanation = "Scope and requirements remained identical to baseline agreement."
                else:
                    status = "MODIFIED"
                    explanation = f"Scope expanded: {matching_followup.deliverable}"
                    change_order_needed = True

                diff_items.append(ScopeDiffItem(
                    req_id=matching_followup.req_id,
                    task_name=matching_followup.task_name,
                    status=status,
                    previous_hours=base_task.expected_hours,
                    new_hours=matching_followup.expected_hours,
                    delta_hours=delta,
                    explanation=explanation,
                    change_order_required=(status == "MODIFIED" and delta > 0)
                ))
            else:
                task_key = base_task.task_name.lower()
                is_deferred = task_key in deferred_keys
                status = "DEFERRED" if is_deferred else "REMOVED"
                explanation = (
                    "Deferred to Phase 2 per client request to balance sprint budget."
                    if is_deferred
                    else "Removed from the follow-up scope and no longer included in this delivery."
                )
                diff_items.append(ScopeDiffItem(
                    req_id=base_task.req_id,
                    task_name=base_task.task_name,
                    status=status,
                    previous_hours=base_task.expected_hours,
                    new_hours=0.0,
                    delta_hours=-base_task.expected_hours,
                    explanation=explanation,
                    change_order_required=False
                ))

        # 2. Check for brand new items added in follow-up that were not in baseline
        for f_key, f_task in followup_tasks_map.items():
            found_in_base = any(self._are_tasks_matching(base_key, f_key) for base_key in baseline_tasks_map.keys())
            if not found_in_base:
                diff_items.append(ScopeDiffItem(
                    req_id=f_task.req_id,
                    task_name=f_task.task_name,
                    status="OUT_OF_SCOPE",
                    previous_hours=0.0,
                    new_hours=f_task.expected_hours,
                    delta_hours=f_task.expected_hours,
                    explanation="Newly introduced feature not present in baseline discovery. Requires formal Change Order approval.",
                    change_order_required=True
                ))
                change_order_needed = True

        net_hours_delta = sum(item.delta_hours for item in diff_items)
        net_cost_delta = net_hours_delta * HOURLY_RATE_USD

        summary = (
            f"Scope Delta Analysis for {baseline_sow.client_name}:\n"
            f"- Total Scope Items Tracked: {len(diff_items)}\n"
            f"- Net Hours Delta: {net_hours_delta:+.1f} hours\n"
            f"- Net Budget Impact: ${net_cost_delta:+,.2f} USD\n"
            f"- Change Order Status: {'REQUIRED (Scope Altered)' if change_order_needed else 'Not Required'}"
        )

        return ScopeDiffReport(
            baseline_meeting_id=baseline_sow.meeting_id,
            followup_meeting_id=followup_meeting_id,
            client_name=baseline_sow.client_name,
            diff_items=diff_items,
            net_hours_delta=net_hours_delta,
            net_cost_delta=net_cost_delta,
            change_order_required=change_order_needed,
            summary_of_changes=summary,
            human_approved=False
        )

    def _are_tasks_matching(self, key1: str, key2: str) -> bool:
        if "radius" in key1 and "radius" in key2:
            return True
        if "recurring" in key1 and "recurring" in key2:
            return True
        if "paypal" in key1 and "paypal" in key2:
            return True
        if "privileges" in key1 and "privileges" in key2:
            return True
        if "telemedicine" in key1 and "telemedicine" in key2:
            return True
        if "epic" in key1 and "epic" in key2:
            return True
        if "symptom" in key1 and "symptom" in key2:
            return True
        return False

diff_agent = DiffAgent()

