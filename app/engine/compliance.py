"""
RevMatrix AI - Compliance & Stopping Rules Engine
Enforces strict regulatory bounds, anti-harassment limits, quiet hours, and chargeback freezes.
"""
from datetime import datetime, timezone, timedelta
from typing import Tuple
from app.models.domain import CaseRecord, CaseStatus
from app.config import settings

class ComplianceGuard:
    
    @staticmethod
    def evaluate_compliance(case: CaseRecord, channel_type: str = "general") -> Tuple[bool, str]:
        """
        Evaluates whether an intervention is permissible under strict regulatory & business guardrails.
        Returns: (is_allowed: bool, reason: str)
        """
        # Rule 1: Dispute / Chargeback immediate freeze
        if case.is_disputed or case.status == CaseStatus.HALTED_DISPUTE:
            return False, "STOPPING RULE TRIGGERED: Active payment dispute / chargeback logged. All automated outreach frozen for legal compliance."

        # Rule 2: Max outreach attempts exceeded (Anti-harassment bound)
        if case.attempts_count >= settings.MAX_ATTEMPTS_PER_48H:
            return False, f"STOPPING RULE TRIGGERED: Maximum threshold of {settings.MAX_ATTEMPTS_PER_48H} attempts reached within cooldown window. Escalated to manual CS hold."

        # Rule 3: Hard decline stopping rule (Never retry card that is expired or reported stolen)
        if case.diagnostic and case.diagnostic.decline_type.value == "hard_decline":
            if channel_type in ["smart_retry", "mandate_failure"]:
                return False, "STOPPING RULE TRIGGERED: Hard decline detected (Card Expired / Account Closed). Retries permanently disabled; must request new payment method."

        # Rule 4: Indian Telecom / RBI Quiet Hours Compliance (9 PM to 8 AM IST)
        # IST is UTC + 5:30
        now_utc = datetime.utcnow()
        ist_now = now_utc + timedelta(hours=5, minutes=30)
        current_hour_ist = ist_now.hour

        if channel_type in ["hinglish_voice", "whatsapp_interactive"]:
            if current_hour_ist >= settings.QUIET_HOURS_START_IST or current_hour_ist < settings.QUIET_HOURS_END_IST:
                return False, f"QUIET HOURS PAUSE: Current time {ist_now.strftime('%I:%M %p IST')} is within restricted hours (9 PM - 8 AM). Outreach queued for 08:30 AM."

        # Rule 5: Active Promise-to-Pay (PTP) cooldown
        if case.ptp and case.ptp.status == "active":
            if case.ptp.promised_date > datetime.utcnow():
                return False, f"PTP PROTECTION: Customer has active Promise-to-Pay committed until {case.ptp.promised_date.strftime('%Y-%m-%d')}. Dunning paused."

        # Rule 6: Already recovered
        if case.status == CaseStatus.RECOVERED:
            return False, "STOPPING RULE TRIGGERED: Transaction already successfully recovered."

        return True, "COMPLIANCE PASSED: All guardrails satisfied."
