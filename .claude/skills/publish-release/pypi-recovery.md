# Recovering From a Failed Publish

This guide condenses the "Production PyPI uploads are final" warning in the [release checklist](../../../docs/development/release-checklist.md#publish-to-pypi). Every recovery action here is outward-facing: present the diagnosis and the proposed action, and wait for the user to confirm.

## A Build or Verification Job Failed

The publish jobs depend on every verification job, so nothing has been uploaded. Read the failed job's log:

```bash
gh run view <run id> --repo netbox-community/netbox --log-failed
```

- **Verify the release tag** (in the build job): the tag doesn't match the version in `netbox/release.yaml`. The tag points at the wrong commit, or `release.yaml` wasn't bumped.
- **verify-dependencies**: `requirements.txt` has drifted from `base_requirements.txt`, or the wheel's `Requires-Dist` doesn't match `requirements.txt`.
- **verify-sdist**: the sdist ships unexpected configuration files, or can't rebuild a valid wheel.
- **smoke-test** or **cli-smoke-test**: the installed wheel fails `netbox check`, `netbox upgrade`, or its CLI commands.

Each of these needs a fix merged to `main`. Since the tag and the GitHub release already exist, discuss with the user whether to delete and recreate the release and its tag at the fixed commit (nothing has reached PyPI, so the version is still free), or to ship the fix as the next patch version.

## The Publish Job Failed

First, find out whether PyPI accepted any file:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/netbox/X.Y.Z/json   # 404: nothing accepted
gh run view <run id> --repo netbox-community/netbox --log-failed
```

Then:

1. **No file accepted, and the cause can be fixed without changing the built distributions** (e.g. a trusted publisher or environment misconfiguration): once the user has fixed the cause, re-run only the failed publish job. This reuses the artifacts the original run built and verified:

    ```bash
    gh run view <run id> --repo netbox-community/netbox --json jobs --jq '.jobs[] | "\(.databaseId) \(.name) \(.conclusion)"'
    gh run rerun <run id> --repo netbox-community/netbox --job <publish job id>
    ```

    **Never re-run all jobs** (or use the Re-run all jobs button): that rebuilds the distributions.

2. **The fix requires changing package contents or metadata**: prepare a new NetBox version and tag. The current one can't be reused.

3. **PyPI accepted either file**: don't retry. Production publishing fails on duplicate filenames by design, so a retry fails at the file already accepted. Instead:
    - Record the accepted filenames and their SHA-256 hashes (the job log prints them).
    - Ask the user to yank the incomplete release on PyPI. This is done in the PyPI web UI, by a project owner.
    - Publish a new NetBox version. Never combine files from separate builds.

## Optional: Rehearse on Test PyPI

A rehearsal is useful after changes to packaging or publishing, but isn't needed for every release. Dispatch it from the release tag while the production deployment is still awaiting approval, and approve production only after the rehearsal succeeds:

```bash
gh workflow run release.yml --repo netbox-community/netbox --ref vX.Y.Z
```

The rehearsal rebuilds the distributions, so it validates the packaging and publishing path, not the exact files awaiting production approval. Test PyPI also never accepts the same filename twice: once it has accepted a file for a tag, dispatching that tag again fails, and a further rehearsal needs a new version.

To test the rehearsal package, create a fresh venv (the one in step 5 of the skill doesn't exist yet at this point). Install the pinned runtime dependencies from PyPI first, then the candidate alone from Test PyPI:

```bash
rm -rf $SCRATCH/netbox-rehearsal
python3 -m venv $SCRATCH/netbox-rehearsal
$SCRATCH/netbox-rehearsal/bin/python -m pip install --upgrade pip
$SCRATCH/netbox-rehearsal/bin/python -m pip install -r requirements.txt
$SCRATCH/netbox-rehearsal/bin/python -m pip install --no-deps \
  --index-url https://test.pypi.org/simple/ "netbox==X.Y.Z"
```

Then run `netbox --version` and `netbox check` from `$SCRATCH/netbox-rehearsal/bin/`, with the environment variables shown in step 5 of the skill.

Dispatching the workflow from a branch, rather than a tag, runs the build and verification jobs as a dry run without publishing anywhere.
