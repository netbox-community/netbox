#!/usr/bin/env python3
"""Produce an issue-triage verdict with one tool-less Anthropic Messages API call.

Design rationale
----------------
This script holds ANTHROPIC_API_KEY, but the model it calls is given NO tools. A
prompt injection in untrusted issue content therefore has no mechanism to read the
runner environment or filesystem (e.g. /proc/self/environ) or to post anything; the
model can only return text. All repo/issue context is gathered deterministically by
the workflow and passed in as data. The comment is posted by a separate job that
holds the GitHub token but no Anthropic key, so the secret and the write capability
are never co-located.

The triage prompt itself lives in the workflow (TRIAGE_PROMPT) so it is reviewed
alongside the workflow; this script only supplies the gathered context as data.

Output: a single line of JSON on stdout: {"should_comment": bool, "body": str}.
Fails closed (no comment) on any API or parse error; exits non-zero on configuration
errors (missing key/prompt, 4xx from the API) so they are not silently swallowed.
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def _read(path: str) -> str:
    if not path:
        return ""
    try:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _fail_closed(msg: str, fatal: bool = False) -> None:
    level = "error" if fatal else "warning"
    sys.stderr.write(f"::{level}::triage: {msg}\n")
    print(json.dumps({"should_comment": False, "body": ""}))
    if fatal:
        sys.exit(1)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _fail_closed("ANTHROPIC_API_KEY not set", fatal=True)
    system = os.environ.get("TRIAGE_PROMPT", "").strip()
    if not system:
        _fail_closed("TRIAGE_PROMPT not set", fatal=True)

    user = (
        '<issue number="{num}">\n<title>{title}</title>\n<body>\n{body}\n</body>\n</issue>\n\n'
        "<issue_templates>\n{templates}\n</issue_templates>\n\n"
        "<release_list>\n{releases}\n</release_list>\n\n"
        "<duplicate_candidates>\n{dups}\n</duplicate_candidates>"
    ).format(
        num=os.environ.get("ISSUE_NUMBER", ""),
        title=os.environ.get("ISSUE_TITLE", ""),
        body=os.environ.get("ISSUE_BODY", ""),
        templates=_read(os.environ.get("TEMPLATES_PATH", "")),
        releases=_read(os.environ.get("RELEASES_PATH", "")),
        dups=_read(os.environ.get("DUP_CANDIDATES_PATH", "")),
    )

    payload = json.dumps(
        {
            "model": MODEL,
            "max_tokens": 1024,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
    ).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        # Bad key, retired model, malformed request: a config problem, so fail loudly.
        _fail_closed(f"API returned HTTP {exc.code}", fatal=400 <= exc.code < 500 and exc.code != 429)
        return
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        _fail_closed(f"API call failed: {exc}")
        return

    text = "".join(
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ).strip()
    if text.startswith("```"):
        text = text.strip("`")
        brace = text.find("{")
        text = text[brace:] if brace != -1 else text

    try:
        verdict = json.loads(text)
        should = bool(verdict.get("should_comment"))
        body = verdict.get("body", "") if should else ""
    except (json.JSONDecodeError, AttributeError):
        _fail_closed("model did not return parseable JSON")
        return

    print(json.dumps({"should_comment": should, "body": body}))


if __name__ == "__main__":
    main()
