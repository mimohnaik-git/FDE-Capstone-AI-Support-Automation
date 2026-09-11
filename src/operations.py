"""Operational controls layered around, but not inside, frozen V1 inference."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KILL_SWITCH_FILE = PROJECT_ROOT / "storage" / "auto_response.disabled"
KILL_SWITCH_REASON = "Automatic responses are disabled by the operational kill switch."
KILL_SWITCH_REASON_CODE = "KILL_SWITCH_ENABLED"


def kill_switch_path() -> Path:
    configured = os.getenv("SUPPORT_KILL_SWITCH_FILE")
    return Path(configured).resolve() if configured else DEFAULT_KILL_SWITCH_FILE


def is_kill_switch_enabled() -> bool:
    """Read dynamic state for every request; no deployment or process restart required."""
    environment_enabled = os.getenv("SUPPORT_KILL_SWITCH", "").strip().lower() in {
        "1", "true", "yes", "on", "enabled",
    }
    return environment_enabled or kill_switch_path().is_file()


def kill_switch_escalation(orchestrator: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Persist one explicit escalation while bypassing all frozen inference stages."""
    try:
        normalized = orchestrator.ingester.normalize_ticket(payload)
        decision = {
            "ticket_id": normalized["ticket_id"], "ticket": normalized,
            "classification": {}, "retrieval": [],
            "routing": {"action": "ESCALATE", "reason_code": KILL_SWITCH_REASON_CODE, "reason": KILL_SWITCH_REASON},
            "generation": {}, "guardrails": {}, "selected_action": "ESCALATE",
            "prediction": "ESCALATE", "reason": KILL_SWITCH_REASON,
            "reason_code": KILL_SWITCH_REASON_CODE, "response_released": False,
            "processing_status": "COMPLETED", "requirement_ids": ["A8", "A11"],
        }
        decision_id = orchestrator.logger.log_decision(decision)
        if not orchestrator.logger.get_decision_by_id(decision_id):
            raise RuntimeError("Kill-switch audit record could not be read back")
        return {
            "ticket_id": normalized["ticket_id"], "status": "ESCALATE", "action": "ESCALATE",
            "response_released": False, "response_text": None, "response": None,
            "classification": {}, "guardrails": {}, "reason": KILL_SWITCH_REASON,
            "reason_code": KILL_SWITCH_REASON_CODE, "decision_id": decision_id,
            "processing_status": "COMPLETED", "failure_state": None,
        }
    except Exception:
        return {
            "ticket_id": str(payload.get("ticket_id") or "UNKNOWN"), "status": "ESCALATE",
            "action": "ESCALATE", "response_released": False, "response_text": None,
            "response": None, "classification": {}, "guardrails": {},
            "reason": "Automatic response suppressed; kill-switch audit persistence failed.",
            "reason_code": "AUDIT_PERSISTENCE_FAILED", "decision_id": None,
            "processing_status": "FAILED", "failure_state": "AUDIT_PERSISTENCE_FAILED",
        }
