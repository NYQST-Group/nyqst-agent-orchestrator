# Dify Output Display, Artifact Rendering & Conversation UI

> Deep analysis for clean-room reimplementation.
> Source: `~/nyqst-dify/upstream-dify/web/` (Next.js + React + Zustand)

---

## 1. Architecture Overview

Dify's output display system has five major layers:

1. **SSE Transport** (`service/base.ts`) -- Fetch + ReadableStream reader that parses `data:` lines and dispatches ~25 event types through typed callbacks.
2. **Chat State Hook** (`base/chat/chat/hooks.ts`) -- `useChat` manages a tree-structured conversation (not a flat list), using Immer for immutable updates. Streaming tokens are appended to mutable response items and then committed to the tree via `updateCurrentQAOnTree`.
3. **Chat Container** (`base/chat/chat/index.tsx`) -- Maps the linearised thread (`chatList`) to `<Question>` and `<Answer>` components. Handles auto-scroll with a user-scroll-override mechanism.
4. **Markdown Renderer** (`base/markdown/`) -- `react-markdown` with remark-gfm, remark-math, remark-breaks, rehype-katex, rehype-raw, plus custom component overrides for code, images, think blocks, forms, buttons, audio, video.
5. **Workflow Tracing** (`workflow/run/`) -- A recursive tree renderer that formats node execution traces into collapsible panels with status indicators, timing, and token counts.

---

## 2. Chat Message Rendering Pipeline

### 2.1 Data Model

The core type hierarchy:

```
IChatItem (type.ts)
  +-- id: string
  +-- content: string              -- raw markdown text
  +-- isAnswer: boolean            -- question vs answer
  +-- citation?: CitationItem[]    -- RAG sources
  +-- agent_thoughts?: ThoughtItem[] -- tool call chain
  +-- message_files?: FileEntity[] -- attached files
  +-- workflow_run_id?: string     -- links to workflow trace
  +-- workflowProcess?: WorkflowProcess -- inline trace
  +-- more?: MessageMore           -- time, tokens, latency, tokens/s
  +-- annotation?: Annotation      -- human-edited override
  +-- feedback?: FeedbackType      -- like/dislike + content
  +-- adminFeedback?: FeedbackType
  +-- log?: {role, text, files}[]  -- prompt log
  +-- sibling navigation fields    -- prevSibling, nextSibling, siblingCount, siblingIndex
```

`ChatItem` extends `IChatItem` with `isError`, `workflowProcess`, `conversationId`, and `allFiles`.

`ChatItemInTree` adds `children?: ChatItemInTree[]` for tree-structured conversations (branching on edit/regenerate).

### 2.2 Rendering Decision Tree

The `<Answer>` component (`chat/answer/index.tsx`) decides what to render based on the item's fields:

```
Answer
  +-- WorkflowProcessItem     (if workflowProcess exists)
  +-- LoadingAnim              (if responding && content empty && no agent thoughts)
  +-- BasicContent             (if content non-empty && no agent thoughts)
  |   +-- Markdown
  +-- AgentContent             (if agent_thoughts array has items)
  |   +-- Markdown per thought.thought
  |   +-- Thought/ToolDetail per thought.tool
  |   +-- FileList per thought.message_files
  +-- FileList                 (if allFiles or message_files)
  +-- Annotation badge         (if annotation present)
  +-- SuggestedQuestions       (inline follow-up chips)
  +-- Citation                 (if citation array non-empty && not streaming)
  +-- ContentSwitch            (if siblingCount > 1, for branch navigation)
```

The `<Question>` component renders user messages right-aligned with:
- FileList for attached files
- Markdown for content
- Edit mode (textarea + resend button) when user clicks edit
- ContentSwitch for sibling navigation
- Copy and edit action buttons (hover-revealed)

### 2.3 Markdown Pipeline

The `<Markdown>` component (`base/markdown/index.tsx`) applies a preprocessing pipeline before passing content to react-markdown:

