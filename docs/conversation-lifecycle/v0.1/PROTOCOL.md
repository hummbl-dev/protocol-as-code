# HUMMBL Conversation Lifecycle Protocol v0.1

**Status: CANDIDATE COMPANY PROTOCOL — CROSS-PLATFORM — NON-CANON UNTIL REVIEWED**

Issue: hummbl-dev/hummbl-dev#159

## Purpose

Define a reusable Conversation Lifecycle Protocol (CLP) whose
initial v0.1 profile closes ChatGPT chats and multi-tool work
sessions safely, preserves durable value, produces a resumable
handoff, and records what could and could not be verified.

> If this chat became unavailable now, could a human or another
> authorized agent recover the decisions, evidence, artifacts,
> constraints, open work, and next action without reconstructing
> the entire transcript?

## Repository responsibility map

| Repo | Responsibility |
|------|---------------|
| `protocol-as-code` | Lifecycle states, capability declarations, ordered closeout procedure, step outcomes, completion contract, platform-adapter requirements, fixtures |
| `agent-handoffs` | Reusable session-handoff profile |
| `execution-receipts` | Closeout execution receipt profile |
| `claude-config` / `apex-nexus` | Platform-specific adapters (existing `/end-session` is prior art) |
| ChatGPT / future providers | Capability-aware adapters invoking the common protocol |

## Lifecycle states

```text
OPEN → ACTIVE → CLOSING → CLOSED
                ↑
          CHECKPOINTING
                ↓
          INTERRUPTED → ABANDONED
```

| State | Meaning |
|-------|---------|
| `OPEN` | Session started, no substantive work yet |
| `ACTIVE` | Substantive work in progress |
| `CHECKPOINTING` | Producing a resumable checkpoint without asserting completion |
| `CLOSING` | Only bounded preservation and verification actions allowed |
| `CLOSED` | Closeout complete, receipt emitted |
| `INTERRUPTED` | Session interrupted (crash, rate limit, context pressure) |
| `ABANDONED` | Session abandoned without closeout |

Once `CLOSING` begins, only bounded preservation and verification
actions are allowed. No new substantive implementation work should
begin.

## Capability contract

Each adapter declares capabilities before executing provider-specific
checks:

| Capability | Meaning |
|-----------|---------|
| `chat_context_read` | Can read conversation context |
| `connected_source_read` | Can read from connected sources (GitHub, Drive, etc.) |
| `connected_source_write` | Can write to connected sources |
| `local_filesystem_read` | Can read local files |
| `local_filesystem_write` | Can write local files |
| `shell_execution` | Can execute shell commands |
| `git_state_read` | Can read Git state |
| `coordination_bus_write` | Can write to coordination bus |
| `durable_memory_write` | Can write to durable memory |
| `artifact_creation` | Can create artifacts (issues, PRs, etc.) |
| `artifact_verification` | Can verify artifact existence |
| `automation_creation` | Can create automations |

Each required step must resolve to one of:

| Result | Meaning |
|--------|---------|
| `PASS` | Check succeeded |
| `FAIL` | Check failed |
| `NOT_APPLICABLE` | Check not relevant to this session |
| `UNAVAILABLE` | Tool/capability not available |
| `DECLINED` | Operator declined the check |

`UNAVAILABLE` is an honest protocol outcome. An adapter must never
claim a check, write, memory update, bus post, file save, or artifact
exists unless the relevant tool confirms it.

## Invocation profiles

| Profile | When to use |
|---------|-------------|
| `end_chat` | Conversational sessions with no meaningful external mutations |
| `end_work_session` | Sessions that used GitHub, email, calendars, Drive, etc. |
| `session_checkpoint` | Interruptions, context-window pressure, planned pauses |

## Ordered closeout procedure

### 1. Freeze and scope
- Enter `CLOSING` state
- Stop substantive implementation
- Declare closeout profile and available capabilities
- Identify the session mission and time/work boundary

### 2. Outcome and decision audit
Classify session outputs: completed, in_progress, blocked,
rejected_or_reversed, unknown_unverified.

Preserve decisions separately from hypotheses, candidate terminology,
recommendations, externally verified facts, user-reported facts, local
execution receipts, and model inference.

### 3. Artifact reconciliation
Inventory all claimed artifacts and mutations. For each: claimed,
confirmed, unconfirmed, failed, not_created. Only confirmed artifacts
may be represented as durable outputs.

### 4. Unpreserved-value audit
Identify material value that exists only in conversation context:
decisions, architectural boundaries, evidence-backed findings,
constraints, reusable procedures, approved recommendations,
unresolved risks, action-ready work.

