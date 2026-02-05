"""Research Assistant LangGraph agent.

An agentic assistant that uses tools to search documents, list notebooks,
and compare manifest versions.  The LLM decides when to call tools vs
respond directly, enabling multi-step reasoning.

Per ADR-005, this uses LangGraph for orchestration while the platform
kernel (run ledger, artifacts) remains the authoritative record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated
from uuid import UUID

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.agents.tools.research_tools import build_research_tools
from intelli.config import settings
from intelli.services.knowledge.rag_service import RagService, RetrievedChunk
from intelli.services.runs.ledger_service import LedgerService


@dataclass
class ResearchState:
    """State for the research assistant graph."""

    messages: Annotated[list[BaseMessage], add_messages] = field(default_factory=list)
    context_pointer_id: str | None = None
    manifest_sha256: str | None = None
    sources: list[dict] = field(default_factory=list)
    error: str | None = None
    run_id: UUID | None = None


SYSTEM_PROMPT = """You are a research assistant that analyzes documents by using tools. \
Act first, explain after.

Tools available:
- search_documents: Search uploaded documents for relevant content
- list_notebooks: List notebooks the user can access
- get_document_info: Get metadata about a specific document
- compare_manifests: Compare two versions of a notebook

Rules:
1. ALWAYS call search_documents before answering any question about document content. \
Do not answer from memory or ask the user to clarify — search first, then respond. \
Exceptions: for greetings respond directly without tools; for listing notebooks use list_notebooks; \
for comparing versions use compare_manifests.
2. Pass manifest_sha256 from context below when calling search_documents.
3. If the first search is insufficient, call search_documents again with a different query. \
Repeat until you have enough evidence, up to 3 searches.
4. When the user asks you to produce an output (glossary, summary, table, etc.), \
produce it immediately after searching. Do not ask which format — pick the most useful one.
5. Be direct and concise. Never list your capabilities unless explicitly asked. \
For greetings, respond warmly and briefly — do NOT call any tools.
6. End with a confidence note (High/Medium/Low) only when the evidence is ambiguous.

## Citation Format
When citing sources from search_documents results:
- Use numbered citations [1], [2], [3] inline with your text
- Each citation number corresponds to the order sources appear in search results
- ALWAYS cite when quoting or paraphrasing document content
- Multiple sources for one claim: "The lease term is 5 years [1][2]"
- Single source: "According to the agreement [1], the deposit is..."

## Citation Examples
GOOD: "The tenant must provide 30 days notice [1] before terminating the lease."
BAD: "The tenant must provide 30 days notice before terminating the lease." (no citation)
BAD: "According to source 1, the tenant..." (use [1] format, not "source 1")

## Tool Usage
When using search_documents:
- Search BEFORE answering questions about document content
- Use specific, targeted queries (not vague)
- If first search doesn't find relevant info, try different keywords
- Maximum 3 search attempts per question

Current context:
- manifest_sha256: {manifest_sha256}"""


def _format_sources(sources: list[dict]) -> str:
    """Format retrieved sources for the LLM context."""
    if not sources:
        return "No sources available."

    formatted = []
    for i, source in enumerate(sources, start=1):
        path = source.get("path_hint") or source.get("artifact_sha256", "unknown")[:12]
        content = source.get("content", "")
        score = source.get("score", 0)
        formatted.append(f"[{i}] {path} (relevance: {score:.2f})\n{content}")

    return "\n\n".join(formatted)


def _chunks_to_dicts(chunks: list[RetrievedChunk]) -> list[dict]:
    """Convert RetrievedChunk objects to serializable dicts."""
    return [
        {
            "chunk_id": str(chunk.chunk_id),
            "artifact_sha256": chunk.artifact_sha256,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "score": chunk.score,
            "path_hint": chunk.path_hint,
        }
        for chunk in chunks
    ]


class ResearchAssistantGraph:
    """Research assistant using LangGraph for orchestration."""

    def __init__(
        self,
        session: AsyncSession,
        ledger: LedgerService | None = None,
        checkpointer=None,
    ):
        self.session = session
        self.ledger = ledger
        self.rag_service = RagService(session)
        self.tools = build_research_tools(session)
        self._llm = self._build_llm()
        self._graph = self._build_graph(checkpointer=checkpointer)

    def _get_llm(self) -> ChatOpenAI:
        """Get the cached LLM client (created once per graph instance)."""
        return self._llm

    def _build_llm(self) -> ChatOpenAI:
        """Build the ChatOpenAI instance from settings."""
        kwargs: dict = {
            "model": settings.chat_model,
            "api_key": settings.openai_api_key,
            "streaming": True,
            "temperature": settings.chat_model_temperature,
            "max_tokens": settings.chat_model_max_tokens,
        }
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url

        # Reasoning model support (o1, o3, o4-mini)
        if settings.chat_model_reasoning_effort:
            kwargs["model_kwargs"] = {
                "reasoning_effort": settings.chat_model_reasoning_effort,
            }

        return ChatOpenAI(**kwargs)

    def _build_graph(self, checkpointer=None) -> StateGraph:
        """Build the LangGraph state graph with an agentic tool-use loop.

        Architecture:
            agent ──(tools_condition)──► tools ──► agent  (loop)
              │
              └──(END condition)──► END

        The agent node sends messages + system prompt to the LLM.  The LLM
        decides whether to call a tool or respond directly.  If it calls
        a tool, the ToolNode executes it, and control returns to the agent
        for another round.
        """
        graph = StateGraph(ResearchState)

        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(self.tools))

        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")

        return graph.compile(checkpointer=checkpointer)

    async def _agent_node(self, state: ResearchState) -> dict:
        """LLM agent node: decides whether to answer or use a tool."""
        system_content = SYSTEM_PROMPT.format(
            manifest_sha256=state.manifest_sha256 or "not set",
        )

        # Build message list: system prompt + conversation history
        llm_messages = [SystemMessage(content=system_content)] + list(state.messages)

        llm = self._get_llm().bind_tools(self.tools)
        response = await llm.ainvoke(llm_messages)

        return {"messages": [response]}

    async def ainvoke(self, state: ResearchState) -> ResearchState:
        """Invoke the graph synchronously (returns final state)."""
        result = await self._graph.ainvoke(state)
        return ResearchState(**result)

    async def astream(self, state: ResearchState):
        """Stream graph execution events."""
        async for event in self._graph.astream(state, stream_mode="updates"):
            yield event

    async def astream_events(self, state: ResearchState, config: dict | None = None):
        """Stream detailed events including LLM tokens.

        Args:
            state: Initial graph state.
            config: LangGraph config dict. Must include {"configurable": {"thread_id": ...}}
                    for checkpointer-backed multi-turn conversations.
        """
        async for event in self._graph.astream_events(state, version="v2", config=config):
            yield event


async def create_research_assistant(
    session: AsyncSession,
    ledger: LedgerService | None = None,
    checkpointer=None,
) -> ResearchAssistantGraph:
    """Factory function to create a research assistant graph."""
    return ResearchAssistantGraph(session=session, ledger=ledger, checkpointer=checkpointer)
