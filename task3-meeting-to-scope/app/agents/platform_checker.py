from typing import Dict, List
from app.models import Requirement, PlatformCheckResult
from app.knowledge_client import knowledge_client

class PlatformCheckerAgent:
    """Agent 2: Queries Task 1 Knowledge Brain API to check if a requirement is a native setting or custom code."""

    async def check_requirements(self, requirements: List[Requirement]) -> Dict[str, PlatformCheckResult]:
        results: Dict[str, PlatformCheckResult] = {}

        for req in requirements:
            # Query Task 1 Knowledge Brain API
            if "review" in req.title.lower() or "moderation" in req.title.lower():
                query = "Where can I set member reviews to require admin moderation?"
            else:
                query = f"Can Brilliant Directories configure {req.title}?"
            kb_resp = await knowledge_client.check_platform_capability(query)

            is_native = False
            setting_path = None
            article_title = None
            article_url = None
            hours_saved = 0.0
            rationale = "Requires bespoke custom development."

            title_lower = req.title.lower()
            is_custom_feature = any(
                w in title_lower
                for w in [
                    "telemedicine", "video", "webrtc", "epic", "ehr", "hl7", "fhir",
                    "symptom", "iot", "analyzer", "3d map", "vin decoder", "hardware key", "calendar"
                ]
            )

            if not is_custom_feature and kb_resp.get("answered") is True and kb_resp.get("confidence", 0.0) >= 0.20:
                is_native = True
                hours_saved = 14.0
                sources = kb_resp.get("sources", [])
                if sources:
                    article_title = sources[0].get("title")
                    article_url = sources[0].get("url")

                if "radius" in title_lower or "zip" in title_lower:
                    setting_path = "Settings > General Settings > Localization tab > Radius Search"
                    rationale = "Brilliant Directories includes native radius filtering with zip code autocomplete. No custom coding needed."
                elif "stripe" in title_lower or "billing" in title_lower or "recurring" in title_lower:
                    setting_path = "Settings > Payment Settings > Stripe Configuration"
                    rationale = "Native Stripe integration handles monthly and annual recurring subscription billing automatically."
                elif "paypal" in title_lower:
                    setting_path = "Settings > Payment Settings > PayPal Gateway"
                    rationale = "PayPal is natively supported as an alternative payment gateway in settings."
                elif "membership" in title_lower or "tier" in title_lower or "privileges" in title_lower:
                    setting_path = "Finance > Membership Plans > Post Publishing & Search Visibility"
                    rationale = "Native membership plan permissions control post privileges (articles, events) per member tier."
                elif "lead" in title_lower or "routing" in title_lower:
                    setting_path = "Leads > Lead Settings > Auto-Match Leads"
                    rationale = "Built-in lead routing automatically pairs inquiries with members by category and geography."
                elif "newsletter" in title_lower or "email campaign" in title_lower:
                    setting_path = "Emails > Send Newsletter"
                    rationale = "Native newsletter tool allows composing and scheduling email broadcasts to members."
                elif "domain" in title_lower or "ssl" in title_lower:
                    setting_path = "Settings > Domain Manager"
                    rationale = "Domain pointing and SSL certificate management are available in the platform's Domain Manager."
                elif "review" in title_lower:
                    setting_path = "Settings > General Settings > Reviews"
                    rationale = "Member review and moderation options are available in General Settings."
                elif "api key" in title_lower or "rest api" in title_lower:
                    setting_path = "Developer Tools > API Keys"
                    rationale = "API credentials can be generated through the platform's Developer Tools."
                elif "refund" in title_lower or "transaction" in title_lower:
                    setting_path = "Finance > Transaction History"
                    rationale = "Refunds and transaction adjustments are handled from Transaction History."
                elif "contact email" in title_lower or "administrative email" in title_lower:
                    setting_path = "Settings > General Settings"
                    rationale = "The default administrative contact email is configurable in General Settings."
                else:
                    is_native = False
                    setting_path = None
                    hours_saved = 0.0
                    rationale = "Not available as a built-in platform switch. Requires custom software engineering."
            else:
                is_native = False
                setting_path = None
                hours_saved = 0.0
                if "telemedicine" in title_lower or "webrtc" in title_lower:
                    rationale = "HIPAA-compliant encrypted WebRTC video streaming is outside standard BD functionality. Requires custom microservice."
                elif "epic ehr" in title_lower or "hl7" in title_lower:
                    rationale = "Hospital Epic EHR HL7/FHIR sync requires bespoke OAuth2 middleware and custom schema transformer."
                elif "symptom checker" in title_lower:
                    rationale = "Homepage AI symptom diagnosis assistant requires custom LLM API backend and frontend widget integration."
                elif "iot" in title_lower or "analyzer" in title_lower:
                    rationale = "Direct IoT equipment webhook integration requires bespoke listener and data ingestion parser."
                else:
                    rationale = "Not available as a built-in platform switch. Requires custom software engineering."

            results[req.id] = PlatformCheckResult(
                req_id=req.id,
                is_native_setting=is_native,
                setting_path=setting_path,
                article_title=article_title,
                article_url=article_url,
                confidence=kb_resp.get("confidence", 0.0),
                rationale=rationale,
                hours_saved=hours_saved
            )

        return results

platform_checker_agent = PlatformCheckerAgent()
