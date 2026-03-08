# [GAP-025] DEC-045 locks Langfuse self-hosted (MIT license) for observability and billing data. KNOWLEDGE-MAP Section 10 lists "Langfuse self-hosted deployment (sizing, backup strategy)" as an external dependency TBD. The docker-compose.yml has a `profiles: ["observability"]` profile referenced in hypothesis-code-alignment.md H8 discussion, but there is no specification for: Langfuse container resource sizing, backup strategy, data retention policy, or how the Langfuse REST API will be accessed from the FastAPI backend for billing queries.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-025
- **Severity**: HIGH
- **Description**: DEC-045 locks Langfuse self-hosted (MIT license) for observability and billing data. KNOWLEDGE-MAP Section 10 lists "Langfuse self-hosted deployment (sizing, backup strategy)" as an external dependency TBD. The docker-compose.yml has a `profiles: ["observability"]` profile referenced in hypothesis-code-alignment.md H8 discussion, but there is no specification for: Langfuse container resource sizing, backup strategy, data retention policy, or how the Langfuse REST API will be accessed from the FastAPI backend for billing queries.
- **Affected BL Items**: BL-012 (billing — uses Langfuse REST API for cost data), BL-013 (quota middleware)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; billing-metering-extract.md Section 4.2; DEC-045
- **Resolution**: Add a Langfuse deployment specification: container resource requirements (CPU, RAM), data retention policy (30 days minimum for billing), backup schedule (daily), and a `docker-compose.langfuse.yml` or addition to the `observability` profile. Define the REST API call pattern for billing queries.
- **Owner Recommendation**: DevOps / infrastructure track
- **Wave**: W0 — required before BL-012 implementation

---

### GAP-026 — Search Provider Selection Requires Cost Comparison