### 5. Preservation routing
1. Update the existing canonical issue, PR, document, or receipt
2. Create one bounded coordination artifact when no canonical home exists
3. Emit a structured handoff packet
4. Update durable memory only for stable cross-session patterns
5. Leave ephemeral discussion in the chat

Do not create an issue merely because an idea was mentioned. Require
materiality, actionability, an identifiable owner/home, and sufficient
scope.

### 6. Privacy and disclosure check
- Classify destination as public, private, internal, or chat-only
- Minimize copied context
- Exclude credentials, secrets, private health/relationship info,
  personal identifiers, proprietary source content
- Prefer references over transcript replication
- Preserve claim posture and provenance through compression

### 7. Open-work and dependency map
Record next action, owner, blockers, dependency order, stop conditions,
required approvals, expiry/reevaluation date, what must not be done.

### 8. Handoff and receipt
Produce one machine-readable handoff packet, one closeout execution
receipt, confirmed artifact links, and a concise human-readable session
closeout. A handoff transfers context, not ambient authority.

### 9. Readiness disposition

| Disposition | Meaning |
|-------------|---------|
| `READY_TO_RESUME` | All checks passed, handoff complete |
| `READY_WITH_GAPS` | Resumable but some checks unavailable |
| `NOT_READY` | Cannot resume without human intervention |
| `CHECKPOINT_ONLY` | Checkpoint produced, session not closed |

### 10. Final response
State disposition, what was durably preserved, material open work,
first next action, and any unavailable or failed preservation step.

## Idempotency and supersession

Repeated closeout invocation must not create duplicate issues,
handoffs, or receipts by default. Adapters should:
- Search for existing closeout artifacts for the same session
- Update or supersede when safe
- Link superseding and superseded receipts
- Preserve failed attempts
- Never silently overwrite evidence

## Stop conditions

Stop and report rather than improvising when:
- Canonical destination is ambiguous
- User has not authorized a consequential external write
- Private context would be exposed to a public destination
- An artifact cannot be verified after creation
- A connector/tool is unavailable
- Material claims cannot retain provenance through compression
- Session contains unresolved high-consequence work
- Closeout would trigger new implementation scope
- Required handoff receiver or authority boundary is unknown

## Minimum ChatGPT adapter behavior

1. Use conversation context to build the outcome audit
2. Inspect connected sources only when relevant and authorized
3. Verify every write through connector return data
4. Mark local Git, shell, bus, filesystem, or memory checks `UNAVAILABLE`
5. Create bounded GitHub/docs artifacts when canonical home exists
6. Otherwise produce a complete in-chat handoff
7. Distinguish chat closeout from work-session closeout
8. Never promise asynchronous continuation
9. Never treat hidden reasoning as handoff evidence
10. Keep products as consumers, not protocol owners

## Closeout receipt schema

See `closeout-receipt.schema.json` for the JSON Schema.

## Validation scenarios

1. Trivial informational chat where closeout is unnecessary
2. Strategy chat with decisions but no external writes
3. GitHub work session with confirmed issues/comments
4. Mixed session containing private and public material
5. Session where a connector write fails
6. Repeated closeout invocation
7. Interrupted session with only a checkpoint
8. Session with unverified claimed artifact
9. Session requiring human approval before preservation
10. Session whose only safe durable output is an in-chat handoff

## Success criteria

- [x] `protocol-as-code` contains a validated session-closeout profile and schema
- [x] Negative fixtures demonstrate invalid closeout receipts
- [ ] `agent-handoffs` contains a compatible handoff profile — SEPARATE REPO
- [ ] `execution-receipts` contains a compatible closeout receipt profile — SEPARATE REPO
- [x] Existing Claude `/end-session` behavior is mapped as one adapter, not the universal protocol
- [x] A ChatGPT adapter can complete the protocol with partial capabilities and honest `UNAVAILABLE` outcomes
- [x] Repeated closeout does not create duplicate durable artifacts (idempotency rules defined)
- [x] Public preservation tests prove private context is minimized (privacy check step)
- [x] Handoff compression preserves claim posture, evidence references, constraints
- [ ] One end-to-end dry run closes a real HUMMBL ChatGPT work session — PENDING

## Non-goals

- A universal conversation ontology
- Storage of full transcripts in public repos
- Automated publication of private context
- Production memory synchronization
- Automatic issue creation for every idea
- Autonomous continuation after closeout
- Cross-provider runtime implementation
- New canonical HUMMBL/BaseN terminology

## References

- Issue: hummbl-dev/hummbl-dev#159
- Related: hummbl-dev/hummbl-dev#160 (ChatGPT adapter), #161 (transfer intake)
- Prior art: `/end-session` in claude-config / apex-nexus
