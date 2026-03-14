---
document_id: GML-RENDERING
version: 1
date: 2026-02-19
---

# GML Rendering Analysis: Strategy Per Tag

> **Purpose**: Rendering strategy for all 18 GML tags, classified by difficulty, with @assistant-ui/react integration approach and phased implementation plan.
> **Source material**: `TECHNICAL-DEEP-DIVE.md`, `QUALITY-METHODS.md`, `GML_REPORT_RENDERING_PATTERNS.md`, `GML_CSS_EXTRACTION.md`

---

## Summary Table

| Tag | Category | Difficulty | Phase | React Component | Library Needed |
|-----|----------|-----------|-------|-----------------|---------------|
| `gml-row` | Layout | Easy | 1 | `GmlRow` (div flex) | none |
| `gml-primarycolumn` | Layout | Easy | 1 | `GmlPrimaryColumn` (div w-3/4) | none |
| `gml-sidebarcolumn` | Layout | Medium | 1 | `GmlSidebarColumn` | none |
| `gml-halfcolumn` | Layout | Easy | 1 | `GmlHalfColumn` (div max-w-50%) | none |
| `gml-inlinecitation` | Content | Medium | 1 | `GmlInlineCitation` | none |
| `gml-gradientinsightbox` | Content | Easy | 1 | `GmlGradientInsightBox` | none |
| `gml-blockquote` | Content | Medium | 1 | `GmlBlockquote` | none |
| `gml-infoblockmetric` | Content | Medium | 1 | `GmlInfoBlockMetric` | none |
| `gml-infoblockevent` | Content | Medium | 2 | `GmlInfoBlockEvent` | none |
| `gml-infoblockstockticker` | Content | Medium | 2 | `GmlInfoBlockStockTicker` | none |
| `gml-downloadfile` | Content | Medium | 2 | `GmlDownloadFile` | none |
| `gml-chartcontainer` | Content | Hard | 2 | `GmlChartContainer` | react-plotly.js / plotly.js |
| `gml-viewreport` | Viewer | Hard | 2 | `GmlViewReport` | slide-out panel |
| `gml-viewwebsite` | Viewer | Hard | 3 | `GmlViewWebsite` | none (link card) |
| `gml-viewpresentation` | Viewer | Hard | 3 | `GmlViewPresentation` | reveal.js (deferred) |
| `gml-viewgenerateddocument` | Viewer | Hard | 3 | `GmlViewGeneratedDocument` | none (link card) |
| `gml-components` | Meta | Easy | 1 | `null` (render nothing) | none |
| `gml-header-elt` | Meta | Easy | 1 | Augmented h1–h6 | none |

---

## Section 1: Complete GML Tag Inventory

GML is a custom markup language emitted by the Superagent LLM. The parser is `unified + rehype-parse`. After parsing, a healer walks the AST and corrects structural violations (wrong nesting, misplaced widgets). The healed AST is rendered via `hast-to-jsx` with a component registry mapping each GML tag to a React component.

The 18 tags divide into four categories:

```
Layout  (4): gml-row, gml-primarycolumn, gml-sidebarcolumn, gml-halfcolumn
Content (8): gml-chartcontainer, gml-gradientinsightbox, gml-infoblockmetric,
             gml-infoblockevent, gml-infoblockstockticker, gml-inlinecitation,
             gml-blockquote, gml-downloadfile
Viewers (4): gml-viewreport, gml-viewwebsite, gml-viewpresentation,
             gml-viewgenerateddocument
Meta    (2): gml-components, gml-header-elt
```

Standard HTML tags (`h1`–`h6`, `p`, `ul`, `ol`, `table`, `strong`, `em`, etc.) are used freely within GML containers and rendered natively or with light prose styling.

---

### 1.1 Layout Tags

#### `gml-row`

- **Syntax**: `<gml-row>...children...</gml-row>`
- **Purpose**: Top-level section wrapper. Establishes a horizontal flex row that stacks vertically on mobile.
- **Required attributes**: none
- **Children**: `gml-primarycolumn`, `gml-sidebarcolumn`, `gml-halfcolumn`
- **Width constraint**: none (top-level, unrestricted)
- **Superagent CSS**: `flex flex-col @3xl:flex-row flex-wrap gml-row`

#### `gml-primarycolumn`

- **Syntax**: `<gml-primarycolumn>...children...</gml-primarycolumn>`
- **Purpose**: Main content column (approximately 75% width on wide screens).
- **Required attributes**: none
- **Children**: content widgets (`gml-chartcontainer`, `gml-gradientinsightbox`, `gml-blockquote`, `gml-inlinecitation`), standard HTML
- **Width constraint**: must be inside `gml-row`
- **Superagent CSS**: `w-full @3xl:w-3/4 gap-[20px] @3xl:pr-5 gml-primarycolumn`

#### `gml-sidebarcolumn`

- **Syntax**: `<gml-sidebarcolumn>...children...</gml-sidebarcolumn>`
- **Purpose**: Sidebar column for metrics, events, and insight cards.
- **Required attributes**: none
- **Children**: `gml-infoblockmetric`, `gml-infoblockevent`, `gml-infoblockstockticker`, `gml-gradientinsightbox`
- **Width constraint**: must be inside `gml-row`
- **Special behaviour**: Superagent measures primary column height and truncates sidebar items that overflow (complex responsive logic). Each child is wrapped in `<div class="w-full">` and subsequent children receive `mt-7`.

