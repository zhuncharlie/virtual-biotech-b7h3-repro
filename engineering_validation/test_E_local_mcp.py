"""Step E -- a real local MCP tool call, not a mock.

Launches this repo's actual src/mcp_servers/single_cell_mcp/server.py exactly
as setup_mcp.py configures it for a real run (same interpreter, same -I flag,
same stdio transport), and calls get_census_info() -- a read-only tool that
hits the CELLxGENE Census cloud endpoint directly. No Open Targets mirror, no
Tahoe data, no Tabula Sapiens file needed: this tool has no local-bulk-data
prerequisite, which is why it's the right choice for an "independently
initializable read-only MCP tool" per the brief (not every MCP server in this
repo qualifies -- e.g. `genetics`/`target` need the 40GB Open Targets mirror
present first; that dependency would need to be stated explicitly, not here).

This test exercises the repo's actual MCP code against a real external data
source. It does NOT exercise the model at all -- no LLM call happens here, so
it has no DeepSeek dependency. It is a prerequisite check for step C/D's
mcp_servers= wiring, run standalone first since it's cheaper to debug alone.
"""
import asyncio
import json
import sys
from pathlib import Path

from _common import write_log

REPO_ROOT = Path(__file__).resolve().parents[2] / "TheVirtualBiotech"
SERVER_PATH = REPO_ROOT / "src" / "mcp_servers" / "single_cell_mcp" / "server.py"


async def run():
    if not SERVER_PATH.exists():
        write_log("test_E_local_mcp", {"ok": False, "error": f"server script not found: {SERVER_PATH}"})
        print(f"FAILED: {SERVER_PATH} does not exist")
        sys.exit(2)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as e:
        write_log("test_E_local_mcp", {"ok": False, "stage": "import", "error": str(e)})
        print("mcp client library not importable yet -- run inside the vbt conda env.")
        sys.exit(2)

    params = StdioServerParameters(command=sys.executable, args=["-I", str(SERVER_PATH)], env=None)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            if "get_census_info" not in tool_names:
                write_log(
                    "test_E_local_mcp",
                    {"ok": False, "error": "get_census_info not exposed", "tools_seen": tool_names},
                )
                print("FAILED: get_census_info not in exposed tools:", tool_names)
                sys.exit(1)
            result = await session.call_tool("get_census_info", arguments={})
            payload = result.content[0].text if result.content else None

    record = {
        "ok": True,
        "server_path": str(SERVER_PATH),
        "tools_exposed_count": len(tool_names),
        "tools_exposed_sample": tool_names[:10],
        "get_census_info_raw_response": payload,
        "note": "real network call to CELLxGENE Census cloud endpoint; no local bulk data required",
    }
    write_log("test_E_local_mcp", record)
    print(json.dumps({k: v for k, v in record.items() if k != "get_census_info_raw_response"}, indent=2))
    print("census info payload:", payload)


if __name__ == "__main__":
    asyncio.run(run())
