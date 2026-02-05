export interface TourStep {
  id: string
  route: string
  title: string
  commentary: string
  feedbackPrompt: string
}

export const TOUR_STEPS: TourStep[] = [
  {
    id: 'overview',
    route: '/overview',
    title: 'Welcome to Intelli',
    commentary: `### The module layout

Intelli is built as a **modular intelligence platform**. Each card on this page represents a capability module — some are live (**Now**), some are next, and others are planned.

The architecture follows a **backbone pattern**: a shared data layer (pointers → manifests → artifacts) underpins every module. This means research outputs can flow into analysis, which feeds decisions — all with full provenance.

**Key concept:** Everything is versioned. Every document, every query result, every workflow output gets a content-addressed SHA256 and an immutable audit trail.`,
    feedbackPrompt: 'Does the module layout make sense? Any modules missing for your workflow?',
  },
  {
    id: 'docs-list',
    route: '/docs',
    title: 'Doc Intelligence — Notebooks',
    commentary: `### Versioned notebooks

Each row here is a **pointer** — a named, versioned reference to a collection of documents. Think of it like a git branch that points to a manifest (a tree of artifacts).

The data model is:
- **Pointer** → names a collection (e.g. "Q4 Research")
- **Manifest** → a snapshot of the collection's contents at a point in time
- **Artifacts** → the actual files (PDFs, CSVs, etc.), stored by SHA256

When you upload a new version, a new manifest is created and the pointer advances — but the old version is never lost.`,
    feedbackPrompt: 'Is the pointer/manifest/artifact model clear? What would help you understand it better?',
  },
  {
    id: 'docs-notebook',
    route: '/docs/demo-1',
    title: 'Doc Intelligence — Notebook View',
    commentary: `### Upload, index, ask

This is where you interact with a single notebook. The workflow is:

1. **Upload** documents into the notebook
2. **Index** them — this creates embeddings for semantic search
3. **Ask** questions — the RAG pipeline retrieves relevant chunks and generates cited answers

Every question-answer pair is recorded as a **run** with full provenance: which model, which chunks were retrieved, what the scores were.

The citations link back to specific artifact chunks, so you can always verify the source.`,
    feedbackPrompt: 'How does the upload → index → ask workflow feel? What would you change?',
  },
  {
    id: 'research',
    route: '/research',
    title: 'Research Assistant',
    commentary: `### Streaming agent chat

The Research module provides a conversational interface backed by your indexed documents. Unlike simple RAG, this uses an **agent loop** — the model can decide to search multiple times, refine its query, or synthesize across sources.

Responses stream in real-time via SSE (Server-Sent Events). Each message is associated with a run, so the full conversation history and tool calls are auditable.

**Coming next:** Multi-step research plans where the agent breaks down complex questions into sub-tasks.`,
    feedbackPrompt: 'What types of research questions would you most want to ask? Any missing capabilities?',
  },
  {
    id: 'analysis',
    route: '/analysis',
    title: 'Analysis Intelligence',
    commentary: `### Coming next: DAG workflows

This module will support **repeatable analysis workflows** — think of them as directed acyclic graphs (DAGs) where each node is a processing step.

Planned capabilities:
- **Entity extraction** from documents
- **Relationship mapping** between entities
- **Comparative analysis** across document sets
- **Custom workflow templates** you can save and re-run

Each workflow execution becomes a run with input/output manifests, making results fully reproducible.`,
    feedbackPrompt: 'What analysis workflows would be most valuable for your work?',
  },
  {
    id: 'tour-complete',
    route: '/overview',
    title: 'Tour Complete',
    commentary: `### Thank you for taking the tour!

You've seen the core of Intelli:
- **Overview** — the module dashboard
- **Doc Intelligence** — versioned notebooks with RAG
- **Research Assistant** — agent-powered Q&A
- **Analysis** — upcoming workflow engine

The platform is designed to grow module by module while keeping everything connected through the shared data backbone.

Your feedback helps shape what gets built next. Use the form below to share any overall thoughts.`,
    feedbackPrompt: 'Overall impressions? What would make you want to use this daily?',
  },
]
