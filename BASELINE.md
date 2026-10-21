# Baseline: the system under reproduction

**Original repository:** https://github.com/harrisongzhang/TheVirtualBiotech
**Baseline commit:** `71f9da68c95c5ee0ef4c1d9b8f45f10693de022d` (HEAD at the
time this reproduction started; the paper's own commit/data-availability
statement could not be independently confirmed from the bioRxiv/PMC text —
this is a *method reconstruction* against the current repo state, not a
verified byte-for-byte replay of the paper's original run).

**Claimed paper:** "The Virtual Biotech: A Multi-Agent AI Framework for
Therapeutic Discovery and Development" (bioRxiv DOI
10.64898/2026.02.23.707551).

## Code modifications made for this reproduction

**None, to the original repository's source.** Zero diffs against commit
`71f9da68c95c5ee0ef4c1d9b8f45f10693de022d`.

The only intervention is a runtime wrapper script,
[`run/config/run_b7h3_formal.py`](run/config/run_b7h3_formal.py), run as a
separate process that:

1. Sets `ANTHROPIC_BASE_URL` / `ANTHROPIC_API_KEY` in its own subprocess
   environment only (DeepSeek's Anthropic-API-compatible endpoint), to
   route the unmodified `claude_agent_sdk` calls through DeepSeek instead of
   Anthropic. See `engineering_validation/` for the layered tests (A–F, E2)
   that verified this works with the SDK unmodified before this run.
2. Monkeypatches `claude_agent_sdk.ClaudeAgentOptions` at the Python level —
   not the repo's source files — to strip `WebFetch`/`WebSearch` from the
   CSO's and every specialist's tool list, per the requested study design
   (no general web search; database MCP servers only). The original repo
   hardcodes these two tools into `gradio_cso_app.py`'s `allowed_tools` and
   into most specialists' tool lists in `src/agents/registry.py`; there is
   no built-in flag for this, so it is done by intercepting the
   `ClaudeAgentOptions` constructor call instead of editing those files.
3. Calls the repo's own, completely unmodified `run_vbt.py:_run_turns()` —
   the same function the repo's official headless entry point
   (`python run_vbt.py run "<query>"`) uses. This is not a reimplementation
   of the runner.

Both points (1) and (2) are visible by reading the ~100-line script in full.

## What this reproduction required locally

- Open Targets 25.09 reference archive (3508 Parquet files, ~29GB) — an
  unconditional startup gate of the formal entry point
  (`require_reference_data()`), not a B7-H3-specific dependency. Downloaded
  with the original repo's own `tools/download_open_targets.py`, verified
  with `tools/doctor.py --skip-api-key`. Not included in this repo (see
  `data_provenance.md`).
- DeepSeek API credential, provided by the user directly into the original
  repo's own `.env` (never read/printed/logged by the reproduction tooling;
  existence-only checks).
- conda env `vbt` per the original repo's `environment.yml`.

## Engineering validation performed before the real run

See [`engineering_validation/README.md`](engineering_validation/README.md)
for the full layered test record (A: basic DeepSeek API call, B: tool-use
loop, C/D: SDK multi-agent delegation + review loopback, E: real local MCP
server called directly, E2: real local MCP server called by a DeepSeek-routed
agent, F: model-routing audit). All passed before the B7-H3 run below was
attempted.
