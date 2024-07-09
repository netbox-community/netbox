# Release Checklist

This documentation describes the process of packaging and publishing a new NetBox release. There are three types of release:

* Major release (e.g. v2.11 to v3.0)
* Minor release (e.g. v3.2 to v3.3)
* Patch release (e.g. v3.3.0 to v3.3.1)

While major releases generally introduce some very substantial change to the application, they are typically treated the same as minor version increments for the purpose of release packaging.

## Minor Version Releases

### Address Constrained Dependencies

Sometimes it becomes necessary to constrain dependencies to a particular version, e.g. to work around a bug in a newer release or to avoid a breaking change that we have yet to accommodate. (Another common example is to limit the upstream Django release.) For example:

```
# https://github.com/encode/django-rest-framework/issues/6053
djangorestframework==3.8.1
```

These version constraints are added to `base_requirements.txt` to ensure that newer packages are not installed when updating the pinned dependencies in `requirements.txt` (see the [Update Requirements](#update-requirements) section below). Before each new minor version of NetBox is released, all such constraints on dependent packages should be addressed if feasible. This guards against the collection of stale constraints over time.

### Close the Release Milestone

Close the [release milestone](https://github.com/netbox-community/netbox/milestones) on GitHub after ensuring there are no remaining open issues associated with it.

### Update the Release Notes

Check that a link to the release notes for the new version is present in the navigation menu (defined in `mkdocs.yml`), and that a summary of all major new features has been added to `docs/index.md`.

### Manually Perform a New Install

Start the documentation server and navigate to the current version of the installation docs:

```no-highlight
mkdocs serve
```

Follow these instructions to perform a new installation of NetBox in a temporary environment. This process must not be automated: The goal of this step is to catch any errors or omissions in the documentation, and ensure that it is kept up-to-date for each release. Make any necessary changes to the documentation before proceeding with the release.

### Merge the Release Branch

Submit a pull request to merge the `feature` branch into the `develop` branch in preparation for its release. Once it has been merged, continue with the section for patch releases below.

### Rebuild Demo Data (After Release)

After the release of a new minor version, generate a new demo data snapshot compatible with the new release. See the [`netbox-demo-data`](https://github.com/netbox-community/netbox-demo-data) repository for instructions.

---

## Patch Releases

### Notify netbox-docker Project of Any Relevant Changes

Notify the [`netbox-docker`](https://github.com/netbox-community/netbox-docker) maintainers (in **#netbox-docker**) of any changes that may be relevant to their build process, including:

* Significant changes to `upgrade.sh`
* Increases in minimum versions for service dependencies (PostgreSQL, Redis, etc.)
* Any changes to the reference installation

### Update Python Dependencies

Before each release, update each of NetBox's Python dependencies to its most recent stable version. These are defined in `requirements.txt`, which is updated from `base_requirements.txt` using `pip`. To do this:

1. Upgrade the installed version of all required packages in your environment (`pip install -U -r base_requirements.txt`).
2. Run all tests and check that the UI and API function as expected.
3. Review each requirement's release notes for any breaking or otherwise noteworthy changes.
4. Update the package versions in `requirements.txt` as appropriate.

In cases where upgrading a dependency to its most recent release is breaking, it should be constrained to its current minor version in `base_requirements.txt` with an explanatory comment and revisited for the next major NetBox release (see the [Address Constrained Dependencies](#address-constrained-dependencies) section above).

### Update UI Dependencies

Check whether any UI dependencies (JavaScript packages, fonts, etc.) need to be updated by running `yarn outdated` from within the `project-static/` directory. [Upgrade these dependencies](./web-ui.md#updating-dependencies) as necessary, then run `yarn bundle` to generate the necessary files for distribution.

### Rebuild the Device Type Definition Schema

Run the following command to update the device type definition validation schema:

```nohighlight
./manage.py buildschema --write
```

This will automatically update the schema file at `contrib/generated_schema.json`.

### Update & Compile Translations

Updated language translations should be pulled from [Transifex](https://app.transifex.com/netbox-community/netbox/dashboard/) and re-compiled for each new release. Follow the documented process for [updating translated strings](./translations.md#updating-translated-strings) to do this.

### Update Version and Changelog

* Update the `VERSION` constant in `settings.py` to the new release version.
* Update the example version numbers in the feature request and bug report templates under `.github/ISSUE_TEMPLATES/`.
* Replace the "FUTURE" placeholder in the release notes with the current date.

Commit these changes to the `develop` branch and push upstream.

### Verify CI Build Status

Ensure that continuous integration testing on the `develop` branch is completing successfully. If it fails, take action to correct the failure before proceeding with the release.

### Submit a Pull Request

Submit a pull request titled **"Release vX.Y.Z"** to merge the `develop` branch into `master`. Copy the documented release notes into the pull request's body.

Once CI has completed on the PR, merge it. This effects a new release in the `master` branch.

### Create a New Release

Create a [new release](https://github.com/netbox-community/netbox/releases/new) on GitHub with the following parameters.

* **Tag:** Current version (e.g. `v3.3.1`)
* **Target:** `master`
* **Title:** Version and date (e.g. `v3.3.1 - 2022-08-25`)
* **Description:** Copy from the pull request body

Once created, the release will become available for users to install.

### Update the Development Version

On the `develop` branch, update `VERSION` in `settings.py` to point to the next release. For example, if you just released v3.3.1, set:

```
VERSION = 'v3.3.2-dev'
```

Commit this change with the comment "PRVB" (for _post-release version bump_) and push the commit upstream.

### Update the Public Documentation

After a release has been published, the public NetBox documentation needs to be updated. This is accomplished by running two actions on the [netboxlabs-docs](https://github.com/netboxlabs/netboxlabs-docs) repository.

First, run the `build-site` action, by navigating to Actions > build-site > Run workflow. This process compiles the documentation along with an overlay for integration with the documentation portal at <https://netboxlabs.com/docs>. The job should take about two minutes.

Once the documentation files have been compiled, they must be published by running the `deploy-kinsta` action. Select the desired deployment environment (staging or production) and specify `latest` as the deploy tag.

Clear the CDN cache from the [Kinsta](https://my.kinsta.com/) portal. Navigate to _Sites_ / _NetBox Labs_ / _Live_, select _CDN_ in the left-nav, click the _Clear CDN cache_ button, and confirm the clear operation.

Finally, verify that the documentation at <https://netboxlabs.com/docs/netbox/en/stable/> has been updated.
