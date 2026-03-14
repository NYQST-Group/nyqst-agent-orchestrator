# Demo Incident And Fallback Rules

The deployment lane needs explicit failure behavior because the repo does not yet have CI-backed release confidence, staging parity, or production monitoring. If something breaks and there are no written stop and fallback rules, the operator becomes the runtime. This document exists to stop that. I^1 I^2

## North-Star Intent

When the demo stack degrades, the response should be:

- fast
- explicit
- bounded
- honest

The operator should know when to continue, when to explain a feature is out of scope, when to fall back safely, and when to stop the demo entirely.

## Current-State Anchor

The repo and issue corpus already tell us the main operational weaknesses:

- no trustworthy CI/CD lane yet. I^1
- no formal validation gate written into execution by default. I^2
- no complete monitoring/alerting specification. I^3
- no real staging specification. I^4
- tenant isolation is not fully formalized for a shared demo environment. I^5
- run ledger concurrency and ARQ worker behavior have real known risks. I^6

These are not reasons to abandon the demo lane. They are reasons to make operator rules explicit.

## Stop Conditions

Stop the demo immediately if any of these happen:

- sign-in fails and no already-tested fallback login path exists
- the seeded project or corpus cannot be accessed
- upload or grounded ask fails on the promised path
- the run timeline or event stream is visibly corrupted or contradictory
- the frontend cannot route into the main shell
- the environment exposes one tenant’s data to another audience

Stopping is better than improvising a false story.

## Rollback Triggers

Treat each of the following as a `rollback trigger` to the last known-good demo state:

- a new change breaks `/health/ready`
- `validate.sh` or buyer-path smoke regresses after an edit
- the chosen index backend becomes unhealthy after configuration changes
- UI preview/build breaks after an otherwise “small” frontend change
- event sequencing or run visibility becomes unreliable under the demonstrated flow

Rollback here means return to the previously smoke-tested commit, env file, and seed data set.

## Safe Fallbacks

These are allowed fallbacks when used deliberately and followed by a rerun of the relevant smoke steps:

- disable Langfuse and continue without observability UI
- switch the demo to document-grounded mode if internet research was not explicitly promised
- switch from local Langfuse to no-Langfuse if the port conflict or local profile causes instability
- switch from `opensearch` to `pgvector` for a small corpus demo if retrieval remains acceptable and smoke is rerun
- use standard login with a pre-created tenant/user if demo bootstrap is unavailable but auth is still functional
- use `npm -C ui run dev` as a last-resort local fallback only if the built UI preview path is temporarily blocking rehearsal and the UI smoke is rerun afterward

## What Can Be Explained As “Not In This Demo”

These are acceptable to state plainly if asked, provided the product team has not explicitly promised them for the meeting:

- enterprise SSO
- staging parity
- CI-backed auto-deploy
- proactive monitoring and alerting
- scheduled or webhook-triggered workflows
- background-worker-heavy async flows
- multi-tenant shared demo hosting

Do not present these as finished just because related docs or issues exist.

## What Invalidates The Demo Outright

The demo is invalid, not merely degraded, if:

- the stack cannot produce one grounded answer with inspectable provenance
- the sample corpus is missing or obviously fake filler
- the run/activity trail shown to the buyer is untrustworthy
- the host environment must be manually repaired live to continue the core path
- the environment is being shared in a way that makes tenant boundaries questionable

## Gap-Specific Rules

### CI And Validation Gaps

- Because `GAP-038` and `GAP-039` remain open, manual smoke evidence is mandatory before every buyer session.

### Monitoring And Staging Gaps

- Because `GAP-040` and `GAP-042` remain open, this environment should be described as an operator-managed demo host, not as a fully staged deployment pipeline.

### Tenant Isolation Gap

- Because `GAP-043` remains open, do not run unrelated customer demos from the same long-lived shared environment.

### Run Ledger And Worker Risks

- Because `GAP-022` is a real run-ledger concurrency risk, avoid concurrency-heavy or fan-out-heavy flows in the live demo unless they have been specifically stress-tested.
- Because `GAP-023` is a real worker registration risk, do not promise queue/background-worker-dependent behavior unless that bug has been fixed and revalidated.

## Judgment Required

Do not treat fallback as a permission slip to improvise. A fallback is only safe if it preserves a truthful story about the product being shown. If the fallback changes the nature of the demo, hides a critical capability failure, or leaves the operator guessing, it is not a safe fallback. I^1 I^6

## Builder Accountability

The builder or operator responsible for incident behavior must verify personally:

- that there is a last known-good demo state to return to
- that every promised feature has either a real fallback or a stop condition
- that background-worker and concurrency risks are not silently ignored
- that “not in this demo” lines are prepared in advance rather than invented under pressure
- that no one continues past a release failure just because the shell still looks polished

Fake completion includes:

- calling the demo resilient because it has a lot of docs
- continuing a broken grounded-answer path and hoping the buyer does not notice
- masking a worker failure by pretending the feature is simply “slow”
- treating tenant-isolation uncertainty as acceptable because the environment is only temporary

## Issue Hooks

- `I^1` - `GAP-038`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the CI/CD absence this document has to compensate for.
- `I^2` - `GAP-039`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the missing validation-gate reason manual smoke is mandatory.
- `I^3` - `GAP-040`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the reason Langfuse cannot be treated as full monitoring.
- `I^4` - `GAP-042`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the reason this pack speaks about an operator-managed demo host rather than a mature staging lane.
- `I^5` - `GAP-043`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the tenant-isolation constraint on shared demo hosting.
- `I^6` - `GAP-022` and `GAP-023`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), are the real run-ledger and worker risks that must shape fallback rules.
