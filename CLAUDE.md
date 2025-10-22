# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetBox is a Django-based web application for modeling and documenting network infrastructure. It serves as the **source of truth** for network automation, providing a comprehensive data model for network primitives (devices, cables, IP addresses, VLANs, circuits, etc.) with REST and GraphQL APIs.

**Tech Stack:**
- Python 3.10+ with Django framework
- PostgreSQL database
- Redis for caching and background tasks
- TypeScript (transpiled to JavaScript)
- Sass (compiled to CSS)
- Bootstrap 5, HTMX, Tom Select, and other front-end libraries

## Development Setup

### Initial Configuration

1. **Working Directory**: All Django management commands run from `/netbox/` (not the repository root)
   - Repository root: `/home/user/netbox/`
   - Django project root: `/home/user/netbox/netbox/`

2. **Configuration File**: Copy `netbox/netbox/configuration_example.py` to `configuration.py` and set:
   - `ALLOWED_HOSTS = ['*']` for development
   - `DEBUG = True`
   - `DEVELOPER = True` (enables creating database migrations)
   - Database and Redis connection settings
   - `SECRET_KEY` (generate with `generate_secret_key.py`)

3. **Test Configuration**: For running tests, set environment variable:
   ```bash
   export NETBOX_CONFIGURATION=netbox.configuration_testing
   ```

### Common Commands

#### Python/Django Commands
All commands below should be run from the `netbox/` directory:

```bash
# Run development server
./manage.py runserver

# Run tests (full suite)
python manage.py test

# Run tests with database reuse (faster, but fails if schema changed)
python manage.py test --keepdb

# Run tests in parallel (recommended: specify a number lower than CPU count)
python manage.py test --parallel 4

# Run specific test modules
python manage.py test dcim.tests.test_views ipam.tests.test_views

# Check for missing migrations
python manage.py makemigrations --check

# Run Django system check
python manage.py check
```

#### Code Quality

```bash
# Lint Python code (from repository root)
ruff check netbox/

# Install and enable pre-commit hooks (from repository root)
pip install ruff pre-commit
pre-commit install
```

Pre-commit automatically runs:
- Ruff linter
- Django system check
- Missing migrations check
- Documentation build validation
- Yarn validation (TypeScript/Sass)
- Static asset bundle verification

#### Front-End Development

Front-end assets are in `netbox/project-static/`. From that directory:

```bash
# Install dependencies (first time)
yarn

# Build all static assets
yarn bundle

# Build only styles or scripts
yarn bundle:styles
yarn bundle:scripts

# Validate TypeScript and linting
yarn validate

# Check types only
yarn validate:types

# Lint only
yarn validate:lint

# Format code
yarn format
```

## Architecture

### Django Apps Structure

NetBox is organized into Django apps, each representing a domain:

- **dcim** - Data Center Infrastructure Management (devices, racks, cables, sites)
- **ipam** - IP Address Management (IPs, prefixes, VLANs, VRFs, ASNs)
- **circuits** - Circuit and provider management
- **virtualization** - Virtual machines and clusters
- **vpn** - VPN tunnels, L2VPN, IPSec configuration
- **wireless** - Wireless LANs and links
- **tenancy** - Multi-tenancy and contacts
- **users** - User accounts and permissions
- **core** - Core data models (jobs, data sources)
- **extras** - Extensibility features (custom fields, webhooks, scripts)
- **utilities** - Shared utilities and helpers

Each app typically contains:
- `models.py` - Database models
- `views.py` - View logic
- `forms.py` - Form definitions
- `tables.py` - Table definitions for list views
- `filtersets.py` - Filter logic for search/filtering
- `api/` - REST API serializers and views
- `graphql.py` - GraphQL schema (if applicable)
- `tests/` - Test suite

### Model Features System

NetBox models support various features through mixin classes:

- **Change Logging** (`ChangeLoggingMixin`) - Automatic change history
- **Custom Fields** (`CustomFieldsMixin`) - User-defined fields
- **Tags** (`TagsMixin`) - Tagging support
- **Webhooks/Event Rules** (`EventRulesMixin`) - Automated event triggers
- **Journaling** (`JournalingMixin`) - Historical commentary
- **Custom Validation** (`CustomValidationMixin`) - User-defined validation rules
- **Bookmarks** (`BookmarksMixin`) - User bookmarks
- **Contacts** (`ContactsMixin`) - Contact associations

