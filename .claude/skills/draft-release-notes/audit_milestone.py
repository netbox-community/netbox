#!/usr/bin/env python3
"""List the commits since the previous release which aren't linked to an issue in the release's milestone."""

import argparse
import json
import re
import subprocess

OWNER, NAME = 'netbox-community', 'netbox'
BATCH_SIZE = 50
ISSUE_REF = re.compile(r'\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?):? #(\d+)', re.IGNORECASE)
ISSUE_FIELDS = 'number title milestone { title } labels(first: 20) { nodes { name } }'


def run(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def graphql(fields):
    """Query the repository. Fields which can't be resolved (e.g. an issue number which is a PR) return None."""
    query = f'{{ repository(owner: "{OWNER}", name: "{NAME}") {{ {" ".join(fields)} }} }}'
    result = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={query}'], capture_output=True, text=True)
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise SystemExit(result.stderr) from None
    if not response.get('data') or any(error.get('type') != 'NOT_FOUND' for error in response.get('errors', [])):
        raise SystemExit(result.stderr)
    return response['data']['repository']


def get_commits(base, head):
    """Return the SHA, subject, and changed paths (relative to the first parent) of each first-parent commit."""
    log = run(
        'git', 'log', '--first-parent', '--diff-merges=first-parent', '--reverse', '--name-only',
        '--format=%x00%H%x09%s', f'{base}..{head}',
    )
    commits = []
    for entry in log.split('\0')[1:]:
        header, *paths = entry.splitlines()
        sha, subject = header.split('\t', 1)
        commits.append((sha, subject, [path for path in paths if path]))
    return commits


def get_areas(paths):
    """Return the areas of the codebase to which the given paths belong."""
    areas = set()
    for path in paths:
        if path.startswith('netbox/translations/'):
            areas.add('translations')
        elif '/tests/' in path:
            areas.add('tests')
        elif path.startswith('netbox/'):
            areas.add('app')
        elif path in ('base_requirements.txt', 'requirements.txt', 'pyproject.toml'):
            areas.add('dependencies')
        elif path in ('contrib/openapi.json', 'contrib/generated_schema.json'):
            areas.add('schema')
        elif path == 'upgrade.sh' or path.startswith('contrib/'):
            areas.add('install')
        elif path.startswith('docs/') or path in ('mkdocs.yml', 'README.md'):
            areas.add('docs')
        else:
            areas.add('tooling')
    return areas


def get_links(commits):
    """Map each commit to its pull requests and to the issues it references or its PRs close."""
    links = {}
    for i in range(0, len(commits), BATCH_SIZE):
        batch = commits[i:i + BATCH_SIZE]
        data = graphql(
            f'c{j}: object(oid: "{sha}") {{ ... on Commit {{ associatedPullRequests(first: 3) {{ nodes {{ '
            f'number closingIssuesReferences(first: 10) {{ nodes {{ {ISSUE_FIELDS} }} }} }} }} }} }}'
            for j, (sha, _, _) in enumerate(batch)
        )
        for j, (sha, _, _) in enumerate(batch):
            # A commit which hasn't been pushed resolves to None
            if (commit := data[f'c{j}']) is None:
                links[sha] = {'prs': None, 'issues': {}}
                continue
            prs = commit['associatedPullRequests']['nodes']
            issues = {issue['number']: issue for pr in prs for issue in pr['closingIssuesReferences']['nodes']}
            links[sha] = {'prs': [pr['number'] for pr in prs], 'issues': issues}

    # Issues referenced only in a commit subject (e.g. "Fixes #123: ...")
    missing = {
        int(number) for sha, subject, _ in commits
        for number in ISSUE_REF.findall(subject) if int(number) not in links[sha]['issues']
    }
    if missing:
        data = graphql(f'i{number}: issue(number: {number}) {{ {ISSUE_FIELDS} }}' for number in missing)
        for sha, subject, _ in commits:
            for number in map(int, ISSUE_REF.findall(subject)):
                if issue := data.get(f'i{number}'):
                    links[sha]['issues'].setdefault(number, issue)
    return links


def escape(text):
    """Escape pipes for use in a Markdown table cell."""
    return text.replace('|', r'\|')


def describe_issue(issue):
    milestone = issue['milestone']['title'] if issue['milestone'] else 'no milestone'
    types = [label['name'] for label in issue['labels']['nodes'] if label['name'].startswith('type:')]
    return f"#{issue['number']} ({', '.join([milestone, *types])})"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('milestone', help='Release milestone, e.g. v4.7.5')
    parser.add_argument('--head', default='origin/main', help='Last commit of the release (default: origin/main)')
    parser.add_argument('--base', help='Previous release tag (default: the latest tag before --head)')
    args = parser.parse_args()

    base = args.base or run('git', 'describe', '--tags', '--abbrev=0', f'{args.head}^').strip()
    commits = get_commits(base, args.head)
    links = get_links(commits)

    uncovered, routine, linked_issues = [], 0, set()
    for sha, subject, paths in commits:
        issues = links[sha]['issues']
        linked_issues.update(issues)
        areas = get_areas(paths)
        in_milestone = any(
            issue['milestone'] and issue['milestone']['title'] == args.milestone for issue in issues.values()
        )
        if subject.startswith('Release v') or areas == {'translations'} or set(paths) == {'.github/VOUCHED.td'}:
            routine += 1
        # Always list reverts, which cancel out the commit they revert
        elif subject.startswith('Revert ') or not in_milestone:
            uncovered.append((sha, subject, links[sha]['prs'], issues, areas))

    print(f'# Milestone audit: {args.milestone} ({base}..{args.head})\n')
    print(
        f'{len(commits)} commits: {len(commits) - len(uncovered) - routine} linked to the milestone, '
        f'{routine} routine (releases, translations, vouched contributors), '
        f'{len(uncovered)} reverts or not linked to the milestone.\n'
    )
    print('## Reverts, and commits not linked to the milestone\n')
    print('| Commit | Subject | PRs | Linked issues | Areas changed |')
    print('|---|---|---|---|---|')
    for sha, subject, prs, issues, areas in uncovered:
        prs = 'not on GitHub' if prs is None else ', '.join(f'#{pr}' for pr in prs) or '-'
        issues = ', '.join(map(describe_issue, issues.values())) or '-'
        print(f"| {sha[:9]} | {escape(subject)} | {prs} | {issues} | {', '.join(sorted(areas))} |")

    milestone_issues = json.loads(run(
        'gh', 'issue', 'list', '--repo', f'{OWNER}/{NAME}', '--milestone', args.milestone,
        '--state', 'closed', '--limit', '500', '--json', 'number,title,stateReason',
    ))
    unmatched = [
        issue for issue in milestone_issues
        if issue['stateReason'] == 'COMPLETED' and issue['number'] not in linked_issues
    ]
    print('\n## Milestone issues not linked to any commit\n')
    print('| Issue | Title |')
    print('|---|---|')
    for issue in sorted(unmatched, key=lambda issue: issue['number']):
        print(f"| #{issue['number']} | {escape(issue['title'])} |")


if __name__ == '__main__':
    main()
