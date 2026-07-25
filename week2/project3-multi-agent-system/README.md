# Project 3: Multi-Agent System (Router + Specialists)

## Overview

A multi-agent system built with LangGraph that routes incoming requests to one of three specialist agents — code, research, or data analysis — instead of relying on a single general-purpose agent. A router node classifies each request and hands it off via a conditional edge, with each specialist scoped to only the tools its job requires.

## Architecture

```
router → [conditional edge] → code specialist
                             → research specialist (Tavily-grounded search)
                             → data analysis specialist (calculate tool)
```

The router reads the user's message, classifies it into exactly one category, and passes the **original, unmodified message** through to whichever specialist handles it — the router never rewrites or summarizes the request itself, to avoid introducing a second point where meaning could be silently distorted before the specialist ever sees it.

## Design decisions

**Enum-constrained routing output.** The router's structured output uses a Python `Enum` (`SpecialistType`) instead of a plain string for the specialist field. A free-text field lets the model return anything close-but-not-exact (`"Code"`, `"coding_help"`), which would silently break routing with no error. The `Enum` makes invalid output fail loudly at validation instead of routing nowhere.

**Classify, don't rewrite.** Early in design, having the router "clean up" ambiguous requests before passing them to a specialist was considered and rejected — it adds a second LLM transformation step where meaning could be dropped or distorted, with no way to detect it downstream. The router only classifies.

**Least-privilege tooling.** Each specialist has access only to what its job needs: the code specialist has no search or execution access; the research specialist has search but no code execution; the data specialist has one narrow `calculate` tool, not a general code sandbox. This maps directly to OWASP's "excessive agency" mitigation for LLM agents.

**Text-only code specialist (v1).** The code specialist explains and writes code but does not execute it. Real execution (a sandboxed runner) is a deliberately deferred v2 enhancement, not an oversight — building the full router-to-specialist pipeline mattered more first.

**Narrow `calculate` tool over full execution.** For the data-analysis specialist, a full code-execution sandbox was considered but a single restricted-`eval()` tool was chosen instead. LLMs are known to make arithmetic errors reasoning through numbers as text, so real computation was necessary — but a narrow tool avoids the security surface of running arbitrary LLM-generated code.

## Connection to Project 2

Project 2's most significant finding was that, with no real search tool, the planning agent hallucinated confidently from model memory — producing three different, wrong descriptions of the same real framework across separate runs. Project 3's research specialist directly addresses this: it performs a live Tavily search before generating any answer, grounding the response in current, real information instead of frozen training data.

This also carried forward Project 2's "acknowledge gaps rather than hallucinate" prompting pattern. Tested against "what's the current inflation rate in Dubai?", the specialist retrieved real UAE-wide inflation data but explicitly stated it could not confirm a Dubai-specific figure, since the data it found didn't isolate the city — instead of blending the two into a falsely precise answer.

## Failure modes

### 1. Ambiguous classification at the code/data-analysis boundary

**Input:** *"Can you analyze this CSV and write a script to clean it?"*

**What happened:** The router classified this as `code`, reasoning it "requires coding and programming logic." The specialist returned a generic CSV-cleaning script template — not an actual analysis of any real data, since none was ever provided.

**Root cause:** The request genuinely straddles two categories. "Analyze" leans data-analysis, "write a script" leans code. The router resolves ambiguity deterministically by picking one, with no mechanism to recognize or act on compound intent.

**Mitigation:** Allow the router to return multiple specialists for compound requests and merge outputs, or have each specialist detect when a request needs a different specialist's capability and hand off. Not implemented in this version — documented as a known architectural limitation.

### 2. Prompt-induced invalid tool calls, masked by a second LLM call

**Input:** *"What's a good way to visualize sales data over time?"*

**What happened:** The router classified this as `data_analysis` (defensible — visualization is data-analysis-adjacent). The data specialist's prompt instructs the model to "always use the tool for calculations," which pushed the LLM to invoke `calculate` even though the request had no actual numbers. Logging `response.tool_calls` revealed the model invented two non-existent function calls — `stddev(sales_data)` and `trend_line(sales_data)` — referencing a variable that was never defined. Both would fail inside `calculate`'s `eval()` and return an error string. A second LLM call, with no instruction to surface tool failures, then produced a fluent, generic answer with no indication anything had failed underneath.

**Root cause (two distinct bugs):**
- The prompt over-constrains the model into calling the tool even when nothing needs calculating.
- The code only reads `response.tool_calls[0]` — the first tool call. Any additional tool call is silently discarded and never attempted, meaning the system can't currently handle a case where more than one calculation is genuinely needed.

**Mitigation:** Soften the prompt to "use the tool only when a genuine calculation is needed"; loop through all of `response.tool_calls` rather than only the first; and pass tool errors explicitly into the second LLM call so it can acknowledge a failed calculation instead of silently generating around it.

### 3. Router classification boundary — code vs. research

**Input:** *"What's the best Python library for scraping live stock prices?"*

**What happened:** The router chose `research`, reasoning that "best" depends on current, real-world state. Tavily search returned real current library names (YFinance, BeautifulSoup) but the specialist explicitly declined to pick one, stating the search results didn't clearly indicate a "best" option.

**Root cause:** This exposes a real tradeoff in the architecture: routing subjective "which tool is best" questions to `research` trades hallucination risk for a hedged, less decisive answer, since search results rarely state a definitive winner the way a confident (but potentially outdated) code-specialist answer would.

**Mitigation:** For this class of query, a hybrid path — research specialist gathers current options, then hands off to the code specialist to recommend and demonstrate one — would combine current facts with confident synthesis. Documented as a known limitation rather than solved in this version.

## Known limitations

- Code specialist is text-only; no execution/verification of generated code (planned v2)
- Data-analysis specialist only processes the first of multiple tool calls in a single turn
- No mechanism for compound requests spanning more than one specialist
- No persistence — each request is stateless across turns (no `MemorySaver`, unlike Project 2)

## Stack (100% free tier)

- **Groq API** (free tier) — router and specialist LLM calls
- **Tavily** (free tier, 1,000 credits/month) — live web search for the research specialist
- **LangGraph / LangChain** — orchestration, open source

## Repo structure

```
project3-multi-agent-system/
  main.py                 # graph assembly, entry point
  state.py                # shared state schema (RouterState, SpecialistType)
  nodes/
    router.py              # classification + conditional routing
    code_specialist.py
    research_specialist.py
    data_analysis_specialist.py
  README.md
```

