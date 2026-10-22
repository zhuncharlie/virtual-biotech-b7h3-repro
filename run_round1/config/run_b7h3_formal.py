"""Formal B7-H3 lung-cancer (LUAD + SCLC) case-study run through the repo's
REAL entry point (reuses CSOSession from gradio_cso_app.py, exactly as
run_vbt.py does) -- this does not answer the science itself, it asks the
actual Virtual Biotech system to.

Two deliberate deviations from the plain repo default, both requested by
the user and applied WITHOUT editing the repo's own source:

1. Disease scope is stated explicitly in the query (LUAD + SCLC), so the
   CSO does not have to guess or default to a broader "lung cancer" framing
   (the previous validation-only run used a generic framing and the CSO
   proceeded under NSCLC+SCLC, not LUAD+SCLC).

2. WebSearch / WebFetch are stripped from every role (CSO + all
   specialists) at construction time via a monkeypatch of
   claude_agent_sdk.ClaudeAgentOptions, per the user's instruction to match
   the paper's reported setting of disabling general web search/scraping
   and keeping only the curated database MCP servers. The repo has no
   built-in flag for this -- WebFetch/WebSearch are hardcoded into
   gradio_cso_app.py's allowed_tools list and into most specialists' tool
   lists in src/agents/registry.py -- so this is done by intercepting the
   ClaudeAgentOptions call before construction, not by editing those files.

Spatial transcriptomics / Visium is still out of scope for this pass (per
earlier agreement), stated in the query text.

Everything else (CSO delegation, real specialist roster, real MCP servers,
provenance plan/claims, run directory/audit artifacts) is the repo's own,
unmodified behavior.
"""
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "TheVirtualBiotech"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/anthropic"
OPEN_TARGETS_DATA_PATH = "/mnt/beegfs/xqinag/data/open_targets_25.09"
STRIPPED_TOOLS = ("WebFetch", "WebSearch")

QUERY = (
    "Evaluate the therapeutic candidacy of B7-H3 (CD276) in lung cancer. "
    "Scope the disease strictly to lung adenocarcinoma (LUAD) and small cell "
    "lung cancer (SCLC) -- not NSCLC broadly, not other lung histologies. "
    "General web search and web scraping are disabled for this study; use "
    "only the configured database MCP servers (Open Targets, CELLxGENE "
    "Census, etc.) and your own prior knowledge, clearly labeled as such "
    "when you rely on it. Spatial transcriptomics / Visium analysis is out "
    "of scope for this pass."
)


def _install_tool_stripping_patch():
    import claude_agent_sdk

    original_options = claude_agent_sdk.ClaudeAgentOptions

    def patched_options(*args, **kwargs):
        allowed = kwargs.get("allowed_tools")
        if allowed:
            kwargs["allowed_tools"] = [t for t in allowed if t not in STRIPPED_TOOLS]
        agents = kwargs.get("agents")
        if agents:
            for agent_def in agents.values():
                if getattr(agent_def, "tools", None):
                    agent_def.tools = [t for t in agent_def.tools if t not in STRIPPED_TOOLS]
        return original_options(*args, **kwargs)

    claude_agent_sdk.ClaudeAgentOptions = patched_options


def _load_deepseek_key() -> str:
    for line in (REPO_ROOT / ".env").read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("DEEPSEEK_API_KEY not found in .env")


async def main() -> int:
    key = _load_deepseek_key()
    os.environ["ANTHROPIC_BASE_URL"] = DEEPSEEK_BASE_URL
    os.environ["ANTHROPIC_API_KEY"] = key
    os.environ["OPEN_TARGETS_DATA_PATH"] = OPEN_TARGETS_DATA_PATH
    del key

    _install_tool_stripping_patch()

    sys.path.insert(0, str(REPO_ROOT))
    os.chdir(REPO_ROOT)
    import run_vbt as rvbt

    run_dir = await rvbt._run_turns([QUERY], rvbt.DEFAULT_MODEL_ID, quiet=False)
    if run_dir is None:
        print("[ERROR] run did not complete", file=sys.stderr)
        return 1

    print(f"\n[RUN_DIR]={run_dir}")
    rvbt._report_run(run_dir)
    return 0


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
