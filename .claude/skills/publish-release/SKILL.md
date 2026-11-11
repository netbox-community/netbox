---
name: publish-release
description: Publish a NetBox core (this repository, not a plugin) release after its "Release vX.Y.Z" PR has merged — check the publishing prerequisites, create the GitHub release and tag, watch the PyPI publishing workflow, verify and smoke-test the published package, and close out the milestone. Use when a maintainer asks to publish, tag, or ship a NetBox release whose release PR is merged.
---

# Publish a NetBox Release

This skill automates the checklist's steps from [Confirm Package Publishing Prerequisites](../../../docs/development/release-checklist.md#confirm-package-publishing-prerequisites) onward, after the release PR (prepared with the `prepare-release` skill) has merged. The checklist remains the authoritative process.

Creating the GitHub release pushes the `vX.Y.Z` tag, and the tag push starts `.github/workflows/release.yml`, which publishes to PyPI. **Files uploaded to PyPI can never be replaced**, so check everything before step 3, and confirm with the user before every outward-facing action.

Run commands from the repository root. Write temporary files to the session scratchpad (`$SCRATCH` below).

## 1. Verify the Merge

```bash
git status --porcelain                                        # must be empty
git fetch origin --tags
gh repo set-default --view                                    # must be netbox-community/netbox
gh pr list --repo netbox-community/netbox --head release-vX.Y.Z --state merged --json number,mergeCommit
git checkout --detach <merge commit SHA>
grep '^version:' netbox/release.yaml                          # must be "X.Y.Z"
git ls-remote --tags origin vX.Y.Z                            # must print nothing
gh run list --repo netbox-community/netbox --workflow ci.yml --commit <merge commit SHA> --json status,conclusion
```

- The release PR must be merged. Its merge commit is the **release commit**, and every remaining step uses it rather than `main` HEAD. Automated commits (source translation strings, the VOUCHED list) can land on `main` after the PR merges, and they must not end up in the tag.
- `netbox/release.yaml` must hold the version being released. The published package version comes from this file, not from the tag.
- If the tag already exists, stop: the release has been created, at least in part.
- The CI run for the release commit must have succeeded.

## 2. Check the Publishing Prerequisites

These checks are read-only. **Never change repository or environment settings yourself**; report what's missing and let the user decide.

**The `pypi` environment's approval gate.** The checklist requires the `pypi` environment to have required reviewers with **Prevent self-review** enabled, and deployments restricted to `v*` tags:

```bash
gh api repos/netbox-community/netbox/environments/pypi \
  --jq '{rules: [.protection_rules[] | {type, prevent_self_review, reviewers: [.reviewers[]?.reviewer | .login // .slug]}], policy: .deployment_branch_policy}'
gh api repos/netbox-community/netbox/environments/pypi/deployment-branch-policies \
  --jq '[.branch_policies[] | {name, type}]'
```

Expect a `required_reviewers` rule with `prevent_self_review: true` and at least one reviewer, a policy with `custom_branch_policies: true`, and a `{"name": "v*", "type": "tag"}` branch policy. (The second command returns 404 when no custom policy is configured.)

**If any of these is missing, stop.** Explain that creating the release will publish to PyPI immediately, with no approval step, and ask whether to fix the environment first (under Settings → Environments → `pypi`) or to proceed regardless.

**The PyPI trusted publisher.** Its configuration on PyPI can't be queried. Treat it as confirmed if the previous release's publish job succeeded and the workflow's publish jobs haven't changed since:

```bash
PREV=$(git describe --tags --abbrev=0 HEAD^)
gh run list --workflow release.yml --event push --branch $PREV --json databaseId,conclusion,url
git diff $PREV..HEAD -- .github/workflows/release.yml
```

Otherwise, ask the user to confirm that the trusted publisher on PyPI still matches this repository, `release.yml`, and the `pypi` environment name.

## 3. Create the Release

Render the release body from the merged release notes:

```bash
python3 .claude/skills/draft-release-notes/render_release_notes.py X.Y.Z --format release > $SCRATCH/release-body.md
```

Show the user the title and body, and state plainly that creating the release pushes the tag and starts publishing to PyPI. Only after they confirm:

```bash
gh release create vX.Y.Z --repo netbox-community/netbox \
  --target <release commit SHA> \
  --title "vX.Y.Z - YYYY-MM-DD" \
  --notes-file $SCRATCH/release-body.md
```

The date in the title is `published` from `netbox/release.yaml`. The checklist targets `main`. Targeting the release commit's SHA instead keeps out anything pushed to `main` after the release PR merged.

## 4. Watch the Workflow

The tag push starts a `release.yml` run within a minute or so:

