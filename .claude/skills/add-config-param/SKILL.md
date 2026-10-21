---
name: add-config-param
description: Step-by-step guide for adding a new configuration parameter to NetBox, covering both static parameters (settings.py) and dynamic parameters (database-backed, editable via the admin UI). Use when the user asks to add a new configuration option, setting, or parameter to NetBox.
---

# Adding a Configuration Parameter to NetBox

NetBox has two distinct kinds of configuration parameters. Choose the right one before writing any code:

| Type | Where defined | Changed by | Takes effect |
|---|---|---|---|
| **Static** | `settings.py` via `param(...)` | Editing `configuration.py` + restart | On WSGI restart |
| **Dynamic** | `config/parameters.py` `PARAMS` tuple | Admin UI or `configuration.py` | Immediately (cached in Redis) |

**Use dynamic** when:
- Operators need to tune the value without a service restart
- The parameter controls UI behavior or defaults (banners, page sizes, default values)
- Examples: `PAGINATE_COUNT`, `MAINTENANCE_MODE`, `BANNER_TOP`

**Use static** when:
- The value must not change at runtime (auth backends, database config, secret keys)
- The value controls infrastructure that requires a restart anyway
- Examples: `ALLOWED_HOSTS`, `REMOTE_AUTH_BACKEND`, `LOGGING`

---

## Adding a Dynamic Configuration Parameter

Dynamic parameters are defined in `netbox/netbox/config/parameters.py`, stored in the `ConfigRevision.data` JSONField, cached in Redis, and editable via Admin > System > Configuration History.

### Step 1 — Add to `PARAMS`

**File:** `netbox/netbox/config/parameters.py`

Add a `ConfigParam` entry to the `PARAMS` tuple, grouped logically with related parameters:

```python
ConfigParam(
    name='MY_PARAM',
    label=_('My param'),
    default=<default_value>,
    description=_("One-sentence description of what this controls"),
    field=forms.BooleanField,   # or IntegerField, CharField, JSONField, SimpleArrayField
    # field_kwargs only when extra widget/validation config is needed:
    field_kwargs={
        'widget': forms.Textarea(attrs={'class': 'font-monospace'}),
    },
),
```

**Common `field` choices:**

| Field | Use for |
|---|---|
| `forms.CharField` (default) | Short strings |
| `forms.BooleanField` | On/off toggles |
| `forms.IntegerField` | Counts, sizes, timeouts |
| `forms.JSONField` | Dicts/lists with free-form structure |
| `SimpleArrayField` | Lists of strings (add `field_kwargs={'base_field': forms.CharField()}`) |

The `default` value is returned whenever no `ConfigRevision` row exists and the parameter is not hard-coded in `configuration.py`.

### Step 2 — Use the parameter in code

Access via `get_config()` (request-scoped, cached) or the `ConfigItem` callable (deferred):

```python
from netbox.config import get_config

# One-time read:
value = get_config().MY_PARAM

# Deferred (evaluated later):
from netbox.config import ConfigItem
MY_PARAM = ConfigItem('MY_PARAM')
```

`get_config()` returns the `Config` object which tries:
1. Hard-coded value in Django `settings` (set by `configuration.py`)
2. Redis-cached active `ConfigRevision`
3. `ConfigParam.default`

### Step 3 — Document in the configuration docs

Add a section to the appropriate file under `docs/configuration/`:

| File | Category |
|---|---|
| `miscellaneous.md` | General / doesn't fit elsewhere |
| `default-values.md` | Default values for object fields |
| `security.md` | Auth, permissions, URL validation |
| `data-validation.md` | `CUSTOM_VALIDATORS`, `PROTECTION_RULES` |
| `graphql-api.md` | GraphQL settings |
| `error-reporting.md` | Sentry, logging |
| `remote-authentication.md` | Remote auth settings |
| `development.md` | Developer-only flags |
| `system.md` | Low-level system settings |

Template for a dynamic parameter doc section:

```markdown
## MY_PARAM

!!! tip "Dynamic Configuration Parameter"

Default: `<default_value>`

One or two sentences describing what the parameter does, what values are accepted,
and any side effects.
```

### Step 4 — Register in the dynamic params index

**File:** `docs/configuration/index.md`

Add the new parameter to the bulleted list under "Dynamic Configuration Parameters", keeping the list alphabetically ordered:

