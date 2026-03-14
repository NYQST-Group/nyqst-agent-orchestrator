# Demo Release Smoke Checklist

This checklist exists because the repo does not yet have a trustworthy automated deployment lane. The answer to “is the demo good to show?” therefore has to come from explicit smoke evidence, not optimism. If this checklist is skipped, the deployment is not demo-ready no matter how complete the product docs are. I^1 I^2

## North-Star Intent

The smoke path should prove two things:

- the platform boots and behaves coherently
- the buyer journey actually works on the deployed environment

Both matter. Passing only platform smoke is not enough.

## Current-State Anchor

The repo already gives us the core pieces of a smoke gate:

- `bash scripts/dev/validate.sh` validates infra, migrations, backend readiness, API smoke, and UI build. I^1
- `scripts/smoke-test.sh` verifies backend health, demo auth, sessions, pointers, and frontend availability. I^2
- health endpoints exist at `/health`, `/health/ready`, and `/api/v1/health` depending on which path is being used. I^3
- the UI login path and demo bootstrap auth already exist. I^4

What the repo does not yet provide is a single buyer-path release gate. This document becomes that gate.

## Release Gate

The demo is `demo-ready` only if:

- platform smoke passes
- buyer-path smoke passes
- any promised optional feature smoke also passes

Failure in any one category means the deployment is not ready to show.

## Platform Smoke

| Check | Classification | Command or action | Pass condition |
| --- | --- | --- | --- |
| Full validation | `required for demo` | `INTELLI_REQUIRE_RAG=1 bash scripts/dev/validate.sh` | exits `0`; RAG is not skipped |
| Backend ready | `required for demo` | `curl -fsS http://localhost:${INTELLI_API_PORT:-8000}/health/ready` | returns ready status |
| Backend detailed health | `required for demo` | `curl -fsS http://localhost:${INTELLI_API_PORT:-8000}/health` | returns healthy or acceptable degraded state that matches the chosen feature set |
| API smoke | `required for demo` | `python scripts/dev/smoke_api.py --require-rag --base-url http://localhost:${INTELLI_API_PORT:-8000}` | auth, upload, pointer advance, and grounded ask pass |
| UI build | `required for demo` | `npm -C ui run build` | exits `0` |
| UI preview or chosen host-run UI process | `required for demo` | open the served UI origin | login page loads without broken assets |

## Buyer-Path Smoke

Run these checks in the actual deployed UI/API pair, not only through scripts:

| Check | Classification | Pass condition |
| --- | --- | --- |
| Sign in | `required for demo` | Demo bootstrap or standard login reaches the shell without auth errors |
| Dashboard truth | `required for demo` | The dashboard loads and shows real activity or a real empty-state framing rather than placeholder filler |
| Open seeded project/task | `required for demo` | Seeded project and task are visible and legible |
| Shell context treatment | `required for demo` | Business and working context lines render correctly for the promised buyer path |
| View or upload seeded docs | `required for demo` | The corpus is available and upload/view path works if that is part of the meeting |
| Grounded ask over docs | `required for demo` | One known question returns a grounded answer against the seeded corpus |
| Provenance and citations | `required for demo` | Citations or source references are visible enough to inspect |
| Run or activity visibility | `required for demo` | The run or activity trail is visible enough to explain what just happened |
| Bundle or artifact visibility | `required for demo` | The resulting bundle/artifact state is inspectable if the flow produces it |
| Settings and model controls | `required for demo` | Settings and model selector open and close cleanly without breaking shell state |

## Feature Smoke If Promised

These checks are `required for specific feature`. Run them only if the meeting explicitly promises the feature:

- web research
  - run one internet research step
  - verify cited domains are visible
  - verify the provider path is real, not placeholder
- workflow execution
  - run one deterministic workflow with at least one visible output
  - verify the run log is legible
- decisions
  - open a decision and confirm linked artifacts or citations if that surface is part of the demo

If a feature is not promised in the meeting, it does not need to pass this section. If it is promised, failure here is a release failure.

## Explicit Fail Conditions

The smoke gate fails if any of the following are true:

- `validate.sh` passes only because RAG was skipped
- the login page loads but sign-in fails
- the shell loads but context treatment, dashboard truth, or model/settings affordances are visibly broken or placeholder-grade on the promised buyer path
- the seeded project or corpus cannot be found
- the answer is uncited or obviously not grounded
- the UI only works through a one-off dev-only trick that was not retested
- the corpus shown is smoke-only filler rather than the agreed demo set

## Judgment Required

Do not let “we ran some checks” count as a release decision. The point of this checklist is to make the demo falsifiable before a buyer does it for you. If the answer path was not tested end-to-end on the actual deployed stack, then the smoke gate did not happen. I^1 I^2

## Builder Accountability

The builder or operator responsible for release smoke must verify personally:

- that the scripted checks were run on the real target host and port choices
- that RAG was required rather than silently skipped
- that the seeded buyer path was exercised in the UI
- that any promised optional feature was tested explicitly
- that a failed check stops the release rather than becoming a verbal caveat

Fake completion includes:

- running `validate.sh` without `INTELLI_REQUIRE_RAG=1`
- checking the API only and declaring the full demo ready
- using a different corpus in rehearsal than in the buyer meeting
- skipping provenance visibility because “the answer looked right”

## Issue Hooks

- `I^1` - [scripts/dev/validate.sh](../../../scripts/dev/validate.sh) is the current validated platform smoke entrypoint.
- `I^2` - [scripts/smoke-test.sh](../../../scripts/smoke-test.sh) is the current broader local smoke harness for backend and frontend checks.
- `I^3` - [src/intelli/api/health.py](../../../src/intelli/api/health.py) and [src/intelli/api/v1/health.py](../../../src/intelli/api/v1/health.py) define the live health endpoints.
- `I^4` - [src/intelli/api/v1/auth.py](../../../src/intelli/api/v1/auth.py), [ui/src/api/auth.ts](../../../ui/src/api/auth.ts), and [ui/src/components/auth/LoginPage.tsx](../../../ui/src/components/auth/LoginPage.tsx) define the current sign-in and demo-login path.
- `I^5` - `GAP-039`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the reason this release gate must stay explicit rather than implied.