#### `gml-halfcolumn`

- **Syntax**: `<gml-halfcolumn>...children...</gml-halfcolumn>`
- **Purpose**: Half-width column for side-by-side comparisons. Two `gml-halfcolumn` elements sit inside a `gml-row` to form a 50/50 split.
- **Required attributes**: none
- **Children**: standard HTML, content widgets
- **Width constraint**: must be inside `gml-row`
- **Superagent CSS**: `flex-2 max-w-[50%]`

---

### 1.2 Content Tags

#### `gml-chartcontainer`

- **Syntax**: `<gml-chartcontainer props='<JSON>'></gml-chartcontainer>`
- **Purpose**: Renders a Plotly chart. The `props` attribute is a JSON-encoded `ChartObject` (see Section 2.2 of TECHNICAL-DEEP-DIVE).
- **Required attributes**: `props` — JSON string conforming to `ChartObject` schema
- **Props schema** (abbreviated):
  ```typescript
  interface ChartObject {
    data: DataTrace[];        // required; each trace has name, type, data[]
    layout?: LayoutConfig;    // Plotly layout
    title?: string;
    citation?: ChartCitation; // optional source link
  }
  ```
- **Chart types**: `bar`, `scatter`, `line`, `bubble`, `histogram`, `box`, `candlestick`, `stacked_bar`, `clustered_column`, `donut`
- **Children**: none (self-closing or empty)
- **Width constraint**: must be inside `gml-primarycolumn`

#### `gml-gradientinsightbox`

- **Syntax**: `<gml-gradientinsightbox>...children...</gml-gradientinsightbox>`
- **Purpose**: Highlighted insight callout box with a gradient background and a "Superagent Insight" (or equivalent) badge header.
- **Required attributes**: none
- **Children**: standard HTML (`p`, `ul`, `ol`, `strong`, etc.)
- **Width constraint**: must be inside `gml-primarycolumn`
- **Superagent CSS**: `border border-black/10 rounded-xl my-5`, badge is `flex items-center gap-2 rounded-full border px-3 py-0.5 bg-gradient-badge`

#### `gml-blockquote`

- **Syntax**: `<gml-blockquote props='<JSON>'></gml-blockquote>`
- **Purpose**: Styled pull-quote or extended quotation with optional citation.
- **Required attributes**: `props` — JSON string
- **Props schema** (`ed` in source):
  ```typescript
  interface BlockquoteProps {
    quote_text: string;
    citation_identifier?: string;  // links to entity store
  }
  ```
- **Children**: none (props-driven)
- **Width constraint**: must be inside `gml-primarycolumn`

#### `gml-infoblockmetric`

- **Syntax**: `<gml-infoblockmetric props='<JSON>'></gml-infoblockmetric>`
- **Purpose**: KPI/metric display card — label, value, trend indicator.
- **Required attributes**: `props` — JSON string
- **Props schema** (`eG` in source):
  ```typescript
  interface InfoBlockMetricProps {
    formatted_metric: string;    // display value, e.g. "$2.4M"
    description: string;         // label, e.g. "Total Revenue"
    sentiment?: "up" | "down" | "neutral";
    citation_identifier?: string;
  }
  // Note: field aliases seen in docs: "label" → description, "value" → formatted_metric, "trend" → sentiment
  ```
- **Children**: none (props-driven)
- **Width constraint**: must be inside `gml-sidebarcolumn`

#### `gml-infoblockevent`

- **Syntax**: `<gml-infoblockevent props='<JSON>'></gml-infoblockevent>`
- **Purpose**: Event or milestone card for a timeline — date, title, description.
- **Required attributes**: `props` — JSON string
- **Props schema** (`eO` in source):
  ```typescript
  interface InfoBlockEventProps {
    date: string;           // ISO date string
    event: string;          // event title/name
    citation_identifier?: string;
  }
  ```
- **Children**: none (props-driven)
- **Width constraint**: must be inside `gml-sidebarcolumn`

#### `gml-infoblockstockticker`

- **Syntax**: `<gml-infoblockstockticker props='<JSON>'></gml-infoblockstockticker>`
- **Purpose**: Financial ticker card — symbol, price, change, company name.
- **Required attributes**: `props` — JSON string
- **Props schema** (`eW` in source):
  ```typescript
  interface InfoBlockStockTickerProps {
    symbol: string;
    companyName: string;
    price: number | string;
    change: number | string;
    changePercent: number | string;
    citation_identifier?: string;
  }
  ```
- **Children**: none (props-driven)
- **Width constraint**: must be inside `gml-sidebarcolumn`

#### `gml-inlinecitation`

- **Syntax**: `<gml-inlinecitation identifier="entity-abc-123"/>`
- **Purpose**: Inline superscript citation marker. Looks up entity metadata by identifier from the entity store (populated via `references_found` stream events). Renders as `[N]` with click-to-expand.
- **Required attributes**: `identifier` — matches a `citationIdentifier` from the entity store
- **Children**: none (self-closing)
- **Width constraint**: none (inline, unrestricted)

#### `gml-downloadfile`

- **Syntax**: `<gml-downloadfile props='<JSON>'></gml-downloadfile>` or with `identifier` attribute
- **Purpose**: File download card — looks up a generated artifact by identifier and renders a download button.
- **Required attributes**: `identifier` or `props` containing identifier — resolves to a citation entity with a download URL
- **Children**: none (props-driven)
- **Width constraint**: none (unrestricted)

