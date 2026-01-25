# Architectural Consistency Analysis

*Date: 2026-01-23*  
*Purpose: Identify inconsistencies between UI, Backend, and Schema approaches*

---

## Executive Summary

After reviewing the codebase, **there are significant inconsistencies** between the three approaches (UI agent, Workflow agent, Holistic System agent). These inconsistencies fall into several categories:

1. **Two Different Event Systems** (not explained)
2. **Naming Convention Mismatches** (camelCase vs snake_case + field name differences)
3. **Type Definition Conflicts** (Claim, Evidence, Decision)
4. **Missing Implementations** (schemas defined but no backend/UI)
5. **Conceptual Mismatches** (EvidenceSpan vs Evidence)

**Critical Finding**: The three agents appear to have worked independently without coordination, resulting in overlapping but incompatible definitions.

---

## 1. Event System Confusion (CRITICAL)

### 1.1 Two Completely Different Event Concepts

**Problem**: There are TWO different "Event" concepts that are NOT explained or distinguished:

#### System 1: Run Ledger Events (Execution Tracking)
- **Purpose**: Track agent execution, tool calls, LLM interactions
- **TypeScript**: `RunLedgerEvent` in `src/types/events.ts`
- **Python**: `RunEventType` enum in `src/intelli/db/models/runs.py`
- **Database**: `run_events` table
- **Examples**: `tool_call_started`, `llm_request`, `checkpoint`, `run_completed`

#### System 2: Domain Events (Business Events)
- **Purpose**: Track lease breaks, rent reviews, deadlines, alerts
- **Schema**: `Event` in `schemas/event.schema.json`
- **Database**: ❌ NOT IMPLEMENTED
- **TypeScript**: ❌ NO TYPES
- **Python**: ❌ NO MODELS
- **Examples**: `lease_break`, `rent_review`, `covenant_test`

### 1.2 The Confusion

**Why This Is a Problem:**
- Both use "Event" terminology
- No documentation explains they're different
- UI has types for RunLedgerEvent but NOT domain Events
- Backend has models for RunLedgerEvent but NOT domain Events
- Schema defines domain Events but NO implementation exists
- Workflows reference domain Events but system can't support them

**Impact:**
- Developers will confuse the two
- Can't implement lease event management (critical requirement)
- Schema defines something that doesn't exist in code

**Recommendation:**
- Rename one to avoid confusion:
  - Option A: `RunLedgerEvent` → `RunExecutionEvent` (keep domain `Event`)
  - Option B: Domain `Event` → `BusinessEvent` or `DomainEvent` (keep `RunLedgerEvent`)
- Document the distinction clearly
- Implement domain Event system (currently missing)

---

## 2. Naming Convention Inconsistencies

### 2.1 Field Name Mismatches (Beyond Language Conventions)

**Language Conventions (OK):**
- TypeScript: `camelCase` (tenantId, projectId)
- Python: `snake_case` (tenant_id, project_id)
- ✅ This is expected and fine

**Field Name Differences (PROBLEM):**

| Concept | TypeScript | Python Backend | Schema | Status |
|---------|-----------|----------------|--------|--------|
| **Content Hash** | `contentHash` | `sha256` | `content_hash` | ❌ **INCONSISTENT** |
| **MIME Type** | `mimeType` | `media_type` | `media_type` | ⚠️ Partial |
| **File Size** | `sizeBytes` | `size_bytes` | N/A | ✅ Consistent (language) |
| **Storage Key** | `storageKey` | `storage_uri` | N/A | ❌ **INCONSISTENT** |
| **Created By Run** | `createdByRunId` | ❌ Missing | N/A | ❌ **MISSING** |
| **Logical Type** | `logicalType` | ❌ Missing | N/A | ❌ **MISSING** |

### 2.2 Artifact Model Comparison

