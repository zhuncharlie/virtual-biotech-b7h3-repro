"""Step B — tool_use / tool_result round trip, one no-side-effect tool.

The tool (get_server_time) has no filesystem or network effect — it returns a
fixed string. We only care whether the model: (1) emits a tool_use block,
(2) we feed back a tool_result, (3) it produces a final text answer that uses
the tool's return value. Confirms DeepSeek's "Fully Supported" tool fields
claim actually round-trips end to end, not just that the field is accepted.
"""
import subprocess
import sys
import textwrap

from _common import SPECIALIST_MODEL_ID, isolated_env, require_credential, write_log

SCRIPT = textwrap.dedent(
    """
    import json, anthropic
    client = anthropic.Anthropic()
    tools = [{{
        "name": "get_server_time",
        "description": "Returns a fixed, no-side-effect timestamp string for testing.",
        "input_schema": {{"type": "object", "properties": {{}}, "required": []}},
    }}]
    messages = [{{"role": "user", "content": "Call get_server_time, then tell me what it returned, verbatim."}}]
    resp1 = client.messages.create(model={model!r}, max_tokens=256, tools=tools, messages=messages)
    tool_use_blocks = [b for b in resp1.content if b.type == "tool_use"]
    if not tool_use_blocks:
        print(json.dumps({{"ok": False, "reason": "model did not call the tool", "stop_reason": resp1.stop_reason}}))
        raise SystemExit(0)
    tu = tool_use_blocks[0]
    FIXED_VALUE = "TEST-TIMESTAMP-1738000000"
    messages.append({{"role": "assistant", "content": resp1.content}})
    messages.append({{
        "role": "user",
        "content": [{{"type": "tool_result", "tool_use_id": tu.id, "content": FIXED_VALUE}}],
    }})
    resp2 = client.messages.create(model={model!r}, max_tokens=128, tools=tools, messages=messages)
    final_text = "".join(b.text for b in resp2.content if b.type == "text")
    print(json.dumps({{
        "ok": True,
        "tool_called": tu.name,
        "tool_input": tu.input,
        "final_text": final_text,
        "fixed_value_echoed": FIXED_VALUE in final_text,
        "response_model_field_turn1": resp1.model,
        "response_model_field_turn2": resp2.model,
    }}))
    """
).format(model=SPECIALIST_MODEL_ID)


def main():
    credential = require_credential()
    env = isolated_env(credential)
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT], capture_output=True, text=True, env=env, timeout=90
    )
    record = {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    write_log("test_B_tool_loop", record)
    if proc.returncode != 0:
        print("FAILED — see validation/logs/test_B_tool_loop.json")
        sys.exit(1)
    print("OK:", proc.stdout.strip())


if __name__ == "__main__":
    main()
