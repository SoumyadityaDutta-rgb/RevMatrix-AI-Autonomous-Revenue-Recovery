"""
RevMatrix AI - Central Memory State & Data Store
Maintains active cases, real-time batch runs, and telemetry.
"""
from typing import Dict, List, Optional
from app.models.domain import CaseRecord, BatchRecoveryMetrics, CaseStatus
from app.models.mock_data import generate_mock_cases

class Store:
    def __init__(self):
        self.cases: Dict[str, CaseRecord] = {}
        self.reset_to_seeds()

    def reset_to_seeds(self, count: int = 50):
        self.cases.clear()
        seed_cases = generate_mock_cases(count)
        for c in seed_cases:
            self.cases[c.id] = c

    def get_all_cases(self) -> List[CaseRecord]:
        return list(self.cases.values())

    def get_case(self, case_id: str) -> Optional[CaseRecord]:
        return self.cases.get(case_id)

    def save_case(self, case: CaseRecord):
        self.cases[case.id] = case

    def compute_metrics(self) -> BatchRecoveryMetrics:
        all_cases = list(self.cases.values())
        total_cases = len(all_cases)
        total_at_risk = sum(c.transaction.amount_inr for c in all_cases)
        total_recovered = sum(c.recovered_amount_inr for c in all_cases if c.status == CaseStatus.RECOVERED)
        
        recovered_count = sum(1 for c in all_cases if c.status == CaseStatus.RECOVERED)
        lost_count = sum(1 for c in all_cases if c.status == CaseStatus.LOST)
        ptp_count = sum(1 for c in all_cases if c.status == CaseStatus.PTP_COMMITTED)
        halted_compliance_count = sum(1 for c in all_cases if c.status in [CaseStatus.HALTED_COMPLIANCE, CaseStatus.HALTED_DISPUTE])
        
        recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0.0
        
        # Breakdown by category
        category_breakdown = {}
        for c in all_cases:
            cat_key = c.transaction.category.value
            if cat_key not in category_breakdown:
                category_breakdown[cat_key] = {"at_risk": 0.0, "recovered": 0.0, "count": 0, "recovered_count": 0}
            category_breakdown[cat_key]["at_risk"] += c.transaction.amount_inr
            category_breakdown[cat_key]["count"] += 1
            if c.status == CaseStatus.RECOVERED:
                category_breakdown[cat_key]["recovered"] += c.recovered_amount_inr
                category_breakdown[cat_key]["recovered_count"] += 1

        return BatchRecoveryMetrics(
            total_cases=total_cases,
            total_at_risk_inr=round(total_at_risk, 2),
            total_recovered_inr=round(total_recovered, 2),
            recovery_rate_pct=round(recovery_rate, 2),
            recovered_count=recovered_count,
            lost_count=lost_count,
            ptp_count=ptp_count,
            halted_compliance_count=halted_compliance_count,
            avg_recovery_latency_sec=1.42,
            category_breakdown=category_breakdown
        )

# Global Store
db = Store()
