---
    key: EPIC-STUDIO
    title: Studio (notebook + infinite canvas) with provenance
    type: epic
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:XL, track:studio, type:epic]
    ---

    ## Problem

    Users need a workspace to build intelligence: narrative notebook + spatial canvas with links and diffs.

    ## Proposed solution

    Implement notebook pages/blocks and an infinite canvas with block library, linking, inspector, and pinning from other modules.

    ## Dependencies

    - EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)

    ## Acceptance criteria

    - [ ] Notebook supports pages and blocks (text, evidence embed, app output embed)
- [ ] Canvas supports pan/zoom, blocks, edges, inspector
- [ ] Can pin app outputs and diffs to canvas
- [ ] Provenance inspector shows run and source links

    ## Test plan

    - [ ] Vitest: stores and block reducers
- [ ] E2E: pin output to canvas and reload persists layout (if persistence in scope)

    ## Notes / references

    - See docs/02_USER_FLOWS_MASTER.md Flow 4
