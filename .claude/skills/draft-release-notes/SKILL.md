---
name: draft-release-notes
description: Draft the release notes for a NetBox core (this repository, not a plugin) patch release from its GitHub milestone, audit the commits since the previous release for noteworthy changes missing from the milestone, and render the notes as the release PR or GitHub release body. Use when the user asks to draft, preview, or update the release notes or changelog for an upcoming NetBox release, to check a release milestone against the commit log, or when the prepare-release skill reaches its release notes step.
---

# Draft NetBox Release Notes

Each patch release has a GitHub milestone named for it (e.g. `v4.7.5`), and every issue closed as completed must carry one (`.github/workflows/enforce-milestone.yml` reopens any that don't). The milestone is therefore the starting point for the release notes. But it only holds the issues someone assigned to it, so this skill also audits every commit since the previous release for changes the milestone misses. It then turns the issues into a section of `docs/release-notes/version-X.Y.md`.

The notes are published text. Present the draft to the user for review and editing; never commit it unreviewed.

## 1. Gather the Milestone

```bash
gh issue list --milestone vX.Y.Z --state all --limit 200 \
  --json number,title,state,stateReason,labels,url
```

- Warn about any issue still open. The release should not proceed until it is closed or moved to another milestone.
- Skip issues closed as `NOT_PLANNED` or `DUPLICATE`; only `COMPLETED` issues are candidates.

## 2. Audit the Commits Against the Milestone

A change whose issue was never assigned to the milestone, or was assigned to the wrong one, is invisible to step 1, even though it shipped. Check every commit since the previous release:

```bash
git fetch origin main --tags
python3 .claude/skills/draft-release-notes/audit_milestone.py vX.Y.Z
```

The script follows each first-parent commit on `main` since the previous release tag to its PR, and to the issues that the PR closes or the commit subject references (`Fixes #N`). It skips release commits, translation updates, and updates to the list of vouched contributors (`.github/VOUCHED.td`), and prints two tables:

- **Reverts, and commits not linked to the milestone**, with each linked issue's milestone and `type:` label, and the areas of the codebase changed (`app`, `dependencies`, `install`, `schema`, `docs`, `tests`, `tooling`). Reverts are always listed, even when their issue is in the milestone. A commit marked "not on GitHub" hasn't been pushed, so its PR and issues can't be looked up.
- **Milestone issues not linked to any commit**

To audit a past release, pass `--base vPREV --head vX.Y.Z`.

Review every row; the script only finds the gaps, and deciding what's noteworthy is up to you:

- **Linked issue with no milestone, or a different one**: the change shipped in this release, so the issue belongs in this milestone. Propose moving it (`gh issue edit N --milestone vX.Y.Z`). Once the user confirms, it goes through the remaining steps like any other issue.
- **No linked issue**: read the PR and the diff (`gh pr view P --json title,body,files`, `git show --stat <sha>`). Changes confined to `tooling`, `tests`, or `docs` are rarely noteworthy. For any other change, decide whether users would notice it: a bug fix, a change in behavior or in the API, a new feature, a performance change, or a dependency upgrade. If they would, search for an issue the PR should have referenced (`gh search issues --repo netbox-community/netbox "<keywords>"`) and propose assigning it to the milestone. If no issue exists, tell the user; every entry links to an issue, and opening one is up to them.
- **A commit and its revert** cancel out, and neither belongs in the notes. For example, in v4.7.1, the fix for #23097 (which had no milestone) was reverted before the release.
- **Milestone issues not linked to any commit**: confirm that each one actually shipped. It may have been fixed by a commit which didn't reference it (check `git log` for related changes), or closed without a code change (e.g. an investigation, such as #23362 in v4.7.4). Or it may have been fixed on `feature` instead (`git log origin/feature --oneline --grep "#N"`), in which case it belongs in the next minor release's milestone, and not in these notes.

Report a verdict for every row: noteworthy and how to handle it, or not noteworthy and why. Make no milestone changes without the user's confirmation.

## 3. Sort Into Sections

Assign each issue by its `type:` label, then sort each section by ascending issue number:

| Label | Section |
|---|---|
| `type: feature` | `### Enhancements` |
| `type: performance` | `### Performance Improvements` |
| `type: bug` | `### Bug Fixes` |
| `type: housekeeping`, `type: documentation`, `type: translation` | Omitted |
| `type: deprecation`, `type: removal`, or no `type:` label | Flag for the user |

Omit any section that ends up empty.

## 4. Write Each Entry

For each included issue, read the issue body and the PR(s) that closed it:

```bash
gh issue view N --json title,body,closedByPullRequestsReferences
gh pr view P --json title,body,files
```

Use parallel subagents to read the issues when there are more than a dozen or so, asking each one for a proposed entry plus a one-line note on what changed.

Each entry is one line:

```markdown
* [#N](https://github.com/netbox-community/netbox/issues/N) - <description>
```

Write the description for the end user, not from the issue title or the code:

- Describe the effect of the change, so that it makes sense without reading the issue.
- Start with a verb: Add, Fix, Prevent, Restrict, Support, Enable, Correct, Avoid, Display.
- Use "Fix exception when ..." for crashes and HTTP 500 errors.
- Include terms users will search for: exception names, field and parameter names in backticks, "REST API", "GraphQL", the UI view involved.
- No trailing period.

Examples from v4.7.4 (issue title → entry):

| Issue title | Entry |
|---|---|
| Add device from location page has wrong argument | Pre-populate the location when adding a non-racked device from a location's view |
| Every non-bulk change enqueues its own Search cache update job instead of coalescing — RQ queue flood | Coalesce search cache updates rather than enqueuing a background job for each change |
| Bookmark, journal entry and related API endpoints fail for objects without a REST serializer | Fix exception when listing bookmarks, journal entries, and other objects assigned to objects which have no REST API serializer |
| Please add several more basic widely used trunk cable profiles ... | Add 8C1P, 12C1P, and 24C1P trunk cable profiles |

## 5. Flag Judgment Calls

Recommend omitting, but let the user decide:

- Changes with no user-visible effect, such as internal helpers, tests, or CI (e.g. #23432, a TypeScript type guard fix, was left out of v4.7.4).
- Dependency upgrades filed as features (e.g. #23383, an upgrade of `strawberry-graphql-django`).
- Bugs introduced and fixed within the same release cycle, which no user ever saw.

Present every issue in a table grouped as **included**, **omitted**, and **needs your decision**, with a short reason for each omission.

## 6. Add Warnings

Place a warning above the first section for anything a user or operator must act on: an API or GraphQL change they need to adapt to, a dependency upgrade requiring action (the prepare-release skill passes these in), or a new minimum version. State what to do, concretely:

```markdown
!!! warning "GraphQL Circuit Status Values"
    The GraphQL enum for circuit and virtual circuit status ... must be updated to use the prefixed form (e.g. `{exact: STATUS_ACTIVE}`). See [#23469](https://github.com/netbox-community/netbox/issues/23469) for details.
```

Use absolute URLs for links; relative links to other docs pages break in the PR and release bodies.

## 7. Output

The section goes at the top of `docs/release-notes/version-X.Y.md`, directly below the `# NetBox vX.Y` heading, and is separated from the previous release by `---`:

```markdown
# NetBox vX.Y

## vX.Y.Z (YYYY-MM-DD)

!!! warning "..."
    ...

### Enhancements

* ...

### Bug Fixes

* ...

---

## vX.Y.(Z-1) (...)
```

The date is the planned release date (the milestone's due date, and `published` in `netbox/release.yaml`).

## Rendering the PR and Release Bodies

Once the section is in the docs file, render the GitHub bodies from it rather than by hand:

```bash
python3 .claude/skills/draft-release-notes/render_release_notes.py X.Y.Z --format pr       # release PR body
python3 .claude/skills/draft-release-notes/render_release_notes.py X.Y.Z --format release  # GitHub release body
```

The script drops the `## vX.Y.Z` heading and converts admonitions to GitHub alerts (`> [!WARNING]`, dropping the title). The `release` format also promotes `###` headings to `##`, as the release checklist specifies.

## Why These Choices

- **Start from the milestone, then audit the commits.** The milestone provides each change's issue, type label, and context, which commit subjects often lack (e.g. `fix(core): ...`). But the milestone workflow only catches issues closed with no milestone, not issues given the wrong one, or never linked to the fix at all. Only the commit log shows everything that shipped.
- **The audit is scripted, the verdicts aren't.** Mapping some 50 commits to PRs and issues takes one batched GraphQL query in the script, but well over a hundred separate `gh` calls by hand. Whether a change is noteworthy depends on reading it.
- **Entries are rewritten, not copied.** Issue titles describe the reporter's symptom; the notes must describe the change for someone who never saw the issue.
- **Rendering is scripted.** The docs file is the single source of truth, so the PR body and the release body (often created in a later session) can't drift from it or from each other.

## References

- [`docs/development/release-checklist.md`](../../../docs/development/release-checklist.md): Update Version and Changelog
- [`docs/release-notes/`](../../../docs/release-notes/): Past release notes, for style