---

### 1.3 Viewer Tags

All viewer tags accept `props='{"identifier": "<uuid>"}'` and resolve to a generated artifact entity. They render as interactive preview cards that open a slide-out or navigate to the artifact.

#### `gml-viewreport`

- **Syntax**: `<gml-viewreport props='{"identifier": "uuid"}'></gml-viewreport>`
- **Purpose**: Renders a card linking to a generated report. Clicking opens a slide-out panel that downloads and displays the report content.
- **Entity type required**: `GENERATED_REPORT`
- **Width constraint**: none (unrestricted)

#### `gml-viewwebsite`

- **Syntax**: `<gml-viewwebsite props='{"identifier": "uuid"}'></gml-viewwebsite>`
- **Purpose**: Preview card for a generated website artifact.
- **Entity type required**: `WEBSITE`
- **Width constraint**: not in width map (unrestricted)

#### `gml-viewpresentation`

- **Syntax**: `<gml-viewpresentation props='{"identifier": "uuid"}'></gml-viewpresentation>`
- **Purpose**: Embeds or links to a generated presentation/slides artifact.
- **Entity type required**: `GENERATED_PRESENTATION`
- **Width constraint**: not in width map (unrestricted)

#### `gml-viewgenerateddocument`

- **Syntax**: `<gml-viewgenerateddocument props='{"identifier": "uuid"}'></gml-viewgenerateddocument>`
- **Purpose**: Preview card for a generated document (PDF, DOCX, etc.).
- **Entity type required**: `GENERATED_DOCUMENT`
- **Width constraint**: not in width map (unrestricted)

---

### 1.4 Meta Tags

#### `gml-components`

- **Syntax**: `<gml-components>...</gml-components>`
- **Purpose**: Component registry or manifest declaration. Not a visible content tag — appears to be a structural wrapper used by the Superagent codebase for internal component registration. In the renderer it maps to `ComponentsRegistry`.
- **Required attributes**: unknown (internal use)
- **Rendering**: render `null` (invisible). Log a warning if encountered unexpectedly.

#### `gml-header-elt`

- **Syntax**: Applied as a transform on standard `h1`–`h6` elements, not as a standalone tag. The renderer replaces the native h1–h6 handlers with versions that generate slug-based IDs (`gml-header-elt-{slug}`) for anchor-link navigation.
- **Purpose**: Makes all headings anchor-linkable within the report.
- **Required attributes**: none (automatic from heading text)
- **Implementation**: Intercept `h1`–`h6` in the rehype-to-jsx handler, compute a slug from the text content, set `id="gml-header-elt-{slug}"`.

---

## Section 2: Rendering Strategy Per Tag

### 2.1 Layout Tags

---

#### `gml-row` — Easy | Phase 1

```tsx
// GmlRow.tsx
export function GmlRow({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col xl:flex-row flex-wrap gap-5 my-6">
      {children}
    </div>
  )
}
```

**Notes**: Superagent uses `@3xl:flex-row` (container query). We use `xl:flex-row` (viewport breakpoint) since we are not yet using container queries. Straightforward.

**Dependencies**: none

---

#### `gml-primarycolumn` — Easy | Phase 1

```tsx
export function GmlPrimaryColumn({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full xl:w-3/4 flex flex-col gap-5 xl:pr-5">
      {children}
    </div>
  )
}
```

**Dependencies**: none

---

#### `gml-sidebarcolumn` — Medium | Phase 1

The sidebar requires children to be individually wrapped. Superagent adds overflow truncation (measures primary column height and cuts off sidebar items that would overflow). For Phase 1 we skip height-matching and render all children stacked.

```tsx
export function GmlSidebarColumn({ children }: { children: React.ReactNode }) {
  const items = React.Children.toArray(children)
  return (
    <div className="w-full xl:flex-1 flex flex-col">
      {items.map((child, i) => (
        <div key={i} className={cn("w-full", i > 0 && "mt-7")}>
          {child}
        </div>
      ))}
    </div>
  )
}
```

**Phase 2 enhancement**: Add ResizeObserver to match sidebar height to primary column height.

**Dependencies**: none

---

#### `gml-halfcolumn` — Easy | Phase 1

```tsx
export function GmlHalfColumn({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex-1 min-w-0 max-w-[50%]">
      {children}
    </div>
  )
}
```

**Dependencies**: none

---

### 2.2 Content Tags

---

#### `gml-gradientinsightbox` — Easy | Phase 1

Wrap children in a styled card with a badge header. No external library needed. The Superagent label is "Superagent Insight" — we relabel to "Key Insight" or leave configurable.

```tsx
export function GmlGradientInsightBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="my-5 rounded-xl border border-black/10 bg-gradient-to-l from-neutral-50 to-transparent p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="rounded-full border border-black/10 px-3 py-0.5 text-xs font-semibold">
          Key Insight
        </span>
      </div>
      <div className="prose prose-sm max-w-none">{children}</div>
    </div>
  )
}
```

**Dependencies**: none (shadcn Badge can substitute for the pill if preferred)

---

#### `gml-inlinecitation` — Medium | Phase 1

Requires an entity lookup context. The entity store is populated by `references_found` stream events. The component reads from a React context (or Zustand store) keyed by `citationIdentifier`.

