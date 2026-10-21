"""Step E2 -- a DeepSeek-routed Agent actually calling the real single_cell MCP
server and using its result to answer, closing the gap test E left open.

Test E (test_E_local_mcp.py) proved the repo's real single_cell_mcp stdio
server works and returns real CELLxGENE Census data -- but that call was made
directly by an MCP client script, with NO model/agent in the loop. Rename that
result precisely: "real MCP server independently callable" -- it says nothing
about whether an LLM-driven agent can discover, call, and use that same tool
correctly when routed through DeepSeek.

This script closes that gap: it builds a single claude_agent_sdk agent (same
specialist model id this repo uses), wires in the REAL
src/mcp_servers/single_cell_mcp/server.py as an external stdio MCP server
(reusing the exact command/args shape setup_mcp.py already wrote into
mcp_config.json -- not a reimplementation), restricts its tools to exactly
one real tool (get_census_info), and requires it to report the actual
total_cell_count and total_gene_count in its final answer. We parse the
answer and cross-check the numbers against a second, independent direct MCP
call (bypassing the model) to confirm the agent didn't hallucinate plausible-
looking numbers instead of actually using the tool result.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

from _common import SPECIALIST_MODEL_ID, DEEPSEEK_BASE_URL, require_credential, write_log

REPO_ROOT = Path(__file__).resolve().parents[2] / "TheVirtualBiotech"
MCP_CONFIG_PATH = REPO_ROOT / "mcp_config.json"


async def get_ground_truth_census_info() -> dict:
    """Independent direct MCP call (no model), used only to check the agent's
    final answer against reality -- not part of what we're testing."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_path = REPO_ROOT / "src" / "mcp_servers" / "single_cell_mcp" / "server.py"
    params = StdioServerParameters(command=sys.executable, args=["-I", str(server_path)], env=None)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_census_info", arguments={})
            return json.loads(result.content[0].text)


async def run():
    credential = require_credential()
    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ClaudeSDKClient,
            TextBlock,
            ToolUseBlock,
        )
    except ImportError as e:
        write_log("test_E2_agent_real_mcp", {"ok": False, "stage": "import", "error": str(e)})
        print("claude_agent_sdk not importable -- run inside the vbt conda env.")
        sys.exit(2)

    if not MCP_CONFIG_PATH.exists():
        write_log(
            "test_E2_agent_real_mcp",
            {"ok": False, "error": f"{MCP_CONFIG_PATH} missing -- run setup_mcp.py in the repo first."},
        )
        print(f"FAILED: {MCP_CONFIG_PATH} does not exist -- run `python setup_mcp.py` in the repo first.")
        sys.exit(2)

    mcp_config = json.loads(MCP_CONFIG_PATH.read_text())
    single_cell_cfg = mcp_config["mcpServers"]["single_cell"]  # reuse the real, generated stdio spec

    ground_truth = await get_ground_truth_census_info()

    sdk_env = {"ANTHROPIC_BASE_URL": DEEPSEEK_BASE_URL, "ANTHROPIC_API_KEY": credential}

    options = ClaudeAgentOptions(
        model=SPECIALIST_MODEL_ID,
        system_prompt=(
            "You are a single-cell data specialist. Call the get_census_info tool "
            "exactly once, then report the exact total_cell_count and total_gene_count "
            "values it returned, verbatim, as two lines: 'cells: <N>' and 'genes: <N>'."
        ),
        allowed_tools=["mcp__single_cell__get_census_info"],
        mcp_servers={"single_cell": single_cell_cfg},
        max_turns=5,
        permission_mode="bypassPermissions",
        env=sdk_env,
    )

    transcript = []
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is the current size of the CELLxGENE Census in cells and genes?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        transcript.append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolUseBlock):
                        transcript.append({"type": "tool_use", "name": block.name, "input": block.input})

    final_text = "\n".join(e["text"] for e in transcript if e["type"] == "text")
    called_real_tool = any(
        e["type"] == "tool_use" and e["name"].endswith("get_census_info") for e in transcript
    )
    cells_match = re.search(r"cells?:?\s*([\d,]+)", final_text, re.I)
    genes_match = re.search(r"genes?:?\s*([\d,]+)", final_text, re.I)
    reported_cells = int(cells_match.group(1).replace(",", "")) if cells_match else None
    reported_genes = int(genes_match.group(1).replace(",", "")) if genes_match else None

    record = {
        "ok": called_real_tool and reported_cells == ground_truth["total_cell_count"]
        and reported_genes == ground_truth["total_gene_count"],
        "model_requested": SPECIALIST_MODEL_ID,
        "mcp_server": "single_cell (real stdio subprocess, src/mcp_servers/single_cell_mcp/server.py)",
        "called_real_tool": called_real_tool,
        "ground_truth": ground_truth,
        "agent_reported_cells": reported_cells,
        "agent_reported_genes": reported_genes,
        "numbers_match_ground_truth": reported_cells == ground_truth["total_cell_count"]
        and reported_genes == ground_truth["total_gene_count"],
        "transcript": transcript,
    }
    write_log("test_E2_agent_real_mcp", record)
    print(json.dumps({k: v for k, v in record.items() if k != "transcript"}, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
