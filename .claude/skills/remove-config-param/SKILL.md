---
name: remove-config-param
description: Step-by-step guide for removing a configuration parameter from NetBox, covering both static parameters (settings.py) and dynamic parameters (database-backed). Use when the user asks to remove, delete, or deprecate a configuration option or setting.
---

# Removing a Configuration Parameter from NetBox

Before touching any files, determine which type of parameter you are removing:

| Type | Where defined | How to tell |
|---|---|---|
| **Static** | `settings.py` via `getattr(configuration, ...)` | Appears in `settings.py`; not in `config/parameters.py` `PARAMS` |
| **Dynamic** | `config/parameters.py` `PARAMS` tuple | Appears in `PARAMS`; editable via Admin > System > Configuration History |

Run a broad grep before starting to find all usages:

```bash
grep -r 'MY_PARAM' netbox/ --include='*.py' -l
grep -r 'MY_PARAM' docs/ -l
```

---

## Removing a Dynamic Configuration Parameter

### Step 1 — Find all usages in code

Before removing the parameter definition, identify every call site:

```bash
grep -r 'MY_PARAM\|my_param' netbox/ --include='*.py'
```

For `get_config().MY_PARAM` and `ConfigItem('MY_PARAM')` patterns specifically:

```bash
grep -r "get_config()\.MY_PARAM\|ConfigItem('MY_PARAM')" netbox/ --include='*.py'
```

Remove or replace every usage. The replacement depends on the reason for removal:
- **Parameter folded into another**: replace with the new parameter access
- **Hard-coded default**: replace `get_config().MY_PARAM` with the literal default value
- **Feature removed**: remove the surrounding code entirely

### Step 2 — Remove from `PARAMS`

**File:** `netbox/netbox/config/parameters.py`

Delete the `ConfigParam(...)` block for the parameter from the `PARAMS` tuple.

### Step 3 — Remove from the dynamic params index

**File:** `docs/configuration/index.md`

Remove the bullet-point entry for `MY_PARAM` from the "Dynamic Configuration Parameters" list.

### Step 4 — Remove the documentation section

**File:** `docs/configuration/<category>.md` (whichever file the parameter was documented in)

Delete the `## MY_PARAM` section and its content, including the trailing `---` separator.

### Step 5 — Remove from the example config (if present)

**File:** `netbox/netbox/configuration_example.py`

If a commented `# MY_PARAM = ...` line was added when the parameter was introduced, remove it.

### No migration needed

Dynamic parameters are stored as keys in the `ConfigRevision.data` JSONField. Removing the `ConfigParam` definition from `PARAMS` means the UI no longer shows the field and the `Config` object no longer exposes the attribute — but old `ConfigRevision` rows in the database will silently retain the key in their JSON blob. This is harmless and requires no migration.

---

## Removing a Static Configuration Parameter

### Step 1 — Find all usages in code

```bash
grep -r 'MY_PARAM' netbox/ --include='*.py'
```

Remove every reference. For Django settings accessed via `settings.MY_PARAM`, also search templates:

```bash
grep -r 'MY_PARAM' netbox/templates/
```

### Step 2 — Remove from `settings.py`

**File:** `netbox/netbox/settings.py`

1. Delete the `MY_PARAM = getattr(configuration, 'MY_PARAM', ...)` line.
2. If the parameter was required (listed in the required-parameter check near the top), remove it from that tuple:
   ```python
   # Before:
   for parameter in ('ALLOWED_HOSTS', 'MY_PARAM', 'SECRET_KEY', 'REDIS'):
   # After:
   for parameter in ('ALLOWED_HOSTS', 'SECRET_KEY', 'REDIS'):
   ```
3. Remove any validation block that immediately followed the `getattr` line (e.g. `if MY_PARAM not in (...): raise ImproperlyConfigured(...)`).

### Step 3 — Remove from the example config

**File:** `netbox/netbox/configuration_example.py`

Delete the commented `# MY_PARAM = ...` line.

### Step 4 — Remove the documentation section

**File:** `docs/configuration/<category>.md`

Delete the `## MY_PARAM` section and its content, including the trailing `---` separator.

---

## Deprecation vs. Immediate Removal

If the parameter is used by existing deployments, consider a two-phase removal:

**Phase 1 (current release) — Deprecate:**
1. Keep the `getattr` / `ConfigParam` definition in place so existing configs don't break.
2. Add a deprecation warning comment in `settings.py` (see how `SENTRY_DSN` is handled with `# TODO: Remove in NetBox vX.Y`).
3. Log a `warnings.warn(...)` or add a startup notice if the parameter is still set.
4. Mark the doc section as deprecated.

**Phase 2 (future release) — Remove:**
Follow the full removal steps above.

---

## Common Gotchas

- **Remove all call sites first** — if code still calls `get_config().MY_PARAM` or `settings.MY_PARAM` after the definition is gone, startup or runtime will raise `AttributeError`.
- **Old `ConfigRevision` rows retain the key in their JSON blob** — this is harmless and requires no migration. The risk is code: any remaining call to `get_config().MY_PARAM` or `settings.MY_PARAM` after the definition is gone will raise `AttributeError`. Remove all code references *before* removing the `ConfigParam` definition.
- **`configuration.py` in user deployments** — removing a static parameter may cause a `TypeError` or silent failure if users have `MY_PARAM = ...` in their local `configuration.py`. Document the removal in the release notes.
- **No `ruff format`** on existing files — use `ruff check` only.

## Summary Checklist

### Dynamic parameter

| # | File(s) | Action |
|---|---|---|
| 1 | All `.py` files | Remove all `get_config().MY_PARAM` and `ConfigItem('MY_PARAM')` usages |
| 2 | `netbox/netbox/config/parameters.py` | Remove `ConfigParam(...)` block from `PARAMS` |
| 3 | `docs/configuration/index.md` | Remove bullet-point entry |
| 4 | `docs/configuration/<category>.md` | Remove `## MY_PARAM` section |
| 5 | `netbox/netbox/configuration_example.py` | Remove commented entry (if present) |

### Static parameter

| # | File(s) | Action |
|---|---|---|
| 1 | All `.py` and template files | Remove all `settings.MY_PARAM` / `MY_PARAM` usages |
| 2 | `netbox/netbox/settings.py` | Remove `getattr` line; remove from required-params tuple; remove validation block |
| 3 | `netbox/netbox/configuration_example.py` | Remove commented entry |
| 4 | `docs/configuration/<category>.md` | Remove `## MY_PARAM` section |

## References

- Dynamic param definitions: `netbox/netbox/config/parameters.py`
- Config loading / `Config` class: `netbox/netbox/config/__init__.py`
- `ConfigRevision` model: `netbox/core/models/config.py`
- Static config loading: `netbox/netbox/settings.py` lines 67–213
- Example config: `netbox/netbox/configuration_example.py`
- Documentation: `docs/configuration/`
- `add-config-param` skill: `.claude/skills/add-config-param/SKILL.md` (reverse of this skill)
