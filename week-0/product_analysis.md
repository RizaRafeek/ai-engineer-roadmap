Claude appears to be agentic in at least some of my usage, since it produced actual files (like presentations or documents) rather than just chat text — indicating it invokes tools beyond plain text generation. Claude is proprietary — Anthropic never releases its model weights publicly, so the only way to use Claude is through their API/interface, unlike open-source models like Llama that you can download and run yourself. I'm not fully certain Claude's answers are genuinely real-time, since I never saw an explicit citation or a visible "searching the web" step — it's possible the model's training cutoff is just recent enough to feel current without actually performing live retrieval. Overall, Claude's file-generation behavior is the clearest architectural signal I observed; the retrieval question would need a test with a clearly time-sensitive query to confirm.

Most AI products aren't training their own foundation model. They're combining someone else's model (via API) with their own custom logic — search, retrieval, UI, tool integrations. That combination is the product's real intellectual property, even though the core "brain" is licensed from elsewhere

Perplexity appears to be RAG-based, evidenced clearly by the ~10 citations it attaches to answers, showing it retrieves and grounds its responses in real sources rather than answering purely from memorized training data. The underlying foundation model is likely proprietary — probably GPT and/or Claude accessed via API — but that model isn't something Perplexity itself trained or owns; Perplexity's actual product and IP is the retrieval and citation layer it built around someone else's model. The retrieval layer appears to search the live web given how current and citation-heavy the answers feel, though I confirmed it lacks file-generation tools (unlike Claude), which sharpened the RAG-vs-agentic distinction for me.

NotebookLM is RAG-based, evidenced by its explicit refusal to answer questions outside the provided source material, and further confirmed by its retrieval mechanism: when I asked something out-of-scope, it offered to search the web but required me to manually approve and import specific sources before using them to answer — a more tightly scoped and user-gated retrieval flow than Perplexity's fully automatic citation-based search. This is a proprietary model, and since NotebookLM is a first-party Google product, the underlying model is very likely Gemini (probably a Flash variant, optimized for the fast, grounded Q&A the product needs) rather than a licensed third-party model. This case sharpened an important nuance: RAG isn't one uniform pattern — NotebookLM's retrieval is tightly scoped and requires explicit user approval to expand, in contrast to Perplexity's default open-web retrieval.


Checkpoint — Day 2 (Claude, Perplexity, NotebookLM)
The most reliable RAG signal has been direct, observable evidence — explicit citations (Perplexity) or the model stating it can't answer from its source and offering to search (NotebookLM). "Feels current" isn't reliable, since a model can seem up-to-date purely from its training cutoff, with no live retrieval involved.
The biggest surprise was catching my own reasoning error: after labeling Claude agentic (file generation), I assumed Perplexity was too — until checking an actual memory showed Perplexity can't generate files, correcting it to RAG. This showed architecture conclusions need fresh evidence per product, not carryover from the last one. I also learned RAG isn't one pattern — Perplexity retrieves from the open web by default, while NotebookLM stays scoped to user-provided sources unless explicitly approved to search further.

Copilot Chat appears to be a single well-structured LLM call, not RAG (no citations or external source references observed) and not agentic (it gives instructions and guidance but never edits files or executes tasks on its own — I remained the one performing every action). The interface displayed "Claude Haiku" at some point during use, suggesting Copilot may use Anthropic's Claude models for at least some requests, though I couldn't confirm this via an explicit model-selection setting. Compared to Claude directly, Copilot is architecturally simpler in behavior despite feeling capable — Claude actually executes tasks (generating downloadable files), while Copilot only ever advises, leaving execution entirely to me.

Based on general product-design incentives, I'd hypothesize most in-house customer support chatbots are either simple LLM calls or basic RAG (retrieving from a FAQ/policy knowledge base) rather than agentic — cost and risk both favor this: agentic systems that can autonomously take actions (refunds, cancellations) are expensive to run at scale and risky if they make mistakes, whereas most support queries (order status, return windows) are repetitive lookups well-suited to RAG without needing multi-step autonomous reasoning.

Claude:

Foundation model: Claude models (Sonnet, Haiku, etc.) — Anthropic's proprietary models
Retrieval: Uncertain/unconfirmed — no citations observed, though live search capability is known to exist generally
Orchestration: Decides whether to ask clarifying questions, follow a multi-step explanation, or invoke tools (like file creation) based on the task
Application: Delivers output as chat text or as actual files (documents, presentations) depending on what was requested

Perplexity:

Foundation model: Possibly selectable (Claude, GPT, or similar) — proprietary
Retrieval: RAG, live web search, with visible citations
Orchestration: Appears fairly lightweight/single-pass — retrieve once, generate once — plus a UX layer suggesting follow-up questions
Application: Text-based chat answers with inline citation markers

NotebookLM:

Foundation model: Google's Gemini models (likely Flash variant)
Retrieval: RAG, tightly scoped to user-provided source material by default
Orchestration: Multi-step, visible decision flow — refuses out-of-scope questions, offers to search the web, waits for user approval, shows candidate sources, requires manual import before using them to answer
Application: Delivers output as text answers or in requested formats (notes, summaries)

Copilot:

Foundation model: Multiple options available (GPT, Claude, etc.) — proprietary, user-selectable in some configurations
Retrieval: No evidence of RAG — no citations observed, likely a well-prompted single call
Orchestration: Asks clarifying questions when multiple solutions are possible before proceeding — light orchestration around ambiguity resolution
Application: Delivers step-by-step text instructions in a chat panel; does not execute actions itself — user must perform every step manually

Amazon Help:

Foundation model: Unknown — no direct evidence, likely not even using a generative model at all for this specific search feature (this might just be traditional keyword/semantic search, not an LLM-based system)
Retrieval: Keyword/context-based search over a help-article knowledge base — arguably RAG-adjacent, but possibly not even AI-based, just traditional search
Orchestration: None observed — single-pass search-and-list, no multi-step behavior, no clarifying questions, no generated synthesis
Application: Simple text list of matching article links and short descriptions

The presence and depth of the orchestration layer mattered most for whether a product felt "smart" versus "generic." Amazon Help had essentially no orchestration — same fixed search-and-list behavior regardless of who asked or what they actually needed — and felt the most generic of the five. In contrast, Claude, NotebookLM, and even simple-LLM-call Copilot all showed orchestration behavior — asking clarifying questions, waiting for approval before expanding retrieval, deciding whether a task needed a tool (like file creation) versus a plain text answer — and all three felt noticeably smarter, even though their underlying retrieval and foundation-model setups were quite different. This suggests raw model quality or even accuracy isn't what creates the "smart" impression on its own — it's whether the product adapts its behavior to the specific situation in front of it, rather than doing the same fixed thing every time.