```markdown
* [`MY_PARAM`](./miscellaneous.md#my_param)
```

### Step 5 — Optionally add to the example config

If the parameter is important enough that operators should know they can hard-code it, add a commented entry to `netbox/netbox/configuration_example.py`:

```python
# MY_PARAM = <default_value>
```

Place it near related parameters.

### No migration needed

Dynamic parameters are stored in the `ConfigRevision.data` JSONField, which already exists. No database migration is required when adding a new `ConfigParam`.

---

## Adding a Static Configuration Parameter

Static parameters live in `settings.py` and are read at startup from `configuration.py`. They take effect only after the WSGI service is restarted.

### Step 1 — Add to `settings.py`

**File:** `netbox/netbox/settings.py`

Add a line in the "Set static config parameters" block, alphabetically within its logical group. `param()` wraps `get_param()` (in `netbox/netbox/settings_utils.py`), which reads the value from `configuration.py` and validates it:

```python
MY_PARAM = param('MY_PARAM', <default_value>, types=<type>)
```

For required parameters, omit the default; `get_param()` raises `ImproperlyConfigured` if the parameter is missing:

```python
MY_PARAM = param('MY_PARAM', types=str)  # Required
```

### Step 2 — Add validation

Declare the parameter's constraints as keyword arguments to `param()` rather than writing an `ImproperlyConfigured` check by hand. Default values are not validated.

| Argument | Validation |
|---|---|
| `types` | A type or tuple of types (e.g. `types=(list, tuple)`). `bool` is rejected for `int` unless explicitly listed. |
| `choices` | The value must be one of the given values |
| `min_value` / `max_value` | Inclusive numeric bounds |
| `min_length` | Minimum length (e.g. of a string) |
| `allow_none` | Permit an explicit `None` (rejected by default). Set this when `None` is a documented value. |
| `validators` | Callables invoked as `validator(name, value)`; each should raise `ImproperlyConfigured` on failure |

```python
MY_PARAM = param('MY_PARAM', 'option_a', choices=('option_a', 'option_b'))
MY_LIMIT = param('MY_LIMIT', 100, types=int, min_value=1, allow_none=True)
```

For complex validation (importable paths, valid URLs, comparisons with other parameters, etc.) follow the patterns of `PROXY_ROUTERS` or `RELEASE_CHECK_URL` in `settings.py`.

### Step 3 — Add to the example config

**File:** `netbox/netbox/configuration_example.py`

Add a commented entry with a brief inline comment explaining the parameter:

```python
# MY_PARAM = 'default_value'    # Short description of what this does
```

### Step 4 — Document

Add a section to the appropriate `docs/configuration/*.md` file:

```markdown
## MY_PARAM

Default: `<default_value>`

One or two sentences describing the parameter, accepted values, and any constraints.

---
```

Static parameters do **not** get the `!!! tip "Dynamic Configuration Parameter"` admonition.

---

## Common Gotchas

- **Dynamic params don't need a migration** — the value is stored in the `ConfigRevision.data` JSONField which already exists.
- **Hard-coding a dynamic param in `configuration.py` overrides the UI** — the loop after the static parameters in `settings.py` (`for config_param in CONFIG_PARAMS: ...`) sets the Django setting, which `Config.__getattr__` checks first. Document this behaviour in the parameter's doc page.
- **`forms.BooleanField` with `required=False`**: the `ConfigFormMetaclass` always adds `required=False`, so a `BooleanField` correctly represents a three-state (True / False / unset-use-default) UI. No extra `field_kwargs` needed for booleans.
- **`SimpleArrayField` needs `base_field`**: always pass `field_kwargs={'base_field': forms.CharField()}`.
- **No `ruff format`** on existing files — use `ruff check` only.

## References

- Dynamic param definitions: `netbox/netbox/config/parameters.py`
- Config loading / `Config` class: `netbox/netbox/config/__init__.py`
- `ConfigRevision` model: `netbox/core/models/config.py`
- `ConfigRevisionForm` (metaclass): `netbox/core/forms/model_forms.py`
- Static config loading: the "Set static config parameters" block in `netbox/netbox/settings.py`; `get_param()` in `netbox/netbox/settings_utils.py`
- Example config: `netbox/netbox/configuration_example.py`
- Config tests: `netbox/netbox/tests/test_config.py`
- Documentation: `docs/configuration/`
