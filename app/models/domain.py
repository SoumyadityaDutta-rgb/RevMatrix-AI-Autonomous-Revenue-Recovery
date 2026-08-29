"""
RevMatrix AI - Domain Data Models & Enums
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class FailureCategory(str, Enum):
    PAYMENT_DEGRADATION = "payment_degradation"
    CHECKOUT_DROPOFF = "checkout_dropoff"
    FAILED_SUBSCRIPTION = "failed_subscription"
    B2B_RECEIVABLES = "b2b_receivables"
    MANDATE_FAILURE = "mandate_failure"

class DeclineType(str, Enum):
    SOFT = "soft_decline"       # Low balance, temporary bank downtime, rate limit, timeout
    HARD = "hard_decline"       # Expired card, stolen/lost card, invalid account, unauthorized
    UNKNOWN = "unknown"

class RecoveryChannel(str, Enum):
    SMART_RETRY = "smart_retry"
    UPI_DEEP_LINK = "upi_deep_link"
    WHATSAPP_INTERACTIVE = "whatsapp_interactive"
    HINGLISH_VOICE = "hinglish_voice"
    EMAIL_DUNNING = "email_dunning"
    TIERED_B2B_ESCALATION = "tiered_b2b_escalation"

class CaseStatus(str, Enum):
    AT_RISK = "at_risk"
    DIAGNOSED = "diagnosed"
    INTERVENTION_ACTIVE = "intervention_active"
    PTP_COMMITTED = "ptp_committed"
    RECOVERED = "recovered"
    HALTED_DISPUTE = "halted_dispute"
    HALTED_COMPLIANCE = "halted_compliance"
    LOST = "lost"

class Customer(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    company_name: Optional[str] = None
    language_preference: str = "hinglish" # hinglish, english, hindi

class TransactionContext(BaseModel):
    transaction_id: str
    order_id: Optional[str] = None
    subscription_id: Optional[str] = None
    invoice_id: Optional[str] = None
    amount_inr: float
    category: FailureCategory
    error_code: Optional[str] = None
    error_description: Optional[str] = None
    issuer_bank: Optional[str] = None
    payment_method: str = "card" # card, upi, netbanking, mandate
    created_at: datetime = Field(default_factory=datetime.utcnow)
    overdue_days: int = 0
    cart_items: Optional[List[str]] = None

class DiagnosticResult(BaseModel):
    category: FailureCategory
    decline_type: DeclineType
    root_cause: str
    confidence_score: float # 0.0 to 1.0
    recommended_strategy: str
    is_retryable: bool
    optimal_retry_timestamp: Optional[datetime] = None
    bank_downtime_detected: bool = False
    payday_aligned: bool = False

class InterventionPlan(BaseModel):
    case_id: str
    strategy_name: str
    channel: RecoveryChannel
    action_description: str
    razorpay_action_type: str # create_payment_link, schedule_mandate_retry, issue_discount_link, update_invoice
    payload: Dict[str, Any] = {}
    is_compliant: bool = True
    compliance_reason: Optional[str] = None

class PTPRecord(BaseModel):
    case_id: str
    customer_id: str
    promised_date: datetime
    amount: float
    status: str = "active" # active, fulfilled, breached
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcript_snippet: Optional[str] = None

class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    case_id: str
    event_type: str # DIAGNOSIS, INTERVENTION, COMPLIANCE_CHECK, TOOL_EXECUTION, PTP_RECORDED, RECOVERY_CONFIRMED, STOPPING_RULE_TRIGGERED
    actor: str = "RevMatrix-Agent"
    details: Dict[str, Any]
    hash_signature: str # Cryptographic hash for tamper evidence

class CaseRecord(BaseModel):
    id: str
    customer: Customer
    transaction: TransactionContext
    status: CaseStatus = CaseStatus.AT_RISK
    attempts_count: int = 0
    last_attempt_at: Optional[datetime] = None
    diagnostic: Optional[DiagnosticResult] = None
    active_intervention: Optional[InterventionPlan] = None
    ptp: Optional[PTPRecord] = None
    recovered_amount_inr: float = 0.0
    recovery_timestamp: Optional[datetime] = None
    is_disputed: bool = False
    audit_logs: List[AuditLogEntry] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BatchRecoveryMetrics(BaseModel):
    total_cases: int
    total_at_risk_inr: float
    total_recovered_inr: float
    recovery_rate_pct: float
    recovered_count: int
    lost_count: int
    ptp_count: int
    halted_compliance_count: int
    avg_recovery_latency_sec: float
    category_breakdown: Dict[str, Dict[str, Any]]
