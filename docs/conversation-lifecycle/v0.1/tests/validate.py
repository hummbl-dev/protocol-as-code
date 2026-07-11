#!/usr/bin/env python3
"""Conversation Lifecycle Closeout Receipt validator v0.1.

Validates closeout receipts against the schema and enforces semantic rules:
- Artifact truthfulness: claimed artifacts must have evidence
- Privacy: unpreserved_value with sensitive descriptions must not route to public
- Capability consistency: preservation_writes requiring capabilities not declared
- Disposition honesty: READY_TO_RESUME requires no missing_checks

Uses only Python stdlib.
"""

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "schema_version", "session_id", "closeout_profile", "lifecycle_state",
    "capabilities_declared", "session_mission", "outcome_audit",
    "artifact_reconciliation", "unpreserved_value", "preservation_writes",
    "open_work", "readiness_disposition", "handoff_packet_ref",
    "closeout_receipt_ref", "invoked_at"
]

VALID_PROFILES = {"end_chat", "end_work_session", "session_checkpoint"}
VALID_STATES = {"OPEN", "ACTIVE", "CHECKPOINTING", "CLOSING", "CLOSED",
                "INTERRUPTED", "ABANDONED"}
VALID_CAPS = {"chat_context_read", "connected_source_read",
              "connected_source_write", "local_filesystem_read",
              "local_filesystem_write", "shell_execution",
              "git_state_read", "coordination_bus_write",
              "durable_memory_write", "artifact_creation",
              "artifact_verification", "automation_creation"}
VALID_ARTIFACT_STATUS = {"claimed", "confirmed", "unconfirmed", "failed", "not_created"}
VALID_DISPOSITIONS = {"READY_TO_RESUME", "READY_WITH_GAPS", "NOT_READY", "CHECKPOINT_ONLY"}
VALID_STEP_RESULTS = {"PASS", "FAIL", "NOT_APPLICABLE", "UNAVAILABLE", "DECLINED"}

CAPABILITY_FOR_DESTINATION = {
    "existing_issue": {"connected_source_write", "artifact_creation"},
    "existing_pr": {"connected_source_write", "artifact_creation"},
    "new_artifact": {"artifact_creation"},
    "handoff_packet": {"chat_context_read"},
    "durable_memory": {"durable_memory_write"},
    "chat_only": {"chat_context_read"},
}

SENSITIVE_KEYWORDS = {"health", "private", "personal", "credential", "secret",
                      "relationship", "family", "medical"}


