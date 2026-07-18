# Project 1 — Tool-Calling Agent (Study Tracker)

A minimal agent that logs study sessions from natural language ("I studied arrays for 45 minutes") using LLM function calling — built twice: once as a raw request loop against the Groq API directly, once rebuilt in LangGraph, to see exactly what the framework abstracts away.

## Why this exists

Before touching any agent framework, the goal was to understand the actual mechanism behind "AI agents": a model can't take action on its own — it can only ask, via a structured tool-call request, for your code to run something on its behalf. Everything else (LangGraph, LangChain, MCP) is a layer of convenience on top of that one loop.

## Structure

```
project1-tool-calling-agent/
├── raw_loop/
│   └── test_groq.py          # hand-written request → tool-call → execute → respond loop
├── langgraph_version/
│   └── test_lg.py            # same agent, rebuilt as a LangGraph StateGraph
├── sessions.json             # shared local storage — flat JSON, list of {topic, duration_minutes, date}
└── eval_results.md           # full test log, failure modes found, and fixes
```

## How it works

**Tool:** `log_session(topic: str, duration_minutes: int)` — the only tool the agent has. `date` is deliberately **not** a model-provided field; it's stamped by the code itself via `datetime.now()`, after an early test showed the model would fill an optional date field with unusable placeholder text (`"today"`) rather than a real date. This was the first concrete lesson of the project: prefer code-level correctness over prompt-level hoping, whenever a value can be computed instead of guessed.

**Raw loop (`raw_loop/test_groq.py`):**
1. Send the user message + tool schema to Groq
2. Check `response.choices[0].message.tool_calls`
3. If present and the name matches `log_session`, parse the JSON arguments and execute the function directly
4. If absent, print the model's plain-text response
5. Wrapped in `try/except` — the model occasionally generates malformed tool-call syntax or violates its own schema (see `eval_results.md`), and the loop needs to survive that without crashing

**LangGraph version (`langgraph_version/test_lg.py`):**
- Same tool, redefined with the `@tool` decorator (auto-generates the schema from the function's name, docstring, and type hints — no hand-written JSON dictionary)
- Two-node graph: `agent` (reasoning, via `llm_with_tools.invoke(...)`) and `tools` (acting, via the prebuilt `ToolNode`)
- A `should_continue` routing function replaces the raw loop's inline `if tool_calls:` check, deciding whether to route to `tools` or to `END`
- `tools → agent` loops back after execution, giving the model a chance to generate a natural-language confirmation or handle a multi-step request — this is the one piece of behavior the raw loop didn't have by default

## What building both versions revealed

- **LangGraph doesn't add new capability here — it formalizes bookkeeping you'd otherwise do by hand.** Message-history management, tool-name routing, and argument parsing (raw JSON strings vs. LangChain's already-parsed dicts) are all things the raw loop required writing manually.
- **The convenience has a real cost.** LangGraph's default agent loop makes a second API call after every tool execution, to generate a friendly confirmation message. The raw loop confirms locally via `print()` at zero extra cost. At Groq's free-tier rate limits, this is a genuine 2x throughput difference for tool-heavy workloads — a tradeoff worth knowing rather than defaulting into blindly.
- **No amount of schema or prompt engineering fully eliminates model unreliability.** Even after tightening the tool description to fix false positives, the model still occasionally generated malformed function-call syntax or violated its own declared schema. Code-level guardrails (`try/except`, explicit tool-name verification before execution) are non-negotiable regardless of prompt quality.

Full test log and all three documented failure modes: see [`eval_results.md`](./eval_results.md).

## Running it

```bash
cd raw_loop && python test_groq.py
# or
cd langgraph_version && python test_lg.py
```

Both require `GROQ_API_KEY` set as an environment variable, and both read/write the shared `sessions.json` one directory up.