**TypeScript `Artifact` Interface:**
```typescript
interface Artifact extends TenantScopedEntity {
  contentHash: ContentHash;        // ← sha256 in Python
  logicalType: ArtifactLogicalType; // ← Missing in Python
  mimeType: ArtifactMimeType;      // ← media_type in Python
  sizeBytes: number;                // ← size_bytes in Python
  filename?: string;               // ← filename in Python ✅
  schemaRef?: SchemaRef;            // ← Missing in Python
  createdByRunId?: UUID;           // ← Missing in Python
  storageKey: string;              // ← storage_uri in Python
  metadata: Record<string, unknown>; // ← Missing in Python
}
```

**Python `Artifact` Model:**
```python
class Artifact(Base, TimestampMixin):
    sha256: Mapped[str]            # ← contentHash in TypeScript
    media_type: Mapped[str]        # ← mimeType in TypeScript
    size_bytes: Mapped[int]        # ← sizeBytes in TypeScript ✅
    filename: Mapped[str | None]   # ← filename ✅
    storage_uri: Mapped[str]       # ← storageKey in TypeScript
    storage_class: Mapped[str]     # ← Missing in TypeScript
    created_by: Mapped[UUID | None] # ← Different concept
    reference_count: Mapped[int]   # ← Missing in TypeScript
    # Missing: logicalType, schemaRef, createdByRunId, metadata
```

**Issues:**
1. `contentHash` vs `sha256` - different field names
2. `storageKey` vs `storage_uri` - different field names
3. `logicalType` exists in TypeScript but NOT in Python
4. `createdByRunId` exists in TypeScript but NOT in Python
5. `reference_count` exists in Python but NOT in TypeScript
6. `storage_class` exists in Python but NOT in TypeScript

**Impact:**
- API responses won't match TypeScript types
- Frontend will have type errors
- Missing fields can't be used

---

## 3. Claim Type Inconsistencies

### 3.1 Claim Status Values

**TypeScript (`src/types/evidence.ts`):**
```typescript
type ClaimStatus =
  | 'draft'
  | 'proposed'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'superseded';
```

**Schema (`schemas/claim.schema.json`):**
```json
"status": {
  "enum": ["draft", "submitted", "under_review", "decided", "superseded"]
}
```

**Differences:**
- TypeScript: `'proposed'` → Schema: `'submitted'`
- TypeScript: `'approved'` / `'rejected'` → Schema: `'decided'` (single state)

**Impact:**
- Can't map between TypeScript and Schema
- Workflow logic will differ
- Status transitions incompatible

### 3.2 Claim Structure Differences

**TypeScript `Claim`:**
```typescript
interface Claim extends ProjectScopedEntity {
  type: ClaimType;                    // Enum: 'requirement', 'risk', etc.
  status: ClaimStatus;                 // Enum: 'draft', 'proposed', etc.
  title: string;                       // ← Missing in schema
  content: string;                     // ← statement in schema
  confidence: ClaimConfidence;         // ← Missing in schema
  tags: string[];                      // ← Missing in schema
  claimSchemaId?: UUID;                // ← claim_type_id in schema
  structuredData?: Record<string, unknown>; // ← context in schema
  parentClaimId?: UUID;                // ← Missing in schema
  createdByRunId?: UUID;               // ← Missing in schema
  ownerId?: UUID;                      // ← Missing in schema
  reviewDeadline?: Timestamp;          // ← Missing in schema
}
```

**Schema `Claim`:**
```json
{
  "claim_type_id": "string",           // ← type/claimSchemaId in TypeScript
  "statement": "string",               // ← content in TypeScript
  "severity": "string",                // ← Missing in TypeScript
  "status": "enum",                    // ← Different values
  "context": "object",                 // ← structuredData in TypeScript
  "source": "ClaimSource",             // ← Missing in TypeScript
  "evidence": "Evidence[]",            // ← Missing in TypeScript (has links)
  "quantification": "Quantification"   // ← Missing in TypeScript
}
```

**Major Differences:**
1. **Title field**: TypeScript has `title`, Schema has NO title (only `statement`)
2. **Confidence**: TypeScript has `confidence`, Schema has NO confidence
3. **Evidence**: Schema has `evidence` array, TypeScript has `ClaimSupportLink` separate
4. **Severity**: Schema has `severity`, TypeScript has NO severity
5. **Quantification**: Schema has `quantification`, TypeScript has NO quantification
6. **Source**: Schema has `source`, TypeScript has NO source tracking

