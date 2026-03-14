# Superagent JS Bundle Extraction - Design Signals Summary

**Extraction Date**: 2026-02-20
**Source**: Next.js production bundles (112 files, 7.5 MB)
**Method**: Minified code pattern analysis + manifest catalog

---

## Executive Summary

Superagent is a **Gradient** (AI agent generation platform) built on Next.js with heavy emphasis on real-time streaming chat, structured document generation via custom **GML markup language**, and multi-channel deployment (web, PDF, presentations).

### Core Architecture Pillars
1. **Chat Engine**: SSE/streaming message protocol with agent reasoning traces
2. **Document Generation**: GML markup language + Plotly charting
3. **Deployment Platform**: Built-in website/artifact deployment API
4. **State Management**: Recoil atoms + selectors (not Redux/Zustand)
5. **Analytics**: Heavy instrumentation (PostHog recorder, GA4, social pixels)

---

## File Inventory Breakdown

| Category | Count | Size | Key Files |
|----------|-------|------|-----------|
| **App Shell** | 1 | 1.8 MB | `_app-7122b4604941924b.js` |
| **Chat Streaming** | 1 | 389 KB | `591-ee776d1e90f29cf3.js` |
| **GML Rendering** | 1 | 344 KB | `4d022aba-d65484ccff3256c9.js` |
| **Page Components** | 4 | 656 KB | `[chatId]`, `index`, `1889-*`, `937-*` |
| **Framework/Runtime** | 2 | 275 KB | React + Next.js bundles |
| **Styling** | 1 | 213 KB | `55ccf76ff5ccbea2.css` |
| **Fonts** | 5 | ~150 KB | DM Mono + ATSeasonSans |
| **Analytics** | 12 | ~3 MB | PostHog, GA4, Facebook, Twitter |
| **Other** | 84 | ~1.1 MB | Favicons, manifests, etc. |

---

## Key Design Signals

### 1. Chat Streaming Architecture

**Endpoint**: `/api/chat/message/stream`
**Protocol**: Server-Sent Events or Fetch ReadableStream
**Format**: NDJSON (newline-delimited JSON)

```
Client: POST /api/chat/message { "content": "..." }
Server: GET /api/chat/message/stream { "type": "token", "content": "..." }
        GET /api/chat/message/stream { "type": "done", "metadata": {...} }
```

**Evidence**:
- Dedicated 391 KB bundle (`591-*.js`) for streaming logic
- Retry mechanism: `/api/chat/retry`
- Trace link generation: `/api/chat/trace-link` (likely LangSmith integration)

### 2. GML (Gradient Markup Language)

Custom XML-like markup for structured document generation. 17 unique custom elements:

**View Types**:
- `gml-viewreport` — Report layout
- `gml-viewwebsite` — Website layout
- `gml-viewpresentation` — Slide presentation
- `gml-viewgenerateddocument` — Generic document

**Layout Primitives**:
- `gml-row`, `gml-primarycolumn`, `gml-halfcolumn`, `gml-sidebarcolumn`

**Data Visualization**:
- `gml-chartcontainer` (Plotly.js integration)
- `gml-infoblockmetric`, `gml-infoblockevent`, `gml-infoblockstockticker`
- `gml-gradientinsightbox`

**Content**:
- `gml-blockquote`, `gml-inlinecitation`, `gml-downloadfile`, `gml-header-elt`

**Rendering Engine**: 344 KB bundle dedicated to GML → React component conversion

### 3. State Management: Recoil

**Pattern Evidence**:
```javascript
// In minified _app bundle:
selector  // ~28 occurrences
atom      // ~2 occurrences
useChat   // 1 occurrence
```

**Estimated Atoms**:
- `chatState` — Current messages, status, generation
- `userState` — Profile, workspace, preferences
- `documentState` — Generated artifacts, metadata
- `featureFlagsState` — Feature toggles
- `navigationState` — Current route, sidebar state

**NOT used**: Redux, Zustand, Context (except for providers)

### 4. Deployment Capabilities

**APIs**:
- `POST /api/deploy` — Deploy website artifact
- `GET /api/website/status` — Check deployment status
- `POST /api/browser-use/user-input-done` — Signal browser automation completion

**Evidence**: Website deployment is first-class feature, not addon

### 5. Browser Automation

**APIs**:
- `POST /api/browser-use/user-input-done` — Callback on user input event
- `GET/POST /api/browser-profile` — Manage browser automation profiles
- `POST /api/browser-profile/opt-out` — Privacy control

**Inference**: Superagent can instrument and control browser automation tasks

### 6. Charting Library

**Primary**: Plotly.js (via `react-plotly.js`)
**NOT**: Recharts (references in docs are incorrect)
**Timeline**: Custom Timeline component for temporal data

**Integration**: Deep in GML rendering layer (`gml-chartcontainer`)

### 7. Design System

**Framework**: Tailwind CSS v4
**Custom Tokens**:
- `--chat-footer-h` — Chat input footer height
- `--chart-1` through `--chart-5` — Data viz colors
- `--color-*` — Extended palette (Amber, Blue, etc.)
- `--animate-pulse-scale`, `--animate-pulse-scale-mini` — Custom animations

**Fonts**:
- **DM Mono** (Google Fonts) — Code/data display
- **ATSeasonSans** (self-hosted) — UI typography

### 8. Analytics Stack

Heavy instrumentation across 5 channels:

