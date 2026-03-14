---
document_id: NDM-SCHEMA-V1
version: 1
date: 2026-03-14
status: locked
abbreviation: NDM = NYQST Document Model (also referred to as MarkupDocument)
gap: GAP-082
prerequisite_for: BL-004
---

# NYQST Document Model (NDM) v1 — JSON Schema Specification

> **Purpose**: Formal specification of the MarkupDocument JSON schema used by the backend (BL-004 report generation node, DEC-015a). This is the structured Pydantic representation of a GML report, distinct from the GML string format (used by the frontend, DEC-015b).
>
> **Relationship to GML**: NDM is the backend JSON AST. GML is the serialised string format emitted by the LLM. The backend (BL-004) parses the LLM GML output and validates/stores it as NDM. The frontend receives the raw GML string and renders it via rehype-to-JSX (DEC-015b).
>
> **Source**: Derived from GML-RENDERING-ANALYSIS.md tag inventory and orchestration-extract.md Section 3.1.

---

## 1. Node Type Taxonomy

NDM has four node categories corresponding to the 18 GML tags plus standard HTML prose nodes:

| Category | Node Types | Count |
|---|---|---|
| Layout | `row`, `primary_column`, `sidebar_column`, `half_column` | 4 |
| Content | `chart`, `gradient_insight_box`, `blockquote`, `info_block_metric`, `info_block_event`, `info_block_stock_ticker`, `inline_citation`, `download_file` | 8 |
| Viewer | `view_report`, `view_website`, `view_presentation`, `view_generated_document` | 4 |
| Meta | `components`, `header_element` | 2 |
| Prose | `heading`, `paragraph`, `list`, `list_item`, `table`, `table_row`, `table_cell`, `text`, `html_element` | 9 |

**Total node types**: 27

---

## 2. Schema Definitions (Pydantic v2)

### 2.1 Root Document

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Any
from enum import Enum
import hashlib

class MarkupDocument(BaseModel):
    """Root NDM document. Contains a sequence of top-level row nodes."""
    schema_version: Literal["ndm-v1"] = "ndm-v1"
    document_id: str  # UUID, assigned at creation
    title: str
    user_query: str  # The original research query that produced this document
    generated_at: str  # ISO 8601 timestamp
    sections: list["RowNode"]  # Top-level layout sections
    citations: list["CitationRef"] = Field(default_factory=list)  # Citation registry
    metadata: dict[str, Any] = Field(default_factory=dict)  # Run context (run_id, plan_set_id, etc.)

    def sha256(self) -> str:
        """Content hash for artifact storage."""
        content = self.model_dump_json(exclude={"document_id", "generated_at"})
        return hashlib.sha256(content.encode()).hexdigest()
```

### 2.2 Layout Nodes

```python
class RowNode(BaseModel):
    type: Literal["row"]
    children: list[Union["PrimaryColumnNode", "SidebarColumnNode", "HalfColumnNode"]]

class PrimaryColumnNode(BaseModel):
    type: Literal["primary_column"]
    children: list[Union[
        "ChartNode", "GradientInsightBoxNode", "BlockquoteNode",
        "InlineCitationNode", "DownloadFileNode",
        "HeadingNode", "ParagraphNode", "ListNode", "TableNode"
    ]]

class SidebarColumnNode(BaseModel):
    type: Literal["sidebar_column"]
    children: list[Union[
        "InfoBlockMetricNode", "InfoBlockEventNode",
        "InfoBlockStockTickerNode", "GradientInsightBoxNode"
    ]]

class HalfColumnNode(BaseModel):
    type: Literal["half_column"]
    children: list[Union[
        "HeadingNode", "ParagraphNode", "ListNode", "TableNode",
        "ChartNode", "GradientInsightBoxNode", "InlineCitationNode"
    ]]
```

### 2.3 Content Nodes

#### Chart Node

```python
class DataTrace(BaseModel):
    name: str
    type: Literal[
        "bar", "scatter", "line", "bubble", "histogram",
        "box", "candlestick", "stacked_bar", "clustered_column", "donut"
    ]
    data: list[Any]  # x/y arrays, OHLC tuples, etc. — structure varies by chart type
    color: Optional[str] = None  # Override HSLA palette if specified

class LayoutConfig(BaseModel):
    title: Optional[str] = None
    xaxis: Optional[dict[str, Any]] = None
    yaxis: Optional[dict[str, Any]] = None
    showlegend: Optional[bool] = None

class ChartCitation(BaseModel):
    citation_number: int
    citation_identifier: str  # UUID linking to CitationRef

