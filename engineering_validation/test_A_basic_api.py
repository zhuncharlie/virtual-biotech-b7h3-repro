"""Step A — basic API call through DeepSeek's Anthropic-compatible endpoint.

Sends one request with the literal model id this repo uses for specialists
(claude-sonnet-4-5-20250929) and records exactly what the response claims the
model actually was. Does not assume the request model name equals the model
that ran.
"""
import subprocess
import sys
import textwrap

from _common import SPECIALIST_MODEL_ID, isolated_env, require_credential, write_log

SCRIPT = textwrap.dedent(
    """
    import json, anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model={model!r},
        max_tokens=64,
        messages=[{{"role": "user", "content": "Reply with exactly the word: pong"}}],
    )
    print(json.dumps({{
        "requested_model": {model!r},
        "response_model_field": resp.model,
        "response_id": resp.id,
        "stop_reason": resp.stop_reason,
        "text": "".join(b.text for b in resp.content if b.type == "text"),
        "usage": resp.usage.model_dump() if hasattr(resp.usage, "model_dump") else dict(resp.usage),
    }}))
    """
).format(model=SPECIALIST_MODEL_ID)


def main():
    credential = require_credential()
    env = isolated_env(credential)
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT], capture_output=True, text=True, env=env, timeout=60
    )
    record = {
        "requested_model": SPECIALIST_MODEL_ID,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }
    write_log("test_A_basic_api", record)
    if proc.returncode != 0:
        print("FAILED — see validation/logs/test_A_basic_api.json for desensitized stderr")
        sys.exit(1)
    print("OK:", proc.stdout.strip())


if __name__ == "__main__":
    main()
