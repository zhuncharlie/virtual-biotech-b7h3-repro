"""Invoke the repo's REAL run_vbt.py entry point with the B7-H3 query,
routed to DeepSeek via env vars scoped to this one subprocess only.

This script does not answer the science question itself -- it asks the
actual Virtual Biotech system (CSOSession via run_vbt.py) to do it, and
just plumbs credentials through without ever printing/logging the key.

Framed per standing instruction: engineering-chain validation of the
formal entry point (CSO delegation, real role config, real session
records, model routing), NOT a B7-H3 scientific result.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "TheVirtualBiotech"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/anthropic"
OPEN_TARGETS_DATA_PATH = "/mnt/beegfs/xqinag/data/open_targets_25.09"

QUERY = (
    "Evaluate the therapeutic candidacy of B7-H3 in lung cancer. "
    "For this validation pass, skip spatial transcriptomics / Visium analysis; "
    "focus on the evidence sources available without it."
)


def main() -> int:
    env_path = REPO_ROOT / ".env"
    deepseek_key = None
    for line in env_path.read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            deepseek_key = line.split("=", 1)[1].strip()
            break
    if not deepseek_key:
        print("DEEPSEEK_API_KEY not found in .env", file=sys.stderr)
        return 2

    child_env = dict(os.environ)
    child_env["ANTHROPIC_BASE_URL"] = DEEPSEEK_BASE_URL
    child_env["ANTHROPIC_API_KEY"] = deepseek_key
    child_env["OPEN_TARGETS_DATA_PATH"] = OPEN_TARGETS_DATA_PATH
    del deepseek_key  # drop the only local reference promptly

    proc = subprocess.run(
        [sys.executable, "run_vbt.py", "run", QUERY],
        cwd=str(REPO_ROOT),
        env=child_env,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
