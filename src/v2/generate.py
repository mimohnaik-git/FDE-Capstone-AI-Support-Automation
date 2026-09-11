"""Deterministic task-oriented synthesis for the isolated V2 candidate."""

from dataclasses import dataclass
from typing import Any, Dict, List

from src.generate import FAILURE_INSUFFICIENT_DOCUMENTATION

GENERATOR_VERSION = "deterministic-resolution-synthesis-v2.0.0"


@dataclass
class TaskOrientedGroundedProviderV2:
    """Release only retrieved passage text, preserving exact source attribution."""
    name: str = "offline-grounded-v2"
    model: str = GENERATOR_VERSION

    def generate(self, system_instructions: str, customer_input: str,
                 retrieved_context: List[Dict[str, Any]], structured_schema: Dict[str, Any]) -> Dict[str, Any]:
        if not retrieved_context:
            return {"answer": None, "citations": [], "supported": False,
                    "uncertainty": FAILURE_INSUFFICIENT_DOCUMENTATION}
        first = retrieved_context[0]; passage = str(first.get("passage", "")).strip()
        if not passage:
            return {"answer": None, "citations": [], "supported": False,
                    "uncertainty": FAILURE_INSUFFICIENT_DOCUMENTATION}
        section = str(first.get("section", "Document")); title = str(first.get("title") or first["document_id"])
        prefix = "Documented resolution" if section.lower() == "resolution" else "Documented guidance"
        return {"answer": f"{prefix} from {title}:\n\n{passage}",
                "citations": [{"document_id": first["document_id"], "chunk_id": first["chunk_id"]}],
                "supported": True, "uncertainty": None}