**Impact:**
- Cannot use TypeScript types with Schema definitions
- Missing features in TypeScript (severity, quantification)
- Missing features in Schema (title, confidence, owner, deadline)
- Evidence linking approach differs (embedded vs separate links)

---

## 4. Evidence vs EvidenceSpan Confusion

### 4.1 Two Different Concepts

**TypeScript `EvidenceSpan`:**
- **Purpose**: A span of text in a document (location-based)
- **Fields**: `documentArtifactId`, `blockId`, `pageNumber`, `startOffset`, `endOffset`, `content`
- **Use**: Anchor claims to specific document locations

**Schema `Evidence`:**
- **Purpose**: A piece of evidence supporting/refuting a claim (concept-based)
- **Fields**: `evidence_type`, `relationship`, `strength`, `extraction_id`, `document_id`, `location`, `summary`
- **Use**: Represent evidence as a concept with relationship to claim

### 4.2 The Relationship

**How They Should Relate:**
- `EvidenceSpan` = WHERE the evidence is (location in document)
- `Evidence` = WHAT the evidence is (concept, relationship, strength)
- `Evidence` should reference `EvidenceSpan` via `location` or `extraction_id`

**Current State:**
- TypeScript has `EvidenceSpan` but NO `Evidence` type
- Schema has `Evidence` but NO `EvidenceSpan` definition
- TypeScript has `ClaimSupportLink` linking claims to evidence spans
- Schema has `Evidence` as array property of `Claim`
- **These are NOT aligned**

**Impact:**
- Can't map between TypeScript and Schema
- Evidence concept is split across two different models
- No clear relationship between location (EvidenceSpan) and concept (Evidence)

---

## 5. Decision Type Inconsistencies

### 5.1 Decision Structure Differences

**TypeScript `Decision`:**
```typescript
interface Decision extends ProjectScopedEntity {
  type: DecisionType;                  // Enum: 'approval', 'rejection', etc.
  context: DecisionContext;             // Enum: 'claim_review', 'corpus_promotion', etc.
  subjectType: 'claim' | 'corpus' | 'model' | 'run' | 'artifact';
  subjectId: UUID;
  deciderId: UUID;
  outcome: 'approved' | 'rejected' | 'deferred' | 'escalated';
  rationale: string;
  conditions?: DecisionCondition[];
  expiresAt?: Timestamp;
  supersedesDecisionId?: UUID;
  runId?: UUID;
}
```

**Schema `Decision`:**
```json
{
  "claim_id": "uuid",                  // ← subjectId in TypeScript (but more specific)
  "decision_type": "string",            // ← type in TypeScript
  "rationale": "string",                // ← rationale ✅
  "conditions": "string[]",             // ← conditions (different structure)
  "follow_up_actions": "array",         // ← Missing in TypeScript
  "decided_by": "string",               // ← deciderId in TypeScript
  "decided_at": "date-time",            // ← Missing in TypeScript (has createdAt)
  "approval_chain": "Approval[]"        // ← Missing in TypeScript
}
```

**Differences:**
1. **Subject**: TypeScript has `subjectType`/`subjectId` (generic), Schema has `claim_id` (specific)
2. **Context**: TypeScript has `context` enum, Schema has NO context
3. **Outcome**: TypeScript has `outcome` enum, Schema has NO outcome field
4. **Approval Chain**: Schema has `approval_chain`, TypeScript has NO approval chain
5. **Follow-up Actions**: Schema has `follow_up_actions`, TypeScript has NO follow-up actions
6. **Expiration**: TypeScript has `expiresAt`, Schema has NO expiration

**Impact:**
- Cannot map between TypeScript and Schema
- TypeScript is more generic (can decide on any subject)
- Schema is more specific (only for claims)
- Missing features in each direction

---

## 6. Missing Implementations

### 6.1 Schema-Defined But Not Implemented

