# Citation Feature Debugging Report

## Date: February 4, 2026

## Problem Statement
Citations were not appearing in the UI. The user reported that:
1. Citations `[1]`, `[2]`, etc. were not showing as clickable links in assistant messages
2. Sources panel was not populating with document excerpts
3. After implementing fixes, the agent would end after tool calls without generating a response

## What Was Tested

### Initial Investigation
1. **Frontend Code Review**
   - Checked `CitationAwareText` component - correctly parses `[1]`, `[2]` patterns
   - Checked `useThreadSources` hook - only extracted sources from tool call results, not from SSE stream
   - Checked `SourcesPanel` - correctly displays sources when provided
   - Checked `ChatPanel` - correctly configured with `CitationAwareText` as text renderer

2. **Backend Code Review**
   - Checked adapter (`src/intelli/agents/adapters/__init__.py`) - converts LangGraph events to AI SDK format
   - Found that `_format_data_chunk` handles sources but only when explicitly passed
   - Checked `search_documents` tool - returns JSON string with source array
   - Found that adapter doesn't extract sources from tool results automatically

3. **Event Flow Analysis**
   - Backend sends `source-document` events via `_format_data_chunk` when sources are in node output
   - Frontend expects `source-document` parts in message content
   - AI SDK's `DefaultChatTransport` should convert SSE `source-document` events to message parts
   - Frontend hook only looked for tool call results, not `source-document` parts

## Changes Attempted

### Change 1: Frontend Hook Enhancement
**File**: `ui/src/hooks/use-thread-sources.ts`
- Added `isSourceDocumentPart` type guard
- Added logic to extract sources from `source-document` parts in addition to tool call results
- Extracts metadata from `providerMetadata.custom`

**Result**: Frontend now ready to receive sources from SSE stream

### Change 2: Backend Adapter Source Extraction
**File**: `src/intelli/agents/adapters/__init__.py`
- Added source extraction in `on_tool_end` handler for `search_documents` tool
- Parses JSON tool output and emits `source-document` events
- Emits `tool-output-available` first, then source events

**Result**: Backend now emits sources, but caused agent to end prematurely

### Change 3: Tool Enhancement
**File**: `src/intelli/agents/tools/research_tools.py`
- Added `chunk_index` to tool results

**Result**: More complete source metadata

### Change 4: Error Handling
**File**: `ui/src/pages/ResearchPage.tsx`
- Added error display for failed notebook loading

**Result**: Better UX for error cases

## What We Observed

### Before Changes
- Citations did not appear in messages
- Sources panel was empty
- No errors in console (silent failure)

### After Changes
- **Critical Issue**: Agent would complete tool call but then end without generating a response
- Tool calls executed successfully
- Sources were being emitted (verified in code)
- But agent flow stopped after tool completion

### Root Cause Hypothesis
The issue appears to be that:
1. The adapter is correctly converting LangGraph events to SSE format
2. Sources are being extracted and emitted
3. BUT: The agent's decision-making flow (LangGraph's `tools_condition`) may be affected by the event emission order or timing
4. OR: The AI SDK's `DefaultChatTransport` may be interpreting the source-document events as completion signals

## Technical Details

### Event Flow (Expected)
```
LangGraph ToolNode executes → on_tool_end event → 
Adapter emits tool-output-available → 
Adapter emits source-document events → 
LangGraph continues to agent node → 
Agent generates response with citations
```

### Event Flow (Observed After Changes)
```
LangGraph ToolNode executes → on_tool_end event → 
Adapter emits tool-output-available → 
Adapter emits source-document events → 
[STOPS HERE - agent doesn't continue]
```

### Key Files Involved
1. `src/intelli/agents/adapters/__init__.py` - Event conversion
2. `src/intelli/agents/graphs/research_assistant.py` - Agent graph definition
3. `ui/src/hooks/use-thread-sources.ts` - Source extraction
4. `ui/src/components/chat/CitationAwareText.tsx` - Citation rendering
5. `ui/src/providers/assistant-runtime.tsx` - AI SDK transport setup

## Next Steps / Recommendations

1. **Investigate LangGraph Event Flow**
   - Check if emitting source-document events interferes with LangGraph's state machine
   - Verify that tool results are properly added to state before emitting sources
   - Consider emitting sources in a different event handler (e.g., `on_chain_end`)

2. **Check AI SDK Behavior**
   - Verify that `source-document` events don't signal completion to the transport
   - Check if event ordering matters for AI SDK v3
   - Review AI SDK documentation for proper source-document event handling

3. **Alternative Approaches**
   - Consider emitting sources as part of the final message metadata instead of separate events
   - Use a different event type that doesn't interfere with agent flow
   - Extract sources from tool results on the frontend only (current approach, but needs tool results in message)

4. **Debugging Tools**
   - Add logging to see exact event sequence
   - Check LangGraph state after tool execution
   - Verify AI SDK message structure includes tool results

## Files Modified (All Reverted)
- `src/intelli/agents/adapters/__init__.py`
- `ui/src/hooks/use-thread-sources.ts`
- `src/intelli/agents/tools/research_tools.py`
- `ui/src/pages/ResearchPage.tsx`

## Current State
All changes have been reverted. System is back to original state where:
- Citations don't appear (original problem)
- Agent flow works correctly (no premature ending)
- Sources panel doesn't populate
