"""Steps C+D — real claude_agent_sdk delegation and review loopback.

Mirrors this repo's actual mechanism (run.py:~157-234), not a reimplementation:
Virtual Biotech's CSO is a `claude_agent_sdk.ClaudeAgentOptions` with
`system_prompt={"type": "preset", "preset": "claude_code", ...}`, an `agents={}`
dict of `AgentDefinition`s for the specialists/reviewer, and an `env={}` dict
that is handed to the underlying Claude Code subprocess the SDK spawns. That
`env` dict is the documented, SDK-native injection point for pointing this one
run at DeepSeek's endpoint -- it does NOT require exporting anything in this
engineering assistant's own shell or editing any global Claude Code config.

This script builds a deliberately minimal version of that same structure:
  - one orchestrator ("mock-cso") using the specialist model id
  - one specialist subagent using the specialist model id, with one
    no-side-effect tool (returns a fixed string, same as test B)
  - one reviewer subagent using the chief-of-staff/reviewer model id, whose
    prompt requires it to flag a deliberately incomplete specialist answer
  - the orchestrator must: delegate -> get specialist's (incomplete) answer
    -> delegate to reviewer -> get reviewer's flagged gap -> re-delegate to
    the specialist with the reviewer's feedback -> final answer

Requires: `claude_agent_sdk` installed (vbt conda env) and DEEPSEEK_API_KEY set.
Not executed until both are true -- see validation/logs/test_CD_*.json for the
actual run record once it is.
"""
import asyncio
import json
import sys

from _common import (
    CHIEF_OF_STAFF_REVIEWER_MODEL_ID,
    DEEPSEEK_BASE_URL,
    SPECIALIST_MODEL_ID,
    require_credential,
    write_log,
)

NO_SIDE_EFFECT_TOOL_RESULT = "TEST-FACT-42: the sky is calibration-blue today."


async def run():
    credential = require_credential()
    try:
        from claude_agent_sdk import (
            AgentDefinition,
            AssistantMessage,
            ClaudeAgentOptions,
            ClaudeSDKClient,
            TextBlock,
            ToolUseBlock,
            create_sdk_mcp_server,
            tool,
        )
    except ImportError as e:
        write_log("test_CD_sdk_delegation_review", {"ok": False, "stage": "import", "error": str(e)})
        print("claude_agent_sdk not importable yet -- run inside the vbt conda env.")
        sys.exit(2)

    sdk_env = {"ANTHROPIC_BASE_URL": DEEPSEEK_BASE_URL, "ANTHROPIC_API_KEY": credential}

    specialist = AgentDefinition(
        description="[Test] trivial specialist with one no-side-effect tool.",
        prompt=(
            "You are a test specialist. When asked to look something up, call the "
            "get_test_fact tool, then answer using ONLY the first half of what it "
            "returns (deliberately omit the second half) so a reviewer has something "
            "concrete to flag as incomplete. If given reviewer feedback, answer fully."
        ),
        tools=["mcp__testtools__get_test_fact"],
        model=SPECIALIST_MODEL_ID,
    )
    reviewer = AgentDefinition(
        description="[Test] reviewer that checks specialist completeness.",
        prompt=(
            "You are a test reviewer. You will be shown a specialist's answer and the "
            "full fact it was supposed to use. If the answer omits part of the fact, "
            "say exactly: GAP FOUND: <what was omitted>. Otherwise say: COMPLETE."
        ),
        tools=[],
        model=CHIEF_OF_STAFF_REVIEWER_MODEL_ID,
    )

    # Minimal in-process MCP server exposing the one no-side-effect tool, via
    # claude_agent_sdk's own tool()/create_sdk_mcp_server() -- this is the
    # SDK-native in-process server type (McpSdkServerConfig), which the
    # transport knows how to serialize. A raw FastMCP instance is NOT
    # JSON-serializable and fails at connect() (see run log: first attempt
    # raised TypeError: Object of type FastMCP is not JSON serializable).

    @tool("get_test_fact", "Returns a fixed, no-side-effect test fact.", {})
    async def get_test_fact(args):
        return {"content": [{"type": "text", "text": NO_SIDE_EFFECT_TOOL_RESULT}]}

    test_mcp = create_sdk_mcp_server(name="testtools", tools=[get_test_fact])

    options = ClaudeAgentOptions(
        model=SPECIALIST_MODEL_ID,
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": (
                "You are a test orchestrator (stand-in for the CSO). Delegate the user's "
                "question to the 'specialist' subagent. Then delegate the specialist's raw "
                f"answer plus this full fact -- {NO_SIDE_EFFECT_TOOL_RESULT!r} -- to the "
                "'reviewer' subagent. If the reviewer reports a gap, re-delegate to the "
                "specialist with the reviewer's feedback and get a corrected answer. Only "
                "then give the user the final, corrected answer."
            ),
        },
        allowed_tools=["Task", "Agent"],
        agents={"specialist": specialist, "reviewer": reviewer},
        mcp_servers={"testtools": test_mcp},
        max_turns=20,
        permission_mode="bypassPermissions",
        env=sdk_env,
    )

    transcript = []
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Look up the test fact and tell me about it.")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        transcript.append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolUseBlock):
                        transcript.append({"type": "tool_use", "name": block.name, "input": block.input})

    record = {
        "ok": True,
        "specialist_model_requested": SPECIALIST_MODEL_ID,
        "reviewer_model_requested": CHIEF_OF_STAFF_REVIEWER_MODEL_ID,
        "delegated_to_specialist": any(
            e.get("type") == "tool_use" and "specialist" in json.dumps(e.get("input", {})) for e in transcript
        ),
        "delegated_to_reviewer": any(
            e.get("type") == "tool_use" and "reviewer" in json.dumps(e.get("input", {})) for e in transcript
        ),
        "mentions_gap_or_complete": any(
            "GAP FOUND" in e.get("text", "") or "COMPLETE" in e.get("text", "") for e in transcript
        ),
        "transcript": transcript,
    }
    write_log("test_CD_sdk_delegation_review", record)
    print(json.dumps({k: v for k, v in record.items() if k != "transcript"}, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
