# Autonomous setup — running the build from the cloud

This project is built partly by **unattended Claude Code cloud Routines**, so the
work continues even when no computer is on. Routines run on Anthropic's
infrastructure and are billed against a Claude subscription (no Anthropic API key
needed). This guide covers the one-time setup and the per-phase loop.

> These are browser/CLI steps the maintainer performs once. The agents then run
> from the cloud against [CLAUDE.md](../CLAUDE.md).

## One-time prerequisites

### 1. Install the Claude GitHub App on this repo

This lets cloud routines read issues, push branches, open and merge PRs, and cut
releases.

- In a local Claude Code session: `/install-github-app`, or
- Install from <https://github.com/apps/claude> and grant access to
  `txthedx/autonomous-care-algorithms`.

No `ANTHROPIC_API_KEY` secret is required for the subscription/Routines path.

### 2. Confirm the runbook is present

[CLAUDE.md](../CLAUDE.md) at the repo root is the operating procedure every cloud
agent reads on a fresh clone. Keep it current as conventions evolve.

## Phase 0 — the fully hands-off algorithm-backlog Routine

Create one scheduled Routine that clears the algorithm backlog on its own.

1. Go to <https://claude.ai/code/routines> → **New routine** (or `/schedule` in
   the CLI).
2. **Repository:** `txthedx/autonomous-care-algorithms`.
3. **Schedule:** daily (clears the open `algorithm` issues in a few days), or
   every few hours to go faster. Minimum interval is 1 hour.
4. **Environment:** allow network to `github.com` and PyPI; setup script
   `pip install -e ".[dev]"`.
5. **Prompt:**
   > Read CLAUDE.md. Select the lowest-numbered open issue labeled `algorithm`.
   > Implement it end to end exactly per CLAUDE.md: verify every clinical value
   > against the cited primary source via web search before writing code; create
   > the condition module and tests; update pyproject.toml, CITATION.cff,
   > CHANGELOG.md, README.md, and index.html; open a PR with the standard body;
   > wait for both CI jobs to pass, then merge, tag and publish the release, and
   > tick the issue's checkbox in roadmap #9. If you cannot verify the sources
   > or CI fails, do NOT merge — leave the PR open, comment explaining why, apply
   > the `clinical-review-needed` label, and stop.

This Routine is **fully hands-off**: it implements and merges scored algorithm
modules without per-issue input, with the verify-before-code rule and the
green-CI gate as safeguards.

## Phases 1–6 — the engine, with a review gate

The backend layers (registry, dispatch, MCP, REST, adapter, eval) are
architectural and higher-stakes than a scored module, so they get a light human
gate via **ultraplan** plus a **PR merge** checkpoint.

For each phase, in order (see the phase table in
[docs/architecture.md](architecture.md)):

1. **Plan with ultraplan on Claude Code on the web.** Start a session at
   <https://claude.ai/code>, open this repo, and run the phase's ultraplan
   (offloads the deep plan to the cloud). **Review it in the browser.**
2. **Import the approved plan** back into the repo as `docs/plans/phase-N.md`.
3. **Create a phase Routine** pointed at that plan file, with the prompt: *read
   CLAUDE.md and docs/plans/phase-N.md; implement the phase; run tests; open a PR
   with the standard body; **do not merge** — stop for human review.*
4. **Merge the PR yourself** after a look. (The ultraplan review was the first
   checkpoint; the PR is the second.)

Phase 0 keeps running in parallel the whole time.

## Monitoring and the kill switch

- **Run history & logs:** <https://claude.ai/code> (routine runs) plus the
  repo's PRs, releases, and Actions tab.
- **Pause / stop anytime:** disable the routine in the routines UI — no code
  change, takes effect immediately.
- **Audit:** every change arrives as a PR with the verified sources quoted in the
  body, so the trail is reviewable after the fact.

## Notes and limits

- Routines and ultraplan are 2026 research-preview features; validate current
  behavior with a single manual run before relying on the schedule.
- Routines default to pushing `claude/*` branches; merging via `gh pr merge`
  uses the GitHub App's API permissions — confirm on the first run.
- Each run draws on the Claude subscription usage and a daily routine-run cap;
  daily cadence keeps cost modest.