```tsx
// Assumes CitationContext provides: getCitation(identifier) → { number, title, url }
export function GmlInlineCitation({ identifier }: { identifier: string }) {
  const citation = useCitation(identifier) // reads from SourcesContext
  if (!citation) return null

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <a
          href={citation.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center text-xs text-blue-600 hover:underline"
        >
          [{citation.number}]
        </a>
      </TooltipTrigger>
      <TooltipContent>
        <p className="max-w-xs text-xs">{citation.title}</p>
      </TooltipContent>
    </Tooltip>
  )
}
```

**Dependencies**: shadcn `Tooltip`, existing `SourcesContext` (already in platform)

**Why Medium**: needs context wiring and number assignment logic (auto-incrementing citation numbers per message).

---

#### `gml-blockquote` — Medium | Phase 1

Parses `props` JSON, renders a styled pullquote. Optional citation link.

```tsx
interface BlockquoteProps {
  quote_text: string
  citation_identifier?: string
}

export function GmlBlockquote({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<BlockquoteProps>(propsJson)
  if (!parsed) return null

  return (
    <div className="my-5">
      <blockquote className="border-l-4 border-neutral-300 pl-4 italic text-neutral-700">
        <p>{parsed.quote_text}</p>
        {parsed.citation_identifier && (
          <GmlInlineCitation identifier={parsed.citation_identifier} />
        )}
      </blockquote>
    </div>
  )
}
```

**Dependencies**: `safeParseProps` utility (shared JSON error handler), `GmlInlineCitation`

---

#### `gml-infoblockmetric` — Medium | Phase 1

Parses `props` JSON, renders a KPI card with label, value, and trend badge.

```tsx
interface InfoBlockMetricProps {
  formatted_metric: string
  description: string
  sentiment?: "up" | "down" | "neutral"
  citation_identifier?: string
}

const SENTIMENT_CONFIG = {
  up:      { label: "↑", className: "text-green-700 bg-green-50" },
  down:    { label: "↓", className: "text-red-700 bg-red-50" },
  neutral: { label: "→", className: "text-neutral-600 bg-neutral-100" },
}

export function GmlInfoBlockMetric({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<InfoBlockMetricProps>(propsJson)
  if (!parsed) return null

  const sentiment = parsed.sentiment ? SENTIMENT_CONFIG[parsed.sentiment] : null

  return (
    <div className="my-5 rounded-xl border border-neutral-200 p-4">
      <p className="text-xs text-neutral-500">{parsed.description}</p>
      <p className="text-2xl font-bold text-neutral-900">{parsed.formatted_metric}</p>
      {sentiment && (
        <span className={cn("mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-semibold", sentiment.className)}>
          {sentiment.label}
        </span>
      )}
    </div>
  )
}
```

**Dependencies**: shadcn `Card` (optional), `safeParseProps`

**Note**: Field name aliases observed in the wild: `label` / `description`, `value` / `formatted_metric`, `trend` / `sentiment`. The `safeParseProps` should normalise both forms.

---

#### `gml-infoblockevent` — Medium | Phase 2

Similar card pattern to metric. Displays a date-stamped event.

```tsx
interface InfoBlockEventProps {
  date: string   // ISO date
  event: string  // title
  citation_identifier?: string
}

export function GmlInfoBlockEvent({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<InfoBlockEventProps>(propsJson)
  if (!parsed) return null

  return (
    <div className="my-5 rounded-xl border border-neutral-200 p-4">
      <p className="text-xs text-neutral-400">{formatDate(parsed.date)}</p>
      <p className="text-sm font-semibold text-neutral-800">{parsed.event}</p>
      {parsed.citation_identifier && (
        <GmlInlineCitation identifier={parsed.citation_identifier} />
      )}
    </div>
  )
}
```

**Dependencies**: `safeParseProps`, `formatDate` utility

---

#### `gml-infoblockstockticker` — Medium | Phase 2

Financial ticker card. Requires parsing price/change/percent fields and displaying a direction indicator.

```tsx
interface InfoBlockStockTickerProps {
  symbol: string
  companyName: string
  price: number | string
  change: number | string
  changePercent: number | string
  citation_identifier?: string
}

export function GmlInfoBlockStockTicker({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<InfoBlockStockTickerProps>(propsJson)
  if (!parsed) return null

  const isPositive = Number(parsed.change) >= 0

  return (
    <div className="my-5 rounded-xl border border-neutral-200 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold text-neutral-900">{parsed.symbol}</p>
          <p className="text-xs text-neutral-500">{parsed.companyName}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold">{parsed.price}</p>
          <p className={cn("text-xs font-semibold", isPositive ? "text-green-600" : "text-red-600")}>
            {isPositive ? "+" : ""}{parsed.change} ({parsed.changePercent}%)
          </p>
        </div>
      </div>
    </div>
  )
}
```

**Dependencies**: `safeParseProps`

---

#### `gml-downloadfile` — Medium | Phase 2

Looks up a generated artifact entity by identifier, renders a download card/button.

```tsx
export function GmlDownloadFile({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<{ identifier: string }>(propsJson)
  if (!parsed?.identifier) return null

  const entity = useEntity(parsed.identifier) // from entity/citation store
  if (!entity) return null

  return (
    <div className="my-5">
      <a
        href={entity.external_url}
        download
        className="flex items-center gap-2 rounded-lg border border-neutral-200 p-3 text-sm hover:bg-neutral-50"
      >
        <DownloadIcon className="h-4 w-4" />
        <span>{entity.title ?? "Download file"}</span>
      </a>
    </div>
  )
}
```