**Step 1: Preprocess think tags**
`<think>` tags are converted to `<details data-think=true>` with an `[ENDTHINKFLAG]` sentinel before `</details>`. This allows the think block to render as a collapsible section using standard HTML5 details/summary elements through rehype-raw.

**Step 2: Preprocess LaTeX**
Backslash-bracket and backslash-paren LaTeX notation is normalised to dollar-sign notation. Code blocks are temporarily replaced with placeholders to avoid corrupting inline code.

**Step 3: React-Markdown rendering**
Configuration:
- **remark plugins**: remark-gfm (tables, strikethrough), remark-math, remark-breaks
- **rehype plugins**: rehype-katex (math rendering), rehype-raw (allows HTML passthrough), custom plugin to strip `ref` attributes and invalid tag names
- **URL transform**: Custom function that whitelists http, https, mailto, xmpp, irc, ircs, abbr schemes. Blocks data: URIs by default (configurable). Handles relative paths and fragments.
- **Disallowed elements**: iframe, head, html, meta, link, style, body

**Custom component overrides** (registered in react-markdown `components` prop):
| HTML element | Custom component | Behaviour |
|---|---|---|
| `code` | `CodeBlock` | Language detection, syntax highlighting, Mermaid, ECharts, SVG, ABC music |
| `img` | `Img` / `PluginImg` | Image rendering with plugin context |
| `video` | `VideoBlock` | Video player |
| `audio` | `AudioBlock` | Audio player |
| `a` | `Link` | Custom link handling |
| `p` | `Paragraph` / `PluginParagraph` | Paragraph with plugin context |
| `button` | `MarkdownButton` | Interactive button support |
| `form` | `MarkdownForm` | Form rendering in markdown |
| `script` | `ScriptBlock` | Script handling (sandboxed) |
| `details` | `ThinkBlock` | Reasoning/thought display |

### 2.4 Code Block Rendering

The `CodeBlock` component (`markdown-blocks/code-block.tsx`) handles multiple render modes based on the language annotation:

| Language | Renderer | Notes |
|---|---|---|
| `mermaid` | Dynamic import of Mermaid component | Renders flowcharts, sequence diagrams etc |
| `echarts` | `echarts-for-react` (ReactEcharts) | Parses JSON config, 3-state: loading/success/error. Handles streaming (incomplete JSON detection). Debounced resize. |
| `svg` | Custom SVGRenderer with toggle | Switches between rendered SVG and source view |
| `abc` | MarkdownMusic | ABC music notation rendering |
| All others | `react-syntax-highlighter` (hljs) | Light/dark theme via atelierHeath. Line numbers enabled. |

All code blocks share a header bar showing the language name (with capitalisation map) and a copy button. SVG blocks additionally get a source/preview toggle.

The ECharts renderer is particularly sophisticated:
- Tracks streaming state with refs to avoid re-renders
- Attempts JSON.parse first, then falls back to Function constructor evaluation for JS object literals
- Detects incomplete JSON by counting braces and brackets
- Limits `finished` event processing to 3 times to prevent infinite loops
- Debounces resize with 200ms timeout

---

## 3. Streaming Message Display (SSE to Incremental Render)

### 3.1 SSE Transport Layer

`service/base.ts` exports two key functions:

**`handleStream(response, ...callbacks)`**: Reads the response body using `ReadableStream.getReader()` and `TextDecoder`. Splits accumulated buffer on newlines, parses lines starting with `data: ` as JSON.

Event dispatch (exhaustive list of SSE event types):
- `message` / `agent_message` -- Text tokens. Calls `onData(answer, isFirstMessage, {conversationId, taskId, messageId})`
- `agent_thought` -- Tool call intermediate step
- `message_file` -- File attachment from agent
- `message_end` -- Final metadata including citations, files
- `message_replace` -- Content moderation replacement
- `workflow_started` / `workflow_finished` -- Workflow lifecycle
- `node_started` / `node_finished` / `node_retry` -- Individual node execution
- `iteration_started` / `iteration_next` / `iteration_completed` -- Loop iterations
- `loop_started` / `loop_next` / `loop_completed` -- Loop constructs
- `parallel_branch_started` / `parallel_branch_finished` -- Parallel execution
- `text_chunk` / `text_replace` -- Text streaming variants
- `agent_log` -- Agent debug logging
- `tts_message` / `tts_message_end` -- Text-to-speech audio chunks
- `datasource_processing` / `datasource_completed` / `datasource_error` -- Data source nodes

