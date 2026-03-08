# [GAP-014] The streaming-events-extract.md documents 22 confirmed Superagent event types plus 4 NYQST proposed types, with complete Pydantic schemas and the NDJSON envelope format. The orchestration-extract.md documents the full fan-out dispatch pattern. However, there is no document that specifies the explicit integration contract between the two: which LangGraph events (on_tool_start, on_chat_model_stream, on_end) map to which SSE event types (node_tool_event, message_delta, done). The LangGraphToAISDKAdapter pseudocode in streaming-events-extract.md is an example, not a locked contract.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-014
- **Severity**: CRITICAL
- **Description**: The streaming-events-extract.md documents 22 confirmed Superagent event types plus 4 NYQST proposed types, with complete Pydantic schemas and the NDJSON envelope format. The orchestration-extract.md documents the full fan-out dispatch pattern. However, there is no document that specifies the explicit integration contract between the two: which LangGraph events (on_tool_start, on_chat_model_stream, on_end) map to which SSE event types (node_tool_event, message_delta, done). The LangGraphToAISDKAdapter pseudocode in streaming-events-extract.md is an example, not a locked contract.
- **Affected BL Items**: BL-001 (Research Orchestrator), BL-002 (RunEvent schema extensions)
- **Source Evidence**: streaming-events-extract.md (Two-Stream Architecture, LangGraph → AI SDK Adapter); orchestration-extract.md Section 1.3; KNOWLEDGE-MAP Phase 0 deliverables
- **Resolution**: Create a formal "Event Contract v1" document (referenced in KNOWLEDGE-MAP as a Phase 0 deliverable but not yet produced as a locked spec). The contract must: enumerate every LangGraph event hook (on_tool_start, on_tool_end, on_chat_model_stream, on_chain_start, on_chain_end) and specify exactly which SSE event type each maps to, what payload fields are included, and which LangGraph state fields are read for each mapping.
- **Owner Recommendation**: Backend architecture lead (BL-002 owner)
- **Wave**: P0 — this is a Phase 0 deliverable per KNOWLEDGE-MAP and must exist before BL-001 implementation

---

### GAP-015 — Tool Fallback Chain Strategy Not Specified in BL-001