#!/usr/bin/env python3
"""Tests for the Conversation Lifecycle Closeout Receipt validator."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate import validate_receipt

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES_DIR / name, encoding="utf-8") as f:
        return json.load(f)


class TestValidReceipts(unittest.TestCase):
    def test_valid_work_session_closeout(self):
        errors = validate_receipt(load_fixture("valid-work-session-closeout.json"))
        self.assertEqual(errors, [], f"Expected no errors: {errors}")

    def test_valid_chat_closeout(self):
        errors = validate_receipt(load_fixture("valid-chat-closeout.json"))
        self.assertEqual(errors, [], f"Expected no errors: {errors}")

    def test_valid_checkpoint(self):
        errors = validate_receipt(load_fixture("valid-checkpoint.json"))
        self.assertEqual(errors, [], f"Expected no errors: {errors}")


class TestInvalidReceipts(unittest.TestCase):
    def test_invalid_unverified_artifact(self):
        """Artifact claimed as verified but no evidence and no verification capability."""
        errors = validate_receipt(load_fixture("invalid-unverified-artifact.json"))
        self.assertTrue(len(errors) > 0, f"Expected errors: {errors}")

    def test_invalid_missing_required(self):
        """Missing disposition_reasons and missing_checks."""
        errors = validate_receipt(load_fixture("invalid-missing-required.json"))
        self.assertTrue(any("Missing required field" in e for e in errors),
                        f"Expected missing field error: {errors}")

    def test_invalid_privacy_violation(self):
        """Sensitive content routed to public issue."""
        errors = validate_receipt(load_fixture("invalid-privacy-violation.json"))
        self.assertTrue(any("sensitive" in e.lower() for e in errors),
                        f"Expected privacy error: {errors}")


class TestSemanticRules(unittest.TestCase):
    def _base_receipt(self) -> dict:
        return {
            "schema_version": "conversation_lifecycle_closeout.v0.1",
            "session_id": "test-001",
            "closeout_profile": "end_chat",
            "lifecycle_state": "CLOSED",
            "capabilities_declared": ["chat_context_read"],
            "session_mission": "test",
            "outcome_audit": [],
            "artifact_reconciliation": [],
            "unpreserved_value": [],
            "preservation_writes": [],
            "open_work": [],
            "readiness_disposition": "READY_WITH_GAPS",
            "disposition_reasons": ["test"],
            "missing_checks": ["test"],
            "handoff_packet_ref": "this",
            "closeout_receipt_ref": "this",
            "invoked_at": "2026-07-10T12:00:00Z"
        }

    def test_ready_to_resume_with_missing_checks_fails(self):
        r = self._base_receipt()
        r["readiness_disposition"] = "READY_TO_RESUME"
        r["missing_checks"] = ["some check"]
        errors = validate_receipt(r)
        self.assertTrue(any("READY_TO_RESUME" in e for e in errors))

    def test_ready_to_resume_with_unavailable_fails(self):
        r = self._base_receipt()
        r["readiness_disposition"] = "READY_TO_RESUME"
        r["missing_checks"] = []
        r["preservation_writes"] = [{
            "destination": "durable_memory",
            "check": "bus post",
            "result": "UNAVAILABLE",
            "evidence_ref": None
        }]
        errors = validate_receipt(r)
        self.assertTrue(any("UNAVAILABLE" in e for e in errors))

    def test_checkpoint_profile_requires_checkpointing_state(self):
        r = self._base_receipt()
        r["closeout_profile"] = "session_checkpoint"
        r["lifecycle_state"] = "CLOSED"
        errors = validate_receipt(r)
        self.assertTrue(any("session_checkpoint" in e for e in errors))

    def test_claimed_artifact_without_evidence_fails(self):
        r = self._base_receipt()
        r["artifact_reconciliation"] = [{
            "artifact_type": "pr",
            "identifier": "999",
            "status": "claimed",
            "evidence_ref": None
        }]
        errors = validate_receipt(r)
        self.assertTrue(any("claimed" in e for e in errors))

    def test_pass_without_capability_fails(self):
        r = self._base_receipt()
        r["capabilities_declared"] = ["chat_context_read"]
        r["preservation_writes"] = [{
            "destination": "existing_issue",
            "check": "update issue",
            "result": "PASS",
            "evidence_ref": "gh"
        }]
        errors = validate_receipt(r)
        self.assertTrue(any("capabilities" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