```bash
gh run list --repo netbox-community/netbox --workflow release.yml --event push --branch vX.Y.Z --json databaseId,status,url
gh run watch <run id> --repo netbox-community/netbox --exit-status    # in the background
gh run view <run id> --repo netbox-community/netbox --json jobs --jq '.jobs[] | "\(.databaseId) \(.name): \(.status) \(.conclusion)"'
```

Report the results of the build and verification jobs: **Build package artifacts**, **Verify dependency pins are in sync**, **Verify the sdist builds a wheel**, **Smoke test wheel CLI (no dependencies)**, and **Smoke test wheel install**.

When **Publish package to PyPI** is waiting on the `pypi` environment, tell the user that a colleague must approve the deployment in the Actions UI (the environment prevents self-review). **Never approve a deployment yourself**, for example through the `pending_deployments` API.

If any job fails, stop and follow [pypi-recovery.md](pypi-recovery.md). Never re-run the whole workflow.

## 5. Verify the Publication

1. The publish job deployed to the `pypi` environment:

    ```bash
    gh api "repos/netbox-community/netbox/deployments?environment=pypi&ref=vX.Y.Z" --jq '.[] | {id, environment, created_at}'
    ```

2. PyPI lists exactly one wheel and one sdist for the version:

    ```bash
    curl -sf https://pypi.org/pypi/netbox/X.Y.Z/json | python3 -c 'import json, sys
    for f in json.load(sys.stdin)["urls"]:
        print(f["packagetype"], f["filename"], f["digests"]["sha256"])'
    ```

3. Smoke-test the published wheel, following [Test-installing the wheel](../../../docs/development/building-the-package.md#test-installing-the-wheel) but installing from PyPI. It builds `psycopg[c]`, which needs the PostgreSQL client headers (`libpq-dev`) and a compiler. If pip can't find the new version yet, wait a minute and retry.

    ```bash
    python3 -m venv $SCRATCH/netbox-wheel-test
    $SCRATCH/netbox-wheel-test/bin/python -m pip install --upgrade pip
    $SCRATCH/netbox-wheel-test/bin/python -m pip install --no-cache-dir "netbox==X.Y.Z"
    $SCRATCH/netbox-wheel-test/bin/netbox --version
    PYTHONPATH=$PWD/scripts \
    NETBOX_CONFIGURATION=smoketest_configuration \
    NETBOX_ROOT=$SCRATCH/netbox-wheel-root \
    NETBOX_SMOKETEST_BASE=$SCRATCH/netbox-wheel-root \
    $SCRATCH/netbox-wheel-test/bin/netbox check
    ```

    `netbox --version` must report `X.Y.Z`, and `netbox check` must report no issues.

## 6. Close Out the Milestone

Confirm each change with the user before making it.

```bash
gh api 'repos/netbox-community/netbox/milestones?state=open&per_page=100' \
  --jq '.[] | {number, title, due_on, open_issues}'
```

1. If milestone `vX.Y.Z` still has open issues, list them and ask whether to move them to the next milestone (`gh issue edit N --milestone vX.Y.(Z+1)`).
2. Close it: `gh api -X PATCH repos/netbox-community/netbox/milestones/<number> -f state=closed`
3. If milestone `vX.Y.(Z+1)` doesn't exist yet, create it, due two weeks after this release (patch releases ship every two weeks):

    ```bash
    gh api repos/netbox-community/netbox/milestones -f title=vX.Y.(Z+1) -f due_on=YYYY-MM-DDT00:00:00Z
    ```

## 7. Hand Off

Give the user:

- The release URL, the PyPI project URL (`https://pypi.org/project/netbox/X.Y.Z/`), and the workflow run URL
- The milestone changes made
- Remaining tasks for them: merging `main` into `feature`

Finally, return the checkout to `main` (`git checkout main`), since step 1 left it on the detached release commit.

## Why These Choices

- **Stop on a missing approval gate.** Without one, the tag push uploads straight to PyPI, where a mistake can only be corrected by publishing a new version. The checklist depends on the gate as the final review point.
- **Never approve or re-run publishing automatically.** Approval is deliberately a second person's decision, and re-running the wrong jobs rebuilds distributions that PyPI may already have accepted.
- **Render the body from the merged docs.** The release notes in `docs/release-notes/` are the reviewed text; rendering from them avoids copying the PR body by hand.

## References

- [`docs/development/release-checklist.md`](../../../docs/development/release-checklist.md): The authoritative release process
- [`docs/development/building-the-package.md`](../../../docs/development/building-the-package.md): Building and test-installing the package
- [`.github/workflows/release.yml`](../../../.github/workflows/release.yml): The publishing workflow
- [pypi-recovery.md](pypi-recovery.md): What to do when publishing fails
