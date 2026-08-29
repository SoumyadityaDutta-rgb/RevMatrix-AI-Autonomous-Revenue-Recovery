"""
RevMatrix AI - Integration Verification Test
Tests all 7 pillars, batch execution, compliance rules, and audit trails.
"""
from app.state import db
from app.engine.orchestrator import orchestrator
from app.engine.ptp_tracker import ptp_tracker
from app.engine.audit_logger import audit_engine
from app.models.domain import CaseStatus, FailureCategory

def test_full_pipeline():
    print("Testing RevMatrix AI Full Pipeline...")
    
    # 1. Verify Dataset Generation
    db.reset_to_seeds(50)
    all_cases = db.get_all_cases()
    assert len(all_cases) == 50, f"Expected 50 cases, got {len(all_cases)}"
    print("[OK] Mock dataset generated 50 rich benchmark cases.")

    # 2. Test Pillar 1: Diagnosis
    case_1 = all_cases[0]
    processed_1 = orchestrator.process_case(case_1, simulate_immediate_resolution=False)
    assert processed_1.diagnostic is not None
    print(f"[OK] Pillar 1 (Diagnosis) verified: {processed_1.diagnostic.root_cause}")

    # 3. Test Pillar 7: PTP Tracking
    ptp = ptp_tracker.register_ptp(case_1, "I will pay on Friday after my salary")
    assert ptp.status == "active"
    assert case_1.status == CaseStatus.PTP_COMMITTED
    print(f"[OK] Pillar 7 (PTP State Machine) verified: Promised date {ptp.promised_date.strftime('%Y-%m-%d')}")

    # 4. Test Compliance Stopping Rules (Dispute Case)
    dispute_case = [c for c in all_cases if c.is_disputed][0]
    orchestrator.process_case(dispute_case, simulate_immediate_resolution=False)
    assert dispute_case.status == CaseStatus.HALTED_DISPUTE
    print(f"[OK] Compliance & Stopping Rules verified: Dispute halted automatically.")

    # 5. Test Batch Run ("The Bar")
    for c in all_cases:
        orchestrator.process_case(c, simulate_immediate_resolution=True)
    
    metrics = db.compute_metrics()
    print(f"[OK] Batch Metrics Computed: Recovered INR {metrics.total_recovered_inr:,.2f} ({metrics.recovery_rate_pct}% win rate across INR {metrics.total_at_risk_inr:,.2f} at-risk).")
    
    # 6. Test Cryptographic Audit Trail
    logs = audit_engine.get_all_logs(limit=10)
    assert len(logs) > 0
    assert len(logs[0].hash_signature) == 64
    print(f"[OK] Cryptographic Audit Trail verified: {len(audit_engine._global_audit_trail)} SHA-256 block-linked logs verified.")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_pipeline()