**Dependencies**: entity store / `useEntity` hook, lucide-react `DownloadIcon`

---

#### `gml-chartcontainer` — Hard | Phase 2

The most complex content tag. Parses a `ChartObject` JSON blob, validates it, maps to Plotly trace configs, and renders via `react-plotly.js`.

**Architecture**:
1. `safeParseProps<ChartObject>()` — parse and validate the JSON
2. `buildPlotlyTraces(chartObject)` — map each `DataTrace` to a Plotly trace using the switch-statement logic from TECHNICAL-DEEP-DIVE Section 2.4
3. Render with `<Plot data={traces} layout={layout} config={plotlyConfig} />`
4. Error boundary renders a red-bordered fallback if Plotly throws

```tsx
import dynamic from 'react-plotly.js/factory'  // dynamic import for SSR safety (N/A here but good practice)
import Plotly from 'plotly.js-basic-dist-min'   // tree-shakeable Plotly bundle
const Plot = createPlotlyComponent(Plotly)

export function GmlChartContainer({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<ChartObject>(propsJson)
  if (!parsed) return <ChartErrorFallback />

  const { traces, layout } = buildPlotlyData(parsed)

  return (
    <div className="my-5 relative min-h-[28rem]">
      <ErrorBoundary fallback={<ChartErrorFallback />}>
        <div className="rounded-xl border p-0 max-h-[320px] aspect-[41/29]">
          <Plot
            data={traces}
            layout={{ ...layout, autosize: true, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)" }}
            config={{ displayModeBar: false, displaylogo: false }}
            className="w-full h-full"
            useResizeHandler
          />
        </div>
        {parsed.citation && (
          <GmlInlineCitation identifier={String(parsed.citation.citation_number)} />
        )}
      </ErrorBoundary>
    </div>
  )
}
```

**`buildPlotlyData` function**: Implements the full switch statement from TECHNICAL-DEEP-DIVE 2.4 with the x_type auto-detection and the HSLA color palette.

**Why Hard**:
- External library (Plotly) with large bundle (~3MB for full build, ~500KB for basic dist)
- 10 chart type mappings to implement correctly
- Color palette must match or be adapted
- Error boundary required
- Responsive sizing with `useResizeHandler`
- Optional citation integration

**Dependencies**: `react-plotly.js`, `plotly.js-basic-dist-min` (or `plotly.js-cartesian-dist` for line/bar/scatter subsets)

**Bundle size note**: Use `plotly.js-basic-dist-min` (~500KB gzipped ~170KB) rather than the full bundle. Only adds `candlestick` if needed (use `plotly.js-finance-dist`).

---

### 2.3 Viewer Tags

All four viewer tags share the same resolution pattern:
1. Parse `props` JSON to get `identifier`
2. Look up the entity from the artifact store by identifier
3. Validate the entity's `entity_type` matches the expected type
4. Render a preview card; clicking opens the artifact

---

#### `gml-viewreport` — Hard | Phase 2

The Superagent implementation downloads report content and displays it in a slide-out panel. For Phase 2, we render a simple preview card that navigates to the report. Full slide-out is Phase 3.

```tsx
export function GmlViewReport({ props: propsJson }: { props: string }) {
  const parsed = safeParseProps<{ identifier: string }>(propsJson)
  if (!parsed?.identifier) return null

  const entity = useEntity(parsed.identifier)
  if (!entity || entity.entity_type !== "GENERATED_REPORT") return null

  return (
    <ReportPreviewCard
      title={entity.title ?? "View Report"}
      description={entity.description}
      onClick={() => openReportSlideout(entity)}
    />
  )
}
```

**Why Hard**: Requires the slide-out panel infrastructure (sheet component), async content fetch, GML renderer recursion (the report content is itself GML), and navigation state management.

**Dependencies**: shadcn `Sheet`, artifact store, navigation/routing

---

#### `gml-viewwebsite` — Hard | Phase 3

Renders a website preview card. For our platform, websites are generated Next.js/React apps. A simple link card suffices for Phase 3.

**Dependencies**: entity store, link card component

---

#### `gml-viewpresentation` — Hard | Phase 3

Presentations are slide decks (likely generated as reveal.js or similar). For Phase 3, render a link card. Embedded presentation viewer is deferred — it requires iframe sandboxing or reveal.js integration.

**Dependencies**: entity store, link card; reveal.js for embedded mode (deferred)

---

#### `gml-viewgenerateddocument` — Hard | Phase 3

Generated documents (PDF, DOCX) render as a download/preview card. Phase 3 may add an inline PDF viewer via `react-pdf`.

**Dependencies**: entity store, link card; `react-pdf` for inline preview (deferred)

---

### 2.4 Meta Tags

#### `gml-components` — Easy | Phase 1

Render nothing. This tag is an internal Superagent artifact that will not appear in our LLM output. If encountered, return `null` silently.

```tsx
export function GmlComponents() {
  return null
}
```

---

#### `gml-header-elt` — Easy | Phase 1

Not a standalone tag — applied as a transform on `h1`–`h6` elements during the hast-to-JSX rendering pass. Adds a slug-based `id` for anchor navigation.

