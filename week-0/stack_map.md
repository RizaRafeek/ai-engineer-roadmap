## Stack Map

### Foundation Models
- **Claude**: Anthropic's proprietary models (Sonnet, Haiku, etc.) — no public weights
- **Perplexity**: Possibly selectable (Claude, GPT, or similar) — proprietary
- **NotebookLM**: Google's Gemini models (likely Flash variant) — first-party Google product
- **Copilot**: Multiple options available (GPT, Claude, etc.) — proprietary, user-selectable in some configurations
- **Chatbots (general)**: Unknown — likely not even a generative model for basic search features

### Retrieval Layer
- **Perplexity**: RAG, live open-web search, ~10 visible citations per answer
- **NotebookLM**: RAG, tightly scoped to user-provided sources by default; offers to search the web but requires manual approval/import before using new sources
- **Claude**: Uncertain/unconfirmed — no citations observed in my usage, though live search is known to exist generally
- **Copilot**: No evidence of RAG — no citations observed, likely a well-prompted single call
- **Chatbots (general)**: Keyword/context-based search over a help-article knowledge base — RAG-adjacent at best, possibly not AI-based at all

The most reliable signal for RAG has been direct, observable evidence — explicit citations (Perplexity) or the model stating it can't answer and offering to search (NotebookLM). "Feels current" isn't reliable on its own, since a model can seem up-to-date purely from its training cutoff with no live retrieval involved. RAG also isn't one uniform pattern — Perplexity's default open-web retrieval and NotebookLM's scoped, user-gated retrieval are architecturally different approaches to the same broad category.

### Orchestration Layer
- **Claude**: Decides whether to ask clarifying questions, give a multi-step explanation, or invoke tools (like file creation) based on the task
- **Perplexity**: Fairly lightweight/single-pass — retrieve once, generate once — plus a UX layer suggesting follow-ups
- **NotebookLM**: Multi-step, visible decision flow — refuses out-of-scope questions, offers to search, waits for approval, shows candidate sources before importing
- **Copilot**: Light orchestration around ambiguity resolution — asks clarifying questions when multiple solutions are possible before proceeding
- **Chatbots (general)**: None observed — single-pass search-and-list regardless of who's asking or what they need

The presence and depth of orchestration mattered most for whether a product felt "smart" versus "generic." Generic search-based chatbots had essentially no orchestration and felt the most generic. In contrast, Claude, NotebookLM, and even simple-LLM-call Copilot all showed orchestration behavior and felt noticeably smarter — even though their underlying retrieval and foundation-model setups were quite different.

### Application Layer
- **Claude**: Chat text or actual generated files (documents, presentations) depending on the request
- **Perplexity**: Text-based chat answers with inline citation markers
- **NotebookLM**: Text answers or requested formats (notes, summaries)
- **Copilot**: Step-by-step text instructions in a chat panel — never executes actions itself, user performs every step
- **Chatbots (general)**: Simple list of matching article links and short descriptions

### Synthesis
Across all 5 products, raw model quality or retrieval sophistication alone didn't create the "smart" impression — orchestration did. Whether a product adapted its behavior to the specific situation (asking clarifying questions, gating retrieval behind approval, choosing between a text answer and a generated file) mattered more than which foundation model sat underneath or how good its retrieval was in isolation. The clearest lesson: two products can have similar retrieval quality and still feel completely different in "intelligence" based purely on how much their orchestration layer adapts versus stays fixed.