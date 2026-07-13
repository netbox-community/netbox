# Release Checklist

This documentation describes the process of packaging and publishing a new NetBox release. There are three types of releases:

* Major release (e.g. v3.7.8 to v4.0.0)
* Minor release (e.g. v4.0.10 to v4.1.0)
* Patch release (e.g. v4.1.0 to v4.1.1)

While major releases generally introduce some very substantial changes to the application, they are typically treated the same as minor version increments for the purpose of release packaging.

For patch releases (e.g. upgrading from v4.2.2 to v4.2.3), begin at the [patch releases](#patch-releases) heading below. For minor or major releases, complete the entire checklist.

## Minor Version Releases

### Address Constrained Dependencies

Sometimes it becomes necessary to constrain dependencies to a particular version, e.g. to work around a bug in a newer release or to avoid a breaking change that we have yet to accommodate. (Another common example is to limit the upstream Django release.) For example:

```
# https://github.com/encode/django-rest-framework/issues/6053
djangorestframework==3.8.1
```

These version constraints are added to `base_requirements.txt` to ensure that newer packages are not installed when updating the pinned dependencies in `requirements.txt` (see the [Update Requirements](#update-python-dependencies) section below). Before each new minor version of NetBox is released, all such constraints on dependent packages should be addressed if feasible. This guards against the collection of stale constraints over time.

### Close the Release Milestone

Close the [release milestone](https://github.com/netbox-community/netbox/milestones) on GitHub after ensuring there are no remaining open issues associated with it.

### Update the Release Notes

Check that a link to the release notes for the new version is present in the navigation menu (defined in `mkdocs.yml`), and that a summary of all major new features has been added to `docs/index.md`.

### Update System Requirements

If a new Django release is adopted or other major dependencies (Python, PostgreSQL, Redis) change:

* Update the installation guide (`docs/installation/index.md`) with the new minimum versions.
* Update the upgrade guide (`docs/installation/upgrading.md`) for the current version.
    * Update the minimum versions for each dependency.
    * Add a new row to the release history table. Bold any version changes for clarity.
* Update the minimum PostgreSQL version in the programming error template (`netbox/templates/exceptions/programming_error.html`).
* Update the minimum and supported Python versions in the project metadata file (`pyproject.toml`)

### Manually Perform a New Install

Start the documentation server and navigate to the current version of the installation docs:

```no-highlight
zensical serve
```

Follow these instructions to perform a new installation of NetBox in a temporary environment. This process must not be automated: The goal of this step is to catch any errors or omissions in the documentation and ensure that it is kept up to date for each release. Make any necessary changes to the documentation before proceeding with the release.

### Test Upgrade Paths

Upgrading from a previous version typically involves database migrations, which must work without errors.
Test the following supported upgrade paths:

- From one minor version to another within the same major version (e.g. 4.0 to 4.1).
- From the latest patch version of the previous minor version (e.g. 3.7 to 4.0 or 4.1).

Prior to release, test all these supported paths by loading demo data from the source version and performing:

```no-highlight
./manage.py migrate
```

### Merge the `feature` Branch

Submit a pull request to merge the `feature` branch into the `main` branch in preparation for its release. Once it has been merged, continue with the section for the patch releases below.

### Rebuild Demo Data (After Release)

After the release of a new minor version, generate a new demo data snapshot compatible with the new release. See the [`netbox-demo-data`](https://github.com/netbox-community/netbox-demo-data) repository for instructions.

---

## Patch Releases

### Create a Release Branch

Begin by creating a new branch (based on `main`) to effect the release. This will comprise the changes listed below.

```
git checkout main
git checkout -B release-vX.Y.Z
```

### Notify netbox-docker Project of Any Relevant Changes

Notify the [`netbox-docker`](https://github.com/netbox-community/netbox-docker) maintainers (in **#netbox-docker**) of any changes that may be relevant to their build process, including:

* Significant changes to `upgrade.sh`
* Increases in minimum versions for service dependencies (PostgreSQL, Redis, etc.)
* Any changes to the reference installation

### Update Python Dependencies

Before each release, update each of NetBox's Python dependencies to its most recent stable version. Loose runtime constraints (and per-package descriptions) live in `base_requirements.txt`; `requirements.txt` is the pinned, top-level dependency file consumed by the release archive, the git install flow (`upgrade.sh`), and the published wheel's dependency metadata. Optional dependency groups (for example `ldap`, `saml2`) are declared in `pyproject.toml`.

To update the pinned requirements:

1. Review each constraint in `base_requirements.txt`.
2. Upgrade the installed version of all required packages in your environment (`pip install -U -r base_requirements.txt`).
3. Run all tests and check that the UI and API function as expected.
4. Review each requirement's release notes for any breaking or otherwise noteworthy changes.
5. If upgrading a dependency is breaking, constrain it in `base_requirements.txt` with an explanatory comment and revisit it for the next major NetBox release (see the [Address Constrained Dependencies](#address-constrained-dependencies) section above).
6. Update the pinned versions in `requirements.txt` to the versions you just tested. Keep `requirements.txt` in the existing bare `package==version` format (one top-level package per line, the same package set as `base_requirements.txt`).
7. Verify there is no drift between the policy file and the pins:

    ```no-highlight
    python3 scripts/verify_dependencies.py
    ```

The published wheel's `Requires-Dist` is generated from `requirements.txt` at build time, so the package installs the same tested pins as the archive and git flows.

### Update UI Dependencies

Check whether any UI dependencies (JavaScript packages, fonts, etc.) need to be updated by running `yarn outdated` from within the `project-static/` directory. [Upgrade these dependencies](./web-ui.md#updating-dependencies) as necessary, then run `yarn bundle` to generate the necessary files for distribution:

```
$ yarn bundle
yarn run v1.22.19
$ node bundle.js
✅ Bundled source file 'styles/external.scss' to 'netbox-external.css'
✅ Bundled source file 'styles/netbox.scss' to 'netbox.css'
✅ Bundled source file 'styles/svg/rack_elevation.scss' to 'rack_elevation.css'
✅ Bundled source file 'styles/svg/cable_trace.scss' to 'cable_trace.css'
✅ Bundled source file 'index.ts' to 'netbox.js'
✅ Copied graphiql files
Done in 1.00s.
```

### Update & Compile Translations

Updated language translations should be pulled from [Transifex](https://app.transifex.com/netbox-community/netbox/dashboard/) and re-compiled for each new release. First, retrieve any updated translation files using the Transifex CLI client:

```no-highlight
tx pull --force
```

Then, compile these portable (`.po`) files for use in the application:

```no-highlight
./manage.py compilemessages
```

!!! tip
    Consult the translation documentation for more detail on [updating translated strings](./translations.md#updating-translated-strings) if you've not set up the Transifex client already.

### Update Version and Changelog

* Update the version number and published date in `netbox/release.yaml`. Add or remove the designation (e.g. `beta1`) if applicable.
* No manual `pyproject.toml` version edit is needed: the package version is derived automatically from `release.yaml` (`version` plus any `designation`) by the build backend.
* Add a section for this release at the top of the changelog page for the minor version (e.g. `docs/release-notes/version-4.2.md`) listing all relevant changes made in this release.

!!! tip
    Put yourself in the shoes of the user when recording change notes. Focus on the effect that each change has for the end user, rather than the specific bits of code that were modified in a PR. Ensure that each message conveys meaning absent context of the initial feature request or bug report. Remember to include keywords or phrases (such as exception names) that can be easily searched.

### Rebuild the Device Type Definition Schema

Run the following command to update the device type definition validation schema:

```nohighlight
./manage.py buildschema --write
```

This will automatically update the schema file at `contrib/generated_schema.json`.

### Update the OpenAPI Schema

!!! warning "Disable all plugins first"
    Before generating the OpenAPI schema, disable any installed plugins. This will prevent their schemas from being pulled into the generated snapshot.

Update the static OpenAPI schema definition at `contrib/openapi.json` with the management command below. If the schema file is up-to-date, only the NetBox version will be changed.

```nohighlight
./manage.py spectacular --format openapi-json > ../contrib/openapi.json
```

### Update Development Dependencies

Keep development tooling versions consistent across the project. If you upgrade a dev-only dependency, update all places where it’s pinned so local tooling and CI run the same versions.

* Ruff
    * `.pre-commit-config.yaml`
    * `.github/workflows/ci.yml`

### Submit a Pull Request

Commit the above changes and submit a pull request titled **"Release vX.Y.Z"** to merge the current release branch (e.g. `release-vX.Y.Z`) into `main`. Copy the documented release notes into the pull request's body.

Once CI has completed and a colleague has reviewed the PR, merge it. This effects a new release in the `main` branch.

!!! warning
    To ensure a streamlined review process, the pull request for a release **must** be limited to the changes outlined in this document. A release PR must never include functional changes to the application: Any unrelated "cleanup" needs to be captured in a separate PR prior to the release being shipped.

### Create a New Release

Create a [new release](https://github.com/netbox-community/netbox/releases/new) on GitHub with the following parameters.

* **Tag:** Current version (e.g. `v4.2.1`)
* **Target:** `main`
* **Title:** Version and date (e.g. `v4.2.1 - 2025-01-17`)
* **Description:** Copy from the pull request body, then promote the `###` headers to `##` ones

Once created, the release will become available for users to install from GitHub.

### Publish to Test PyPI

Pushing a release tag triggers the Python package publishing workflow, which publishes the tagged release automatically to **Test PyPI** for maintainer validation. Installing NetBox via pip is not a supported installation path during the v4.6.x preview period; production PyPI publishing is planned for the v4.7.0 feature branch. A manual `workflow_dispatch` run publishes to Test PyPI only when the selected ref is a `v*` release tag; dispatching from a branch runs the build and verification jobs as a dry run without publishing.

After a publish run completes:

* Verify that the build, CLI smoke-test (`cli-smoke-test`), smoke-test, dependency-verification (`verify-dependencies`), and sdist-verification (`verify-sdist`) jobs succeeded. The dependency-verification job fails the release if `requirements.txt` has drifted from `base_requirements.txt` or if the built wheel's `Requires-Dist` does not match `requirements.txt`; the sdist-verification job fails it if the sdist ships unexpected configuration files or cannot rebuild a valid wheel.
* Verify that the publish job used the expected trusted-publishing environment (`testpypi`).
* Confirm that the new version is visible on Test PyPI.
* Install the published wheel into a fresh virtual environment and run `netbox check` against a minimal configuration module. The preview artifact is published to Test PyPI while NetBox's pinned runtime dependencies are expected to resolve from PyPI; to avoid mixed-index dependency resolution during validation, install the pinned dependencies from PyPI first, then install the Test PyPI artifact without resolving dependencies again:

    ```no-highlight
    pip install -r requirements.txt
    pip install --no-deps --index-url https://test.pypi.org/simple/ netbox==<version>
    ```

!!! note "Trusted publishing prerequisites"
    Publishing requires a one-time setup by the project owners: a `netbox` project and a configured GitHub trusted publisher on Test PyPI, plus the corresponding `testpypi` GitHub Actions environment.

The published package version is derived from `netbox/release.yaml` (the `version` field plus any `designation`, e.g. `beta1` becomes `4.7.0b1`), not from the git tag. Ensure the tag and `release.yaml` agree before tagging a pre-release.