```tsx
// In the rehype component override map
const headingComponents = Object.fromEntries(
  ["h1", "h2", "h3", "h4", "h5", "h6"].map((tag) => [
    tag,
    ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
      const text = extractText(children)
      const slug = slugify(text)
      const Tag = tag as keyof JSX.IntrinsicElements
      return <Tag id={`gml-header-elt-${slug}`} {...props}>{children}</Tag>
    },
  ])
)
```

**Dependencies**: `slugify` utility (e.g. `@sindresorhus/slugify` or custom)

---

## Section 3: Two-Phase Rendering Plan

### Phase 1 — Demo-Ready Renderer (Sprint 1–2)

**Goal**: Render a complete research report with layout, inline citations, insight boxes, and KPI metrics. Enough for a compelling demo without charts.

**Tags included** (10 of 18):

| Tag | Why Phase 1 |
|-----|------------|
| `gml-row` | Core layout — nothing renders without it |
| `gml-primarycolumn` | Core layout |
| `gml-sidebarcolumn` | Core layout |
| `gml-halfcolumn` | Core layout (Phase 1 with simplified height logic) |
| `gml-gradientinsightbox` | High visual impact, easy to build |
| `gml-inlinecitation` | Required for citation binding — already partially exists in platform |
| `gml-blockquote` | Minimal effort, good report quality signal |
| `gml-infoblockmetric` | Sidebar KPIs — visually differentiated from plain text |
| `gml-components` | null render, trivial |
| `gml-header-elt` | Augmented headings, trivial |

**Phase 1 deliverable**: A `GmlRenderer` component that accepts a GML string, runs the healer, and renders the above 10 tags. Charts and viewer cards show a placeholder. ~5 working days for an experienced React developer.

**Plain markdown fallback**: During Phase 1, if the orchestrator has not yet been updated to produce GML, it can emit plain markdown. The `GmlRenderer` falls back to a `ReactMarkdown` renderer for any message that does not contain GML tags. This decouples the GML renderer build from the backend work.

---

### Phase 2 — Full Content Renderer (Sprint 3–4)

**Tags added** (8 more):

| Tag | Why Phase 2 |
|-----|------------|
| `gml-chartcontainer` | Requires Plotly integration and 10 trace type mappings |
| `gml-infoblockevent` | Simple card but lower priority than metrics |
| `gml-infoblockstockticker` | Financial data — needed for stock research use cases |
| `gml-downloadfile` | Requires artifact entity store plumbing |
| `gml-viewreport` | Requires slide-out panel + artifact fetch |
| `gml-viewwebsite` | Requires artifact entity store |
| `gml-viewpresentation` | Requires artifact entity store |
| `gml-viewgenerateddocument` | Requires artifact entity store |

**Phase 2 deliverable**: Complete GML rendering. Viewer tags render preview cards (not full embedded viewers). Charts render correctly for all 10 types. ~8 working days.

### Phase 3 — Enhanced Viewers

Embedded presentation viewer (reveal.js or iframe), inline PDF viewer (`react-pdf`), report slide-out with nested GML rendering. These are quality-of-life enhancements, not blockers.

---

## Section 4: JSON Render Approach (AST Strategy)

### Concept

Instead of rendering GML strings directly via rehype, the GML string is first parsed to a typed JSON AST, and React components consume the AST.

```typescript
// Typed AST node
type GmlNode =
  | { type: "gml-row"; children: GmlNode[] }
  | { type: "gml-primarycolumn"; children: GmlNode[] }
  | { type: "gml-chartcontainer"; props: ChartObject }
  | { type: "gml-inlinecitation"; identifier: string }
  | { type: "html"; tag: string; props: Record<string, unknown>; children: GmlNode[] }
  | { type: "text"; value: string }
  // ... all 18 tags
```

The renderer is then a pure `renderNode(node: GmlNode): ReactNode` function.

### Advantages

1. **Decouples parsing from rendering** — the parser runs once server-side or at message ingestion; the React tree is constructed from structured data, not string manipulation.
2. **Enables multiple renderers** — the same AST can drive a web renderer, a PDF renderer (via `@react-pdf/renderer`), or a slide deck exporter.
3. **Testability** — unit tests operate on typed objects, not HTML strings.
4. **Streaming-safe** — the AST can be progressively built during streaming (`node_report_preview_delta`) and nodes can be appended to the tree as the stream arrives.
5. **Validation at parse time** — Zod schemas validate `ChartObject`, `InfoBlockMetricProps`, etc. as part of AST construction. Invalid props result in an error node, not a runtime exception in the renderer.

### Disadvantages

1. **Additional serialisation layer** — GML string → HAST → typed AST → React. Two parse passes.
2. **Custom parser maintenance** — The rehype pipeline (unified + rehype-parse) is battle-tested. A custom AST layer adds code to maintain.
3. **Not necessary for Phase 1** — the direct rehype-to-JSX approach (same as Superagent uses) works fine and is simpler to ship.

### Recommendation

**Do not implement the JSON AST layer for Phase 1 or 2.** Use the rehype-to-JSX approach matching Superagent's architecture:

```
GML string → unified+rehype-parse → HAST → healer(HAST) → hast-to-JSX → React tree
```

This is the proven approach. Revisit the AST layer in Phase 3 if a PDF export or multi-renderer requirement materialises.

