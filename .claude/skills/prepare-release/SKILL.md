---
name: prepare-release
description: Prepare a NetBox core (this repository, not a plugin) patch release vX.Y.Z up to an open release PR — upgrade Python, UI, and dev dependencies, pull translations, bump release.yaml, draft the release notes, regenerate the schemas, validate, and open the "Release vX.Y.Z" pull request. Use when a maintainer asks to prepare, cut, or start a NetBox release. Publishing after the PR merges is the publish-release skill.
---

# Prepare a NetBox Patch Release

This skill automates the [Patch Releases](../../../docs/development/release-checklist.md#patch-releases) section of the release checklist, up to opening the release PR. The checklist remains the authoritative process; if the two disagree, follow the checklist and point out the discrepancy.

**Ground rules**

- **The release PR contains only release changes.** Never fix application code, tests, or lint on the release branch. If an upgrade breaks something, hold it back (step 3) and report it; the fix belongs in a separate PR merged before the release.
- **Confirm before anything outward-facing**: pushing, opening the PR, or editing milestones and issues.
- **Report problems early.** Each step lists what to check; stop and ask whenever something unexpected turns up rather than working around it.
- Run all commands from the repository root, with the NetBox venv active, unless stated otherwise. Write temporary files to the session scratchpad (`$SCRATCH` below), not `/tmp`.

## 0. Inputs

- **Version**: default to a patch bump of `version` in `netbox/release.yaml`. Confirm that an open milestone with the same name exists:

    ```bash
    gh api 'repos/netbox-community/netbox/milestones?state=open&per_page=100' \
      --jq '.[] | select(.title == "vX.Y.Z") | {number, due_on, open_issues, closed_issues}'
    ```

- **Release date**: default to the milestone's `due_on` date.

Confirm both with the user before continuing.

**This skill covers patch releases only.** If the version is `X.Y.0`, or carries a designation such as `beta1` or `rc1`, stop: minor and pre-releases need the manual steps in the checklist's Minor Version Releases section (new install, upgrade path tests, merging `feature`) and target different branches.

## 1. Preflight

Run every check, then report all failures together. All are read-only.

```bash
git fetch origin --tags
git status --porcelain                                  # must be empty
git rev-parse --abbrev-ref HEAD                         # must be main
git rev-parse main origin/main                          # must match
git remote get-url origin                               # must be netbox-community/netbox
gh repo set-default --view                              # must be netbox-community/netbox
gh api repos/netbox-community/netbox --jq .permissions.push   # must be true
gh api orgs/netboxlabs/members/$(gh api user -q .login) --silent   # must succeed
gh run list --workflow ci.yml --branch main --limit 3 --json headSha,status,conclusion
pgrep -af '[m]anage.py test'                            # must find no other test run
```

- **gh default repository**: the `gh` commands in this skill and in `draft-release-notes` rely on it. If it's unset or points at a fork, ask the user to run `gh repo set-default netbox-community/netbox`.
- **CI**: the most recent completed run on `main` must have succeeded. CI skips commits that touch only translations, `contrib/`, or issue templates, so HEAD may have no run of its own; if so, confirm with `git diff --stat <run headSha>..origin/main` that only such paths changed since.
- **Milestone**: `open_issues` must be 0. Otherwise list the open issues and ask whether to wait or move them to the next milestone (`gh issue edit N --milestone vX.Y.(Z+1)`, only after confirmation).
- **Test runs**: the brackets in the `pgrep` pattern stop it from matching the shell that runs it. Without them, it always finds a match.
- **Maintainer status**: a release PR has no linked issue. `AGENTS.md` waives that requirement only for maintainers (members of the `netboxlabs` GitHub organization), which the membership check confirms. Push permission is needed as well, to push the release branch.
- **Tools**: `tx` with a token (`~/.transifexrc` or `$TX_TOKEN`), `msgfmt` (gettext), `zensical`, and the UI package manager matching the lockfile in `netbox/project-static/` (`yarn.lock` → yarn 1; `package-lock.json` → npm). If `netbox/project-static/.nvmrc` exists, `node --version` must satisfy it.

## 2. Create the Release Branch

```bash
git checkout -B release-vX.Y.Z main
```

## 3. Update Python Dependencies

`base_requirements.txt` holds the loose constraints, plus a comment above each package with its changelog URL. `requirements.txt` holds the exact pins that ship.

1. Upgrade the active venv to the latest allowed versions (this is the checklist's procedure, and it modifies the developer's venv):

    ```bash
    pip install -U -r base_requirements.txt
    pip check
    ```

2. Rewrite the pins from the installed versions, keeping the existing `package[extras]==version` format:

    ```bash
    python - <<'PY'
    import re
    from importlib.metadata import version
    from pathlib import Path

    path = Path('requirements.txt')
    lines = []
    for line in path.read_text().splitlines():
        name, extras = re.match(r'^([A-Za-z0-9_.-]+)(\[[^\]]*\])?==', line).groups()
        lines.append(f'{name}{extras or ""}=={version(name)}')
    path.write_text('\n'.join(lines) + '\n')
    PY
    git diff requirements.txt
    ```

3. Review the changelog of every upgraded package across the full version range, using the URL from its comment in `base_requirements.txt`. Use parallel subagents when there are more than a few. Classify each upgrade:
    - **Breaking**: affects NetBox or its users (removed APIs, changed defaults, new minimum versions of Python/PostgreSQL/Django).
    - **Needs a release note warning**: users or operators must act (e.g. the sorl-thumbnail 13.4.0 upgrade in v4.7.4 required `manage.py thumbnail clear` for some storage setups).
    - **Routine**.
4. If an upgrade breaks something (here, or in the tests in step 10), hold it back: constrain it in `base_requirements.txt` with a comment explaining why (and linking the upstream issue, if there is one), reinstall the previous version, and restore its pin. Report every hold to the user. If step 8 has already run, run it again, so that the schemas match the versions that ship.
5. Verify the pins match the constraints:

    ```bash
    python3 scripts/verify_dependencies.py
    ```

## 4. Update UI Dependencies

Work in `netbox/project-static/`. Pick the commands by lockfile.

**npm** (`package-lock.json`):

```bash
npm ci
npm run upgrade    # upgrades all but the held dependencies, and explains what remains behind
npm run check
npm run build
```

**yarn** (`yarn.lock`):

```bash
yarn install --frozen-lockfile
yarn outdated
```

Upgrade patch and minor updates, keeping each entry's existing version style in `package.json`. `yarn upgrade` writes exactly the version spec it's given:

- Under `dependencies` (exact pins): `yarn upgrade <package>@<version>`
- Under `devDependencies` (caret ranges): `yarn upgrade '<package>@^<version>'`

Ask the user about each major upgrade, and about any minor upgrade of `@tabler/core` or `bootstrap`, which take patch releases only. Then:

```bash
yarn validate
yarn bundle
```

**Either way**, stage the rebuilt bundles, then run `scripts/verify-bundles.sh` from the repository root:

```bash
git add netbox/project-static/dist/
scripts/verify-bundles.sh
git diff --cached --stat netbox/project-static/dist/
```

The script rebuilds the bundles and fails if the result differs from the files in the index. Unstaged changes in `dist/` would make it fail even when the build is fine, which is why the bundles are staged first. The last command shows the change in each bundle's size (the bundles are marked binary in `.gitattributes`, so the diffstat reports bytes). Flag any large change for the user.

## 5. Update Translations

1. Ask the user to confirm that they have checked the [Transifex dashboard](https://app.transifex.com/netbox-community/netbox/dashboard/) and machine-translated any language not marked _ready for use_ (see [translations.md](../../../docs/development/translations.md#updating-translated-strings)). This step can't be automated.
2. Pull and compile:

    ```bash
    tx pull --force
    (cd netbox && python manage.py compilemessages)
    ```

3. Confirm that only translation files changed; this should print nothing:

    ```bash
    git status --porcelain netbox/translations | grep -vE 'LC_MESSAGES/django\.(po|mo)$'
    ```

## 6. Bump the Version

Set `version` and `published` in `netbox/release.yaml`:

```yaml
version: "X.Y.Z"
edition: "Community"
published: "YYYY-MM-DD"
```

Do this before step 8: the OpenAPI schema embeds the version. Don't edit `pyproject.toml`; the package version is derived from `release.yaml`.

## 7. Write the Release Notes

Follow the `draft-release-notes` skill, passing it the upgrades that need a warning from step 3. Its commit audit checks every commit since the previous release for noteworthy changes that the milestone misses, and may propose assigning issues to the milestone (confirm each change with the user). Insert the section at the top of `docs/release-notes/version-X.Y.md`.

Then stop and ask the user to review and edit the notes. They are published under the user's name, so they should be in the user's own words (see `AI_POLICY.md`).

## 8. Regenerate the Schemas

Device type definition schema:

```bash
(cd netbox && python manage.py buildschema --write)
```

OpenAPI schema, generated with all plugins disabled. Use a configuration module derived from the testing configuration, so that the output doesn't depend on the local `configuration.py`:

```bash
printf 'from netbox.configuration_testing import *  # noqa: F403\n\nPLUGINS = []\n' > $SCRATCH/release_schema_config.py
(cd netbox && PYTHONPATH=$SCRATCH NETBOX_CONFIGURATION=release_schema_config \
  python manage.py spectacular --format openapi-json > $SCRATCH/openapi.json) \
  && test -s $SCRATCH/openapi.json && cp $SCRATCH/openapi.json contrib/openapi.json
```

The schema is written to the scratchpad first, so a failed run can't leave `contrib/openapi.json` empty. If the command fails, stop and report the error.

Check the result:

- `grep -c '"/api/plugins/' contrib/openapi.json` prints `0`.
- `info.version` in `contrib/openapi.json` is `X.Y.Z`.
- Every other change in `git diff contrib/openapi.json` corresponds to an API change merged this cycle. Flag any that doesn't, because it suggests an unexpected effect of a dependency upgrade.

## 9. Update Development Dependencies

Ruff is pinned in three places, which must agree:

- `.pre-commit-config.yaml`: `rev: vX` under `ruff-pre-commit`
- `.github/workflows/ci.yml`: `version: "X"` under `ruff-action`
- `pyproject.toml`: `ruff==X` in the `dev` group

Look up the latest release (`curl -s https://pypi.org/pypi/ruff/json | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["version"])'`). If it's newer, update all three pins, then `pip install ruff==X` and run `ruff check`. If the new version reports any violations, revert the three pins and tell the user: fixing them is cleanup, which belongs in its own PR.

## 10. Validate

1. Run the full test suite with the `run-tests` skill. Check `pgrep -af '[m]anage.py test'` immediately beforehand, and run it in the background. On a failure, first rule out the test harness: re-run the failing tests without `--parallel`, against a freshly built database (`--noinput`, without `--keepdb`). Then find the responsible upgrade, by reinstalling previous versions one at a time, and hold it back (step 3).

    After holding back any upgrade, rebuild whatever was generated with it before continuing. For a Python package, re-run step 8 (the schemas). For a UI package, restore its previous version in `package.json` and the lockfile, then rebuild, stage, and verify the bundles as at the end of step 4. Then re-run the tests.
2. Run the remaining checks:

    ```bash
    (cd netbox && python manage.py check && python manage.py makemigrations --check --dry-run)
    ruff check
    zensical build
    python3 scripts/verify_dependencies.py
    ```

    A dependency upgrade can generate new migrations; treat any as a breaking upgrade.
3. Start the development server (`python manage.py runserver` from `netbox/`, in the background). Confirm that `/login/` returns HTTP 200 and that `/static/netbox.js` is served. Then ask the user to log in and click through the UI, the REST API browser, and GraphiQL before you continue. Stop the server afterward.

## 11. Check the Scope

`git status --porcelain` may list only these paths:

- `base_requirements.txt`, `requirements.txt`
- `netbox/project-static/package.json`, the lockfile, and `netbox/project-static/dist/`
- `netbox/translations/*/LC_MESSAGES/django.{po,mo}`
- `netbox/release.yaml`
- `docs/release-notes/version-X.Y.md`
- `contrib/generated_schema.json`, `contrib/openapi.json`
- `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `pyproject.toml` (ruff pins only)

A dependency upgrade sometimes forces a change to the documentation build configuration (e.g. v4.7.4 changed `mkdocs.yml` after `mkdocs-material` was dropped). Such a change needs the user's explicit sign-off. For anything else, stop and ask.

## 12. Commit and Open the PR

Confirm with the user before pushing. Then stage files by explicit path (never `git add -A`) and commit with the pre-commit hooks enabled:

```bash
git add <paths from step 11>
git commit -m "Release vX.Y.Z"
git push -u origin release-vX.Y.Z

python3 .claude/skills/draft-release-notes/render_release_notes.py X.Y.Z --format pr > $SCRATCH/pr-body.md
gh pr create --repo netbox-community/netbox --base main --head release-vX.Y.Z \
  --title "Release vX.Y.Z" --body-file $SCRATCH/pr-body.md
```

Ask the user who should review the PR, and add them with `gh pr edit --add-reviewer`. Don't add any "generated by" text to the commit or the PR.

## 13. Hand Off

Summarize for the user:

- Upgraded dependencies worth knowing about, and any that were held back (with reasons)
- Release note judgment calls they made, or still need to make
- The PR URL

Once CI passes, a colleague approves, and the PR is merged, the next step is the `publish-release` skill.

## Why These Choices

- **Version before schemas.** `spectacular` writes the version from `release.yaml` into `contrib/openapi.json`; generating it first leaves a stale version in the schema.
- **A plugin-free configuration derived from the testing configuration.** The checklist requires disabling plugins. A fixed configuration makes the output the same for every maintainer, regardless of their local `configuration.py`.
- **Hold, don't fix.** The checklist forbids functional changes in a release PR so that it can be reviewed quickly. A pin constraint keeps the release moving, and the real fix gets its own review.
- **The milestone date is the release date.** Each patch milestone's due date is the planned release date, and it becomes `published` in `release.yaml` and the release title.

## References

- [`docs/development/release-checklist.md`](../../../docs/development/release-checklist.md): The authoritative release process
- [`docs/development/web-ui.md`](../../../docs/development/web-ui.md): UI dependency management
- [`docs/development/translations.md`](../../../docs/development/translations.md): Transifex setup
- [`scripts/verify_dependencies.py`](../../../scripts/verify_dependencies.py), [`scripts/verify-bundles.sh`](../../../scripts/verify-bundles.sh): Checks also run by CI
- `draft-release-notes` and `run-tests` skills