**`ssePost(url, fetchOptions, otherOptions)`**: Wraps `handleStream` with authentication (CSRF, passport headers), abort controller management, and error handling (401 retry via token refresh, SSO redirect).

### 3.2 State Management During Streaming

The `useChat` hook (`chat/hooks.ts`) manages streaming state:

1. **Before send**: Creates placeholder question and answer items with timestamp-based IDs. Inserts them into the chat tree immediately (optimistic UI).

2. **During streaming** (`onData` callback): Appends text tokens to `responseItem.content` (basic mode) or to the last `agent_thought.thought` (agent mode). After each chunk, calls `updateCurrentQAOnTree` which uses Immer `produce` to update the tree immutably and triggers React re-render.

3. **Agent thought accumulation** (`onThought` callback): Thoughts arrive as individual SSE events. If the thought ID matches the last thought, it updates in place (preserving accumulated `thought` text and `message_files`). Otherwise pushes a new thought.

4. **Workflow events**: `onWorkflowStarted` creates a `workflowProcess` object with `Running` status and empty tracing array. `onNodeStarted`/`onNodeFinished` push/update items in the tracing array. `onWorkflowFinished` updates the status.

5. **Completion** (`onCompleted`): Sets `isResponding=false`. Fetches the full conversation messages from the API to populate `more` metadata (time, tokens, latency, tokens/s) and `log` data. Optionally fetches suggested questions.

6. **Message end** (`onMessageEnd`): Populates `citation` from `metadata.retriever_resources` and `allFiles` from the files array.

### 3.3 Auto-Scroll Behaviour

The Chat container implements a scroll-lock mechanism:
- `userScrolledRef` tracks whether the user has scrolled up (>100px from bottom)
- `isAutoScrollingRef` prevents the scroll event handler from firing during programmatic scrolls
- Auto-scroll is disabled when user has scrolled up, re-enabled when a new conversation starts or the first message ID changes
- `ResizeObserver` on the footer adjusts container padding-bottom dynamically
- Debounced window resize handler (200ms) keeps footer width synchronised

### 3.4 Immer and Auto-Freeze

The hook calls `setAutoFreeze(false)` on mount and restores it on unmount. This is critical because streaming callbacks mutate `responseItem` directly before calling `updateCurrentQAOnTree`, which then uses `produce` to create a new tree state. Without disabling auto-freeze, Immer would throw when the callbacks try to mutate the already-frozen objects.

---

## 4. Thought/Reasoning Display

### 4.1 Think Block (LLM reasoning traces)

The `ThinkBlock` component (`markdown-blocks/think-block.tsx`) renders LLM chain-of-thought content that arrives wrapped in `<think>` tags.

**Preprocessing pipeline**:
1. `preprocessThinkTag` converts `<think>` to `<details data-think=true>` and `</think>` to `[ENDTHINKFLAG]</details>`
2. rehype-raw passes this through as HTML
3. react-markdown maps `<details>` to the `ThinkBlock` component

**Rendering behaviour**:
- If `data-think` is not set, renders a standard `<details>` element
- Otherwise renders a custom collapsible with:
  - Chevron icon that rotates 90 degrees when open (CSS transition)
  - Timer showing elapsed time in 100ms increments
  - Label switches between "Thinking..." and "Thought" when complete
  - Content area with left border and subtle background
- Completion detection: checks for `[ENDTHINKFLAG]` marker in children (recursive check through React element tree) OR `isResponding === false` (user stopped)
- The `[ENDTHINKFLAG]` is stripped from display content via `removeEndThink`
- Default state: open while thinking, then togglable when complete

### 4.2 Agent Thoughts (tool call chain)

The `AgentContent` component renders when `agent_thoughts` array has items:

