"""
RevMatrix AI - Pillar 7: Promise-to-Pay (PTP) State Machine & Tracker
Parses customer commitments, pauses account suspension/churn, and manages scheduled reminder queues.
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models.domain import CaseRecord, PTPRecord, CaseStatus
from app.engine.audit_logger import audit_engine

class PTPTracker:
    
    @staticmethod
    def parse_promise_date(text: str) -> datetime:
        """
        Extracts future commitment date from Hinglish / English conversation snippets.
        """
        text_lower = text.lower()
        now = datetime.utcnow()
        
        if "kal" in text_lower or "tomorrow" in text_lower:
            return now + timedelta(days=1)
        elif "parso" in text_lower or "in 2 days" in text_lower:
            return now + timedelta(days=2)
        elif "friday" in text_lower or "shukrawar" in text_lower:
            days_ahead = (4 - now.weekday()) % 7
            return now + timedelta(days=days_ahead if days_ahead > 0 else 7)
        elif "monday" in text_lower or "somwar" in text_lower:
            days_ahead = (0 - now.weekday()) % 7
            return now + timedelta(days=days_ahead if days_ahead > 0 else 7)
        elif "weekend" in text_lower:
            days_ahead = (5 - now.weekday()) % 7
            return now + timedelta(days=days_ahead if days_ahead > 0 else 7)
        elif "next week" in text_lower or "agle hafte" in text_lower:
            return now + timedelta(days=7)
        
        # Check for numeric dates like "5th", "10 tarik"
        match = re.search(r'(\d{1,2})(?:st|nd|rd|th|\s*tarik|\s*tareekh)', text_lower)
        if match:
            day_num = int(match.group(1))
            if 1 <= day_num <= 31:
                try:
                    target_month = now.month if day_num > now.day else (now.month % 12 + 1)
                    target_year = now.year + (1 if target_month == 1 and day_num <= now.day else 0)
                    return datetime(target_year, target_month, day_num, 10, 0, 0)
                except ValueError:
                    pass
                    
        # Default promise date: 3 days grace
        return now + timedelta(days=3)

    @classmethod
    def register_ptp(cls, case: CaseRecord, user_statement: str) -> PTPRecord:
        promised_date = cls.parse_promise_date(user_statement)
        
        ptp = PTPRecord(
            case_id=case.id,
            customer_id=case.customer.id,
            promised_date=promised_date,
            amount=case.transaction.amount_inr,
            status="active",
            transcript_snippet=user_statement
        )
        
        case.ptp = ptp
        case.status = CaseStatus.PTP_COMMITTED
        
        audit_engine.record(
            case_id=case.id,
            event_type="PTP_RECORDED",
            actor="PTPTracker",
            details={
                "statement": user_statement,
                "parsed_date": promised_date.strftime("%Y-%m-%d"),
                "amount": ptp.amount,
                "action": "SUSPENSION_HOLD_ACTIVATED"
            }
        )
        
        return ptp

ptp_tracker = PTPTracker()
