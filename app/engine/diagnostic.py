"""
RevMatrix AI - Pillar 1: Payment Degradation & Root Cause Diagnostic Engine
Classifies failures into Soft/Hard declines, detects bank-wide degradations, and recommends optimal recovery.
"""
from datetime import datetime, timedelta
import random
from app.models.domain import TransactionContext, DiagnosticResult, FailureCategory, DeclineType

# Known Bank Downtime Simulator & Heatmap (Simulating real-time NPCI/Bank Health)
BANK_HEALTH_REGISTRY = {
    "HDFC": {"status": "healthy", "success_rate": 0.94},
    "SBI": {"status": "degraded", "success_rate": 0.62, "reason": "CBS Maintenance Latency"},
    "ICICI": {"status": "healthy", "success_rate": 0.96},
    "AXIS": {"status": "healthy", "success_rate": 0.92},
    "KOTAK": {"status": "healthy", "success_rate": 0.95},
    "PAYTM_BANK": {"status": "degraded", "success_rate": 0.58, "reason": "UPI Switch Congestion"}
}

# Error Code Classification Matrix
SOFT_DECLINE_CODES = {
    "BAD_REQUEST_PAYMENT_TIMED_OUT": "3DS Authentication Timed Out",
    "PAYMENT_INSUFFICIENT_FUNDS": "Temporary Low Balance",
    "GATEWAY_ERROR": "Issuer Gateway Network Timeout",
    "BANK_TECHNICAL_ERROR": "Bank Server Internal Failure",
    "TRANSACTION_AMOUNT_LIMIT_EXCEEDED": "Daily Limit Hit",
    "OTP_EXPIRED": "OTP Verification Window Expired"
}

HARD_DECLINE_CODES = {
    "CARD_EXPIRED": "Card has Expired",
    "ACCOUNT_CLOSED": "Bank Account is Inactive or Closed",
    "FRAUD_SUSPECTED": "Transaction Flagged by Risk Rules",
    "INVALID_CARD_NUMBER": "Invalid Instrument Credentials",
    "CARD_REPORTED_LOST_STOLEN": "Card Reported Stolen"
}

class DiagnosticEngine:
    
    @staticmethod
    def diagnose(tx: TransactionContext) -> DiagnosticResult:
        """
        Performs multi-layered root-cause analysis on a failed or at-risk transaction.
        """
        category = tx.category
        error_code = tx.error_code or "UNKNOWN"
        bank = (tx.issuer_bank or "UNKNOWN").upper()
        
        # Check bank degradation status
        bank_info = BANK_HEALTH_REGISTRY.get(bank, {"status": "healthy", "success_rate": 0.90})
        is_bank_degraded = bank_info.get("status") == "degraded"
        
        # 1. Hard Decline Check
        if error_code in HARD_DECLINE_CODES or "EXPIRED" in error_code or "FRAUD" in error_code:
            return DiagnosticResult(
                category=category,
                decline_type=DeclineType.HARD,
                root_cause=HARD_DECLINE_CODES.get(error_code, "Instrument permanently invalid or rejected."),
                confidence_score=0.98,
                recommended_strategy="Do NOT retry instrument. Request customer to add alternate UPI ID / new card via dynamic Razorpay link.",
                is_retryable=False,
                optimal_retry_timestamp=None,
                bank_downtime_detected=is_bank_degraded,
                payday_aligned=False
            )
            
        # 2. Bank Downtime Degradation Check
        if is_bank_degraded or error_code in ["GATEWAY_ERROR", "BANK_TECHNICAL_ERROR"]:
            # Schedule retry after bank switch recovers (e.g. 45 mins)
            retry_time = datetime.utcnow() + timedelta(minutes=45)
            return DiagnosticResult(
                category=category,
                decline_type=DeclineType.SOFT,
                root_cause=f"Issuer Bank ({bank}) degradation detected: {bank_info.get('reason', 'Network anomaly')}.",
                confidence_score=0.92,
                recommended_strategy="Activate Smart Delay. Switch to alternate payment rail or wait for bank switch recovery before retrying.",
                is_retryable=True,
                optimal_retry_timestamp=retry_time,
                bank_downtime_detected=True,
                payday_aligned=False
            )
            
        # 3. Soft Decline / Low Balance Check
        if error_code in ["PAYMENT_INSUFFICIENT_FUNDS", "OTP_EXPIRED", "BAD_REQUEST_PAYMENT_TIMED_OUT"]:
            # Check payday cycle alignment
            current_day = datetime.utcnow().day
            is_near_payday = 1 <= current_day <= 7 or current_day >= 28
            retry_delta = timedelta(hours=4) if not is_near_payday else timedelta(hours=12)
            
            return DiagnosticResult(
                category=category,
                decline_type=DeclineType.SOFT,
                root_cause=SOFT_DECLINE_CODES.get(error_code, "Temporary authentication or balance constraint."),
                confidence_score=0.89,
                recommended_strategy="Dispatch dynamic 1-click Razorpay UPI intent link on WhatsApp + Schedule smart mandate retry.",
                is_retryable=True,
                optimal_retry_timestamp=datetime.utcnow() + retry_delta,
                bank_downtime_detected=False,
                payday_aligned=is_near_payday
            )

        # 4. Checkout Drop-Off
        if category == FailureCategory.CHECKOUT_DROPOFF:
            return DiagnosticResult(
                category=category,
                decline_type=DeclineType.SOFT,
                root_cause="User abandoned checkout funnel before OTP/Payment confirmation.",
                confidence_score=0.85,
                recommended_strategy="Instant WhatsApp rescue with 1-click Razorpay UPI pre-filled checkout link & 5% limited-time incentive.",
                is_retryable=False,
                optimal_retry_timestamp=None,
                bank_downtime_detected=False,
                payday_aligned=False
            )

        # 5. B2B Receivables
        if category == FailureCategory.B2B_RECEIVABLES:
            overdue = tx.overdue_days
            tier = "Tier 1: Gentle Reminder" if overdue <= 7 else ("Tier 2: CFO Notification" if overdue <= 21 else "Tier 3: Executive Escalation")
            return DiagnosticResult(
                category=category,
                decline_type=DeclineType.SOFT,
                root_cause=f"Invoice overdue by {overdue} days. Aged receivables aging bucket: {tier}.",
                confidence_score=0.95,
                recommended_strategy=f"Execute {tier} with automated Razorpay Smart Invoice link & ledger reconciliation.",
                is_retryable=False,
                optimal_retry_timestamp=None,
                bank_downtime_detected=False,
                payday_aligned=False
            )

        # Fallback default
        return DiagnosticResult(
            category=category,
            decline_type=DeclineType.SOFT,
            root_cause="Transient payment pipeline failure.",
            confidence_score=0.75,
            recommended_strategy="Fallback to multi-channel dynamic payment link outreach.",
            is_retryable=True,
            optimal_retry_timestamp=datetime.utcnow() + timedelta(hours=2),
            bank_downtime_detected=False,
            payday_aligned=False
        )

# Global Diagnostic Instance
diagnostic_engine = DiagnosticEngine()
