"""
RevMatrix AI - Tamper-Evident Cryptographic Audit Logger
Ensures full compliance, traceability, and auditability for all agent actions.
"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.models.domain import AuditLogEntry

class AuditEngine:
    def __init__(self):
        self._global_audit_trail: List[AuditLogEntry] = []
        self._prev_hash = "GENESIS_REVMETRIX_BLOCK_0000"

    def record(self, case_id: str, event_type: str, actor: str, details: Dict[str, Any]) -> AuditLogEntry:
        timestamp = datetime.utcnow()
        log_id = f"aud_{uuid.uuid4().hex[:10]}"
        
        # Build payload for cryptographic SHA-256 block-linking
        payload = {
            "log_id": log_id,
            "timestamp": timestamp.isoformat(),
            "case_id": case_id,
            "event_type": event_type,
            "actor": actor,
            "details": details,
            "prev_hash": self._prev_hash
        }
        
        serialized = json.dumps(payload, sort_keys=True, default=str)
        hash_signature = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        self._prev_hash = hash_signature

        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=timestamp,
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            details=details,
            hash_signature=hash_signature
        )

        self._global_audit_trail.append(entry)
        return entry

    def get_case_logs(self, case_id: str) -> List[AuditLogEntry]:
        return [l for l in self._global_audit_trail if l.case_id == case_id]

    def get_all_logs(self, limit: int = 200) -> List[AuditLogEntry]:
        return sorted(self._global_audit_trail, key=lambda x: x.timestamp, reverse=True)[:limit]

    def clear(self):
        self._global_audit_trail.clear()
        self._prev_hash = "GENESIS_REVMETRIX_BLOCK_0000"

# Global Audit Instance
audit_engine = AuditEngine()
