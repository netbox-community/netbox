# Building the Package

NetBox package artifacts (a wheel and a source distribution) can be built and verified locally. During the v4.6.x preview period, published artifacts are intended for maintainer validation only, and installing NetBox via pip is not a supported installation path; experimental support for installing from production PyPI is planned for NetBox v4.7.0. This page is intended for maintainers and contributors working on the packaging itself; routine development does not require building a package.

The artifacts are always built by CI from a clean checkout (see `.github/workflows/release.yml`). A local build is useful for testing packaging changes before they are merged.

## Prerequisites

Install the minimum local build tooling (all three are also included in the `dev` optional dependency group):

```no-highlight
python -m pip install --upgrade build packaging twine
```

## Building

Build both the source distribution (sdist) and the wheel into `dist/`:

```no-highlight
python -m build
```

To build only the wheel (faster, and the form most useful for a quick local install test):

```no-highlight
python -m build --wheel
```

The package version and the wheel's runtime dependency metadata are both computed at build time by a Hatchling hook; see [Dynamic metadata](#dynamic-metadata) below.

## Clean-tree caveat

Always build release artifacts from a clean checkout. The build configuration keeps deployment-local files out of the artifacts: the Hatch excludes drop every `configuration*.py` and `ldap_config*.py` except the two tracked configuration templates (`configuration_example.py` and `configuration_testing.py`, which are force-included explicitly), and CI verifies the contents of both the wheel and the sdist before anything is published.

These checks are defense in depth, not a license to build from a dirty tree: other untracked files under `netbox/` can still be picked up by a local build. CI builds from a clean checkout, so the published artifacts are unaffected. For a comparable local build, use a fresh `git clone` or a separate clean worktree rather than your day-to-day development tree.

## Verifying

Check the built artifacts for valid metadata and rendering:

```no-highlight
twine check dist/*
```

Confirm the wheel's version, dependency metadata, and extras match `netbox/release.yaml`, the pinned `requirements.txt`, and the declared optional-dependency groups:

```no-highlight
python scripts/verify_wheel_metadata.py dist/*.whl
```

Confirm the artifacts ship only the two tracked configuration templates, and that the wheel carries the runtime-critical bundled data (`_data/release.yaml`, `_data/mkdocs.yml`, templates, translations, static assets, and the documentation sources; the same content checks CI runs before publishing):

```no-highlight
python scripts/verify_wheel_contents.py dist/*.whl
python scripts/verify_sdist_contents.py dist/*.tar.gz
```

Confirm `requirements.txt` is still consistent with the maintainer policy in `base_requirements.txt` (the same drift guard CI runs before publishing):

```no-highlight
python scripts/verify_dependencies.py
```

## Test-installing the wheel

Install the wheel into a throwaway virtual environment and run the system checks to confirm the package is importable and runnable:

```no-highlight
python -m venv /tmp/netbox-build-test
/tmp/netbox-build-test/bin/python -m pip install --upgrade pip
/tmp/netbox-build-test/bin/python -m pip install dist/*.whl
PYTHONPATH=$PWD/scripts \
NETBOX_CONFIGURATION=smoketest_configuration \
NETBOX_SMOKETEST_BASE=/tmp/netbox-build-test-root \
/tmp/netbox-build-test/bin/netbox check
```

Without configuration, a wheel-installed NetBox looks for `$NETBOX_ROOT/conf/configuration.py` (default `/opt/netbox/conf/configuration.py`), which normally does not exist on a development workstation. The environment variables above point `netbox check` at the same minimal configuration module the release workflow's smoke-test job uses (`scripts/smoketest_configuration.py`); run the command from the repository root so `PYTHONPATH` can find it. `NETBOX_SMOKETEST_BASE` sets the writable scratch directory under which the module creates its media, reports, scripts, and static roots. Any other importable configuration module works the same way via `NETBOX_CONFIGURATION` (and `PYTHONPATH`, if the configuration lives outside the package). To exercise the full post-install task sequence from the wheel, run `netbox upgrade --no-input` (add `--build-docs` to also build the local documentation) against a throwaway database; this is what the release workflow's smoke-test job does.

## Packaging architecture

This section is a developer-facing overview of how the package is assembled and how a pip-installed NetBox behaves at runtime. User-facing installation documentation for the pip install path will be added alongside experimental PyPI support (planned for NetBox v4.7.0); this page does not cover end-user installation steps.

### Dynamic metadata

`scripts/packaging/hatch_metadata.py` is a Hatchling metadata hook (wired in via `[tool.hatch.metadata.hooks.custom]`). It computes the package version from `netbox/release.yaml` and the runtime dependencies from the pinned `requirements.txt`, so the published wheel's `Requires-Dist` carries the exact versions NetBox is tested against. Both fields are declared `dynamic` in `pyproject.toml`; the optional-dependency extras stay static.