See `docs/development/models.md` for the complete features matrix.

### Application Registry

The registry (`extras.registry`) is an in-memory data structure storing application-wide parameters:
- `models` - All registered NetBox models
- `model_features` - Feature support mappings
- `plugins` - Plugin registrations
- `views` - Registered model views
- `tables` - Table column extensions
- `search` - Search index mappings

### Plugin System

NetBox supports plugins as self-contained Django apps. Plugins can:
- Define custom models and database tables
- Add UI views and navigation items
- Extend REST/GraphQL APIs
- Inject template content
- Add middleware
- Register custom scripts and background jobs

Plugin structure: See `docs/plugins/development/index.md`

### Front-End Architecture

Located in `netbox/project-static/`:
- `src/` - TypeScript source (transpiled to JS)
- `styles/` - Sass source (compiled to CSS)
- `dist/` - Compiled/bundled output
- `js/` - Direct-served JavaScript
- `img/` - Images

Front-end follows these principles:
- Use Bootstrap utility classes sparingly (max 4-5 per element)
- Custom classes must be commented
- Reuse SCSS variables (avoid hard-coded values)
- JSDoc comments required for TypeScript functions
- Minimize new dependencies (check bundle size with Bundlephobia)
- Responsive design required for all screen sizes

## Code Style Guidelines

### Python

- Follow PEP 8 with **120 character line limit** (strongly encouraged, not enforced)
- Use `ruff` for linting (ignore: E501, F403, F405)
- Docstrings required for all models and custom methods
- Constants go in `constants.py` (wildcard imports allowed)
- Nested API serializers: Import directly from other apps
  - Example: `from ipam.api.nested_serializers import NestedIPAddressSerializer`
- Prioritize readability over concision
- No easter eggs (business-critical tool)
- Newline at end of every file

### Branching and Commits

- Branch naming: `$issue-$description` (e.g., `1234-device-typerror`)
- Base branches:
  - `main` - Stable releases and patch versions
  - `feature` - Upcoming minor/major releases
- Commit messages should reference issues: `"Fixes #1234: Description"` or `"Closes #1234: Description"`
- Pre-commit hooks run automatically before commits

### Testing

- Tests required for all new functionality
- Run from `netbox/` directory with `NETBOX_CONFIGURATION=netbox.configuration_testing`
- Use `--keepdb` to speed up repeated test runs (if schema unchanged)
- Use `--parallel` for faster execution
- NetBox uses `django-rich` for enhanced test output

### Dependencies

Avoid new dependencies unless absolutely necessary. New dependencies must:
- Have publicly accessible source code
- Use OSS-compatible license
- Be actively maintained (releases within 1 year)
- Be available on PyPI
- Be documented in `base_requirements.txt` with description and repo URL
- Be pinned to specific version in `requirements.txt`

## Project-Specific Notes

### Branding
- Always use "NetBox" (capital N and B) in documentation
- Use "netbox" (lowercase) only in code and filenames
- Never "Netbox" or other variations

### Configuration File
- Development config: `netbox/netbox/configuration.py` (copied from `configuration_example.py`)
- Test config: `netbox/netbox/configuration_testing.py` (use via environment variable)

### Database Migrations
- Only created when `DEVELOPER = True` in configuration
- Check for missing migrations: `./manage.py makemigrations --check`
- Pre-commit hook validates migrations automatically

### Static Assets
- Source files in `project-static/src/` and `project-static/styles/`
- Must be compiled to `dist/` using `yarn bundle`
- Pre-commit hook verifies bundles are up-to-date

### OpenAPI Schema
- Located in API definitions
- Verified by `scripts/verify-openapi.sh`
- Pre-commit hook validates schema changes

## Resources

- **Documentation**: https://docs.netbox.dev/
- **Contributing Guide**: `CONTRIBUTING.md`
- **Plugin Tutorial**: https://github.com/netbox-community/netbox-plugin-tutorial
- **Demo Instance**: https://demo.netbox.dev/
- **Demo Data**: https://github.com/netbox-community/netbox-demo-data
- **Community**: GitHub Discussions, Slack (#netbox on netdev.chat)
