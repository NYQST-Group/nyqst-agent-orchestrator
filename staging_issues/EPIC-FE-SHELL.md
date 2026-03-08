---
    key: EPIC-FE-SHELL
    title: Frontend shell (navigation, routes, base screens)
    type: epic
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:XL, track:frontend, type:epic]
    ---

    ## Problem

    We need a real UI shell early to keep UX coherent and allow parallel screen implementation.

    ## Proposed solution

    Implement app-wide navigation and route map with placeholder screens backed by fixtures.

    ## Dependencies

    - EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Left nav and route map implemented (Projects, Apps, Studio, Documents, CRM, Models, Dashboards, Workflows, Runs, Settings)
- [ ] Screens render loading/empty/error states
- [ ] Fixture-driven screens for Apps and Runs work without backend
- [ ] Mockup component integrated as a dev-only route

    ## Test plan

    - [ ] Vitest component tests for nav + routing
- [ ] Typecheck passes
- [ ] Playwright smoke test: open each route

    ## Notes / references

    - Use mockups/NyqstPortalMockupV2.tsx as reference
