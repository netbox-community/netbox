---
name: run-tests
description: Run NetBox's Django test suite locally. Use when the user asks to run tests, run a specific test module/class/method, or verify changes pass before opening a PR.
---

# Run the NetBox test suite

NetBox uses `django.test.TestCase` (not pytest). The suite is invoked via `manage.py test` from the repo root. CI runs this exact command in `.github/workflows/ci.yml`.

## Canonical command

From the repo root, with the venv active:

```bash
NETBOX_CONFIGURATION=netbox.configuration_testing python netbox/manage.py test netbox/ --parallel
```

`--parallel` runs test processes in parallel and is used in CI. Drop it to debug failures that only appear in parallel mode.

## Prerequisites

1. PostgreSQL and Redis reachable on localhost at their default ports (credentials: `netbox`/`netbox`/`netbox`).
2. `configuration.py` in place — copy from the example and fill in DATABASE, REDIS, SECRET_KEY, ALLOWED_HOSTS. This file is gitignored and must never be committed.
3. Dependencies installed: `pip install -r requirements.txt`.
4. `NETBOX_CONFIGURATION` set to `netbox.configuration_testing` — the test config sets `DATABASES`, `REDIS`, and `PLUGINS` appropriately.

If any of these are missing, surface the gap to the user — do not silently skip.

## Useful variants

Run a single app's tests:

```bash
NETBOX_CONFIGURATION=netbox.configuration_testing python netbox/manage.py test dcim --parallel
```

Run a single module, class, or method (Django dotted-path target):

```bash
NETBOX_CONFIGURATION=netbox.configuration_testing python netbox/manage.py test dcim.tests.test_api
NETBOX_CONFIGURATION=netbox.configuration_testing python netbox/manage.py test dcim.tests.test_api.RackTestCase
NETBOX_CONFIGURATION=netbox.configuration_testing python netbox/manage.py test dcim.tests.test_api.RackTestCase.test_list_objects
```

Speed options:

- `--keepdb` — skip DB rebuild between runs (safe for most iterative work)
- `--parallel` — run tests in parallel across CPU cores (used in CI; don't combine with `--keepdb` without testing first)
- `--failfast` — stop on first failure
- `-v 2` — print each test name as it runs

## Standard test modules per app

| Module | Coverage area |
|---|---|
| `test_api.py` | REST API endpoints (CRUD, filtering, bulk operations) |
| `test_filtersets.py` | FilterSet fields and query behavior |
| `test_models.py` | Model methods, validation, constraints |
| `test_views.py` | UI views (list, create, edit, delete, bulk actions) |
| `test_forms.py` | Form validation |
| `test_tables.py` | Table column rendering |

Specialized modules in some apps: `test_cablepaths.py` (dcim), `test_lookups.py` (ipam).

## After model changes

Always generate migrations before running tests; the test DB build will fail if migrations are missing:

```bash
python netbox/manage.py makemigrations
```

Never write migrations manually — let Django generate them.

## Coverage (matches CI)

```bash
coverage run --source="netbox/" netbox/manage.py test netbox/ --parallel
coverage report --skip-covered --omit '*/migrations/*,*/tests/*'
```

## Why these choices

- **Don't substitute pytest.** The suite uses `django.test.TestCase`; switching to pytest requires `pytest-django` configured against NetBox's settings, which is not set up. Run via `manage.py test` to match CI.
- **Always set `NETBOX_CONFIGURATION`.** Without it, Django loads `configuration.py` (the production config), which likely has a different database or may not exist in dev environments.
- **`--parallel` for full-suite runs.** CI runs parallel; running without it locally can mask race conditions (rare) and is slower on multi-core machines.

## References

- [`AGENTS.md`](../../../AGENTS.md) — Testing and development sections.
- [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) — Authoritative CI invocation.
- [`netbox/netbox/configuration_testing.py`](../../../netbox/netbox/configuration_testing.py) — Test configuration used by the runner.
