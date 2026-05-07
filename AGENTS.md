# NetBox

## Repository Overview

NetBox is an extensible open-source network source-of-truth application powering network automation. It manages network infrastructure data including data center infrastructure (DCIM), IP address management (IPAM), circuits, virtualization, wireless, VPNs, and more. It supports a plugin ecosystem and exposes both a REST API and GraphQL API.

NetBox is the core product maintained by NetBox Labs. The current version is 4.6 (Python 3.12+, Django 6.x).

## Tech Stack

- Python 3.12+ / Django 6.x / Django REST Framework 3.x
- PostgreSQL (required), Redis (required for caching/queuing)
- GraphQL via Strawberry, background jobs via django-rq
- django-tables2 for list views, django-filter for filtering
- drf-spectacular for OpenAPI/Swagger schema generation
- Docs: MkDocs with mkdocs-material theme (in `docs/`)
- Ruff for lint (config in `pyproject.toml`)

## Repository Map

```text
.
├── netbox/                    — Django project root (run manage.py from here)
│   ├── manage.py
│   ├── netbox/                — Core settings, URLs, WSGI, plugin infrastructure
│   │   ├── settings.py        — Main Django settings
│   │   ├── configuration.py   — Instance configuration (gitignored)
│   │   ├── configuration_example.py — Configuration template
│   │   ├── configuration_testing.py — Test configuration
│   │   ├── urls.py            — Root URL routing
│   │   ├── wsgi.py            — WSGI entrypoint
│   │   ├── api/               — Core REST API infrastructure
│   │   ├── graphql/           — Core GraphQL schema
│   │   ├── models/            — Core model infrastructure (features, mixins)
│   │   ├── navigation/        — Navigation menu system
│   │   ├── plugins/           — Plugin system infrastructure
│   │   ├── registry.py        — Object registry
│   │   ├── search/            — Full-text search implementation
│   │   ├── ui/                — UI utilities
│   │   └── tests/             — Core framework tests
│   ├── account/               — User account management
│   ├── circuits/              — Circuit and provider management
│   ├── core/                  — Core data management (data sources, jobs)
│   ├── dcim/                  — Data center infrastructure (devices, racks, cables, etc.)
│   ├── extras/                — Cross-cutting features (custom fields, tags, webhooks, scripts)
│   ├── ipam/                  — IP address management (prefixes, addresses, VLANs, etc.)
│   ├── tenancy/               — Tenancy and organization
│   ├── users/                 — User management and tokens
│   ├── utilities/             — Shared utilities (no models)
│   ├── virtualization/        — Virtual machines and clusters
│   ├── vpn/                   — VPN tunnels and configurations
│   ├── wireless/              — Wireless LANs and links
│   ├── templates/             — Django templates (per-app subdirectories)
│   ├── static/                — Compiled static assets
│   ├── project-static/        — Source static assets
│   ├── media/                 — User-uploaded media
│   └── translations/          — i18n translation files
├── docs/                      — MkDocs documentation source
│   ├── administration/
│   ├── configuration/
│   ├── customization/
│   ├── development/           — Contributing guide, code style
│   ├── features/
│   ├── getting-started/
│   ├── installation/
│   ├── integrations/
│   ├── models/                — Per-model documentation (by app)
│   ├── plugins/
│   ├── reference/
│   └── release-notes/
├── scripts/                   — Database management and verification scripts
├── contrib/                   — Example configs (systemd, nginx, generated schemas)
├── pyproject.toml             — Project metadata, ruff config
├── requirements.txt           — Python dependencies
└── mkdocs.yml                 — Docs site configuration
```

## Architecture

### App Structure

Each Django app (account, circuits, core, dcim, extras, ipam, tenancy, users, virtualization, vpn, wireless) follows a standard layout:

