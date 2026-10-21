"""Shared helpers for the DeepSeek compatibility validation scripts.

Scoping rule: we NEVER call os.environ[...] = ... at import time, and we never
export anything into the parent shell. Each test builds an explicit env dict
(starting from a minimal copy of the current environment) and passes it to the
anthropic client / subprocess it constructs. The engineering assistant's own
Claude Code process environment is untouched.
"""
import json
import os
import sys
import time
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEEPSEEK_BASE_URL = "https://api.deepseek.com/anthropic"

# The reproduced system's own .env, not this engineering assistant's shell/profile.
VBT_ENV_FILE = Path(__file__).resolve().parents[2] / "TheVirtualBiotech" / ".env"

# Literal model ids this repo actually uses (src/config/models.py, src/agents/registry.py)
SPECIALIST_MODEL_ID = "claude-sonnet-4-5-20250929"
CHIEF_OF_STAFF_REVIEWER_MODEL_ID = "claude-haiku-4-5-20251001"


def require_credential() -> str:
    """Existence-only check. Never logs, prints, or returns the value to a log file.

    Checks the real shell env first, then falls back to the reproduced system's
    own .env file (python-dotenv's dotenv_values, which reads into a local dict
    without exporting anything into this process's os.environ or any parent
    shell). Either way the value is returned, never printed/logged.
    """
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key and VBT_ENV_FILE.exists():
        from dotenv import dotenv_values

        key = dotenv_values(VBT_ENV_FILE).get("DEEPSEEK_API_KEY")
    if not key:
        print(
            "DEEPSEEK_API_KEY not found in shell env or "
            f"{VBT_ENV_FILE} ({'exists' if VBT_ENV_FILE.exists() else 'missing'}). "
            "Set it yourself and re-run. Not prompting for the value here.",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def isolated_env(credential: str) -> dict:
    """Build a subprocess-local env with DeepSeek's Anthropic-compatible endpoint.

    Only ANTHROPIC_BASE_URL / ANTHROPIC_API_KEY are added on top of a copy of the
    current environment; nothing is unset, nothing is exported to the parent shell.
    """
    env = dict(os.environ)
    env["ANTHROPIC_BASE_URL"] = DEEPSEEK_BASE_URL
    env["ANTHROPIC_API_KEY"] = credential
    # Claude Code CLI specifically reads AUTH_TOKEN; set both so CLI-backed and
    # bare-SDK paths are covered without guessing which one claude_agent_sdk uses.
    env["ANTHROPIC_AUTH_TOKEN"] = credential
    return env


def write_log(name: str, record: dict) -> Path:
    record["_recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    path = LOG_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(record, f, indent=2, default=str)
    print(f"[log] wrote {path}")
    return path
