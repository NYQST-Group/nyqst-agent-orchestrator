# ADR-001: Data Model Strategy - Domain-First with CDM Mapping

**Status:** Accepted  
**Date:** 2026-01-26  
**Deciders:** Mark Forster, Devin  
**PRD Reference:** [03_PLATFORM.md - CDM Integration](../prd/03_PLATFORM.md), [06_ARCHITECTURE.md - Kernel Objects](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST needs a data model strategy for its relational structures. The question is whether to adopt Microsoft Common Data Model (CDM) as the foundation for commercial entities (Client, Project, Contact, Engagement) or to build a custom model.

Microsoft CDM provides standardized, extensible schemas for common business concepts and enables interoperability with the Microsoft ecosystem (Dynamics, Power Platform) and other CRM systems.

However, NYQST has unique requirements:
- Platform primitives (Artifact, Manifest, Pointer, Run, Session) that have no CDM equivalents
- Domain-specific models (Lease, Covenant, Regulation) not covered by CDM
- Session-Client-Project linkage with specific requirements (context injection, objective tracking)
- Agentic/document-centric architecture that differs from CDM's CRM/ERP focus

---

## Decision

**Domain-first with CDM mapping.**

NYQST will design its own data model for both platform primitives and commercial entities, based on NYQST's specific requirements. CDM will be used as an integration layer, not the foundation.

Specifically:
1. **Platform Primitives** (Artifact, Manifest, Pointer, Run, Session) - Custom NYQST model, no CDM involvement
2. **Commercial Entities** (Client, Project, Contact, Engagement) - Custom NYQST model designed for our needs
3. **CDM Mapping** - Provide mappings to CDM entities for integration with CRM systems (HubSpot, Dynamics, Salesforce)
4. **CDM Helper MCP** - Optional service that helps generate CDM-compatible schemas when integrating with external systems

---

## Options Considered

### Option 1: CDM-First

**Description:** Use Microsoft CDM as the foundation for all commercial entities. Extend CDM with custom attributes for NYQST-specific needs.

**Pros:**
- Industry-standard definitions reduce ambiguity
- Native interoperability with Microsoft ecosystem
- Pre-built schemas for common entities

**Cons:**
- CDM designed for CRM/ERP, not agentic/document-centric architectures
- Tight coupling to Microsoft ecosystem
- Our Session-Client-Project linkage has requirements CDM doesn't model
- Adds complexity and dependency for core operations

### Option 2: Domain-First with CDM Mapping (Selected)

**Description:** Design custom NYQST model based on our requirements. Provide CDM mappings as an integration layer for external systems.

**Pros:**
- Model optimized for NYQST's specific needs
- No dependency on external schema standards for core operations
- Flexibility to evolve model without CDM constraints
- CDM integration available when needed for CRM connectivity

**Cons:**
- Must maintain CDM mappings separately
- No automatic interoperability with CDM-based systems
- More upfront design work

### Option 3: No CDM Integration

**Description:** Build entirely custom model with no CDM consideration.

**Pros:**
- Maximum flexibility
- No external dependencies

**Cons:**
- Harder to integrate with CRM systems later
- May reinvent concepts CDM already defines well
- Missed opportunity for standardization

---

## Decision Rationale

Option 2 (Domain-First with CDM Mapping) was chosen because:

1. **Architecture fit:** NYQST's agentic/document-centric architecture is fundamentally different from CDM's CRM/ERP focus. Forcing our model into CDM's structure would create friction.

2. **Core independence:** Platform primitives (Artifact, Manifest, Pointer, Run, Session) are unique to NYQST and must be custom. Having some entities in CDM and others custom creates inconsistency.

3. **Integration flexibility:** CDM mapping as an integration layer gives us the benefits of CDM interoperability without the constraints of CDM as foundation.

4. **Evolution freedom:** Our understanding of Client-Project-Session relationships will evolve. A custom model lets us iterate without CDM compatibility concerns.

---

## Consequences

### Positive

- Data model optimized for NYQST's specific requirements
- No external dependency for core platform operations
- Can evolve model freely as understanding improves
- CDM integration available when needed for CRM connectivity

### Negative

- Must design and maintain our own commercial entity schemas
- CDM mappings require additional development and maintenance
- No automatic interoperability with CDM-based systems

### Risks

- **Risk:** CDM mappings become stale as our model evolves
  - **Mitigation:** Treat CDM mappings as first-class integration contracts with tests
  
- **Risk:** Custom model diverges too far from industry norms
  - **Mitigation:** Reference CDM and other standards when designing entities; don't reinvent unnecessarily

---

## Implementation Notes

1. **Commercial Entity Design:** When designing Client, Project, Contact, Engagement entities, reference CDM definitions for field naming and relationships where sensible, but don't constrain to CDM structure.

2. **CDM Helper MCP:** Build as optional service that:
   - Proposes CDM-compatible table structures
   - Generates mappings between NYQST entities and CDM entities
   - Helps with CRM integration projects

3. **Integration Testing:** When integrating with CRM systems, test CDM mappings explicitly.

---

## Related ADRs

- ADR-002: Code Generation and Contract Strategy (pending)

---

## References

- [Microsoft Common Data Model](https://docs.microsoft.com/en-us/common-data-model/)
- [CDM Entity Reference](https://docs.microsoft.com/en-us/common-data-model/entity-reference/)
- [NYQST PRD - CDM Integration](../prd/03_PLATFORM.md)