**If a lightweight typed intermediate is desired**, generate a `GmlDocument` object at parse time (just top-level `gml-row` nodes) but keep the inner rendering as hast-to-JSX. This is a small structural win without the full AST schema overhead.

---

## Section 5: @assistant-ui/react Integration

### Current Platform Pattern

The platform uses `@assistant-ui/react` with `useChatRuntime` from `@assistant-ui/react-ai-sdk` and `AssistantRuntimeProvider`. The existing `CitationAwareText` component uses `useMessage` from `@assistant-ui/react`. The `Thread` and `Composer` components from `@assistant-ui/react-ui` handle the chat UI.

### Where GML Rendering Fits

GML output arrives as the `content` field of `node_report_preview_done` stream events — it is **not** the main chat message text. The main chat message (`message_delta` events) is plain text or markdown. The GML report is a structured artifact attached to the conversation.

This means GML rendering is **not** inside the `@assistant-ui/react` message parts pipeline. It is rendered in a separate panel (slide-out, preview card, or inline expanded section), not within the `Thread` component's message bubbles.

**Two integration patterns are viable:**

#### Pattern A: Inline in Message Content (via `makeMarkdownText` override)

If the orchestrator embeds GML directly into the assistant message text (rather than as a separate event), we can override the `Thread`'s text renderer:

```tsx
// In ChatPanel.tsx or Thread configuration
import { makeMarkdownText } from '@assistant-ui/react-markdown'

const GmlAwareText = makeMarkdownText({
  // Override the renderer to detect and render GML
  components: {
    // Map custom elements to GML components if using rehype-raw
  }
})
```

**Drawback**: `@assistant-ui/react` processes messages as markdown. GML is not markdown. Mixing them is fragile.

#### Pattern B: Separate Report Panel (Recommended)

The report GML content arrives via `node_report_preview_done.content` — a separate stream event from the main `message_delta` stream. Store this content in state alongside the message (e.g. in a Zustand slice keyed by `preview_id`). Render it in a dedicated `ReportPanel` component outside the `Thread`.

```tsx
// ReportPanel.tsx — rendered beside or below the Thread
export function ReportPanel({ previewId }: { previewId: string }) {
  const reportContent = useReportStore(s => s.reports[previewId])
  if (!reportContent) return null

  return (
    <div className="report-panel">
      <GmlRenderer content={reportContent.gml} citations={reportContent.citations} />
    </div>
  )
}
```

The `GmlRenderer` runs independently of `@assistant-ui/react`'s message pipeline:

```tsx
// GmlRenderer.tsx
import { unified } from 'unified'
import rehypeParse from 'rehype-parse'
import rehypeReact from 'rehype-react'
import { healGml } from './healer'
import { GML_COMPONENT_REGISTRY } from './registry'

export function GmlRenderer({ content, citations }: { content: string; citations: Citation[] }) {
  const element = useMemo(() => {
    const hast = unified()
      .use(rehypeParse, { fragment: true })
      .parse(content)

    healGml(hast)

    return unified()
      .use(rehypeReact, {
        createElement: React.createElement,
        components: GML_COMPONENT_REGISTRY,
      })
      .stringify(hast)
  }, [content])

  return (
    <CitationProvider citations={citations}>
      {element}
    </CitationProvider>
  )
}
```

**No `ChatModelAdapter` changes required.** GML rendering does not touch the runtime adapter.

#### Pattern C: `MessagePrimitive.Parts` for embedded GML snippets

If short GML snippets appear within assistant messages (not full reports), use `@assistant-ui/react`'s content part extension. Define a custom `ui` content part type:

```tsx
// Extend the message content part type (requires custom runtime)
type GmlContentPart = {
  type: "gml"
  gml: string
}

// In Thread configuration
<Thread assistantMessage={{ components: { Text: GmlAwareMessageText } }} />
```

This is the heaviest integration and only needed if GML is embedded in streaming chat messages (not just in report artifacts). For Phase 1, **Pattern B is the correct choice**.

### Recommended Integration Architecture

```
Stream → Zustand store
  ├── message_delta events    → Thread (via @assistant-ui/react useChatRuntime)
  ├── references_found        → CitationContext (existing SourcesContext)
  └── node_report_preview_done → ReportStore → ReportPanel → GmlRenderer
```

The `GmlRenderer` is a standalone React subtree. It shares the `CitationContext` from the existing `SourcesContext` pattern already present in the platform.

---

## Section 6: Blocking Analysis

### Is GML Rendering Blocking for Phase 1 Backend Work?

**No.** The following can proceed in parallel with GML renderer development:

1. **LangGraph orchestrator work** — the orchestrator can emit plain markdown in the main message stream while GML rendering is being built.
2. **Streaming protocol** — `node_report_preview_done` event handling can be stubbed to store the raw GML string without rendering it.
3. **Citation system** — `references_found` event handling and `SourcesContext` are already partially in the platform. These are independent of GML rendering.

### Minimum Viable Tag Set for a Research Report Demo

8 tags are sufficient for a compelling demo:

```
gml-row
gml-primarycolumn
gml-sidebarcolumn
gml-gradientinsightbox
gml-inlinecitation
gml-infoblockmetric
gml-blockquote
gml-header-elt (h1–h6 with IDs)
```

With these 8, a report renders with:
- Two-column layout (main + sidebar)
- Numbered inline citations
- KPI metric cards
- Highlighted insight callouts
- Stylised blockquotes
- Navigable headings

