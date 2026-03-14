# Demo Seed And Bootstrap

The demo lane does not become autonomous just because the product docs are good. Another agent still needs to know exactly how the demo gets a tenant, a user, a seeded project, a task, and a usable corpus without inventing half of it on the day. This document locks that path and is intentionally honest about what already exists versus what is still only backlog intent. I^1 I^2

## North-Star Intent

The buyer should open Intelli Studio into a prepared environment that already feels inhabited:

- a usable tenant
- a usable user
- a seeded project
- a seeded task
- a seeded bundle/notebook
- at least one buyer-grade sample document package
- at least one known question with a known grounded answer path

The operator should not have to assemble those pieces from memory while the meeting is starting.

## Current-State Anchor

The repo already supports the first half of this path:

- `POST /api/v1/auth/dev-bootstrap` can create or reuse a demo tenant and user when `DEBUG=true`. I^1
- the UI already exposes a `Demo Login` button wired to that endpoint. I^2
- `scripts/dev/smoke_api.py` can create a notebook pointer, upload a tiny artifact, create a manifest, and advance the pointer. I^3

But the repo does not yet contain a buyer-grade one-click sample project package:

- live onboarding intent exists through first-run checklist and sample project issues, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md). I^4
- the current smoke artifact `hello.txt` is valid for platform verification, not for buyer-facing demos. I^3

That gap must be handled explicitly rather than glossed over.

## Seed Contract

Lock the minimum buyer-demo state to the following names and meanings:

- tenant slug: `demo`
- tenant name: `Demo Tenant`
- demo user email: `demo@example.com`
- project: `Sample Lease Review`
- task: `Lease Intake and Grounded Review`
- bundle or notebook: `Lender Pack Intake`
- session module: `research`

These names are not sacred forever. They are sacred for the demo lane because they stop every operator and agent from inventing slightly different seed objects.

## Bootstrap Path

### Step 1: Auth Bootstrap

Preferred bootstrap for the single-host demo lane:

- set `DEBUG=true`
- call `POST /api/v1/auth/dev-bootstrap`
- use the returned JWT in the UI or API smoke path

This is an `accepted shortcut` for operator-controlled demo environments.

### Step 2: Project And Task State

Create or confirm these minimum business wrappers:

- one project named `Sample Lease Review`
- one task named `Lease Intake and Grounded Review`
- one decision-capable project context, even if Decisions are still thin in the live app

If project/task creation is still manual, treat it as a `manual step` and keep the names stable.
Manual creation is an accepted temporary operator workaround, not the intended end-state for this pack.

### Step 3: Bundle Or Notebook State

Create or confirm:

- one bundle/notebook named `Lender Pack Intake`
- one attached document package
- one known grounded question for rehearsal and smoke

If the demo uses the existing notebook/pointer substrate directly, that is acceptable. What matters is that the buyer-path object already exists and has real content.

## Sample Document Rules

### Required For Buyer Demo

At least one representative, reusable, buyer-grade document package:

- real enough to support a meaningful grounded answer
- stable across rehearsals
- already uploaded before the meeting unless the meeting specifically includes ingestion

### Accepted Operator Fallback

If the repo still lacks the planned one-click sample package:

- the operator may use externally supplied sample PDFs or text documents
- once chosen, that document package must be frozen and reused across all rehearsals and demos
- the operator should not improvise a new sample set per meeting

### Not Accepted As Buyer Seed

- the `hello.txt` smoke artifact created by `scripts/dev/smoke_api.py`
- empty projects or empty notebooks shown as if they were deliberate demo state
- ad hoc documents uploaded live without prior rehearsal, unless the meeting explicitly exists to demonstrate ingestion

## When To Use Demo Login And Bootstrap

Use demo bootstrap when:

- the environment is operator-controlled
- the goal is a buyer demo, not shared external self-service access
- the simplest path to a stable tenant/user is more valuable than polishing real auth

Do not rely on demo bootstrap when:

- the environment is publicly exposed
- multiple unrelated tenants share the environment
- the meeting is explicitly about enterprise auth or production readiness

## Demo-Ready Seed Definition

The environment is only `demo-ready` when all of the following are true:

- a reusable demo tenant and user can sign in
- the seeded project and task exist
- the seeded bundle/notebook exists
- a real sample document package is already present
- at least one grounded ask has been rehearsed successfully against that package

If any of those are missing, the deployment may be valid for operator testing, but it is not yet buyer-demo ready.

## Finalization Rule

This pack is only `final-final` when one repeatable seed command or profile exists for the canonical buyer path.

Target command shape:

- `python scripts/dev/seed_demo.py --profile lease-review`

Until that exists, manual seed creation remains an accepted temporary operator workaround rather than a finished autonomous seed lane.

All future seed automation must create the same canonical tenant, project, task, bundle/notebook, and sample corpus names already locked in this document unless the seed contract itself is deliberately revised.

## Judgment Required

Do not let the seed story collapse into “we can just upload something on the day.” That is operator memory masquerading as process. If the sample package is not frozen, the question set is not rehearsed, or the demo path depends on people remembering object names, the bootstrap plan is not done. I^3 I^4

## Builder Accountability

The builder or operator responsible for seed/bootstrap must verify personally:

- that demo auth really works on the chosen host
- that the same project/task/bundle names are reused consistently
- that the sample corpus is buyer-grade rather than smoke-only
- that at least one known grounded question has already been asked successfully
- that the demo does not depend on creating content from scratch under pressure

Fake completion includes:

- saying “Demo Login exists” without confirming it returns a working JWT
- reusing `hello.txt` as if it were a credible buyer corpus
- leaving project/task creation to last-minute improvisation
- assuming a one-click sample project exists because the backlog says it should

## Issue Hooks

- `I^1` - [src/intelli/api/v1/auth.py](../../../src/intelli/api/v1/auth.py) defines `POST /api/v1/auth/dev-bootstrap`.
- `I^2` - [ui/src/api/auth.ts](../../../ui/src/api/auth.ts) and [ui/src/components/auth/LoginPage.tsx](../../../ui/src/components/auth/LoginPage.tsx) show the current `Demo Login` path.
- `I^3` - [scripts/dev/smoke_api.py](../../../scripts/dev/smoke_api.py) is the current substrate/bootstrap smoke path and the source of the `hello.txt` smoke artifact.
- `I^4` - live GitHub issues `#123` (first-run checklist) and `#125` (sample project + sample lease docs package), preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), are the intended onboarding/seed direction that is not yet fully realized in repo state.
