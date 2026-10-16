from typing import List
from app.models import MeetingTranscript

TRANSCRIPT_MEETING_1 = """[00:01] Dave (Lead Consultant): Thanks for joining today, Jennifer and Alex. The purpose of this discovery session is to map out your requirements for the Apex Medical Specialist Directory. Jennifer, could you start by walking us through your core vision?
[00:15] Jennifer (Client CEO): Absolutely Dave. We are building a nationwide directory of certified medical specialists and surgeons. Our patients need to easily find doctors near them. Specifically, we need patients to enter their zip code and filter doctors within a 25-mile or 50-mile radius.
[00:35] Dave (Lead Consultant): Understood. Location and radius search. And how are doctors monetized on the platform?
[00:42] Jennifer (Client CEO): We want automated recurring payments. Verified doctors should be billed $199 per month or $1,999 annually on credit card. We already have an active Stripe merchant account.
[00:58] Alex (Client CTO): In addition to billing, we need strict tier privileges. Basic doctors can only list contact info. Premium verified doctors should be allowed to publish medical articles, community health events, and accept patient inquiries.
[01:15] Dave (Lead Consultant): Perfect, that makes sense. Now Alex, what about technical integrations or custom features?
[01:24] Alex (Client CTO): We have two complex requirements. First, we need a custom HIPAA-compliant telemedicine portal directly embedded into the doctor profile, with encrypted WebRTC video calling so patients can do remote consultations.
[01:45] Jennifer (Client CEO): Yes, that's our key differentiator.
[01:49] Alex (Client CTO): Second, we want to integrate with hospital electronic health record systems—specifically pulling doctor credentials from Epic EHR using their HL7 FHIR API on a nightly sync.
[02:08] Dave (Lead Consultant): Excellent. We will evaluate what can be configured immediately with built-in platform capabilities versus what requires custom engineering, and assemble a comprehensive scope of work."""

TRANSCRIPT_MEETING_2 = """[00:01] Dave (Lead Consultant): Good afternoon Jennifer and Alex. We are reviewing the baseline scope of work we prepared following our first discovery call. Alex, I understand the clinical board has made several adjustments to the scope?
[00:18] Alex (Client CTO): That's right, Dave. First, on the payment side, our European partners requested that we add PayPal support alongside Stripe for doctors who don't want to use direct credit cards.
[00:32] Dave (Lead Consultant): Got it, adding PayPal to the payment gateway setup. And what about the doctor search and membership plans?
[00:41] Jennifer (Client CEO): The zip code radius search and membership tier privileges are perfect as proposed. Keep those exactly as is.
[00:53] Alex (Client CTO): Now for the major changes. On the telemedicine portal, the board decided one-on-one video isn't enough. We need multi-party group therapy sessions supporting up to 6 participants simultaneously, plus calendar appointment booking sync with Google Calendar.
[01:16] Dave (Lead Consultant): That significantly expands the video architecture and websocket server requirements. That will increase the custom development effort.
[01:25] Alex (Client CTO): We understand. To balance the budget, we are deferring the Epic EHR HL7 integration to Phase 2. Remove Epic EHR integration from this sprint entirely.
[01:40] Jennifer (Client CEO): However, Dave, we want to add a brand new feature in its place: an AI Symptom Checker on the homepage. When a patient types their symptoms, an AI recommends the top 3 relevant medical specialties in our directory and links directly to those search results.
[02:05] Dave (Lead Consultant): Understood. The AI Symptom Checker is a newly added deliverable that was not part of the baseline quote. We will produce a Scope Diff Report showing what remained unchanged, what was modified, what was removed, and calculate the formal change order budget."""

TRANSCRIPT_MEETING_3 = """[00:01] Dave (Lead Consultant): Welcome Marcus and Dr. Aris from BioHealth Labs. Let's outline the requirements for your clinical diagnostics directory.
[00:12] Marcus (Client Director): Hi Dave. We operate 40 diagnostic labs across 4 states. First, patients need to submit test requisition inquiries and have them automatically matched to the nearest lab facility by test specialty and geographic proximity.
[00:30] Dr. Aris (Chief Medical Officer): Second, we need to send weekly educational health newsletters and campaign announcements to all 8,500 registered patients and referring physicians.
[00:48] Marcus (Client Director): Third, we need a custom IoT lab equipment sync. When an automated blood analyzer finishes a panel, we want it to securely push test status updates via a REST webhook directly into the patient's private portal.
[01:05] Dave (Lead Consultant): Clear requirements. We will analyze the native capabilities of the platform for lead routing and newsletter marketing, and scope custom development for the IoT webhook sync."""

SAMPLE_TRANSCRIPTS: List[MeetingTranscript] = [
    MeetingTranscript(
        id="meeting-001",
        title="Apex Medical Specialist Directory - Initial Discovery",
        date="2026-10-12",
        client_name="Apex Healthcare Network",
        speakers=["Dave (Lead Consultant)", "Jennifer (Client CEO)", "Alex (Client CTO)"],
        raw_text=TRANSCRIPT_MEETING_1,
        is_followup=False
    ),
    MeetingTranscript(
        id="meeting-002",
        title="Apex Medical Specialist Directory - Scope Shift & Follow-up",
        date="2026-10-15",
        client_name="Apex Healthcare Network",
        speakers=["Dave (Lead Consultant)", "Jennifer (Client CEO)", "Alex (Client CTO)"],
        raw_text=TRANSCRIPT_MEETING_2,
        is_followup=True,
        baseline_meeting_id="meeting-001"
    ),
    MeetingTranscript(
        id="meeting-003",
        title="BioHealth Diagnostics - Initial Discovery & IoT Sync",
        date="2026-10-16",
        client_name="BioHealth Labs",
        speakers=["Dave (Lead Consultant)", "Marcus (Client Director)", "Dr. Aris (Chief Medical Officer)"],
        raw_text=TRANSCRIPT_MEETING_3,
        is_followup=False
    )
]