### sdist and the sdist-to-wheel guard

`python -m build` produces both an sdist and a wheel (the wheel is built from the sdist). The release workflow's `verify-sdist` job rebuilds a wheel from the published sdist and runs `scripts/verify_wheel_metadata.py` and `scripts/verify_wheel_contents.py` against it, so a missing build input (for example the metadata hook or `base_requirements.txt`) cannot regress unnoticed.

### Wheel data layout

Source assets that are not Python modules are force-included with a `netbox/netbox/_data/` target path by `[tool.hatch.build.targets.wheel.force-include]`; because the wheel's `sources = ["netbox"]` setting strips one leading `netbox/`, they install under `netbox/_data/`: templates, translations, the compiled `project-static` bundles, `release.yaml`, the documentation sources (`docs/` and `mkdocs.yml`), the bundled deployment examples (`contrib/`, seven files, unmodified), and the two tracked configuration templates.

The documentation sources ship in the wheel, so a pip-installed instance builds its own copy the same way a checkout does: `netbox upgrade --build-docs` runs the pinned toolchain (`zensical`, `mkdocs`, `mkdocs-material`, `mkdocstrings`; see `requirements.txt`) against the bundled `_data/mkdocs.yml`. The configured `site_dir` is relative to the config file, so the build output lands under `_data/netbox/project-static/docs`, which `collectstatic` then picks up the same way it does for a checkout build. `DOCS_ROOT` always resolves to the installed documentation sources; there is no unconfigured fallback.

At runtime `settings.py` detects the bundled `_data` directory and resolves the install mode, `BASE_DIR`, `NETBOX_ROOT`, and the documentation roots through `resolve_install_paths()` in `netbox/netbox/settings_utils.py`: a wheel install (`_data` present) keeps package data under `_data` and mutable instance files under `NETBOX_ROOT`; a source checkout (no `_data`) keeps the historical layout, where both roots are the project directory.

### Wheel-mode runtime

A pip-installed NetBox keeps mutable instance state out of the immutable, disposable virtual environment. `settings.py` resolves `NETBOX_ROOT` (default `/opt/netbox`, overridable via the environment) as the instance root and defaults the writable paths (`MEDIA_ROOT`, `REPORTS_ROOT`, `SCRIPTS_ROOT`, `STATIC_ROOT`) beneath it. In a checkout `NETBOX_ROOT` equals `BASE_DIR`, so archive and Git installs are unaffected.

Configuration loading is handled by `load_configuration()` in `netbox/netbox/settings_utils.py`. An explicit `NETBOX_CONFIGURATION` module always wins; otherwise, in wheel mode it prefers `NETBOX_ROOT/conf/configuration.py`, loading it by file path, and falls back to a legacy `NETBOX_ROOT/netbox/netbox/configuration.py` with a migration warning. The configuration directory is added to `sys.path` only while the configuration file executes, so sibling imports can resolve; `NETBOX_ROOT` itself is never added, which avoids a stale source tree shadowing the installed package. A checkout keeps importing `netbox.configuration`. For LDAP deployments, `settings.py` exposes the active configuration file's directory as the `CONFIGURATION_DIR` setting, and `load_ldap_config()` loads `ldap_config.py` from that same directory: the active `ldap_config.py` is always the one beside the active `configuration.py`, regardless of install method. One compatibility exception: in checkout mode only, when no sibling file exists, the historical `netbox/netbox/ldap_config.py` module is imported with a `RuntimeWarning`, so existing source installs that use a custom `NETBOX_CONFIGURATION` keep working.

### Console script

`pyproject.toml` registers a single entry point, `netbox` (`netbox.cli:main`). The wrapper resolves a few commands itself before importing Django, so they work without a configuration present:

* `netbox version` / `netbox --version` print the installed package version.
* `netbox setup` creates the local configuration files for the instance: `conf/configuration.py` copied verbatim from the bundled `configuration_example.py` template, plus an empty `local_requirements.txt`, and copies the bundled deployment examples (gunicorn, systemd units, nginx, apache, uwsgi, `netbox.env`) unmodified into `<target>/contrib/`. Nothing is generated or rewritten, and existing files are never overwritten; adapting and installing the examples (paths, systemd, the web server) remains the administrator's responsibility.
* `netbox secret-key` prints a new 50-character `SECRET_KEY` value.

These names are reserved by the wrapper. Every other command falls through to the Django management commands (`netbox upgrade`, `netbox check`, and so on), which require a valid configuration.
