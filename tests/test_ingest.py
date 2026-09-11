import pytest
import json
from src.ingest import CANONICAL_CHANNELS, IngestionError, TicketNormalizationEngine

@pytest.fixture
def engine():
    return TicketNormalizationEngine()

def test_successful_normalization_matches_real_schema(engine):
    """Test that normalization works with real development_tickets.json schema."""
    real_format_ticket = {
        "ticket_id": "DEV-0001",
        "channel": "chat",
        "subject": "",
        "body": "builds that work last week are now fail during dependency resolution.",
        "received_at": "2026-05-23T22:43:00Z",
        "customer_id": "CUST-1131",
        "customer_name": "Xin Kulkarni",
        "customer_tier": "standard",
        "customer_region": "latin_america",
        "language_fluency": "non_fluent"
    }
    
    normalized = engine.normalize_ticket(real_format_ticket)
    
    assert normalized["ticket_id"] == "DEV-0001"
    assert normalized["channel"] == "live_chat"
    assert normalized["canonical_channel"] == "live_chat"
    assert normalized["original_channel"] == "chat"
    assert normalized["subject"] == ""
    assert normalized["received_at"] == "2026-05-23T22:43:00Z"
    assert normalized["customer_tier"] == "standard"
    assert normalized["raw_content"] == "builds that work last week are now fail during dependency resolution."
    assert normalized["customer_id"] == "CUST-1131"
    assert normalized["customer_name"] == "Xin Kulkarni"
    assert normalized["customer_region"] == "latin_america"
    assert normalized["language_fluency"] == "non_fluent"

def test_successful_normalization_across_all_four_required_channels(engine):
    """Test all four channels ingest correctly."""
    channels = {
        'email': 'email',
        'chat': 'live_chat',
        'documentation_comments': 'documentation_comments',
        'community_forum': 'community_forum',
    }
    for channel, canonical in channels.items():
        ticket = {
            'ticket_id': f'test-id-{channel}',
            'channel': channel,
            'body': f'My application is experiencing issues on {channel}.',
            'customer_tier': 'enterprise',
            'customer_id': 'CUST-TEST',
            'customer_name': 'Test User',
            'language_fluency': 'fluent'
        }
        normalized_output = engine.normalize_ticket(ticket)
        assert normalized_output['ticket_id'] == f'test-id-{channel}'
        assert normalized_output['channel'] == canonical
        assert normalized_output['canonical_channel'] == canonical
        assert normalized_output['original_channel'] == channel
        assert normalized_output['customer_tier'] == 'enterprise'
        assert normalized_output['raw_content'].startswith('My application is experiencing')

def test_malformed_json_input_fails_gracefully(engine):
    """Test that malformed JSON fails with clear error."""
    corrupted_string = "{'channel': 'email', invalid_raw_syntax_here}"
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(corrupted_string)
    assert 'JSON' in str(exception_context.value).upper() or 'malformed' in str(exception_context.value).lower()

def test_missing_required_schema_keys_throws_error(engine):
    """Test that missing required keys are caught."""
    incomplete_payload = {
        'ticket_id': 'INCOMPLETE-1',
        'channel': 'email',
        'customer_tier': 'standard',
    }
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(incomplete_payload)
    assert 'content/body' in str(exception_context.value)

def test_invalid_customer_tier_rejection(engine):
    """Test invalid tier is rejected."""
    invalid_tier_payload = {
        'ticket_id': 'INVALID-TIER-1',
        'channel': 'chat', 
        'body': 'Need help.',
        'customer_tier': 'vip-tier',
        'customer_id': 'CUST-X'
    }
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(invalid_tier_payload)
    assert 'Unauthorized customer priority tier value' in str(exception_context.value)

def test_empty_body_string_rejection(engine):
    """Test empty body is rejected."""
    empty_body_payload = {
        'ticket_id': 'EMPTY-1',
        'channel': 'email',
        'body': '   ',
        'customer_tier': 'free',
        'customer_id': 'CUST-X'
    }
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(empty_body_payload)
    assert 'cannot be empty' in str(exception_context.value)

