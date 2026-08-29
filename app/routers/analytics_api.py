"""
RevMatrix AI - Analytics & Audit Trail Router
Provides aggregated metrics, win-rate breakdown, ROI, and tamper-evident audit log query.
"""
from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
from app.state import db
from app.engine.audit_logger import audit_engine
from app.models.domain import BatchRecoveryMetrics, AuditLogEntry

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Audit"])

@router.get("/metrics", response_model=BatchRecoveryMetrics)
def get_recovery_metrics():
    """
    Returns high-level summary metrics, total money recovered ₹, and win rates.
    """
    return db.compute_metrics()

@router.get("/audit-logs", response_model=List[AuditLogEntry])
def get_audit_trail(case_id: Optional[str] = None, limit: int = Query(default=100, le=500)):
    """
    Returns cryptographic tamper-evident audit logs across all cases or for a specific case.
    """
    if case_id:
        return audit_engine.get_case_logs(case_id)
    return audit_engine.get_all_logs(limit=limit)

@router.get("/overview")
def get_dashboard_overview():
    metrics = db.compute_metrics()
    all_cases = db.get_all_cases()
    
    # Recent activity stream
    recent_logs = audit_engine.get_all_logs(limit=10)
    
    return {
        "metrics": metrics,
        "total_active_cases": len(all_cases),
        "recent_audit_events": recent_logs
    }
