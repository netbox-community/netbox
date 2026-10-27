#!/usr/bin/env python3
"""Produce an issue-triage verdict with tool-less Anthropic Messages API calls.

Design rationale
----------------
This script holds ANTHROPIC_API_KEY, but the model it calls is given NO tools. A
prompt injection in untrusted issue content therefore has no mechanism to read the
runner environment or filesystem (e.g. /proc/self/environ) or to post anything; the
model can only return text. All repo/issue context is gathered deterministically by
the workflow and this script, and passed in as data. The comment is posted by a
separate job that holds the GitHub token but no Anthropic key, so the secret and the
write capability are never co-located.

Two calls are made:
  1. The model proposes a few short keyword queries for finding duplicates. The script
     (not the model) sanitizes them and runs `gh search issues` with a read-only token,
     pinned to this repository. The worst an injection can do here is pick a poor query.
  2. The model returns the verdict, given the issue, templates, releases, and the
     duplicate candidates (with truncated bodies).

The prompts live in the workflow (TRIAGE_PROMPT, QUERY_PROMPT) so they are reviewed
alongside the workflow; this script only supplies the gathered context as data.

Output: a single line of JSON on stdout: {"should_comment": bool, "body": str}.
Fails closed (no comment) on any API or parse error; exits non-zero on configuration
errors (missing key/prompt, 4xx from the API) so they are not silently swallowed.
"""
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

MAX_QUERIES = 3
MAX_QUERY_LEN = 80
RESULTS_PER_QUERY = 5
MAX_CANDIDATES = 8
CANDIDATE_BODY_CHARS = 1500


class APIError(Exception):
    def __init__(self, msg: str, fatal: bool = False):
        super().__init__(msg)
        self.fatal = fatal


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


def _load_issue() -> dict:
    # Read the issue from the event payload on disk rather than env vars, which are
    # capped at 128 KiB each and can be exceeded by a long non-ASCII body.
    try:
        event = json.loads(_read(os.environ.get("GITHUB_EVENT_PATH", "")) or "{}")
    except json.JSONDecodeError:
        event = {}
    issue = event.get("issue") or {}
    return {
        "number": issue.get("number") or "",
        "title": issue.get("title") or "",
        "body": issue.get("body") or "",
    }


def _call(api_key: str, system: str, user: str, max_tokens: int) -> str:
    payload = json.dumps(
        {
            "model": MODEL,
            "max_tokens": max_tokens,
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
        raise APIError(f"API returned HTTP {exc.code}", fatal=400 <= exc.code < 500 and exc.code != 429)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        raise APIError(f"API call failed: {exc}")

    if data.get("stop_reason") == "max_tokens":
        raise APIError(f"model response truncated at max_tokens={max_tokens}")

    text = "".join(
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ).strip()
    if text.startswith("```"):
        text = text.strip("`")
        brace = text.find("{")
        text = text[brace:] if brace != -1 else text
    return text


def _issue_xml(issue: dict) -> str:
    return '<issue number="{number}">\n<title>{title}</title>\n<body>\n{body}\n</body>\n</issue>'.format(**issue)


def _sanitize_query(query: str) -> str:
    # Drop search qualifiers (repo:, org:, author:, ...) so a query cannot leave this
    # repo, plus quotes, negation, and boolean operators.
    words = []
    for word in query.replace('"', " ").split():
        word = word.lstrip("-")
        if not word or ":" in word or word in ("OR", "AND", "NOT"):
            continue
        words.append(word)
    return " ".join(words)[:MAX_QUERY_LEN].strip()


def _propose_queries(api_key: str, issue: dict) -> list[str]:
    system = os.environ.get("QUERY_PROMPT", "").strip()
    queries = []
    if system:
        try:
            text = _call(api_key, system, _issue_xml(issue), max_tokens=256)
            proposed = json.loads(text).get("queries", [])
            if isinstance(proposed, list):
                queries = [q for q in proposed if isinstance(q, str)]
        except APIError as exc:
            if exc.fatal:
                raise
            sys.stderr.write(f"::warning::triage: query generation failed: {exc}\n")
        except (json.JSONDecodeError, AttributeError):
            sys.stderr.write("::warning::triage: query generation returned unparseable JSON\n")
    # Fall back to the title if the model proposed nothing usable.
    queries = [s for s in (_sanitize_query(q) for q in queries[:MAX_QUERIES]) if s]
    return queries or [s for s in [_sanitize_query(issue["title"])] if s]


def _search(query: str) -> list[dict]:
    # Arguments are passed as a list (no shell); `--` stops the query being read as flags.
    try:
        result = subprocess.run(
            [
                "gh", "search", "issues",
                "--repo", os.environ["GITHUB_REPOSITORY"],
                "--limit", str(RESULTS_PER_QUERY),
                "--json", "number,state,title,url,body",
                "--", query,
            ],
            capture_output=True, text=True, timeout=30, check=True,
        )
        return json.loads(result.stdout or "[]")
    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError, OSError) as exc:
        sys.stderr.write(f"::warning::triage: search failed: {exc}\n")
        return []


def _duplicate_candidates(queries: list[str], issue_number) -> str:
    seen = {issue_number}
    candidates = []
    for query in queries:
        for hit in _search(query):
            if hit.get("number") in seen:
                continue
            seen.add(hit.get("number"))
            candidates.append(hit)
    entries = []
    for hit in candidates[:MAX_CANDIDATES]:
        body = (hit.get("body") or "")[:CANDIDATE_BODY_CHARS]
        entries.append(
            '<candidate number="{number}" state="{state}" url="{url}">\n<title>{title}</title>\n'
            "<body_excerpt>\n{body}\n</body_excerpt>\n</candidate>".format(
                number=hit.get("number", ""),
                state=hit.get("state", ""),
                url=hit.get("url", ""),
                title=hit.get("title", ""),
                body=body,
            )
        )
    return "\n".join(entries)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _fail_closed("ANTHROPIC_API_KEY not set", fatal=True)
    system = os.environ.get("TRIAGE_PROMPT", "").strip()
    if not system:
        _fail_closed("TRIAGE_PROMPT not set", fatal=True)

    issue = _load_issue()
    if not issue["number"]:
        _fail_closed("could not read issue from GITHUB_EVENT_PATH")
        return

    try:
        queries = _propose_queries(api_key, issue)
    except APIError as exc:
        _fail_closed(str(exc), fatal=exc.fatal)
        return

    user = (
        "{issue}\n\n"
        "<issue_templates>\n{templates}\n</issue_templates>\n\n"
        "<release_list>\n{releases}\n</release_list>\n\n"
        "<duplicate_candidates>\n{dups}\n</duplicate_candidates>"
    ).format(
        issue=_issue_xml(issue),
        templates=_read(os.environ.get("TEMPLATES_PATH", "")),
        releases=_read(os.environ.get("RELEASES_PATH", "")),
        dups=_duplicate_candidates(queries, issue["number"]),
    )

    try:
        text = _call(api_key, system, user, max_tokens=2048)
    except APIError as exc:
        _fail_closed(str(exc), fatal=exc.fatal)
        return

    try:
        verdict = json.loads(text)
        should = verdict.get("should_comment") is True
        body = verdict.get("body") if should else ""
    except (json.JSONDecodeError, AttributeError):
        _fail_closed("model did not return parseable JSON")
        return

    # A verdict to comment is only usable with a non-empty string body.
    if should and not (isinstance(body, str) and body.strip()):
        _fail_closed("model set should_comment without a usable body")
        return

    print(json.dumps({"should_comment": should, "body": body}))


if __name__ == "__main__":
    main()
