"""
RevMatrix AI - Central Autonomous Recovery Orchestrator
Executes the end-to-end bounded recovery loop: Detect -> Diagnose -> Check Compliance -> Intervene -> Audit -> Resolve.
"""
import random
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.domain import CaseRecord, CaseStatus, FailureCategory, DeclineType
from app.engine.diagnostic import diagnostic_engine
from app.engine.compliance import ComplianceGuard
from app.engine.dropoff_recovery import dropoff_agent
from app.engine.subscription_dunning import subscription_agent
from app.engine.b2b_receivables import b2b_chaser
from app.engine.mandate_sequencer import mandate_sequencer
from app.engine.hinglish_voice import hinglish_agent
from app.engine.audit_logger import audit_engine

class RecoveryOrchestrator:
    
    @classmethod
    def process_case(cls, case: CaseRecord, simulate_immediate_resolution: bool = True) -> CaseRecord:
        """
        Processes a single case through the full autonomous pipeline.
        """
        # Step 1: Diagnose root cause
        diagnostic = diagnostic_engine.diagnose(case.transaction)
        case.diagnostic = diagnostic
        case.status = CaseStatus.DIAGNOSED
        
        audit_engine.record(
            case_id=case.id,
            event_type="DIAGNOSIS",
            actor="DiagnosticEngine",
            details={
                "category": diagnostic.category.value,
                "decline_type": diagnostic.decline_type.value,
                "root_cause": diagnostic.root_cause,
                "confidence": diagnostic.confidence_score,
                "is_retryable": diagnostic.is_retryable,
                "bank_downtime": diagnostic.bank_downtime_detected
            }
        )

        # Step 2: Check Compliance & Stopping Rules
        channel_name = case.transaction.category.value
        is_compliant, compliance_reason = ComplianceGuard.evaluate_compliance(case, channel_name)
        
        audit_engine.record(
            case_id=case.id,
            event_type="COMPLIANCE_CHECK",
            actor="ComplianceGuard",
            details={
                "is_allowed": is_compliant,
                "reason": compliance_reason,
                "attempts_count": case.attempts_count
            }
        )
        
        if not is_compliant:
            if "DISPUTE" in compliance_reason or case.is_disputed:
                case.status = CaseStatus.HALTED_DISPUTE
            else:
                case.status = CaseStatus.HALTED_COMPLIANCE
            return case

        # Step 3: Execute Autonomous Intervention Worker
        case.attempts_count += 1
        case.last_attempt_at = datetime.utcnow()
        category = case.transaction.category
        
        if category == FailureCategory.CHECKOUT_DROPOFF:
            plan = dropoff_agent.execute(case)
        elif category == FailureCategory.FAILED_SUBSCRIPTION:
            # If customer prefers voice or hinglish, trigger voice agent
            if case.customer.language_preference == "hinglish" and case.transaction.amount_inr > 2000:
                plan = hinglish_agent.execute(case)
            else:
                plan = subscription_agent.execute(case)
        elif category == FailureCategory.B2B_RECEIVABLES:
            plan = b2b_chaser.execute(case)
        elif category == FailureCategory.MANDATE_FAILURE:
            plan = mandate_sequencer.execute(case)
        else: # PAYMENT_DEGRADATION
            if diagnostic.decline_type == DeclineType.HARD:
                plan = subscription_agent.execute(case)
            elif diagnostic.bank_downtime_detected:
                plan = mandate_sequencer.execute(case)
            else:
                plan = dropoff_agent.execute(case)
                
        case.active_intervention = plan
        case.status = CaseStatus.INTERVENTION_ACTIVE

        # Step 4: Resolution & ROI Simulation (Simulating real-world conversion bump)
        if simulate_immediate_resolution:
            # Dynamic recovery probability calculation
            base_prob = 0.82
            if diagnostic.decline_type == DeclineType.HARD:
                base_prob = 0.65  # Customer must provide new instrument
            elif diagnostic.bank_downtime_detected:
                base_prob = 0.91  # High recovery once bank recovers
            elif category == FailureCategory.B2B_RECEIVABLES and case.transaction.overdue_days > 30:
                base_prob = 0.60
            elif case.ptp:
                base_prob = 0.88

            is_recovered = random.random() < base_prob
            
            if is_recovered:
                case.status = CaseStatus.RECOVERED
                case.recovered_amount_inr = case.transaction.amount_inr
                case.recovery_timestamp = datetime.utcnow()
                
                audit_engine.record(
                    case_id=case.id,
                    event_type="RECOVERY_CONFIRMED",
                    actor="RevMatrixEngine",
                    details={
                        "recovered_amount_inr": case.recovered_amount_inr,
                        "payment_rail": "Razorpay_Smart_Checkout",
                        "status": "SETTLED"
                    }
                )
            else:
                if case.attempts_count >= 3:
                    case.status = CaseStatus.LOST
                else:
                    case.status = CaseStatus.INTERVENTION_ACTIVE

        return case

orchestrator = RecoveryOrchestrator()