def test_invalid_channel_rejection(engine):
    """Test invalid channel is rejected."""
    bad_channel_payload = {
        'ticket_id': 'BAD-CHANNEL-1',
        'channel': 'slack',
        'body': 'Urgent outage.',
        'customer_tier': 'standard',
        'customer_id': 'CUST-X'
    }
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(bad_channel_payload)
    assert 'Invalid source channel' in str(exception_context.value)

def test_invalid_language_fluency_rejection(engine):
    """Test invalid language_fluency is rejected."""
    bad_fluency_payload = {
        'ticket_id': 'BAD-LANGUAGE-1',
        'channel': 'email',
        'body': 'Help needed.',
        'customer_tier': 'standard',
        'customer_id': 'CUST-X',
        'language_fluency': 'semi_fluent'
    }
    with pytest.raises(IngestionError) as exception_context:
        engine.normalize_ticket(bad_fluency_payload)
    assert 'language_fluency' in str(exception_context.value)

def test_normalize_batch_handles_mixed_valid_invalid(engine):
    """Test that batch normalization skips errors and reports them."""
    tickets = [
        {  # Valid
            'ticket_id': 'VALID-1',
            'channel': 'email',
            'body': 'Working ticket.',
            'customer_tier': 'standard',
            'customer_id': 'CUST-1'
        },
        {  # Missing body
            'ticket_id': 'INVALID-1',
            'channel': 'email',
            'customer_tier': 'standard',
            'customer_id': 'CUST-2'
        },
        {  # Valid
            'ticket_id': 'VALID-2',
            'channel': 'chat',
            'body': 'Another working ticket.',
            'customer_tier': 'enterprise',
            'customer_id': 'CUST-3'
        }
    ]
    
    normalized, errors = engine.normalize_batch(tickets)
    
    assert len(normalized) == 2, "Should normalize 2 valid tickets"
    assert len(errors) == 1, "Should have 1 error"
    assert normalized[0]["ticket_id"] == "VALID-1"
    assert normalized[1]["ticket_id"] == "VALID-2"
    assert errors[0]["ticket_id"] == "INVALID-1"


def _complete_ticket(channel="email", **overrides):
    payload = {
        "ticket_id": "T-001",
        "channel": channel,
        "subject": "Cannot sign in",
        "body": "My login fails with an invalid credentials error.",
        "received_at": "2026-05-23T22:43:00Z",
        "customer_id": "CUST-1",
        "customer_name": "Test User",
        "customer_tier": "standard",
        "customer_region": "europe",
        "language_fluency": "fluent",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("email", "email"),
        ("chat", "live_chat"),
        ("live_chat", "live_chat"),
        ("docs_comment", "documentation_comments"),
        ("documentation_comments", "documentation_comments"),
        ("forum", "community_forum"),
        ("community_forum", "community_forum"),
        (" CHAT ", "live_chat"),
    ],
)
def test_channel_aliases_are_deterministic_and_auditable(engine, alias, canonical):
    normalized = engine.normalize_ticket(_complete_ticket(alias))
    assert normalized["channel"] == canonical
    assert normalized["canonical_channel"] == canonical
    assert normalized["original_channel"] == alias
    assert normalized["channel"] in CANONICAL_CHANNELS


def test_json_input_normalizes(engine):
    normalized = engine.normalize_ticket(json.dumps(_complete_ticket("chat", subject="")))
    assert normalized["channel"] == "live_chat"


@pytest.mark.parametrize("value", [None, [], 42, "{invalid_json_payload}"])
def test_malformed_input_raises_controlled_error(engine, value):
    with pytest.raises(IngestionError):
        engine.normalize_ticket(value)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        _complete_ticket(ticket_id=None),
        _complete_ticket(ticket_id="  "),
        _complete_ticket(channel=None),
        _complete_ticket(channel="slack"),
        _complete_ticket(body=None),
        _complete_ticket(body="   "),
        _complete_ticket(body=123),
        _complete_ticket(received_at="not-a-timestamp"),
    ],
)
def test_invalid_ticket_fields_raise_controlled_error(engine, payload):
    with pytest.raises(IngestionError):
        engine.normalize_ticket(payload)


