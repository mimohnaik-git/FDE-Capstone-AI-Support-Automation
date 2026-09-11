"""Validation and canonical normalization for inbound support tickets."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Tuple
from datetime import datetime

CHANNEL_ALIASES = {
    "email": "email",
    "chat": "live_chat",
    "live_chat": "live_chat",
    "docs_comment": "documentation_comments",
    "documentation_comments": "documentation_comments",
    "forum": "community_forum",
    "community_forum": "community_forum",
}
CANONICAL_CHANNELS = frozenset(CHANNEL_ALIASES.values())
VALID_CHANNELS = frozenset(CHANNEL_ALIASES)
VALID_TIERS = frozenset({"free", "standard", "enterprise", "business"})
VALID_FLUENCY = frozenset({"fluent", "non_fluent"})


class IngestionError(ValueError):
    """Controlled failure raised when an inbound ticket cannot be normalized."""


def _required_nonblank_string(payload: Mapping[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(
            f"INGESTION SCHEMATIC FAILURE: '{field}' must be a non-empty string."
        )
    return value.strip()


def _optional_string(payload: Mapping[str, Any], field: str) -> str | None:
    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise IngestionError(
            f"INGESTION SCHEMATIC FAILURE: '{field}' must be a string when supplied."
        )
    return value.strip()


def _validated_timestamp(payload: Mapping[str, Any]) -> str | None:
    timestamp = payload.get("received_at")
    if timestamp is None:
        timestamp = payload.get("timestamp")
    if timestamp is None:
        return None
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise IngestionError(
            "INGESTION SCHEMATIC FAILURE: Timestamp must be a non-empty ISO-8601 string."
        )
    candidate = timestamp.strip()
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IngestionError(
            f"INGESTION SCHEMATIC FAILURE: Invalid ISO-8601 timestamp '{candidate}'."
        ) from exc
    return candidate

class TicketNormalizationEngine:
    """Normalize the four supported source channels to one inference contract."""
    
    @staticmethod
    def validate_raw_schema(raw_payload: Mapping[str, Any]) -> None:
        """Validate fields required by the authoritative inbound schema."""
        if not isinstance(raw_payload, Mapping):
            raise IngestionError(
                "INGESTION SCHEMATIC FAILURE: Inbound payload must resolve to a valid dictionary map."
            )

        _required_nonblank_string(raw_payload, "ticket_id")

        original_channel = _required_nonblank_string(raw_payload, "channel")
        channel_key = original_channel.lower()
        if channel_key not in CHANNEL_ALIASES:
            raise IngestionError(
                f"INGESTION SCHEMATIC FAILURE: Invalid source channel '{original_channel}'. "
                f"Accepted values are: {', '.join(sorted(VALID_CHANNELS))}"
            )

        content_val = (
            raw_payload.get("content")
            if raw_payload.get("content") is not None
            else raw_payload.get("body")
        )
        if not isinstance(content_val, str):
            raise IngestionError(
                "INGESTION SCHEMATIC FAILURE: Ticket content/body must be a string."
            )
        if not content_val.strip():
            raise IngestionError(
                "INGESTION SCHEMATIC FAILURE: Ticket content/body cannot be empty."
            )

        tier = _required_nonblank_string(raw_payload, "customer_tier").lower()
        if tier not in VALID_TIERS:
            raise IngestionError(
                f"INGESTION SCHEMATIC FAILURE: Unauthorized customer priority tier value: '{tier}'"
            )

        if "subject" in raw_payload:
            _optional_string(raw_payload, "subject")

        if "language_fluency" in raw_payload and raw_payload.get("language_fluency") is not None:
            fluency = _required_nonblank_string(raw_payload, "language_fluency").lower()
            if fluency not in VALID_FLUENCY:
                raise IngestionError(
                    f"INGESTION SCHEMATIC FAILURE: Invalid language_fluency value: '{fluency}'"
                )

        _validated_timestamp(raw_payload)

    def normalize_ticket(self, raw_input: Any) -> Dict[str, Any]:
        """Parse and normalize one ticket without copying labels or outcomes."""
        if isinstance(raw_input, str):
            try:
                parsed_data = json.loads(raw_input)
            except (json.JSONDecodeError, TypeError) as exc:
                raise IngestionError(
                    f"INGESTION STRUCTURAL FAILURE: Input is malformed JSON. Context: {exc}"
                ) from exc
        elif isinstance(raw_input, Mapping):
            parsed_data = raw_input
        else:
            raise IngestionError(
                "INGESTION SCHEMATIC FAILURE: Inbound payload must resolve to a valid dictionary map."
            )

        self.validate_raw_schema(parsed_data)

        original_channel = parsed_data["channel"]
        canonical_channel = CHANNEL_ALIASES[original_channel.strip().lower()]
        content_text = parsed_data.get("content")
        if content_text is None:
            content_text = parsed_data["body"]
        subject = _optional_string(parsed_data, "subject") or ""
        timestamp = _validated_timestamp(parsed_data)
        language = parsed_data.get("language_fluency")
        normalized_language = language.strip().lower() if isinstance(language, str) else None
        sender = parsed_data.get("sender") or parsed_data.get("customer_id") or "anonymous_identity"

        # This allowlist deliberately excludes labels, expected results,
        # reference answers, and history from the production inference object.
        return {
            "ticket_id": parsed_data["ticket_id"].strip(),
            "channel": canonical_channel,
            "canonical_channel": canonical_channel,
            "original_channel": original_channel,
            "subject": subject,
            "raw_content": content_text.strip(),
            "customer_tier": parsed_data["customer_tier"].strip().lower(),
            "customer_id": parsed_data.get("customer_id", "UNKNOWN"),
            "customer_name": parsed_data.get("customer_name", "Unknown"),
            "customer_region": parsed_data.get("customer_region"),
            "language_fluency": normalized_language,
            "received_at": timestamp,
            "metadata": {
                "sender_identity": sender,
                "timestamp_recorded": timestamp,
                "original_subject": subject,
            },
        }

    def normalize_batch(self, ticket_list: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Normalize valid records while returning controlled errors for bad ones."""
        if not isinstance(ticket_list, list):
            raise IngestionError("INGESTION BATCH FAILURE: Batch input must be a list.")

        normalized: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        for index, ticket in enumerate(ticket_list):
            try:
                normalized.append(self.normalize_ticket(ticket))
            except IngestionError as exc:
                errors.append(
                    {
                        "index": index,
                        "ticket_id": (
                            ticket.get("ticket_id", "UNKNOWN")
                            if isinstance(ticket, Mapping)
                            else "UNKNOWN"
                        ),
                        "error": str(exc),
                    }
                )
        return normalized, errors
