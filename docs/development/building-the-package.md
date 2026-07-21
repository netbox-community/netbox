# Building the Package

NetBox package artifacts (a wheel and a source distribution) can be built and verified locally. During the v4.6.x preview period, published artifacts are for maintainer validation only. Installing NetBox via pip is not a supported installation path yet. Experimental support for installing from production PyPI is planned for NetBox v4.7.0. This page is intended for maintainers and contributors working on the packaging itself; routine development does not require building a package.

The artifacts are always built by CI from a clean checkout (see `.github/workflows/release.yml`). A local build is useful for testing packaging changes before they are merged.

## Prerequisites

Install the minimum local build tooling (all three are also included in the `dev` optional dependency group):

```no-highlight
python -m pip install --upgrade build packaging twine
```

Building also requires a freshly rendered copy of the documentation site (see [Building](#building) below). The documentation toolchain (`zensical`, `mkdocs`, `mkdocs-material`, `mkdocstrings`) is pinned in `requirements.txt` rather than the `dev` group because it is also needed outside packaging, such as documentation previews and CI's `docs` job.

## Building

Render the documentation site at the repository root before building; both the wheel and the sdist bundle the rendered output, and the release workflow's `build` job renders in the same way:

```no-highlight
python -m pip install -r requirements.txt
zensical build -c -s
```

Always render with `-c` (clean cache) and `-s` (strict mode, abort on warnings) so a stale cache or a degraded build cannot slip into the artifacts. This writes `netbox/project-static/docs/` (gitignored). Building without a prior render fails because the rendered docs directory is a required Hatch force-include: Hatchling raises `FileNotFoundError: Forced include not found` for the missing directory. A render that exits successfully but produces a partial site is caught by `scripts/verify_wheel_contents.py`, which requires both the site root (`index.html`) and a model documentation page (`models/dcim/device/index.html`) in the wheel.

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

Check the built artifacts for valid package metadata and README rendering:

```no-highlight
twine check dist/*
```

Confirm the wheel's version, dependency metadata, and extras match `netbox/release.yaml`, the pinned `requirements.txt`, and the declared optional-dependency groups:

```no-highlight
python scripts/verify_wheel_metadata.py dist/*.whl
```

Confirm the artifacts ship only the two tracked configuration templates, and that the wheel carries the runtime-critical bundled data: `_data/release.yaml`, templates, translations, static assets, and the pre-rendered documentation site under `_data/docs/`. These are the same content checks CI runs before publishing:

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
NETBOX_ROOT=/tmp/netbox-build-test-root \
NETBOX_SMOKETEST_BASE=/tmp/netbox-build-test-root \
/tmp/netbox-build-test/bin/netbox check
```

Without configuration, a wheel-installed NetBox looks for `$NETBOX_ROOT/conf/configuration.py` (default `/opt/netbox/conf/configuration.py`), which normally does not exist on a development workstation. The environment variables above point `netbox check` at the same minimal configuration module used by the release workflow's smoke-test job (`scripts/smoketest_configuration.py`); run the command from the repository root so `PYTHONPATH` can find it. `NETBOX_SMOKETEST_BASE` sets the writable scratch directory under which the module creates its media, reports, and scripts roots; `NETBOX_ROOT` points the fixed collected-static root at the same directory. Any other importable configuration module works the same way via `NETBOX_CONFIGURATION` (and `PYTHONPATH`, if the configuration lives outside the package). To exercise the full post-install task sequence from the wheel, run `netbox upgrade --no-input` with the same environment against a throwaway database (the collected static files land under `$NETBOX_ROOT/static`); this is what the release workflow's smoke-test job does. The documentation ships pre-rendered in the wheel, so there is nothing to build on the instance; `--build-docs` remains a checkout-only convenience for rendering the documentation from its sources.

## Packaging architecture

This section is a developer-facing overview of how the package is assembled and how a pip-installed NetBox behaves at runtime. User-facing installation documentation for the pip install path will be added alongside experimental PyPI support (planned for NetBox v4.7.0); this page does not cover end-user installation steps.

### Dynamic metadata

`scripts/packaging/hatch_metadata.py` is a Hatchling metadata hook (wired in via `[tool.hatch.metadata.hooks.custom]`). It computes the package version from `netbox/release.yaml` and the runtime dependencies from the pinned `requirements.txt`, so the published wheel's `Requires-Dist` carries the exact versions NetBox is tested against. Both fields are declared `dynamic` in `pyproject.toml`; the optional-dependency extras stay static.

### sdist and the sdist-to-wheel guard

`python -m build` produces both an sdist and a wheel, with the wheel built from the sdist. The release workflow's `verify-sdist` job rebuilds a wheel from the candidate sdist and runs `scripts/verify_wheel_metadata.py` and `scripts/verify_wheel_contents.py` against it, so a missing build input (for example the metadata hook or `base_requirements.txt`) cannot regress unnoticed. The rendered documentation site is one such build input: it reaches the sdist through its own force-include (`[tool.hatch.build.targets.sdist.force-include]`), so this guard also fails if that force-include is removed or broken.

### Wheel data layout

Source assets that are not Python modules are force-included with a `netbox/netbox/_data/` target path by `[tool.hatch.build.targets.wheel.force-include]`; because the wheel's `sources = ["netbox"]` setting strips one leading `netbox/`, they install under `netbox/_data/`: templates, translations, the compiled `project-static` bundles, `release.yaml`, the pre-rendered documentation site (rendered by `zensical build` into `netbox/project-static/docs/` before packaging; see [Building](#building) above), the bundled deployment examples (`contrib/`, seven files, unmodified), and the two tracked configuration templates.

The wheel bundles the rendered site itself, not the documentation sources. The documentation build is not run from the installed wheel, and there is nothing to build on the instance. In wheel mode, the default `DOCS_ROOT` and the STATICFILES `docs` prefix source both resolve to the same bundled `_data/docs` directory (see `resolve_install_paths()` in `netbox/netbox/settings_utils.py`), which `collectstatic` then picks up the same way it does for a checkout build. The sdist force-includes the same rendered site (`netbox/project-static/docs/`, kept alongside the markdown sources it was rendered from), so a wheel built from the sdist (the `verify-sdist` job, or `pip install <sdist>`) is identical in this respect.

At runtime `settings.py` detects the bundled `_data` directory and resolves the install mode, `BASE_DIR`, `NETBOX_ROOT`, and the documentation roots through `resolve_install_paths()` in `netbox/netbox/settings_utils.py`: a wheel install (`_data` present) keeps package data under `_data` and mutable instance files under `NETBOX_ROOT`; a source checkout (no `_data`) keeps the historical layout, where both roots are the project directory.

### Wheel-mode runtime

A pip-installed NetBox keeps mutable instance state out of the immutable, disposable virtual environment. `settings.py` resolves `NETBOX_ROOT` (default `/opt/netbox`, overridable via the environment) as the instance root, defaults the writable paths (`MEDIA_ROOT`, `REPORTS_ROOT`, `SCRIPTS_ROOT`) beneath it, and fixes `STATIC_ROOT` to `$NETBOX_ROOT/static`; `STATIC_ROOT` is intentionally not a `configuration.py` parameter, so the collected static path cannot drift from the instance layout the bundled deployment examples expect. In a checkout `NETBOX_ROOT` equals `BASE_DIR`, so archive and Git installs are unaffected.

Configuration loading is handled by `load_configuration()` in `netbox/netbox/settings_utils.py`. An explicit `NETBOX_CONFIGURATION` module always wins; otherwise, in wheel mode it prefers `NETBOX_ROOT/conf/configuration.py`, loading it by file path, and falls back to a legacy `NETBOX_ROOT/netbox/netbox/configuration.py` with a migration warning. The configuration directory is added to `sys.path` only while the configuration file executes, so sibling imports can resolve; `NETBOX_ROOT` itself is never added, which avoids a stale source tree shadowing the installed package. A checkout keeps importing `netbox.configuration`. For LDAP deployments, `settings.py` exposes the active configuration file's directory as the `CONFIGURATION_DIR` setting, and `load_ldap_config()` loads `ldap_config.py` from that same directory by default. This keeps the active LDAP configuration beside the active NetBox configuration, regardless of install method. One compatibility exception remains: in checkout mode only, when no sibling file exists, the historical `netbox/netbox/ldap_config.py` module is imported with a `RuntimeWarning`, so existing source installs that use a custom `NETBOX_CONFIGURATION` keep working.

### Console script

`pyproject.toml` registers a single entry point, `netbox` (`netbox.cli:main`). The wrapper resolves a few commands itself before importing Django, so they work without a configuration present:

* `netbox version` / `netbox --version` print the installed package version.
* `netbox setup` creates the local configuration files for the instance: `conf/__init__.py`, `conf/configuration.py` copied verbatim from the bundled `configuration_example.py` template, and an empty `local_requirements.txt`. It also copies the bundled deployment examples (gunicorn, systemd units, nginx, apache, uwsgi, `netbox.env`) unmodified into `<target>/contrib/`. The examples are copied as-is, and existing files are never overwritten; adapting and installing the examples (paths, systemd, the web server) remains the administrator's responsibility.
* `netbox secret-key` prints a new 50-character `SECRET_KEY` value.

These names are reserved by the wrapper. Every other command falls through to the Django management commands (`netbox upgrade`, `netbox check`, and so on), which require a valid configuration.