class ChartNode(BaseModel):
    type: Literal["chart"]
    chart_type: Literal[
        "bar", "scatter", "line", "bubble", "histogram",
        "box", "candlestick", "stacked_bar", "clustered_column", "donut"
    ]
    traces: list[DataTrace]
    layout: Optional[LayoutConfig] = None
    title: Optional[str] = None
    citation: Optional[ChartCitation] = None
```

#### Text Content Nodes

```python
class GradientInsightBoxNode(BaseModel):
    type: Literal["gradient_insight_box"]
    children: list[Union["ParagraphNode", "ListNode", "HeadingNode"]]

class BlockquoteNode(BaseModel):
    type: Literal["blockquote"]
    quote_text: str
    citation_identifier: Optional[str] = None  # UUID linking to CitationRef

class InfoBlockMetricNode(BaseModel):
    type: Literal["info_block_metric"]
    label: str
    value: str
    trend: Optional[Literal["up", "down", "neutral"]] = None
    subtext: Optional[str] = None
    citation_identifier: Optional[str] = None

class InfoBlockEventNode(BaseModel):
    type: Literal["info_block_event"]
    title: str
    date: str  # ISO 8601 or human-readable
    description: Optional[str] = None
    impact: Optional[Literal["positive", "negative", "neutral"]] = None

class InfoBlockStockTickerNode(BaseModel):
    type: Literal["info_block_stock_ticker"]
    symbol: str
    price: Optional[str] = None  # String to preserve formatting ("$150.23")
    change: Optional[str] = None
    change_pct: Optional[str] = None
    exchange: Optional[str] = None

class InlineCitationNode(BaseModel):
    type: Literal["inline_citation"]
    identifier: str  # UUID — must match a CitationRef.identifier

class DownloadFileNode(BaseModel):
    type: Literal["download_file"]
    identifier: str  # UUID — resolves to an artifact entity with download URL
    filename: Optional[str] = None
```

### 2.4 Viewer Nodes

```python
class ViewerNodeBase(BaseModel):
    identifier: str  # UUID — resolves to an artifact/entity of the appropriate type

class ViewReportNode(ViewerNodeBase):
    type: Literal["view_report"]

class ViewWebsiteNode(ViewerNodeBase):
    type: Literal["view_website"]

class ViewPresentationNode(ViewerNodeBase):
    type: Literal["view_presentation"]

class ViewGeneratedDocumentNode(ViewerNodeBase):
    type: Literal["view_generated_document"]
```

### 2.5 Meta Nodes

```python
class ComponentsNode(BaseModel):
    type: Literal["components"]
    # Render nothing. Internal Superagent artifact, ignored at document level.

class HeaderElementNode(BaseModel):
    type: Literal["header_element"]
    level: Literal[1, 2, 3, 4, 5, 6]
    text: str
    slug: str  # Computed: slugify(text), used for anchor IDs
```

### 2.6 Prose Nodes

```python
class HeadingNode(BaseModel):
    type: Literal["heading"]
    level: Literal[1, 2, 3, 4, 5, 6]
    children: list[Union["TextNode", "InlineCitationNode"]]

class ParagraphNode(BaseModel):
    type: Literal["paragraph"]
    children: list[Union["TextNode", "InlineCitationNode", "HtmlElementNode"]]

class ListNode(BaseModel):
    type: Literal["list"]
    ordered: bool
    children: list["ListItemNode"]

class ListItemNode(BaseModel):
    type: Literal["list_item"]
    children: list[Union["TextNode", "ParagraphNode", "ListNode", "InlineCitationNode"]]

class TableNode(BaseModel):
    type: Literal["table"]
    head: list["TableRowNode"] = Field(default_factory=list)
    body: list["TableRowNode"]

class TableRowNode(BaseModel):
    type: Literal["table_row"]
    cells: list["TableCellNode"]

class TableCellNode(BaseModel):
    type: Literal["table_cell"]
    is_header: bool = False
    children: list[Union["TextNode", "InlineCitationNode"]]

class TextNode(BaseModel):
    type: Literal["text"]
    value: str
    bold: bool = False
    italic: bool = False
    code: bool = False

class HtmlElementNode(BaseModel):
    type: Literal["html_element"]
    tag: str  # "a", "span", "code", "strong", "em", etc.
    props: dict[str, Any] = Field(default_factory=dict)
    children: list[Union["TextNode", "InlineCitationNode"]]
```

### 2.7 Citation Registry

```python
class CitationRef(BaseModel):
    """Entry in the MarkupDocument citation registry."""
    identifier: str  # UUID — matches InlineCitationNode.identifier
    citation_number: int  # Sequential display number (1, 2, 3, ...)
    title: str
    external_url: str
    provider: str  # "brave", "jina", "factset", "user_upload", etc.
    retrieved_at: str  # ISO 8601
    entity_id: Optional[str] = None  # Pointer to the backing Artifact in the substrate
