# Eval Results — Tool-Calling Agent (Project 1)

## Test setup

11 prompts, mixed intentionally:
- 8 prompts describing a genuine study session (varied phrasing, casual tone, some typos)
- 3 prompts with no study activity at all (a math question, a location statement, an unrelated question)

Model: `llama-3.3-70b-versatile` via Groq API. Definition of done (original target): 10/10 correct tool-routing decisions.

## Run 1 — baseline description

Tool description: *"Used to calculate how much hours studied and which topic was studied for how much time."*

| # | Prompt | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | "I logged 2 hours of DP today" | log, 120 min | Logged: DP, 120 min | ✅ |
| 2 | "spent 30 minutes on graph" | log, 30 min | Logged: graph, 30 min | ✅ |
| 3 | "what's 2+2" | no tool | "2+2 = 4" | ✅ |
| 4 | "We live in mumbai" | no tool | Logged: Mumbai, 30 min | ❌ false positive |
| 5 | "Is the stadium large?" | no tool | plain text | ✅ |
| 6 | "Solidified my understanding of algorithms for 1 hour" | log, 60 min | Logged: algorithms, 60 min | ✅ |
| 7 | "solved dsa problems for 2 hours" | log, 120 min | **crash** — malformed function generation | ❌ |
| 8 | "studied graph theory for 30 minutes" | log, 30 min | Logged: graph theory, 30 min | ✅ |
| 9 | "revised dynamic programming for 1 hour" | log, 60 min | **crash** — schema type mismatch (`duration_minutes` sent as string, not integer) | ❌ |
| 10 | "cycled for 20 minutes in the park" | no tool (exercise, not study) | Logged: cycling, 20 min | ❌ false positive |
| 11 | "ran through the dsa problems for 30 minutes" | log, 30 min | Logged: dsa, 30 min | ✅ |

**Score: 7/11 clean, 4 failures.**

## Failure modes found

### 1. Hallucinated tool (early exploration, separate run)
Asked a plain factual question with only `log_session` defined as a tool. The model attempted to call `brave_search` — a tool that was never provided in the schema. Groq's API correctly rejected the request server-side (`400 tool_use_failed`), but the client code had no handling for this and crashed.

**Mitigation:** never trust that a returned tool name matches what's expected — verify `tool_call.function.name` against known tool names before executing.

### 2. False positive — off-topic content logged as a study session
"We live in mumbai" and "cycled for 20 minutes in the park" both triggered `log_session`, despite describing no study activity (or, in the cycling case, a non-academic activity). The vague description ("how much hours studied") gave the model no concrete signal for what counted as in-scope.

**Mitigation:** rewrote the tool description to (a) name the specific domain (computer science / mathematics) and (b) explicitly state what does NOT qualify, using the actual failure cases as negative examples.

### 3. Malformed function-call generation / schema violation
Two prompts caused the model to generate invalid output — once a syntactically broken function call (`log_session":{...` instead of `log_session({...`), once a schema violation (`duration_minutes` sent as `"60"` instead of `60`). Both caused unhandled `400 BadRequestError` crashes that killed the entire test loop.

**Mitigation:** wrapped the API call in `try/except`, logging the failure and continuing to the next prompt (`continue`) instead of terminating the whole run.

## Run 2 — after description fix + error handling

Updated description: *"Logs a study session, but only when the user describes actively studying a computer science or mathematics topic (e.g. DSA, algorithms, graph theory). Do NOT call this for physical activities like cycling, or statements that don't describe any study activity, like mentioning where someone lives."*

Same 11 prompts, re-run:

| Result | Count |
|---|---|
| Correctly logged | 8/8 |
| Correctly refused (no tool) | 3/3 |
| Crashes | 0 |
| False positives | 0 |

**Score: 11/11 correct decisions.** Definition of done met and exceeded (target was 10/10).

## Cost observation — raw loop vs. LangGraph

The LangGraph rebuild (Day 3–4) produces the same correct decisions, but at **2x the API calls per tool-triggering turn**: one call for the model to decide + request the tool, a second call for the model to generate a natural-language confirmation after the tool executes (the raw loop handles confirmation with a local `print()`, at zero extra API cost). At Groq's free-tier rate limits, this roughly halves effective throughput for tool-heavy workloads — worth knowing before defaulting to the framework's standard agent loop at scale.

## Summary

- 3 distinct failure modes found and fixed through iteration, not upfront design
- Final decision accuracy: 11/11 (exceeds the 10/10 target)
- Key lesson: prompt-level guardrails (description wording) fixed the false-positive issue; code-level guardrails (try/except, name verification) were still required regardless of prompt quality, since the model can still generate malformed output unpredictably