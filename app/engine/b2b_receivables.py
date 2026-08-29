"""
RevMatrix AI - Pillar 4: B2B Receivables Chaser
Autonomous aged-debt recovery with compliant multi-tier escalations and Razorpay Invoicing.
"""
from app.models.domain import CaseRecord, InterventionPlan, RecoveryChannel
from app.razorpay_client import rzp_client
from app.engine.audit_logger import audit_engine

class B2BReceivablesChaser:
    
    @staticmethod
    def execute(case: CaseRecord) -> InterventionPlan:
        inv_id = case.transaction.invoice_id or f"inv_{case.id}"
        amount = case.transaction.amount_inr
        overdue_days = case.transaction.overdue_days
        company = case.customer.company_name or "Enterprise Partner"
        
        # Tiered Escalation Matrix
        if overdue_days <= 7:
            tier = "Tier 1: Friendly Reconciliation"
            channel = RecoveryChannel.EMAIL_DUNNING
            subject = f"Friendly Reminder: Invoice {inv_id} for {company}"
            escalation_note = "Dispatched courteous payment link and ledger breakdown to Accounts Payable."
        elif overdue_days <= 21:
            tier = "Tier 2: CFO & Finance Lead Alert"
            channel = RecoveryChannel.TIERED_B2B_ESCALATION
            subject = f"Urgent: Overdue Invoice {inv_id} - Action Required for {company}"
            escalation_note = "Escalated to Finance Head with 1-click Razorpay NEFT/RTGS Virtual Account link."
        else:
            tier = "Tier 3: Executive Escalation & Pre-Legal Notice Draft"
            channel = RecoveryChannel.TIERED_B2B_ESCALATION
            subject = f"FINAL NOTICE: Overdue Payment for Invoice {inv_id} - Suspension Warning"
            escalation_note = "Generated formal final demand notice with dispute-review portal link before service freeze."

        # Generate / Update Razorpay Invoice Link
        rzp_inv = rzp_client.create_or_update_invoice(
            customer_id=case.customer.id,
            amount_inr=amount,
            description=f"B2B Invoice {inv_id} for {company} ({tier})",
            due_date_days=3
        )
        
        plan = InterventionPlan(
            case_id=case.id,
            strategy_name=f"B2B Receivables {tier}",
            channel=channel,
            action_description=escalation_note,
            razorpay_action_type="create_or_update_invoice",
            payload={
                "invoice_id": inv_id,
                "tier": tier,
                "overdue_days": overdue_days,
                "company_name": company,
                "amount": amount,
                "invoice_url": rzp_inv["payment_link"],
                "subject": subject
            }
        )
        
        audit_engine.record(
            case_id=case.id,
            event_type="TOOL_EXECUTION",
            actor="B2BReceivablesChaser",
            details={
                "action": "b2b_escalation_executed",
                "tier": tier,
                "overdue_days": overdue_days,
                "amount": amount,
                "invoice_id": inv_id
            }
        )
        
        return plan

b2b_chaser = B2BReceivablesChaser()