def _check_required(receipt: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in receipt:
            errors.append(f"Missing required field: {field}")
    return errors


def _check_enums(receipt: dict) -> list[str]:
    errors = []
    if receipt.get("closeout_profile") not in VALID_PROFILES:
        errors.append(f"Invalid closeout_profile: {receipt.get('closeout_profile')}")
    if receipt.get("lifecycle_state") not in VALID_STATES:
        errors.append(f"Invalid lifecycle_state: {receipt.get('lifecycle_state')}")
    if receipt.get("readiness_disposition") not in VALID_DISPOSITIONS:
        errors.append(f"Invalid readiness_disposition: {receipt.get('readiness_disposition')}")
    for cap in receipt.get("capabilities_declared", []):
        if cap not in VALID_CAPS:
            errors.append(f"Invalid capability: {cap}")
    for art in receipt.get("artifact_reconciliation", []):
        if art.get("status") not in VALID_ARTIFACT_STATUS:
            errors.append(f"Invalid artifact status: {art.get('status')}")
    for pw in receipt.get("preservation_writes", []):
        if pw.get("result") not in VALID_STEP_RESULTS:
            errors.append(f"Invalid preservation write result: {pw.get('result')}")
    return errors


def _check_artifact_truthfulness(receipt: dict) -> list[str]:
    """Claimed artifacts must have evidence_ref; verified claims need confirmation."""
    errors = []
    caps = set(receipt.get("capabilities_declared", []))
    for art in receipt.get("artifact_reconciliation", []):
        status = art.get("status", "")
        if status == "claimed":
            if not art.get("evidence_ref"):
                errors.append(
                    f"Artifact '{art.get('identifier', '?')}' has status 'claimed' "
                    f"but no evidence_ref"
                )
        if status == "confirmed":
            if "artifact_verification" not in caps and "connected_source_read" not in caps:
                errors.append(
                    f"Artifact '{art.get('identifier', '?')}' is 'confirmed' "
                    f"but no verification capability declared"
                )
    return errors


def _check_capability_consistency(receipt: dict) -> list[str]:
    """Preservation writes requiring capabilities not declared should be UNAVAILABLE."""
    errors = []
    caps = set(receipt.get("capabilities_declared", []))
    for pw in receipt.get("preservation_writes", []):
        dest = pw.get("destination", "")
        result = pw.get("result", "")
        required_caps = CAPABILITY_FOR_DESTINATION.get(dest, set())
        if result == "PASS":
            if required_caps and not (caps & required_caps):
                errors.append(
                    f"Preservation write to '{dest}' returned PASS but "
                    f"required capabilities {required_caps} not declared"
                )
    return errors


def _check_privacy(receipt: dict) -> list[str]:
    """Sensitive unpreserved_value must not route to public destinations."""
    errors = []
    for uv in receipt.get("unpreserved_value", []):
        desc = uv.get("description", "").lower()
        route = uv.get("preservation_route", "")
        if any(kw in desc for kw in SENSITIVE_KEYWORDS):
            if route in ("existing_issue", "existing_pr", "new_artifact"):
                errors.append(
                    f"Unpreserved value contains sensitive content but routes "
                    f"to public destination '{route}'"
                )
    for pw in receipt.get("preservation_writes", []):
        dest = pw.get("destination", "")
        check = pw.get("check", "").lower()
        if any(kw in check for kw in SENSITIVE_KEYWORDS):
            if dest in ("existing_issue", "existing_pr", "new_artifact") and pw.get("result") == "PASS":
                errors.append(
                    f"Preservation write contains sensitive content but writes "
                    f"to public destination '{dest}' with PASS"
                )
    return errors


def _check_disposition_honesty(receipt: dict) -> list[str]:
    """READY_TO_RESUME requires no missing_checks and no UNAVAILABLE writes."""
    errors = []
    disp = receipt.get("readiness_disposition", "")
    if disp == "READY_TO_RESUME":
        if receipt.get("missing_checks"):
            errors.append(
                "readiness_disposition is READY_TO_RESUME but missing_checks is non-empty"
            )
        for pw in receipt.get("preservation_writes", []):
            if pw.get("result") == "UNAVAILABLE":
                errors.append(
                    "readiness_disposition is READY_TO_RESUME but a preservation "
                    "write returned UNAVAILABLE"
                )
    return errors


def _check_checkpoint_state(receipt: dict) -> list[str]:
    """session_checkpoint profile should have CHECKPOINTING or INTERRUPTED state."""
    errors = []
    profile = receipt.get("closeout_profile", "")
    state = receipt.get("lifecycle_state", "")
    if profile == "session_checkpoint":
        if state not in ("CHECKPOINTING", "INTERRUPTED"):
            errors.append(
                f"closeout_profile='session_checkpoint' but lifecycle_state='{state}' "
                f"(expected CHECKPOINTING or INTERRUPTED)"
            )
    return errors


def validate_receipt(receipt: dict) -> list[str]:
    errors = []
    errors.extend(_check_required(receipt))
    if errors:
        return errors
    errors.extend(_check_enums(receipt))
    errors.extend(_check_artifact_truthfulness(receipt))
    errors.extend(_check_capability_consistency(receipt))
    errors.extend(_check_privacy(receipt))
    errors.extend(_check_disposition_honesty(receipt))
    errors.extend(_check_checkpoint_state(receipt))
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate.py <receipt.json> [...]", file=sys.stderr)
        return 2
    all_valid = True
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            receipt = json.load(f)
        errors = validate_receipt(receipt)
        if errors:
            all_valid = False
            print(f"INVALID: {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"VALID: {path}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
