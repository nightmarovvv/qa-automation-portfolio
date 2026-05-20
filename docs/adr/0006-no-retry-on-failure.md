# ADR 006 — No retry-on-failure decorator

**Status:** accepted
**Date:** 2026-05-20

## Context

The `@pytest.mark.flaky(reruns=3)` decorator (and equivalents in vedro,
nose-rerunfailures, behave) is the default response to a flaky test
across most QA codebases. Re-run on red, fail only if it fails twice in
a row. It feels pragmatic. It is not.

## Decision

This repo ships **zero** retry decorators. A failing test is either
asserting on the wrong thing or running against a non-deterministic
SUT — both are bugs in the test, not in the runner. The fix lives in
the assertion or in the wait, never in `reruns=N`.

If a test cannot pass three times in a row, it does not pass once.

## What this implies in practice

- Mock layers use **strict count checks** on exit (`MockedRoute.__aexit__`)
  so "wrong number of calls" surfaces as the assertion message, not as
  "flaky."
- Contexts wait for the **thing the next step needs** (the title input
  the user is about to type into), never for a clock or for the
  container's `hidden` flag.
- Wait timeouts are documented and short (see
  [TESTING.md §5](../../TESTING.md), [ADR-005](0005-fixture-scopes-picked.md)).
- Negative tests assert what should NOT happen (e.g. `mock.requests == []`
  on a client-side reject) so silent regressions can't hide as
  intermittent passes.

## Why this is hard for teams to adopt

`reruns=3` is a one-line ROI: failing tests stop blocking merges
tomorrow. The alternative — owning the assertion until it asserts the
right thing — costs hours per flake the first time. The team needs an
explicit policy or this decision slides every quarter.

That's the role of this ADR: a written, dated promise so the next QA
hire can point at it instead of arguing in PR.

## Consequences

**Good**

- The CI signal stays honest. Green means green. Red means real.
- "Flake budget" conversations end. There is no budget.
- Debug sessions hit root cause faster — every red is a real reproduction.

**Bad**

- A truly nondeterministic external dependency (rate-limited 3rd-party
  API, GPU scheduler, race-prone CI runner) requires per-test resolution
  — quarantine the test, file the bug, fix the dep — not a `reruns=2`
  hack.
- Initial transition from a `flaky=true` codebase is painful: every
  rerun-protected test must be re-examined.

## When opt-out is OK

One case: a test that exists *to detect intermittency itself* —
soak runs counting failures across 1000 iterations. Those live under
`tests/soak/` and report a rate, not pass/fail.

## Plugin

The same rule, packaged: [alexshabunin/pytest-no-retry](https://github.com/alexshabunin/pytest-no-retry)
(MIT). Install it and `--reruns`, `reruns=N` in config, and
`@pytest.mark.flaky(reruns=N)` abort the session at collection time.
Two escape hatches — `@allow_retry("reason")` per-test and
`--allow-retry` for the whole session.

## Reference

- [TESTING.md §1](../../TESTING.md) — assertions carry the diagnosis.
- [ADR-002](0002-mock-count-on-exit.md) — strict mock counts.
- [ADR-005](0005-fixture-scopes-picked.md) — fixture scopes.
