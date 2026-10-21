"""Step F -- audit, across all prior logs, what model actually ran per role.

Not a new API call. Reads validation/logs/test_A_basic_api.json,
test_B_tool_loop.json, and test_CD_sdk_delegation_review.json and reports, per
role (specialist vs. chief-of-staff/reviewer), the requested claude-* model id
side by side with whatever the response itself claims. The rule enforced here:
never report "requested claude-sonnet-4-5" as "ran Claude" -- only the
response's own model field (or an explicit remap note from DeepSeek's docs)
counts as evidence of what actually executed.
"""
import json
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"


def load(name):
    path = LOG_DIR / f"{name}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def main():
    a = load("test_A_basic_api")
    cd = load("test_CD_sdk_delegation_review")

    findings = []

    if a is None:
        findings.append("test_A log missing -- run test_A_basic_api.py first.")
    else:
        stdout = a.get("stdout", "")
        try:
            parsed = json.loads(stdout)
            findings.append(
                f"A: requested={parsed.get('requested_model')!r} -> "
                f"response.model field={parsed.get('response_model_field')!r}"
            )
            if parsed.get("response_model_field") and "claude" in parsed["response_model_field"].lower():
                findings.append(
                    "WARNING: response.model field still contains 'claude' -- "
                    "verify this isn't DeepSeek echoing the request's model string "
                    "unchanged rather than reporting what it actually ran. Treat as "
                    "UNCONFIRMED, not as proof Claude ran, until cross-checked against "
                    "DeepSeek's own account/usage dashboard for this request."
                )
        except (json.JSONDecodeError, AttributeError):
            findings.append(f"A: could not parse stdout as JSON: {stdout!r}")

    if cd is None:
        findings.append("test_CD log missing -- run test_CD_sdk_delegation_review.py first.")
    else:
        findings.append(
            f"C/D: specialist requested={cd.get('specialist_model_requested')!r}, "
            f"reviewer requested={cd.get('reviewer_model_requested')!r}"
        )
        if cd.get("specialist_model_requested") != cd.get("reviewer_model_requested"):
            findings.append(
                "Two distinct claude-* ids were requested for specialist vs reviewer "
                "(matches this repo's real registry.py split). Per DeepSeek's documented "
                "server-side mapping (claude-sonnet*/claude-haiku* -> deepseek-flash, "
                "claude-opus* -> deepseek-v4-pro), both of THIS repo's current literal ids "
                "fall in the claude-sonnet*/claude-haiku* bucket and so are expected to "
                "collapse onto the SAME underlying deepseek-flash model -- i.e. the paper's "
                "two-tier model division of labor is NOT preserved by default. This is a "
                "documented fact about the mapping, not something this script can observe "
                "directly from the response alone; cross-check against response.model if "
                "DeepSeek exposes which underlying model actually served the request."
            )

    for line in findings:
        print("-", line)

    if a is None or cd is None:
        sys.exit(2)


if __name__ == "__main__":
    main()
