from typing import List, Dict
from app.models import Requirement, PlatformCheckResult, TaskEstimate

class EstimationAgent:
    """Agent 3: Breaks requirements into atomic developer tasks with hour estimates and risk ratings."""

    def estimate_tasks(
        self,
        requirements: List[Requirement],
        checks: Dict[str, PlatformCheckResult]
    ) -> List[TaskEstimate]:
        tasks: List[TaskEstimate] = []

        for idx, req in enumerate(requirements, start=1):
            check = checks.get(req.id)
            is_native = check.is_native_setting if check else False
            req_lower = req.title.lower()

            if is_native:
                task = TaskEstimate(
                    task_id=f"TASK-{idx:03d}",
                    req_id=req.id,
                    task_name=f"Configure {req.title}",
                    task_type="NATIVE_CONFIG",
                    best_case_hours=0.5,
                    expected_hours=1.0,
                    worst_case_hours=2.0,
                    risk_level="LOW",
                    setting_reference=check.setting_path if check else "Admin Settings",
                    deliverable=f"Zero-code platform configuration in {check.setting_path if check else 'Settings'}. Verified through sandbox test."
                )
            else:
                # Custom development estimation
                if "group telemedicine" in req_lower or "multi-party" in req_lower:
                    best, exp, worst, risk = 24.0, 36.0, 50.0, "HIGH"
                    desc = "Bespoke SFU WebRTC multi-party video server, token authentication, and embedded dashboard UI."
                elif "telemedicine" in req_lower or "video" in req_lower:
                    best, exp, worst, risk = 16.0, 24.0, 36.0, "HIGH"
                    desc = "Custom HIPAA-compliant WebRTC peer-to-peer video consultation module embedded in member profile."
                elif "epic ehr" in req_lower or "hl7" in req_lower:
                    best, exp, worst, risk = 20.0, 28.0, 40.0, "HIGH"
                    desc = "Custom OAuth2 middleware and HL7 FHIR doctor credential synchronization pipeline."
                elif "symptom checker" in req_lower:
                    best, exp, worst, risk = 10.0, 16.0, 24.0, "MEDIUM"
                    desc = "Interactive AI diagnostic assistant widget with specialist directory taxonomy mapping."
                elif "iot" in req_lower or "analyzer" in req_lower:
                    best, exp, worst, risk = 14.0, 20.0, 30.0, "MEDIUM"
                    desc = "Bespoke REST webhook receiver and automated lab equipment data ingestion parser."
                else:
                    best, exp, worst, risk = 8.0, 14.0, 22.0, "MEDIUM"
                    desc = "Bespoke custom software engineering and API integration."

                task = TaskEstimate(
                    task_id=f"TASK-{idx:03d}",
                    req_id=req.id,
                    task_name=f"Custom Engineering: {req.title}",
                    task_type="CUSTOM_CODE",
                    best_case_hours=best,
                    expected_hours=exp,
                    worst_case_hours=worst,
                    risk_level=risk,
                    setting_reference=None,
                    deliverable=desc
                )

            tasks.append(task)

        return tasks

estimation_agent = EstimationAgent()