```text
<app>/
├── __init__.py
├── models/          — Database models (or models.py for smaller apps)
├── migrations/      — Database migrations
├── api/
│   ├── serializers.py
│   ├── views.py     — DRF viewsets
│   └── urls.py      — NetBoxRouter registrations
├── forms/           — Django forms (model forms, filter forms, bulk edit, etc.)
├── tables/          — django-tables2 table definitions
├── graphql/
│   └── types.py     — Strawberry GraphQL types
├── filtersets.py    — django-filter FilterSets
├── choices.py       — ChoiceSet subclasses
├── views.py         — UI views (registered with register_model_view())
├── urls.py          — URL routing
├── search.py        — SearchIndex registrations
├── signals.py       — Django signal definitions (where applicable)
└── tests/
    ├── test_api.py
    ├── test_filtersets.py
    ├── test_models.py
    ├── test_views.py
    └── test_forms.py
```

### Views

Use `register_model_view()` to register model views by action (e.g. "add", "list", etc.). List views typically don't need to add `select_related()` or `prefetch_related()` on their querysets — prefetching is handled dynamically by the table class so that only relevant fields are prefetched.

### REST API

DRF serializers live in `<app>/api/serializers.py`; viewsets in `<app>/api/views.py`; URLs auto-registered in `<app>/api/urls.py`. `NetBoxModelSerializer` provides standard fields including `url`, `display`, `tags`, and `custom_fields`. drf-spectacular generates the OpenAPI schema automatically. REST API views typically don't need to add `select_related()` or `prefetch_related()` — prefetching is handled dynamically by the serializer.

### GraphQL

Strawberry types live in `<app>/graphql/types.py`. The core GraphQL schema is assembled in `netbox/netbox/graphql/`. Use Strawberry's `@strawberry.type` and `auto` field resolution, following the patterns in existing apps.

### Background Jobs

django-rq drives background task processing. Job classes live in `core/jobs.py` and app-specific `jobs.py` files. Use `JobRunner` subclasses (from `netbox.jobs`) for all background work. The `core` app exposes job status in the UI.

### Plugin System

Plugin infrastructure lives in `netbox/netbox/plugins/`. Plugins are Django apps registered in `PLUGINS` (configuration.py). The plugin API exposes stable extension points: custom models, views, navigation, template extensions, search indexes, object actions, and event rules. Internal NetBox APIs are subject to change without notice.

### Filtering

FilterSets live in `<app>/filtersets.py`, using `NetBoxModelFilterSet` as the base. Used for both UI filtering and API `?field=` params. FK filters must declare an explicit `<field>_id = ModelMultipleChoiceFilter(field_name='<field>', ...)` — don't rely on `Meta.fields` to auto-generate `_id` variants.

### Extras App

`extras` is a catch-all for cross-cutting features: custom fields, custom links, tags, webhooks/event rules, export templates, config contexts, saved filters, bookmarks, notifications, scripts, and reports. New cross-cutting features belong here. Use `FeatureQuery` for generic relations (config contexts, custom fields, tags, etc.).

## Commands

All commands run from the `netbox/` subdirectory with the venv active. There is no Makefile or Justfile; use raw commands.

| Command | What it does |
|---|---|
| `python manage.py runserver` | Start development server |
| `python manage.py test` | Run full test suite (set `NETBOX_CONFIGURATION` first — see Testing) |
| `python manage.py test --keepdb --parallel 4` | Faster test run (no DB rebuild, parallel) |
| `python manage.py test dcim.tests.test_api` | Run a single test module |
| `python manage.py makemigrations` | Generate migrations after model changes |
| `python manage.py migrate` | Apply migrations |
| `python manage.py nbshell` | NetBox-enhanced interactive shell |
| `python manage.py collectstatic` | Collect static assets |
| `ruff check` | Lint (run from repo root) |
| `mkdocs serve` | Preview documentation |
| `mkdocs build` | Build static docs site |

## Development Setup

```bash
python -m venv ~/.venv/netbox
source ~/.venv/netbox/bin/activate
pip install -r requirements.txt

# Copy and configure
cp netbox/netbox/configuration.example.py netbox/netbox/configuration.py
# Edit configuration.py: set DATABASE, REDIS, SECRET_KEY, ALLOWED_HOSTS

cd netbox/
python manage.py migrate
python manage.py runserver
```

Requires PostgreSQL and Redis on localhost at their default ports.

## Testing