| Schema Definition | TypeScript Types | Python Models | Python APIs | Status |
|-------------------|------------------|--------------|-------------|--------|
| **DocumentSource** | ❌ | ❌ | ❌ | **Not Implemented** |
| **DocumentStructure** | ✅ (DocIR, different) | ❌ | ❌ | **Partial** |
| **Extraction** | ❌ | ❌ | ❌ | **Not Implemented** |
| **Event** (domain) | ❌ | ❌ | ❌ | **Not Implemented** |
| **Deadline** | ❌ | ❌ | ❌ | **Not Implemented** |
| **Alert** | ❌ | ❌ | ❌ | **Not Implemented** |
| **Action** | ❌ | ❌ | ❌ | **Not Implemented** |
| **Outcome** | ❌ | ❌ | ❌ | **Not Implemented** |
| **Claim** | ✅ (incompatible) | ❌ | ❌ | **Type Mismatch** |
| **Evidence** | ✅ (different concept) | ❌ | ❌ | **Concept Mismatch** |
| **Decision** | ✅ (incompatible) | ❌ | ❌ | **Type Mismatch** |

**Impact:**
- Schemas define primitives that don't exist in code
- Can't implement workflows that depend on these primitives
- TypeScript types exist but don't match schemas

---

## 7. Conceptual Architecture Differences

### 7.1 Substrate Architecture

**TypeScript Approach:**
- `Artifact` has `logicalType` (document, table, graph, etc.)
- `Artifact` has `createdByRunId` (provenance)
- `Artifact` has `schemaRef` (structured data reference)
- More metadata-rich

