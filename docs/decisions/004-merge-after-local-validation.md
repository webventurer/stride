# 004 — Merge after local validation

**Date:** 2026-09-15
**Status:** Accepted

## Context

Waiting for CI after the same checks and tests pass locally delays delivery without adding a useful decision to the common path. This friction surfaced while merging the TP1 refusal fix in Crypto Bots and Premium Alerts.

## Decision

Passing local checks, build and tests for the code being merged satisfy Stride's validation gate. Once review, approval and Vision checks are complete, merge without waiting for CI. Reuse local results from the current task when the relevant files have not changed. CI continues in the background; report its status separately and surface failures encountered.

This applies to both interactive and unattended delivery. Repository-enforced branch protection and required reviews remain binding. If GitHub requires a CI result before merging, report the blocker rather than bypassing protection.

## Consequences

`/linear:quick` and `/linear:finish` use the shared local-validation rule. No polling loop, additional setting or change to CI configuration is needed. Deployment remains a separate action.
