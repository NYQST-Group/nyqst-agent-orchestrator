# [GAP-032] DEC-047 defers the clarification UI to v1.5 but specifies that v1 includes "schema + backend checkpoint." BL-021 covers the clarification flow. The streaming-events-extract.md documents `clarification_needed` and `update_message_clarification_message` events. However, the API endpoint that accepts user input and resumes the LangGraph run after an interrupt is not specified (no route, no request/response schema, no LangGraph checkpoint resume pattern documented).

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-032
- **Severity**: LOW
- **Description**: DEC-047 defers the clarification UI to v1.5 but specifies that v1 includes "schema + backend checkpoint." BL-021 covers the clarification flow. The streaming-events-extract.md documents `clarification_needed` and `update_message_clarification_message` events. However, the API endpoint that accepts user input and resumes the LangGraph run after an interrupt is not specified (no route, no request/response schema, no LangGraph checkpoint resume pattern documented).
- **Affected BL Items**: BL-021 (clarification flow)
- **Source Evidence**: DEC-047; streaming-events-extract.md (Clarification Events); KNOWLEDGE-MAP Phase 4 deliverables
- **Resolution**: Specify the resume endpoint in BL-021: `POST /api/v1/runs/{run_id}/resume` with body `{user_input: str, interrupt_id: str}`. This calls `graph.ainvoke(Command(resume=user_input), config={thread_id: run_id})` using LangGraph's interrupt/resume pattern. Add to BL-021 acceptance criteria.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1

---

## Category 4: Competitive Intelligence Gaps

### GAP-033 — Superagent GML Formal Spec Not Recovered