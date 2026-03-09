# NetBox

Network source-of-truth and infrastructure resource modeling (IRM) tool combining DCIM and IPAM. Built on Django + PostgreSQL + Redis.

## Tech Stack
- Python 3.12+ / Django / Django REST Framework
- PostgreSQL (required), Redis (required for caching/queuing)
- GraphQL via Strawberry, background jobs via RQ
- Docs: MkDocs (in `docs/`)

## Repository Layout
- `netbox/` — Django project root; run all `manage.py` commands from here
- `netbox/netbox/` — Core settings, URLs, WSGI entrypoint
- `netbox/<app>/` — Django apps: `circuits`, `core`, `dcim`, `ipam`, `extras`, `tenancy`, `virtualization`, `wireless`, `users`, `vpn`
- `docs/` — MkDocs documentation source
- `contrib/` — Example configs (systemd, nginx, etc.) and other resources

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

## Key Commands
All commands run from the `netbox/` subdirectory with venv active.

```bash
# Development server
python manage.py runserver

# Run full test suite
export NETBOX_CONFIGURATION=netbox.configuration_testing
python manage.py test

# Faster test runs (no DB rebuild, parallel)
python manage.py test --keepdb --parallel 4

# Migrations
python manage.py makemigrations
python manage.py migrate

# Shell
python manage.py nbshell   # NetBox-enhanced shell
```

## Architecture Conventions
- **Apps**: Each Django app owns its models, views, API serializers, filtersets, forms, and tests.
- **REST API**: DRF serializers live in `<app>/api/serializers.py`; viewsets in `<app>/api/views.py`; URLs auto-registered in `<app>/api/urls.py`.
- **GraphQL**: Strawberry types in `<app>/graphql/types.py`.
- **Filtersets**: `<app>/filtersets.py` — used for both UI filtering and API `?filter=` params.
- **Tables**: `django-tables2` used for all object list views (`<app>/tables.py`).
- **Templates**: Django templates in `netbox/templates/<app>/`.
- **Tests**: Mirror the app structure in `<app>/tests/`. Use `netbox.configuration_testing` for test config.

## Coding Standards
- Follow existing Django conventions; don't reinvent patterns already present in the codebase.
- New models must include `created`, `last_updated` fields (inherit from `NetBoxModel` where appropriate).
- Every model exposed in the UI needs: model, serializer, filterset, form, table, views, URL route, and tests.
- API serializers must include a `url` field (absolute URL of the object).
- Use `FeatureQuery` for generic relations (config contexts, custom fields, tags, etc.).
- Avoid adding new dependencies without strong justification.

## Branch & PR Conventions
- Branch naming: `<issue-number>-short-description` (e.g., `1234-device-typerror`)
- Use the `main` branch for patch releases; `feature` tracks work for the upcoming minor/major release.
- Every PR must reference an approved GitHub issue.
- PRs must include tests for new functionality.

## Gotchas
- `configuration.py` is gitignored — never commit it.
- `manage.py` lives in `netbox/`, NOT the repo root. Running from the wrong directory is a common mistake.
- `NETBOX_CONFIGURATION` env var controls which settings module loads; set to `netbox.configuration_testing` for tests.
- The `extras` app is a catch-all for cross-cutting features (custom fields, tags, webhooks, scripts).
- Plugins API: only documented public APIs are stable. Internal NetBox code is subject to change without notice.
- See `docs/development/` for the full contributing guide and code style details.