**Python Approach:**
- `Artifact` is minimal (sha256, media_type, size_bytes, storage_uri)
- No logical type (can't distinguish document from table)
- No run provenance (can't track what created it)
- No schema reference (can't link to extraction schemas)
- More storage-focused

**Impact:**
- TypeScript expects features Python doesn't provide
- Can't implement logical type filtering
- Can't track artifact provenance
- Can't link artifacts to schemas

### 7.2 Document Model

**TypeScript Approach:**
- `DocIRDocument` (Document Intermediate Representation)
- Rich structure: pages, blocks, tables, figures
- Evidence anchoring via `DocIRAnchor`
- Highlights via `DocIRHighlight`

**Schema Approach:**
- `DocumentSource` (ingestion metadata)
- `DocumentStructure` (parsed structure)
- `Extraction` (extracted facts)
- More extraction-focused

**Python Approach:**
- ❌ NO DOCUMENT MODEL
- Documents are just `Artifact`s with `media_type: 'application/pdf'`
- No DocIR storage
- No extraction models

**Impact:**
- TypeScript expects DocIR but backend doesn't store it
- Can't implement document viewing features
- Can't anchor evidence to document locations
- Extraction system can't work (no Extraction model)

---

## 8. API Response Mismatches

### 8.1 Artifact API Response

**Python API Response (`ArtifactResponse`):**
```python
{
  "sha256": "abc123...",
  "media_type": "application/pdf",
  "size_bytes": 1024,
  "filename": "lease.pdf",
  "storage_uri": "s3://bucket/key",
  "storage_class": "STANDARD",
  "reference_count": 1,
  "created_at": "2026-01-23T10:00:00Z",
  "created_by": "uuid"
}
```

**TypeScript Expected (`Artifact`):**
```typescript
{
  id: "uuid",                    // ← Missing in Python (sha256 is PK)
  tenantId: "uuid",              // ← Missing in Python
  createdAt: "timestamp",         // ← created_at in Python ✅
  updatedAt: "timestamp",        // ← Missing in Python
  contentHash: "hash",           // ← sha256 in Python (different name)
  logicalType: "document",       // ← Missing in Python
  mimeType: "application/pdf",   // ← media_type in Python (different name)
  sizeBytes: 1024,               // ← size_bytes in Python ✅
  filename: "lease.pdf",         // ← filename ✅
  schemaRef: {...},              // ← Missing in Python
  createdByRunId: "uuid",        // ← Missing in Python
  storageKey: "key",             // ← storage_uri in Python (different)
  metadata: {}                   // ← Missing in Python
}
```

**Mismatches:**
- Missing: `id`, `tenantId`, `updatedAt`, `logicalType`, `schemaRef`, `createdByRunId`, `metadata`
- Different names: `contentHash` vs `sha256`, `mimeType` vs `media_type`, `storageKey` vs `storage_uri`
- Extra in Python: `storage_class`, `reference_count`, `created_by` (different concept)

**Impact:**
- Frontend will have type errors
- Missing fields can't be used
- Field name mismatches require mapping layer

---

## 9. Run Event Type Mismatches

### 9.1 RunEventType Enum Comparison

**Python (`RunEventType` enum):**
```python
RUN_STARTED = "run_started"
RUN_PAUSED = "run_paused"
RUN_RESUMED = "run_resumed"
RUN_COMPLETED = "run_completed"
RUN_FAILED = "run_failed"
RUN_CANCELLED = "run_cancelled"
STEP_STARTED = "step_started"
STEP_COMPLETED = "step_completed"
TOOL_CALL_STARTED = "tool_call_started"
TOOL_CALL_COMPLETED = "tool_call_completed"
LLM_REQUEST = "llm_request"
LLM_RESPONSE = "llm_response"
RETRIEVAL_QUERY = "retrieval_query"
RETRIEVAL_RESULT = "retrieval_result"
ARTIFACT_EMITTED = "artifact_emitted"
MANIFEST_CREATED = "manifest_created"
POINTER_MOVED = "pointer_moved"
CHECKPOINT = "checkpoint"
STATE_UPDATE = "state_update"
USER_INPUT = "user_input"
APPROVAL_REQUESTED = "approval_requested"
APPROVAL_GRANTED = "approval_granted"
APPROVAL_DENIED = "approval_denied"
COMMENT_ADDED = "comment_added"
ERROR = "error"
WARNING = "warning"
```

**TypeScript (`RunLedgerEvent` union):**
```typescript
'thread.message.created'
'agent.plan.proposed'
'agent.plan.updated'
'agent.action.proposed'
'human.comment.added'
'human.approval.recorded'
'tool.call.started'
'tool.call.completed'
'retrieval.query'
'retrieval.result'
'artifact.emitted'
'manifest.created'
'pointer.moved'
'diff.detected'
'evaluation.started'
'evaluation.completed'
'degradation.hook.triggered'
'session.started'
'session.closed'
'run.checkpoint.created'
'run.completed'
'run.failed'
```

**Differences:**
1. **Naming Convention**: Python uses `SNAKE_CASE`, TypeScript uses `dot.notation`
2. **Missing in TypeScript**: `run_started`, `run_paused`, `run_resumed`, `run_cancelled`, `step_started`, `step_completed`, `llm_request`, `llm_response`, `state_update`, `user_input`, `approval_requested`, `approval_granted`, `approval_denied`, `comment_added`, `error`, `warning`
3. **Missing in Python**: `thread.message.created`, `agent.plan.proposed`, `agent.plan.updated`, `agent.action.proposed`, `human.comment.added`, `human.approval.recorded`, `diff.detected`, `evaluation.started`, `evaluation.completed`, `degradation.hook.triggered`, `session.started`, `session.closed`, `run.checkpoint.created`

**Impact:**
- Event types don't match
- Can't serialize/deserialize between frontend and backend
- Missing event types in each direction
- Different naming conventions

---

## 10. Summary of Critical Inconsistencies

### 10.1 Most Critical Issues

1. **Two Event Systems** (Not Explained)
   - RunLedgerEvent vs Domain Event
   - Different purposes, same name
   - No documentation explaining distinction

2. **Artifact Model Mismatch**
   - Field name differences (`contentHash` vs `sha256`, `storageKey` vs `storage_uri`)
   - Missing fields in each direction (`logicalType`, `createdByRunId` vs `reference_count`, `storage_class`)
   - Can't use TypeScript types with Python API

3. **Claim Type Incompatibility**
   - Different status values (`proposed` vs `submitted`, `approved`/`rejected` vs `decided`)
   - Missing fields in each direction (`title`, `confidence` vs `severity`, `quantification`)
   - Evidence linking approach differs

4. **EvidenceSpan vs Evidence**
   - Two different concepts (location vs concept)
   - Not clearly related
   - Can't map between them

5. **Missing Domain Event Implementation**
   - Schema defines Event/Deadline/Alert
   - NO backend implementation
   - NO TypeScript types
   - Critical for lease event management

6. **RunEventType Naming Mismatch**
   - Python: `SNAKE_CASE` (`run_started`)
   - TypeScript: `dot.notation` (`run.completed`)
   - Different event type sets

### 10.2 Impact Assessment

**High Impact:**
- ❌ Cannot implement lease event management (domain Events missing)
- ❌ Cannot use TypeScript types with Python APIs (field name mismatches)
- ❌ Cannot implement extraction system (Extraction model missing)
- ❌ Cannot implement claim/evidence system (models missing, types incompatible)

**Medium Impact:**
- ⚠️ Artifact API responses don't match TypeScript types
- ⚠️ Run event types don't match between Python and TypeScript
- ⚠️ Document viewing features can't work (DocIR not stored)

**Low Impact:**
- ⚠️ Naming convention differences (expected, but field names differ)

---

## 11. Recommendations

### 11.1 Immediate Fixes

1. **Document Event System Distinction**
   - Rename one system to avoid confusion
   - Add clear documentation explaining both
   - Recommend: `RunLedgerEvent` → `RunExecutionEvent`, keep domain `Event`

2. **Align Artifact Field Names**
   - Choose one naming convention for API responses
   - Map between Python snake_case and TypeScript camelCase in API layer
   - Add missing fields (`logicalType`, `createdByRunId` to Python; `reference_count` to TypeScript)

3. **Unify Claim Status Values**
   - Choose one set of status values
   - Map between them if needed
   - Recommend: Use Schema values (`submitted`, `decided`) as canonical

4. **Clarify EvidenceSpan vs Evidence**
   - Document relationship: EvidenceSpan = location, Evidence = concept
   - Make Evidence reference EvidenceSpan via location
   - Add Evidence type to TypeScript

5. **Implement Domain Event System**
   - Create Python models for Event, Deadline, Alert
   - Create TypeScript types matching schemas
   - Create APIs for event management

### 11.2 Architecture Decisions Needed

1. **API Response Format**
   - Should APIs return camelCase (TypeScript-friendly) or snake_case (Python-friendly)?
   - Recommendation: Use camelCase in API responses, convert in API layer

2. **Field Name Standardization**
   - `contentHash` vs `sha256`: Which is canonical?
   - `storageKey` vs `storage_uri`: Which is canonical?
   - Recommendation: Use `contentHash` and `storageKey` in APIs, map to `sha256`/`storage_uri` internally

3. **Missing Field Strategy**
   - Add missing fields to Python models?
   - Remove from TypeScript types?
   - Recommendation: Add missing fields to both (union of features)

4. **Event Type Naming**
   - Standardize on `dot.notation` or `SNAKE_CASE`?
   - Recommendation: Use `dot.notation` in APIs, convert internally

### 11.3 Documentation Needed

1. **Architecture Decision Record (ADR)**
   - Document why two Event systems exist
   - Document naming conventions
   - Document field name choices

2. **Type Mapping Guide**
   - Map TypeScript types → Python models
   - Map Python models → API responses
   - Map Schemas → Implementation

3. **Migration Guide**
   - How to align existing code
   - Breaking changes required
   - Migration path

---

## 12. Conclusion

**The three agents did NOT coordinate**, resulting in:

1. **Overlapping but incompatible definitions** (Claim, Evidence, Decision)
2. **Missing implementations** (domain Events, Extraction, Document models)
3. **Naming inconsistencies** (beyond language conventions)
4. **Conceptual mismatches** (EvidenceSpan vs Evidence)
5. **Two Event systems** (not explained or distinguished)

**Critical Actions:**
1. Document the Event system distinction
2. Align Artifact field names
3. Unify Claim status values
4. Implement domain Event system (currently missing)
5. Add missing fields to align TypeScript and Python models

**Without these fixes:**
- Frontend and backend cannot work together
- Critical features (lease events, extraction) cannot be implemented
- Type safety is broken
- Developer confusion will be high

---

*This analysis reveals that the three approaches need significant alignment before implementation can proceed.*