```

---

## 3. Nesting Rules

These rules are enforced by the backend NDM healer (DEC-040a) and mirror the GML width constraint map from GML-RENDERING-ANALYSIS Appendix:

| Node Type | Must be child of | Cannot contain |
|---|---|---|
| `row` | Document root (`sections[]`) | Another `row` directly |
| `primary_column` | `row` | `info_block_*` nodes |
| `sidebar_column` | `row` | `chart`, `blockquote`, `gradient_insight_box` |
| `half_column` | `row` | `info_block_*`, `sidebar_column` |
| `chart` | `primary_column` | Any children (leaf node) |
| `blockquote` | `primary_column` | Any children (leaf node, text via props) |
| `gradient_insight_box` | `primary_column` | `chart`, `info_block_*` |
| `info_block_metric` | `sidebar_column` | Any children (leaf node) |
| `info_block_event` | `sidebar_column` | Any children (leaf node) |
| `info_block_stock_ticker` | `sidebar_column` | Any children (leaf node) |
| `inline_citation` | Any prose context (inline) | Any children (leaf node) |
| `download_file` | Any block context | Any children (leaf node) |
| Viewer nodes | Any block context | Any children (leaf node) |

**Healer behaviour on violation**: Hoist the node to the nearest valid ancestor. If no valid ancestor exists, discard the node and log a warning. This matches the behaviour of the JavaScript HAST healer in Superagent.

---

## 4. Chart Data Structure

Chart data is stored in a normalised, chart-type-agnostic format:

```python
# For line/bar/scatter/stacked_bar/clustered_column:
DataTrace(
    name="Revenue",
    type="bar",
    data=[
        {"x": "Q1 2025", "y": 2400000},
        {"x": "Q2 2025", "y": 2800000},
    ]
)

# For candlestick:
DataTrace(
    name="AAPL",
    type="candlestick",
    data=[
        {"x": "2025-01-15", "open": 148.5, "high": 152.0, "low": 147.2, "close": 150.8},
    ]
)

# For donut:
DataTrace(
    name="Market Share",
    type="donut",
    data=[
        {"label": "Product A", "value": 45},
        {"label": "Product B", "value": 35},
        {"label": "Other", "value": 20},
    ]
)

# For bubble:
DataTrace(
    name="Companies",
    type="bubble",
    data=[
        {"x": 100, "y": 200, "size": 50, "label": "Corp A"},
    ]
)
```

---

## 5. Section Hierarchy

A well-formed MarkupDocument has the following hierarchy:

```
MarkupDocument
  └─ sections: RowNode[]          # Top-level layout rows
       └─ children:
            ├─ PrimaryColumnNode  # Main content (text, charts, insights)
            │   └─ [HeadingNode, ParagraphNode, ChartNode, GradientInsightBoxNode, ...]
            ├─ SidebarColumnNode  # KPI cards (metrics, events, tickers)
            │   └─ [InfoBlockMetricNode, InfoBlockEventNode, ...]
            └─ HalfColumnNode     # Side-by-side comparisons
                └─ [ParagraphNode, ChartNode, ...]
```

Typical section count: 3–8 rows for a standard research report.

---

## 6. Relationship to GML String Format

```
LLM Output (GML String)
         │
         ▼
  gml_parser.parse(gml_string: str) → HastTree
         │
         ▼
  backend_healer.heal(hast_tree) → HealedHastTree
         │
         ▼
  ndm_builder.build(hast_tree) → MarkupDocument  ← THIS SCHEMA
         │
         ▼
  artifact_service.store(doc.sha256(), doc.json()) → Artifact(sha256, "application/vnd.nyqst.ndm+json")
```

The GML string is also stored as a separate Artifact (`application/vnd.nyqst.gml+xml`) for direct frontend consumption.

---

## 7. Storage

MarkupDocument is stored as:
- **Media type**: `application/vnd.nyqst.ndm+json`
- **Storage**: MinIO object store via `artifact_service`
- **Key**: SHA-256 of the serialised JSON (excluding `document_id` and `generated_at`)
- **Pointer**: A `Pointer` record in the substrate points to the current head artifact for a given `(run_id, preview_id)` pair

---

## Revision Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-14 | Agent (claude-sonnet-4-6) | v1 created from GML-RENDERING-ANALYSIS.md + orchestration-extract.md Section 3.1 (GAP-082 resolution) |