Tests use `django.test.TestCase` (not pytest). Test modules mirror the app structure in `<app>/tests/`. Always set the `NETBOX_CONFIGURATION` environment variable before running tests:

```bash
export NETBOX_CONFIGURATION=netbox.configuration_testing
python manage.py test

# Faster runs
python manage.py test --keepdb --parallel 4

# Single module
python manage.py test dcim.tests.test_api
```

**Standard test modules per app:**

| Module | Coverage area |
|---|---|
| `test_api.py` | REST API endpoints (CRUD, filtering, bulk operations) |
| `test_filtersets.py` | FilterSet fields and query behavior |
| `test_models.py` | Model methods, validation, constraints |
| `test_views.py` | UI views (list, create, edit, delete, bulk actions) |
| `test_forms.py` | Form validation |
| `test_tables.py` | Table column rendering |

Additional specialized test modules exist in some apps (e.g., `test_cablepaths.py` in dcim, `test_lookups.py` in ipam).

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **`ci.yml`** — Main CI pipeline: runs on every PR. Executes linting (ruff) and the full test suite across the supported Python version matrix.
- **`codeql.yml`** — CodeQL security scanning.
- **`claude.yml`** — Claude Code automation hook; triggers on issue/PR comments mentioning `@claude`.
- **`claude-issue-triage.yml`** — Automated issue triage via Claude AI.
- **`close-stale-issues.yml`** / **`close-incomplete-issues.yml`** — Issue hygiene automation.
- **`lock-threads.yml`** — Locks closed issue/PR threads after a period.
- **`update-translation-strings.yml`** — Extracts and updates i18n translation strings.

## Common Tasks

### Add a new model

1. Add the model to the appropriate app's `models/` directory (or create a new module imported from `models/__init__.py`). Inherit from `NetBoxModel` for full feature support (custom fields, tags, etc.).
2. Prompt the user to run `python manage.py makemigrations` — never write migrations manually.
3. Wire up the full surface area: filterset (`filtersets.py`), forms (`forms/`), table (`tables/`), serializer (`api/serializers.py`), viewset (`api/views.py`), URL routes (`api/urls.py`, `urls.py`), UI views (`views.py`), navigation, and a template under `templates/<app>/`.
4. Register a `SearchIndex` in `search.py` if the model should appear in global search.
5. Add tests covering model logic, API, filtersets, forms, and views.

### Add a REST API endpoint

1. Add the serializer to `api/serializers.py` using `NetBoxModelSerializer` for `NetBoxModel`-based models. Include a `url` field.
2. Add the viewset to `api/views.py`. For custom actions use `@action(detail=True, methods=['post'])`.
3. Register the route in `api/urls.py` via `NetBoxRouter`.
4. Ensure a corresponding `FilterSet` exists in `filtersets.py`; add explicit `<field>_id = ModelMultipleChoiceFilter(field_name='<field>', ...)` for FK filters.
5. Add an integration test in `tests/test_api.py`.

### Add a GraphQL type

1. Add a Strawberry type to `<app>/graphql/types.py`, inheriting from the appropriate base (see existing types for examples).
2. Register any new query fields in the app's GraphQL module and ensure it is included in the root schema.
3. Follow the patterns in existing apps — use `auto` fields and lazy-resolve relations.

### Add a filterset field

1. Add the field to `<app>/filtersets.py`. Use `NetBoxModelFilterSet` as the base.
2. For FK relations, add both `<field>` (name/slug lookup) and `<field>_id` (ID lookup) as explicit `ModelMultipleChoiceFilter` entries.
3. Update the filter form in `forms/filtersets.py` to expose the field in the UI.
4. Add a test in `tests/test_filtersets.py`.

### Cut a release

1. Bump `version` in `pyproject.toml`.
2. Update `docs/release-notes/`.
3. Tag and publish a GitHub release.

## Conventions and Patterns

