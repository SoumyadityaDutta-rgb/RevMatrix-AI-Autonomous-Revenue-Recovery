"""
RevMatrix AI - Recovery & Webhook Router
Endpoints to process batches, trigger single case interventions, register PTP, and handle live webhooks.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.state import db
from app.engine.orchestrator import orchestrator
from app.engine.ptp_tracker import ptp_tracker
from app.engine.audit_logger import audit_engine
from app.models.domain import CaseRecord, CaseStatus, FailureCategory, Customer, TransactionContext
import uuid

router = APIRouter(prefix="/api/recovery", tags=["Recovery"])

class PTPRequest(BaseModel):
    case_id: str
    user_statement: str

class WebhookSimulationRequest(BaseModel):
    event: str # payment.failed, subscription.charged_failed, order.dropoff, invoice.overdue
    amount: float
    customer_name: str
    customer_phone: str
    customer_email: str
    error_code: Optional[str] = "PAYMENT_INSUFFICIENT_FUNDS"
    bank: Optional[str] = "HDFC"
    company_name: Optional[str] = None

@router.get("/cases", response_model=List[CaseRecord])
def list_cases(status: Optional[str] = None, category: Optional[str] = None):
    all_cases = db.get_all_cases()
    if status:
        all_cases = [c for c in all_cases if c.status.value == status]
    if category:
        all_cases = [c for c in all_cases if c.transaction.category.value == category]
    return all_cases

@router.get("/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str):
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/cases/{case_id}/process", response_model=CaseRecord)
def process_single_case(case_id: str):
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    updated_case = orchestrator.process_case(case, simulate_immediate_resolution=True)
    db.save_case(updated_case)
    return updated_case

@router.post("/batch/run-all")
def run_batch_recovery():
    """
    Executes autonomous recovery across all unprocessed at-risk cases in batch.
    """
    processed = 0
    all_cases = db.get_all_cases()
    for case in all_cases:
        if case.status in [CaseStatus.AT_RISK, CaseStatus.DIAGNOSED]:
            updated = orchestrator.process_case(case, simulate_immediate_resolution=True)
            db.save_case(updated)
            processed += 1
            
    metrics = db.compute_metrics()
    return {
        "status": "success",
        "processed_cases": processed,
        "metrics": metrics
    }

@router.post("/batch/reset")
def reset_benchmark_dataset(count: int = 50):
    """
    Resets the workspace state with 50 fresh, realistic test cases.
    """
    audit_engine.clear()
    db.reset_to_seeds(count)
    return {"status": "reset_successful", "total_cases": len(db.get_all_cases())}

@router.post("/ptp/commit")
def commit_ptp(req: PTPRequest):
    """
    Extracts commitment date and activates suspension hold.
    """
    case = db.get_case(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    ptp_record = ptp_tracker.register_ptp(case, req.user_statement)
    db.save_case(case)
    
    return {
        "status": "ptp_registered",
        "ptp": ptp_record,
        "case": case
    }

@router.post("/webhook/simulate")
def simulate_razorpay_webhook(req: WebhookSimulationRequest):
    """
    Live presentation webhook injector to simulate an incoming failure event.
    """
    case_id = f"case_live_{uuid.uuid4().hex[:6]}"
    
    # Map event to category
    cat_map = {
        "payment.failed": FailureCategory.PAYMENT_DEGRADATION,
        "subscription.charged_failed": FailureCategory.FAILED_SUBSCRIPTION,
        "order.dropoff": FailureCategory.CHECKOUT_DROPOFF,
        "invoice.overdue": FailureCategory.B2B_RECEIVABLES,
        "mandate.failed": FailureCategory.MANDATE_FAILURE
    }
    category = cat_map.get(req.event, FailureCategory.PAYMENT_DEGRADATION)
    
    cust = Customer(
        id=f"cust_live_{uuid.uuid4().hex[:5]}",
        name=req.customer_name,
        phone=req.customer_phone,
        email=req.customer_email,
        company_name=req.company_name,
        language_preference="hinglish"
    )
    
    tx = TransactionContext(
        transaction_id=f"tx_live_{uuid.uuid4().hex[:8]}",
        amount_inr=req.amount,
        category=category,
        error_code=req.error_code,
        error_description="Injected live simulated webhook event",
        issuer_bank=req.bank,
        payment_method="card" if category == FailureCategory.FAILED_SUBSCRIPTION else "upi",
        overdue_days=14 if category == FailureCategory.B2B_RECEIVABLES else 0
    )
    
    case = CaseRecord(
        id=case_id,
        customer=cust,
        transaction=tx,
        status=CaseStatus.AT_RISK
    )
    
    # Process immediately
    processed_case = orchestrator.process_case(case, simulate_immediate_resolution=True)
    db.save_case(processed_case)
    
    return {
        "message": f"Webhook '{req.event}' ingested and processed autonomously.",
        "case": processed_case
    }