def test_content_alias_is_supported_but_must_be_text(engine):
    payload = _complete_ticket()
    payload.pop("body")
    payload["content"] = "Text supplied through the established content alias."
    assert engine.normalize_ticket(payload)["raw_content"].startswith("Text supplied")

    payload["content"] = {"nested": "not valid ticket text"}
    with pytest.raises(IngestionError):
        engine.normalize_ticket(payload)


def test_unicode_non_english_content_is_preserved(engine):
    content = "ログインできません — कृपया सहायता करें — café ☁️"
    normalized = engine.normalize_ticket(_complete_ticket("docs_comment", body=content))
    assert normalized["raw_content"] == content


def test_very_long_content_is_preserved(engine):
    content = "deployment failure " * 10_000
    normalized = engine.normalize_ticket(_complete_ticket("forum", body=content))
    assert normalized["raw_content"] == content.strip()


def test_unexpected_fields_and_evaluation_targets_do_not_leak(engine):
    payload = _complete_ticket(
        labels={
            "intent": "authentication_failure",
            "urgency": "high",
            "expected_route": "auto_respond",
            "expected_doc_ids": ["DOC-AUTH-001"],
            "must_not_auto_respond": False,
        },
        intent="authentication_failure",
        urgency="high",
        expected_route="auto_respond",
        expected_document_ids=["DOC-AUTH-001"],
        must_auto_respond=True,
        must_not_auto_respond=False,
        ground_truth_answer="Do not expose this.",
        reference_response="Do not expose this either.",
        history={"first_contact_resolution": True, "csat_rating": 5},
        harmless_extra="ignored",
    )
    normalized = engine.normalize_ticket(payload)

    serialized = json.dumps(normalized, ensure_ascii=False)
    for forbidden in (
        "labels",
        "intent",
        "urgency",
        "expected_route",
        "expected_document_ids",
        "must_auto_respond",
        "must_not_auto_respond",
        "ground_truth_answer",
        "reference_response",
        "history",
        "harmless_extra",
        "DOC-AUTH-001",
        "Do not expose",
    ):
        assert forbidden not in serialized


def test_missing_optional_language_is_unknown_not_invented(engine):
    payload = _complete_ticket()
    payload.pop("language_fluency")
    assert engine.normalize_ticket(payload)["language_fluency"] is None


def test_classifier_integration_uses_normalized_subject_and_content(engine):
    from src.classify import ticket_text

    normalized = engine.normalize_ticket(_complete_ticket(subject="Subject marker"))
    assert ticket_text(normalized) == (
        "Subject marker My login fails with an invalid credentials error."
    )


def test_retriever_integration_receives_normalized_text(engine):
    class RecordingRetriever:
        def __init__(self):
            self.query = None

        def query_authoritative_knowledge(self, query, top_k=5):
            self.query = query
            return []

    normalized = engine.normalize_ticket(_complete_ticket("forum"))
    retriever = RecordingRetriever()
    assert retriever.query_authoritative_knowledge(normalized["raw_content"]) == []
    assert retriever.query == normalized["raw_content"]


def test_orchestrator_escalates_and_logs_malformed_ticket():
    from src.orchestrator import SupportAutomationOrchestrator

    orchestrator = SupportAutomationOrchestrator(db_url="sqlite:///:memory:")
    result = orchestrator.process_ticket(_complete_ticket(ticket_id=""))

    assert result["status"] == "ESCALATE"
    assert result["reason"].startswith("ingestion_failure:")
    assert result["decision_id"] is not None
    assert result["audit_record"]["routing_action"] == "ESCALATE"