Charts are the next most impactful addition. A report without charts is demonstrable; a report without layout is not.

### Fallback Strategy

The orchestrator should accept a `rendering_mode` parameter:

| Mode | LLM Output | Renderer |
|------|-----------|---------|
| `gml` | Full GML with layout tags | `GmlRenderer` |
| `markdown` | Standard markdown | `ReactMarkdown` |

During Phase 1, the backend defaults to `markdown`. When `GmlRenderer` reaches Phase 1 completion, the backend switches to `gml`. This allows independent iteration.

### Can We Ship a "Basic" Renderer?

Yes. A partial renderer (8/18 tags) with stub `null` renders for unimplemented tags is the recommended Phase 1 deliverable. The healer runs in full — structurally invalid GML is corrected before rendering regardless of how many tags are implemented. Tags with no registered component silently render as `null` (or as a raw `<span>` fallback), which is the same behaviour as the Superagent renderer for unrecognised tags.

---

## Section 7: Implementation Checklist

### Shared Utilities (build first)

- [ ] `safeParseProps<T>(json: string): T | null` — JSON parse + Zod validation with error logging
- [ ] `slugify(text: string): string` — for gml-header-elt IDs
- [ ] `formatDate(iso: string): string` — for gml-infoblockevent
- [ ] `healGml(tree: HastNode): void` — port of the healer algorithm (TECHNICAL-DEEP-DIVE 1.2)
- [ ] `GML_COMPONENT_REGISTRY` — the tag-to-component map
- [ ] `GmlRenderer` — top-level component wiring unified + healer + rehype-react

### Phase 1 Components

- [ ] `GmlRow`
- [ ] `GmlPrimaryColumn`
- [ ] `GmlSidebarColumn` (simplified, no height matching)
- [ ] `GmlHalfColumn`
- [ ] `GmlGradientInsightBox`
- [ ] `GmlInlineCitation` (requires CitationContext)
- [ ] `GmlBlockquote`
- [ ] `GmlInfoBlockMetric`
- [ ] `GmlComponents` (null render)
- [ ] Augmented h1–h6 heading handler

### Phase 2 Components

- [ ] `GmlChartContainer` + `buildPlotlyData` + all 10 trace type mappings
- [ ] `GmlInfoBlockEvent`
- [ ] `GmlInfoBlockStockTicker`
- [ ] `GmlDownloadFile`
- [ ] `GmlViewReport` (preview card only)
- [ ] `GmlViewWebsite` (link card)
- [ ] `GmlViewPresentation` (link card)
- [ ] `GmlViewGeneratedDocument` (link card)
- [ ] `GmlSidebarColumn` height-matching enhancement

### Phase 2 Infrastructure

- [ ] `useEntity(identifier)` hook — looks up entity from artifact store by identifier
- [ ] `ReportStore` Zustand slice — stores `node_report_preview_done` content keyed by `preview_id`
- [ ] `ReportPanel` component — reads from ReportStore, renders GmlRenderer
- [ ] `CitationNumberAssigner` — auto-increments citation numbers per message

---

## Appendix: Key Reference Data

### Width Constraint Map (healer rules)

| Tag | Allowed Parent Container |
|-----|------------------------|
| `gml-blockquote` | `gml-primarycolumn` |
| `gml-chartcontainer` | `gml-primarycolumn` |
| `gml-gradientinsightbox` | `gml-primarycolumn` |
| `gml-halfcolumn` | `gml-row` |
| `gml-infoblockevent` | `gml-sidebarcolumn` |
| `gml-infoblockmetric` | `gml-sidebarcolumn` |
| `gml-infoblockstockticker` | `gml-sidebarcolumn` |
| `gml-primarycolumn` | `gml-row` |
| `gml-sidebarcolumn` | `gml-row` |
| `gml-downloadfile` | unrestricted |
| `gml-inlinecitation` | unrestricted (inline) |
| `gml-row` | unrestricted (top-level) |
| `gml-viewreport` | unrestricted |
| `gml-viewwebsite` | unrestricted |
| `gml-viewpresentation` | unrestricted |
| `gml-viewgenerateddocument` | unrestricted |

### Confirmed Chart Types (10)

`bar`, `scatter`, `line`, `bubble`, `histogram`, `box`, `candlestick`, `stacked_bar`, `clustered_column`, `donut`

### Superagent Color Palette

```typescript
// Donut / pie (6-stop teal)
const DONUT_COLORS = [
  "hsla(186, 60%, 20%, 1)", "hsla(186, 54%, 36%, 1)", "hsla(186, 44%, 43%, 1)",
  "hsla(186, 44%, 58%, 1)", "hsla(186, 53%, 65%, 1)", "hsla(185, 50%, 80%, 1)",
]
// Stacked bar / clustered column (2-stop)
const BAR_COLORS = ["hsla(186, 54%, 36%, 1)", "hsla(185, 50%, 80%, 1)"]
// Line: green for up, red for down
const LINE_COLOR_POSITIVE = "hsla(103, 40%, 43%, 1)"
const LINE_COLOR_NEGATIVE = "hsla(9, 90%, 48%, 1)"
```

### Plotly Config (as used by Superagent)

```typescript
const plotlyConfig = {
  displayModeBar: false,
  displaylogo: false,
}
```