**PostHog** (Product Analytics):
- Config ID: `phc_USesA3LHTQe1A1ozLZFQEQhTmazV9S4sOZQ561IZsHX`
- Modules: Recorder (251 KB), Surveys (90 KB), Web Vitals, Dead click detection, Exception tracking
- Endpoint: `https://app.posthog.com`

**Google Analytics 4**:
- GTM: `GTM-TMP7WP43`
- 5 separate GA4 properties + AdWords conversion tracking

**Social Pixels**:
- Facebook: `418406606004092`
- Twitter: `adsct` pixel
- LinkedIn: Analytics tracker

**Tracking Headers**:
- `x-posthog-distinct-id`
- `x-posthog-session-id`
- `x-posthog-utm-campaign`, `x-posthog-utm-source`

---

## API Surface Map

### Chat Operations
```
POST   /api/chat/message              Send user message
GET    /api/chat/message/stream       Stream agent response (SSE)
POST   /api/chat/retry                Retry failed message
POST   /api/chat/user-message/generate-title  Auto-title conversation
GET    /api/chat/trace-link           Generate trace viewer link
GET    /api/chat/list                 List chats
GET    /api/chat/citation_download    Download citation data
```

### Documents & Artifacts
```
POST   /api/artifact/download         Download generated artifact
GET    /api/artifact/download-public  Download from public share
GET    /api/preview/thumbnail         Get thumbnail preview
```

### Session & Auth
```
GET    /api/session                   Get current session
POST   /api/session/redeem-token      Redeem invite token
GET    /api/account                   Get account profile
GET    /api/account/personal-info     Get personal details
```

### Deployment
```
POST   /api/deploy                    Deploy website
GET    /api/website/status            Check deployment status
```

### Browser Automation
```
POST   /api/browser-use/user-input-done  Signal automation completion
GET/POST /api/browser-profile          Manage browser profiles
POST   /api/browser-profile/opt-out   Privacy opt-out
```

### Feature Flags
```
GET    /api/feature-flags             Get feature flags
POST   /api/feature_flag/local_evaluation  Client-side eval
GET    /api/early_access_features     List EA features
```

### Projects
```
GET/POST /api/projects                List/create projects
POST   /api/use-case/bulk-create      Bulk create templates
```

---

## Code Quality Signals

### Strengths
1. **Modularity**: 16+ shared chunk bundles (code reuse, fast updates)
2. **Streaming-First**: Native SSE architecture, not polling
3. **Deployment Native**: Website deployment as core feature
4. **Analytics Rigor**: 5-channel instrumentation suggests serious metrics
5. **Custom Domain Language**: GML abstraction shows architectural sophistication

### Gaps/Unknowns
1. **Authentication**: JWT vs session cookies unclear from bundle
2. **Database Layer**: Not visible in frontend (server-side only)
3. **GML Schema**: Inferred from usage; formal spec not visible
4. **SSO**: `/api/sso/google/generate-url` present but details minimal
5. **Error Recovery**: Retry logic present; error boundaries unclear

---

## Estimated Tech Stack

| Layer | Technology |
|-------|-----------|
| **Runtime** | Node.js 18+ |
| **Web Framework** | Next.js 13-14 |
| **React** | v18+ |
| **State** | Recoil |
| **HTTP Client** | Fetch API (native) |
| **Streaming** | ReadableStream / EventSource |
| **CSS** | Tailwind CSS v4 |
| **Charts** | Plotly.js (react-plotly.js) |
| **Components** | shadcn/ui (inferred) |
| **Analytics** | PostHog SDK |
| **Fonts** | Google Fonts + Self-hosted |

---

## Comparison to DocuIntelli Platform Primitives

### Alignment with Superagent Parity Goal

| Feature | Superagent | NYQST Parity Requirement | Gap |
|---------|-----------|-------------------------|-----|
| **Real-time Streaming** | `/api/chat/message/stream` (SSE) | ✓ LangGraph+LLM streaming | Exact same |
| **Document Generation** | GML markup + React rendering | ✓ Artifact generation | Different format (need JSON AST) |
| **State Management** | Recoil atoms | ✓ Session state | Compatible |
| **Deployment API** | `/api/deploy` endpoint | ✓ Website deployment | Same intent |
| **Browser Automation** | `/api/browser-use/*` | ✓ MCP browser tools | Different layer |
| **Multi-channel Output** | Report, Website, Presentation | ✓ Report panel | Superagent is wider |
| **Feature Flags** | `/api/feature-flags` | ✓ DEC-025 experiments | Same pattern |

### Key Difference: Document Rendering

**Superagent**: GML (custom XML) → React components → HTML
**NYQST Target**: JSON AST → rehype → React (DEC-015a/b)

Superagent's GML is a **higher-level abstraction** for domain-specific layouts (reports, websites, presentations). NYQST uses a lower-level Markdown/HTML intermediate that's more flexible for arbitrary content.

---

## Extraction Outputs

All signals extracted to:
- **Manifest**: `/Users/markforster/AirTable-SuperAgent/docs/design-reconstruction/00-inventory/superagent-js-manifest.json`
- **This Summary**: `/Users/markforster/AirTable-SuperAgent/docs/design-reconstruction/00-inventory/EXTRACTION-SUMMARY.md`

---

## Next Steps for Platform Parity

1. **Validate GML findings** against actual Superagent API responses (check `/api/chat/message` payloads)
2. **Confirm streaming protocol** (SSE vs ReadableStream) via network inspection
3. **Extract feature flag names** for A/B testing infrastructure
4. **Map browser-use API** to MCP equivalents (if any)
5. **Compare Recoil atom structure** to NYQST session state needs
