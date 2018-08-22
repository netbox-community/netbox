# Minor Version Bumps

## Update Requirements

Required Python packages are maintained in two files. `base_requirements.txt` contains a list of all the packages required by NetBox. Some of them may be pinned to a specific version of the package due to a known issue. For example:

```
# https://github.com/encode/django-rest-framework/issues/6053
djangorestframework==3.8.1
```

The other file is `requirements.txt`, which lists each of the required packages pinned to its current stable version. When NetBox is installed, the Python environment is configured to match this file. This helps ensure that a new release of a dependency doesn't break NetBox.

Every minor version release should refresh `requirements.txt` so that it lists the most recent stable release of each package. To do this:

1. Create a new virtual environment.
2. Install the latest version of all required packages via pip:

```
pip install -U -r base_requirements.txt
```

3. Run all tests and check that the UI and API function as expected.
4. Update the package versions in `requirements.txt` as appropriate.

## Update Static Libraries

Update the following static libraries to their most recent stable release:

* Bootstrap 3
* Font Awesome 4
* jQuery
* jQuery UI

## Manually Perform a New Install

Create a new installation of NetBox by following [the current documentation](http://netbox.readthedocs.io/en/latest/). This should be a manual process, so that issues with the documentation can be identified and corrected.

## Close the Release Milestone

Close the release milestone on GitHub. Ensure that there are no remaining open issues associated with it.

---

# All Releases

## Verify CI Build Status

Ensure that continuous integration testing on the `develop` branch is completing successfully.

## Update Version and Changelog

Update the `VERSION` constant in `settings.py` to the new release version and add the current date to the release notes in `CHANGELOG.md`.

## Submit a Pull Request

Submit a pull request title **"Release vX.Y.X"** to merge the `develop` branch into `master`. Include a brief change log listing the features, improvements, and/or bugs addressed in the release.

Once CI has completed on the PR, merge it.

## Create a New Release

Draft a [new release](https://github.com/digitalocean/netbox/releases/new) with the following parameters.

* **Tag:** Current version (e.g. `v2.3.4`)
* **Target:** `master`
* **Title:** Version and date (e.g. `v2.3.4 - 2018-08-02`)

Copy the description from the pull request into the release notes.

## Update the Development Version

On the `develop` branch, update `VERSION` in `settings.py` to point to the next release. For example, if you just released v2.3.4, set:

```
VERSION = 'v2.3.5-dev'
```

## Announce the Release

Announce the release on the [mailing list](https://groups.google.com/forum/#!forum/netbox-discuss). Include a link to the release and the (HTML-formatted) release notes.
