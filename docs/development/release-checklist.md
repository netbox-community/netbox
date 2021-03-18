# Release Checklist

## Minor Version Bumps

### Address Pinned Dependencies

Check `base_requirements.txt` for any dependencies pinned to a specific version, and upgrade them to their most stable release (where possible).

### Update Static Libraries

Update the following static libraries to their most recent stable release:

* Bootstrap 3
* Material Design Icons
* Select2
* jQuery
* jQuery UI

### Link to the Release Notes Page

Add the release notes (`/docs/release-notes/X.Y.md`) to the table of contents within `mkdocs.yml`, and point `index.md` to the new file.

### Manually Perform a New Install

Install `mkdocs` in your local environment, then start the documentation server:

```no-highlight
$ pip install -r docs/requirements.txt
$ mkdocs serve
```

Follow these instructions to perform a new installation of NetBox. This process must _not_ be automated: The goal of this step is to catch any errors or omissions in the documentation, and ensure that it is kept up-to-date for each release. Make any necessary changes to the documentation before proceeding with the release.

### Close the Release Milestone

Close the release milestone on GitHub after ensuring there are no remaining open issues associated with it.

### Merge the Release Branch

Submit a pull request to merge the `feature` branch into the `develop` branch in preparation for its release.

---

## All Releases

### Update Requirements

Required Python packages are maintained in two files. `base_requirements.txt` contains a list of all the packages required by NetBox. Some of them may be pinned to a specific version of the package due to a known issue. For example:

```
# https://github.com/encode/django-rest-framework/issues/6053
djangorestframework==3.8.1
```

The other file is `requirements.txt`, which lists each of the required packages pinned to its current stable version. When NetBox is installed, the Python environment is configured to match this file. This helps ensure that a new release of a dependency doesn't break NetBox.

Every release should refresh `requirements.txt` so that it lists the most recent stable release of each package. To do this:

1. Create a new virtual environment.
2. Install the latest version of all required packages `pip install -U -r base_requirements.txt`).
3. Run all tests and check that the UI and API function as expected.
4. Review each requirement's release notes for any breaking or otherwise noteworthy changes.
5. Update the package versions in `requirements.txt` as appropriate.

In cases where upgrading a dependency to its most recent release is breaking, it should be pinned to its current minor version in `base_requirements.txt` (with an explanatory comment) and revisited for the next major NetBox release.

### Verify CI Build Status

Ensure that continuous integration testing on the `develop` branch is completing successfully.

### Update Version and Changelog

Update the `VERSION` constant in `settings.py` to the new release version and annotate the current data in the release notes for the new version. Commit these changes to the `develop` branch.

### Submit a Pull Request

Submit a pull request title **"Release vX.Y.Z"** to merge the `develop` branch into `master`. Copy the documented release notes into the pull request's body.

Once CI has completed on the PR, merge it.

### Create a New Release

Draft a [new release](https://github.com/netbox-community/netbox/releases/new) with the following parameters.

* **Tag:** Current version (e.g. `v2.9.9`)
* **Target:** `master`
* **Title:** Version and date (e.g. `v2.9.9 - 2020-11-09`)

Copy the description from the pull request to the release.

### Update the Development Version

On the `develop` branch, update `VERSION` in `settings.py` to point to the next release. For example, if you just released v2.9.9, set:

```
VERSION = 'v2.9.10-dev'
```
