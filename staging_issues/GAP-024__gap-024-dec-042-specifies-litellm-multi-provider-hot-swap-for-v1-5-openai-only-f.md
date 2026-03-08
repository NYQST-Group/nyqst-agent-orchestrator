# [GAP-024] DEC-042 specifies LiteLLM multi-provider hot-swap for v1.5+ (OpenAI-only for v1). The billing-metering-extract.md documents the LiteLLM + Langfuse integration pattern in detail (Router, callbacks, cost tracking via Langfuse REST API). However, KNOWLEDGE-MAP Section 10 explicitly lists "LiteLLM hot-swap implementation (DEC-042, designed but not coded)" as a deferred item. The current platform uses `langchain_openai.ChatOpenAI` directly. The cost tracking pipeline described in billing-metering-extract.md Section 4.2 requires LiteLLM to be in place for Langfuse to capture per-call costs automatically.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-024
- **Severity**: HIGH
- **Description**: DEC-042 specifies LiteLLM multi-provider hot-swap for v1.5+ (OpenAI-only for v1). The billing-metering-extract.md documents the LiteLLM + Langfuse integration pattern in detail (Router, callbacks, cost tracking via Langfuse REST API). However, KNOWLEDGE-MAP Section 10 explicitly lists "LiteLLM hot-swap implementation (DEC-042, designed but not coded)" as a deferred item. The current platform uses `langchain_openai.ChatOpenAI` directly. The cost tracking pipeline described in billing-metering-extract.md Section 4.2 requires LiteLLM to be in place for Langfuse to capture per-call costs automatically.
- **Affected BL Items**: BL-012 (billing/metering — depends on cost tracking), BL-013 (quota enforcement)
- **Source Evidence**: KNOWLEDGE-MAP Section 10 (Deferred to v1.5+); billing-metering-extract.md Section 4.2; hypothesis-code-alignment.md H5.4 (confirmed: ChatOpenAI only, no LiteLLM)
- **Resolution**: Determine whether v1 billing requires LiteLLM in the critical path. If cost tracking (DEC-045, $2/run budget) is required for v1, LiteLLM must be introduced before BL-012 can be completed. If cost tracking can be approximated (e.g., count tokens from ChatOpenAI response metadata), LiteLLM can remain deferred. Decision required before BL-012 is scheduled.
- **Owner Recommendation**: Architecture lead — needs explicit wave assignment decision
- **Wave**: W1 — decision needed before BL-012 begins; implementation timing depends on decision

---

### GAP-025 — Langfuse Self-Hosted Deployment Not Sized or Planned