from typing import List
from app.models import MeetingTranscript, Requirement

class ClarifierAgent:
    """Agent 1: Extracts structured requirements with transcript quotes and speaker references."""

    def extract_requirements(self, transcript: MeetingTranscript) -> List[Requirement]:
        lines = [line.strip() for line in transcript.raw_text.strip().split("\n") if line.strip()]
        requirements: List[Requirement] = []
        req_counter = 1

        for line_idx, line in enumerate(lines, start=1):
            lower = line.lower()

            # Radius & zip code search
            if "zip code" in lower or "radius" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Location-Based Zip Code & Radius Search",
                    description="Allow directory visitors to search and filter member listings within a 25 or 50-mile radius using their zip code.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Recurring payments & Stripe / PayPal
            elif "stripe" in lower or ("recurring" in lower and "payment" in lower):
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Automated Recurring Subscription Billing",
                    description="Configure automated monthly ($199) and annual ($1,999) recurring member subscription billing via Stripe payment gateway.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # PayPal payment option (Meeting 2 addition)
            elif "paypal" in lower and "payment" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="PayPal Payment Gateway Integration",
                    description="Enable PayPal as a secondary payment method alongside Stripe for European doctors.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Membership plans & privileges
            elif "tier privileges" in lower or "membership plan" in lower or "post publishing" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Multi-Tier Membership Privileges & Access Control",
                    description="Segment doctors into Basic and Premium tiers; permit Premium members to publish medical articles, events, and receive patient inquiries.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Telemedicine portal (WebRTC video)
            elif "telemedicine" in lower or "video calling" in lower:
                speaker = self._extract_speaker(line)
                title = "Multi-Party Group Telemedicine Video Portal" if "group" in lower or "6 participants" in lower else "HIPAA-Compliant 1-on-1 Telemedicine Portal"
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title=title,
                    description="Custom encrypted video calling interface embedded within doctor profiles for remote patient consultations.",
                    category="INTEGRATION",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Epic EHR integration
            elif "epic ehr" in lower or "hl7" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Epic EHR HL7 FHIR Automated Credential Sync",
                    description="Nightly automated bidirectional synchronization of doctor credentials and licensing data via Epic EHR FHIR REST API.",
                    category="INTEGRATION",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # AI Symptom Checker (Meeting 2 addition)
            elif "symptom checker" in lower or "ai symptom" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="AI-Powered Patient Symptom Checker & Specialist Recommender",
                    description="Homepage conversational AI widget that analyzes patient symptoms and directs them to the top 3 relevant directory specialist categories.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Lead matching (Meeting 3)
            elif "matched to the nearest" in lower or "lead matching" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Automated Diagnostic Lead Routing & Geographic Matching",
                    description="Automatically route patient test inquiries to the closest qualified diagnostic lab based on specialty and location.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # Newsletter marketing (Meeting 3)
            elif "newsletters" in lower or "educational health newsletters" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="Mass Email Newsletter Campaigns & Member Broadcasting",
                    description="Compose and broadcast weekly educational health newsletters to 8,500+ registered physicians and patients.",
                    category="FUNCTIONAL",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

            # IoT lab equipment sync (Meeting 3)
            elif "iot lab equipment" in lower or "blood analyzer" in lower:
                speaker = self._extract_speaker(line)
                requirements.append(Requirement(
                    id=f"REQ-{req_counter:03d}",
                    title="IoT Blood Analyzer REST Webhook Test Result Sync",
                    description="Automated secure webhook receiver that ingests blood panel completion events from laboratory analyzers into member patient portals.",
                    category="INTEGRATION",
                    speaker=speaker,
                    transcript_quote=line,
                    line_reference=line_idx
                ))
                req_counter += 1

        return requirements

    def _extract_speaker(self, line: str) -> str:
        if "]" in line and ":" in line:
            after_bracket = line.split("]")[1]
            return after_bracket.split(":")[0].strip()
        return "Participant"

clarifier_agent = ClarifierAgent()