- If `annotation?.logAnnotation` exists, renders that instead (human override)
- If there is accumulated `content`, renders a single Markdown block
- Otherwise iterates through `agent_thoughts`, rendering for each:
  - `thought.thought` as Markdown (the LLM's reasoning text)
  - `thought.tool` as a `<Thought>` component (the tool invocation)
  - `thought.message_files` as a `FileList`

The `<Thought>` component (`chat/thought/index.tsx`):
- Parses `thought.tool` as potentially a JSON array of tool names
- Creates a `toolThoughtList` with name, label, input, output, and isFinished
- Renders each as a `<ToolDetail>` component

The `<ToolDetail>` component (`chat/answer/tool-detail.tsx`):
- Collapsible panel with hammer icon and "Used/Using [tool name]" label
- Spinner animation while not finished
- Expanded view shows Request (tool_input) and Response (observation) sections
- Dataset tools get a special "Knowledge" label

---

## 5. Citation/Source Display from RAG

The citation system has three components:

### 5.1 Citation Container (`chat/citation/index.tsx`)

- Receives `CitationItem[]` from `message_end` metadata (`retriever_resources`)
- Groups citations by `document_id` into `Resources[]` objects
- Calculates how many citation chips fit on one line using hidden measurement elements
- Shows overflow as `+N` button that toggles full display
- Only renders after streaming completes (`!responding`)

### 5.2 Citation Popup (`chat/citation/popup.tsx`)

Each citation chip is a `<Popup>` component using `PortalToFollowElem` (floating UI):
- Trigger: Compact chip showing file icon + document name (max 240px, truncated)
- Popup: Card showing document name, then for each source segment:
  - Segment position badge (`#N`)
  - Full segment content text
  - Hit info (when `showHitInfo` is true): character count, hit count, vector hash (first 7 chars), relevance score as progress bar
  - Link to dataset document page (hover-revealed)

### 5.3 Citation Data Shape

```typescript
CitationItem {
  content: string           // matched text segment
  data_source_type: string  // 'notion' or file-based
  dataset_name: string
  dataset_id: string
  document_id: string
  document_name: string
  hit_count: number
  index_node_hash: string
  segment_id: string
  segment_position: number
  score: number             // relevance score 0-1
  word_count: number
}
```

---

## 6. File Upload and Attachment UI

### 6.1 File Entity Model

```typescript
FileEntity {
  id: string
  name: string
  size: number
  type: string               // MIME type
  progress: number           // upload progress 0-100
  transferMethod: TransferMethod  // 'local_file' | 'remote_url'
  supportFileType: string
  originalFile?: File
  uploadedId?: string        // server-assigned ID after upload
  base64Url?: string         // for preview
  url?: string               // remote URL
  isRemote?: boolean
}
```

Appearance types: image, video, audio, document, code, pdf, markdown, excel, word, ppt, gif, custom.

### 6.2 Upload Infrastructure

File upload uses `XMLHttpRequest` (not fetch) for progress tracking:
- `upload()` in `service/base.ts` creates XHR with auth headers
- Reports progress via `xhr.upload.onprogress`
- Returns `{id, ...}` on 201 status

Two upload contexts exist:
- `file-uploader-in-chat-input/` -- For the chat input area
- `file-uploader-in-attachment/` -- For attachment-style uploads

The `FileList` component (`base/file-uploader/index.ts`) renders uploaded files with:
- Delete action (optional)
- Download action (optional)
- Preview capability (optional)
- File type icon
- Specialised preview components: `audio-preview.tsx`, `video-preview.tsx`, `pdf-preview.tsx`, `file-image-render.tsx`

### 6.3 File Display in Messages

Files appear in multiple locations:
- Question messages: `message_files` rendered above content
- Answer messages: `allFiles` and `message_files` rendered below content
- Agent thoughts: `message_files` per thought rendered inline
- Workflow process: `files` in WorkflowProcess type

---

## 7. Conversation List and Management

### 7.1 Sidebar Architecture (`chat-with-history/sidebar/`)

- `List` component renders pinned and unpinned conversation lists
- `Item` component shows individual conversations with:
  - Active state highlighting
  - Operation menu (rename, pin/unpin, delete)
  - `RenameModal` for conversation renaming
- Conversations are `ConversationItem` objects from `models/share.ts`

### 7.2 Chat Tree Navigation

Conversations are stored as trees, not flat lists. The `useChat` hook:
- Maintains `chatTree` (full tree) and `threadMessages` (linearised path to current leaf)
- `targetMessageId` determines which branch is displayed
- `getThreadMessages(chatTree, targetMessageId)` walks from root to target
- `ContentSwitch` component enables sibling navigation (prev/next arrows with count indicator)
- When user edits a question and resends, a new branch is created under the parent message

### 7.3 Chat-with-History Wrapper

The `chat-with-history/` directory provides a full-page chat experience:
- `ChatWrapper` combines sidebar + chat + header
- `context.tsx` provides shared state (conversation list, current conversation, theme)
- `hooks.tsx` manages conversation CRUD operations
- Mobile-responsive with collapsible sidebar and mobile-specific header

---

## 8. App Preview/Debug Panel

### 8.1 Answer Operation Bar

The `<Operation>` component (`chat/answer/operation.tsx`) renders a floating action bar on hover:

**Always available (non-opening statement)**:
- Copy button (copies content to clipboard)
- Regenerate button (re-sends the question)
- Text-to-speech button (when TTS enabled)

**Feedback system** (two tiers):
- User feedback: like/dislike with optional content (dislike opens modal with textarea)
- Admin feedback: separate like/dislike, displayed alongside user feedback with divider
- Feedback state is tracked locally and synced via `onFeedback` callback
- Tooltip shows feedback label + rating + content

**Annotation system** (when enabled):
- `AnnotationCtrlButton` for adding/editing annotations
- `EditReplyModal` for editing annotation content
- Annotation badge shows author name below the message

**Prompt log** (when `showPromptLog` is true):
- Log button opens prompt/agent/message log modal depending on message type
- `PromptLogModal` shows the raw prompt sent to the LLM
- `AgentLogModal` shows the agent execution log
- Workflow messages open the message log modal

### 8.2 Message Metadata ("More")

The `<More>` component renders beneath the answer bubble:
- Time (formatted as hh:mm A)
- Total tokens (question + answer)
- Latency (seconds, 2 decimal places)
- Tokens per second (when latency > 0)

This data is populated after streaming completes, when the full conversation messages are fetched from the API.

---

## 9. Workflow Run Visualization (Execution Trace)

### 9.1 WorkflowProcess Inline Display

The `WorkflowProcessItem` component (`chat/answer/workflow-process.tsx`) renders inside chat messages:
- Collapsible header with status icon (spinner/check/error)
- Status-aware background colours (running=burn, success=green, failed=red)
- Expands to show `TracingPanel` with the full node execution trace

### 9.2 TracingPanel (`workflow/run/tracing-panel.tsx`)

The main execution trace renderer:
- Takes a flat `NodeTracing[]` list and formats it into a tree via `formatNodeList` utility
- Supports parallel branch grouping with collapsible parallel sections
- Hover state highlights the parallel group with accent colour and vertical line indicator
- Falls through to `SpecialResultPanel` for iteration/loop/retry/agent detail views

### 9.3 NodePanel (`workflow/run/node.tsx`)

Individual node execution card:
- Header: Block icon, title, token count, elapsed time, status icon
- Status indicators: succeeded (green check), failed (warning), stopped (alert), running (spinner), exception (alert), retry
- Collapsible detail section showing:
  - Iteration/Loop/Retry navigation triggers (link to sub-detail views)
  - Agent/Tool log triggers
  - Status messages (stopped-by, exception error, failure error)
  - Input JSON (CodeEditor, read-only)
  - Process data JSON (CodeEditor, read-only)
  - Output JSON (CodeEditor, read-only, with truncation alert and download link)
- Error handling tips via `ErrorHandleTip` component

### 9.4 Node Execution Data

```typescript
NodeTracing {
  node_id: string
  node_type: BlockEnum
  title: string
  status: 'running' | 'succeeded' | 'failed' | 'stopped' | 'exception' | 'retry'
  elapsed_time?: number
  inputs?: any
  outputs?: any
  process_data?: any
  error?: string
  execution_metadata?: {
    total_tokens?: number
    parallel_id?: string
    error_strategy?: string
  }
  extras?: { icon }
  details?: NodeTracing[][]    // iteration/loop sub-traces
  retryDetail?: NodeTracing[]  // retry attempts
  agentLog?: AgentLogItemWithChildren[]
  parallelDetail?: { isParallelStartNode, children, parallelTitle, branchTitle }
  expand?: boolean
  created_by?: { name }
  inputs_truncated?: boolean
  outputs_truncated?: boolean
  outputs_full_content?: { download_url }
}
```

### 9.5 Special Result Panels

The tracing system supports drill-down into:
- **Iteration results**: Shows each iteration as a separate trace list with duration
- **Loop results**: Similar to iteration but with loop variable state per iteration
- **Retry results**: Shows each retry attempt as a node trace
- **Agent/Tool logs**: Hierarchical log view for agent node executions

Navigation uses a stack-based model via `useLogs` hook -- pushing detail views onto the stack and popping back.

---

## 10. Log Viewer / Run History

### 10.1 Log Component (`chat/log/index.tsx`)

The log trigger button appears in the operation bar:
- Determines log type from the message: workflow (has `workflow_run_id`), agent (has `agent_thoughts`), or prompt
- Sets the current log item in the app store
- Opens the corresponding modal: `PromptLogModal`, `AgentLogModal`, or message log modal

### 10.2 App Log Page (`app/log/`)

The app-level log viewer (`app/components/app/log/`) provides:
- `list.tsx` -- Paginated conversation/run list
- `filter.tsx` -- Filtering by status, date, etc
- `var-panel.tsx` -- Variable inspection for workflow runs
- `model-info.tsx` -- Model configuration display

### 10.3 Workflow Log (`app/components/app/workflow-log/`)

Separate workflow-specific log viewer for workflow app types.

---

## 11. Export/Download Capabilities

### 11.1 File Downloads

- `FileList` component supports `showDownloadAction` prop
- Workflow outputs with truncated data provide `outputs_full_content.download_url`
- Code block copy button (clipboard, not download)

### 11.2 DSL Export

- `dsl-export-confirm-modal.tsx` in workflow components handles workflow export
- Exports workflow definition as DSL (domain-specific language) format

### 11.3 Content Copy

- Copy-to-clipboard available on: code blocks, question messages, answer messages
- Uses the `copy-to-clipboard` library
- Toast notification on successful copy

---

## 12. Key Patterns for Reimplementation

### 12.1 Tree-Structured Conversations

Unlike most chat UIs that use flat arrays, Dify maintains a tree where each message can have multiple children (branches). This enables:
- Edit-and-resend creating a new branch
- Sibling navigation (prev/next at the same level)
- Thread linearisation for display

The tree is managed with Immer `produce` and BFS traversal for updates. This is the most complex part of the state management and should be carefully designed in any reimplementation.

### 12.2 Streaming Architecture Pattern

```
SSE Response
  -> ReadableStream.getReader()
  -> TextDecoder
  -> Line-by-line parsing (buffer + split on \n)
  -> JSON.parse of data: prefix lines
  -> Event type dispatch to typed callbacks
  -> Callback mutates response item + calls tree update
  -> React re-render via state update
```

Key insight: The response item is mutated in place during streaming (not immutable), then the tree is updated immutably. This avoids creating new objects on every token while still triggering React re-renders.

### 12.3 Markdown Security

The markdown renderer has several security measures:
- URL whitelisting (only permitted schemes)
- Element disallowing (no iframes, no html/head/meta/style)
- Ref attribute stripping (prevents React ref injection)
- Invalid tag name sanitisation

### 12.4 Component Composition Pattern

Answer rendering uses a "feature detection" pattern:
- Check what data exists on the message (workflowProcess? agent_thoughts? citation? files?)
- Render the appropriate sub-components
- Each sub-component is self-contained and independently testable

### 12.5 Hover-Reveal Action Pattern

Operations (copy, feedback, regenerate, log) are hidden by default and revealed on hover using Tailwind's `hidden group-hover:flex` pattern. This keeps the UI clean during reading but provides full functionality on interaction.

### 12.6 State Store Architecture

Three Zustand stores interact:
- **App store** (`app/store.ts`): Global UI state (current log item, modal visibility)
- **Workflow store**: Workflow editor state (nodes, edges, running status)
- **Features store**: App feature configuration

The chat hook (`useChat`) uses local React state for the conversation tree but reads from stores for global concerns like log modals.

---

## 13. File Reference Index

| Concern | Key Files |
|---|---|
| SSE + streaming | `web/service/base.ts` |
| Chat state management | `web/app/components/base/chat/chat/hooks.ts` |
| Chat container | `web/app/components/base/chat/chat/index.tsx` |
| Answer rendering | `web/app/components/base/chat/chat/answer/index.tsx` |
| Question rendering | `web/app/components/base/chat/chat/question.tsx` |
| Basic content | `web/app/components/base/chat/chat/answer/basic-content.tsx` |
| Agent content | `web/app/components/base/chat/chat/answer/agent-content.tsx` |
| Tool detail | `web/app/components/base/chat/chat/answer/tool-detail.tsx` |
| Workflow process | `web/app/components/base/chat/chat/answer/workflow-process.tsx` |
| Operation bar | `web/app/components/base/chat/chat/answer/operation.tsx` |
| Thought component | `web/app/components/base/chat/chat/thought/index.tsx` |
| Citation container | `web/app/components/base/chat/chat/citation/index.tsx` |
| Citation popup | `web/app/components/base/chat/chat/citation/popup.tsx` |
| Markdown entry | `web/app/components/base/markdown/index.tsx` |
| Markdown wrapper | `web/app/components/base/markdown/react-markdown-wrapper.tsx` |
| Markdown utils | `web/app/components/base/markdown/markdown-utils.ts` |
| Code block | `web/app/components/base/markdown-blocks/code-block.tsx` |
| Think block | `web/app/components/base/markdown-blocks/think-block.tsx` |
| Tracing panel | `web/app/components/workflow/run/tracing-panel.tsx` |
| Node panel | `web/app/components/workflow/run/node.tsx` |
| Type definitions | `web/app/components/base/chat/chat/type.ts` |
| Chat types | `web/app/components/base/chat/types.ts` |
| File types | `web/app/components/base/file-uploader/types.ts` |
| Conversation sidebar | `web/app/components/base/chat/chat-with-history/sidebar/` |
| Log trigger | `web/app/components/base/chat/chat/log/index.tsx` |
| Chat context | `web/app/components/base/chat/chat/context.tsx` |
| App log viewer | `web/app/components/app/log/` |
| Workflow run hook | `web/app/components/workflow-app/hooks/use-workflow-run.ts` |

---

## 14. Dependencies Summary

| Library | Purpose |
|---|---|
| `react-markdown` | Core markdown rendering |
| `remark-gfm` | GitHub-flavoured markdown (tables, strikethrough) |
| `remark-math` + `rehype-katex` | LaTeX math rendering |
| `rehype-raw` | HTML passthrough in markdown |
| `react-syntax-highlighter` (hljs) | Code syntax highlighting |
| `echarts-for-react` | Chart rendering from JSON config |
| `mermaid` (dynamic) | Diagram rendering |
| `immer` | Immutable state updates for chat tree |
| `zustand` | Global state management (stores) |
| `copy-to-clipboard` | Clipboard operations |
| `es-toolkit/compat` | Utility functions (flow, uniqBy, debounce) |
| `reactflow` | Workflow canvas (used in editor, not in trace view) |
| `@remixicon/react` | Icon library |
| `js-cookie` | CSRF token management |
