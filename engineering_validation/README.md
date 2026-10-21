# DeepSeek compatibility validation — layered tests A–F

Scope: these scripts only touch environment variables inside their own subprocess (via
`env VAR=val python script.py` or an explicit env dict passed to the SDK client). None of
them export anything into this shell's persistent profile or into this engineering
assistant's own Claude Code configuration. The reproduced system's credential comes from
`DEEPSEEK_API_KEY`, read from the shell env or this repo's own `.env` (already gitignored).
`_common.py` only checks existence — never prints, logs, or persists the value.

## Status (2026-10-19)

| Step | Script | Result | Notes |
|---|---|---|---|
| A | `test_A_basic_api.py` | PASS (exit 0) | `response.model` echoes the requested id unchanged — not proof of what actually ran underneath; see caveat below. |
| B | `test_B_tool_loop.py` | PASS (exit 0) | Tool call round-trip verified: fixed value echoed verbatim in final answer. |
| C/D | `test_CD_sdk_delegation_review.py` | PASS (exit 0) | First attempt failed (exit 1, `TypeError: Object of type FastMCP is not JSON serializable` — fixed by switching to `claude_agent_sdk.tool()`/`create_sdk_mcp_server()`). Full delegate → independent review → gap found → re-delegate → corrected answer loop confirmed via transcript. |
| E | `test_E_local_mcp.py` | PASS (exit 0) | **Real MCP server independently callable** — no model/agent involved, direct MCP client call only. |
| E2 | `test_E2_agent_real_mcp.py` | PASS (exit 0) | **DeepSeek-routed agent calls the real MCP server and uses the result** — closes the gap E leaves open. Agent's reported numbers cross-checked exact match against an independent ground-truth MCP call. |
| F | `test_F_model_audit.py` | PASS (exit 0) | Specialist (`claude-sonnet-4-5-20250929`) and reviewer (`claude-haiku-4-5-20251001`) ids confirmed distinct per request. Per DeepSeek's documented mapping both fall in the same `deepseek-flash` bucket — **the paper's two-tier model split is not preserved by default**. This is a documented-mapping inference, not something directly observable from the response field (see A's caveat). |

## Run order

- `test_A_basic_api.py` — one bare `anthropic` SDK call against the DeepSeek base_url, model
  id `claude-sonnet-4-5-20250929` (the literal id this repo uses for specialists). Records
  the request model id and the response's `model` field side by side.
- `test_B_tool_loop.py` — same, with one no-side-effect tool (`get_server_time`, fixed string,
  no filesystem/network effect) to confirm `tool_use` → `tool_result` round trip.
- `test_CD_sdk_delegation_review.py` — uses `claude_agent_sdk` (not bare `anthropic`) to build
  a minimal two-tier setup mirroring this repo's actual CSO/specialist/reviewer split:
  orchestrator delegates to a `specialist` (deliberately incomplete answer), then to a
  `reviewer` (Haiku-tier id) which must flag the gap, then re-delegates with feedback.
- `test_E_local_mcp.py` — launches this repo's real `src/mcp_servers/single_cell_mcp/server.py`
  as a local stdio subprocess (same shape `setup_mcp.py` writes into `mcp_config.json`) and
  calls `get_census_info()` directly via an MCP client — no model in the loop.
- `test_E2_agent_real_mcp.py` — same real server, but now a DeepSeek-routed `claude_agent_sdk`
  agent calls it as part of its own tool loop and must report the real numbers; those numbers
  are cross-checked against an independent direct call.
- `test_F_model_audit.py` — not a new call; parses the saved JSON logs from A/C-D and reports,
  per role, what model was requested vs. what the response claims actually ran.

## Important caveat carried through every step

`response.model` in every DeepSeek Anthropic-compatible reply so far has echoed the
**requested** id unchanged (e.g. `claude-sonnet-4-5-20250929`), not a DeepSeek-native name
like `deepseek-flash`. Per DeepSeek's own docs (`../docs/deepseek_anthropic_api.md`) the
server-side remap to `deepseek-flash`/`deepseek-v4-pro` happens regardless, but the API does
not disclose this in the response — only DeepSeek's own account/usage dashboard would, and
that is out of scope here (it would require the user's account access, not something this
assistant should request or access). So: every "requested X" in these logs should be read as
exactly that — a request — not as proof of what executed underneath.

## Role-routing check (no unauthorized model calls)

Confirmed no global `ANTHROPIC_API_KEY`/`ANTHROPIC_BASE_URL` is set in this shell outside of
what these scripts explicitly inject per-subprocess — so there is no path by which any of
these calls could have silently fallen back to a real Anthropic endpoint instead of
DeepSeek's. The credential itself was never read, printed, or logged.