- **Apps**: Each app owns its models, views, serializers, filtersets, forms, and tests. Don't reach across app boundaries except via FK relations and public APIs.
- **Views**: Use `register_model_view()`. List views don't need manual `select_related()`/`prefetch_related()` — the table handles it.
- **REST API**: Serializers don't need manual `select_related()`/`prefetch_related()` — handled dynamically.
- **New models**: Inherit from `NetBoxModel`; include `created` and `last_updated` fields.
- **Every UI model**: Needs model, serializer, filterset, form, table, views, URL route, and tests.
- **API serializers**: Must include a `url` field (absolute URL of the object).
- **Generic relations**: Use `FeatureQuery` for config contexts, custom fields, tags, etc.
- **FK filters**: Always add explicit `<field>_id` variants in FilterSets; don't rely on `Meta.fields`.
- **No new dependencies** without strong justification.
- **No manual migrations**: Prompt the user to run `manage.py makemigrations`.
- **No `ruff format`** on existing files — tends to introduce unnecessary style changes.
- **Linting**: Ruff config in `pyproject.toml`. Line length 120, single quotes. Enabled rules: E/W/F/I/RET/UP/RUF022. Ignored: F403, F405, RET504, UP032.
- **Extras**: Cross-cutting features (custom fields, tags, webhooks, scripts) belong in the `extras` app.
- **Plugin API**: Only documented public APIs are stable. Internal code may change without notice.

## Branch & PR Conventions

- Branch naming: `<issue-number>-short-description` (e.g., `1234-device-typerror`)
- Use the `main` branch for patch releases; `feature` tracks work for the upcoming minor/major release.
- Every PR must reference an approved GitHub issue.
- PRs must include tests for new functionality.

## PR Submission Requirements

**Do not open a PR unless all the following conditions are met:**

1. **Issue reference required** — The PR body must include a `Closes: #<number>` line identifying the associated GitHub issue. PRs without this line must not be submitted.
2. **Issue must be open** — Before opening a PR, verify via `gh issue view <number>` that the referenced issue is currently open. Do not submit a PR against a closed issue.
3. **Issue must be assigned to you** — Verify that the referenced issue is assigned to the submitting user. Do not open a PR for an issue that is unassigned or assigned to someone else.
4. **No exceptions without maintainer status** — These three requirements are waived only for project maintainers (members of the `netboxlabs` GitHub organization). All other contributors must satisfy all three checks before a PR is opened.

**Pre-submission checklist for AI agents:**

```bash
# Confirm the issue is open and assigned before opening a PR
gh issue view <number> --json state,assignees
```

Reject the PR submission and report the problem if the issue is closed, unassigned, or assigned to a different user.

Do not include an entry in the release notes for the PR unless explicitly instructed to do so. (Release notes are typically generated in aggregate as part of the release process to avoid merge conflicts.)

## Troubleshooting

- **Wrong directory for `manage.py`** — `manage.py` lives in `netbox/`, not the repo root. Always `cd netbox/` first or use the full path.
- **Wrong configuration loaded** — Set `NETBOX_CONFIGURATION=netbox.configuration_testing` for tests.
- **`configuration.py` not found** — Copy `configuration.example.py` to `configuration.py` and fill in DATABASE, REDIS, SECRET_KEY, ALLOWED_HOSTS. This file is gitignored and must never be committed.
- **Migration errors** — Never write migrations manually. Run `python manage.py makemigrations` and let Django generate them.
- **Plugin issues** — Only documented public APIs are stable. Internal NetBox code may change without notice.

## Gotchas

- `configuration.py` is gitignored — never commit it.
- `manage.py` lives in `netbox/`, NOT the repo root. Running from the wrong directory is a common mistake.
- `NETBOX_CONFIGURATION` env var controls which settings module loads; set to `netbox.configuration_testing` for tests.
- The `extras` app is a catch-all for cross-cutting features (custom fields, tags, webhooks, scripts).
- Plugins API: only documented public APIs are stable. Internal NetBox code is subject to change without notice.
- See `docs/development/` for the full contributing guide and code style details.

## References

- Documentation: [`docs/`](./docs/)
- Contributing guide: [`docs/development/`](./docs/development/)
- Release notes: [`docs/release-notes/`](./docs/release-notes/)
- Plugin development: [`docs/plugins/`](./docs/plugins/)
- NetBox Labs: <https://netboxlabs.com>
