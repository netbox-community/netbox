---
name: remove-model
description: Step-by-step guide for removing an existing model from NetBox, covering all required touch points in safe deletion order (tests, docs, nav, search, GraphQL, API, views, URLs, forms, filterset, table, choices, model, migration). Use when the user asks to remove, delete, or deprecate a model or object type from NetBox.
---

# Removing a Model from NetBox

Removing a model requires undoing ~13 components. Work in the order below — remove consumers before providers to avoid import errors during the process. Deleting a model is **irreversible once migrated**; confirm with the user before running `makemigrations`.

## 0. Before You Start

Identify:
- **Model name** and **app** — e.g. `MyModel` in `dcim`
- **All references** — run a broad grep before touching anything:

```bash
grep -r 'MyModel\|mymodel\|my-model\|my_model' netbox/ --include='*.py' -l
grep -r 'MyModel\|mymodel\|my-model\|my_model' docs/ -l
grep -r 'mymodel\|my-model' netbox/netbox/navigation/ --include='*.py'
```

Check for:
- Other models with ForeignKey / M2M pointing to this model (they need updating or their own removal first)
- Generic relations via `FeatureQuery` or `ContentType` that reference this model
- Any plugin or external code documented as depending on this model

**Do not proceed if other retained models have non-nullable FKs to this model** — those FK fields must be removed or made nullable first.

## 1. Remove Tests

Delete test methods or entire test classes that exist solely for this model. If the test file contains only this model's tests, delete the file; otherwise remove just the relevant class(es).

Files to check:
- `netbox/<app>/tests/test_api.py`
- `netbox/<app>/tests/test_views.py`
- `netbox/<app>/tests/test_filtersets.py`
- `netbox/<app>/tests/test_models.py`
- `netbox/<app>/tests/test_forms.py`
- `netbox/<app>/tests/test_tables.py`
- Any app-specific test modules (e.g. `test_cablepaths.py`)

## 2. Remove Documentation

1. Delete `docs/models/<app>/<modelname>.md`.
2. Remove the `mkdocs.yml` entry under the relevant `nav:` group.
3. Remove the entry from `docs/development/models.md` (the "Models Index" list).

## 3. Remove Navigation Menu Entry

**File:** `netbox/netbox/navigation/menu.py`

Remove the `get_model_item('<app>', 'mymodel', ...)` line from the relevant `MenuGroup`.

## 4. Remove from Search Index

**File:** `netbox/<app>/search.py`

Delete the `@register_search` class for the model. If the file becomes empty (no other indexes), delete the file itself.

## 5. Remove GraphQL

Remove in this order (schema depends on types, types depend on filters):

1. **`netbox/<app>/graphql/schema.py`** — remove the `my_model` and `my_model_list` fields from the app's `Query` type.
2. **`netbox/<app>/graphql/types.py`** — remove the `MyModelType` class and its `__all__` entry.
3. **`netbox/<app>/graphql/filters.py`** — remove the `MyModelFilter` class and its `__all__` entry.

If any remaining type in `types.py` has a lazy annotation referencing `MyModelType`, remove that annotation too.

## 6. Remove REST API

1. **`netbox/<app>/api/urls.py`** — remove the `router.register('my-models', ...)` line.
2. **`netbox/<app>/api/views.py`** — remove the `MyModelViewSet` class.
3. **`netbox/<app>/api/serializers_/<module>.py`** — remove the serializer class. If this was the only serializer in the module, delete the file and remove its `from .<module> import *` line from `serializers_/__init__.py`.

Also check other serializers that reference this model (e.g. `MyModelSerializer(nested=True)` on related serializers) and remove those fields too.

## 7. Remove URL Routes

**File:** `netbox/<app>/urls.py`

Remove the two `path(...)` entries that call `get_model_urls('<app>', 'mymodel', ...)`.

## 8. Remove Views

**File:** `netbox/<app>/views.py`

Remove all view classes decorated with `@register_model_view(MyModel, ...)`. There are typically seven:

- `MyModelListView`
- `MyModelView`
- `MyModelEditView`
- `MyModelDeleteView`
- `MyModelBulkImportView`
- `MyModelBulkEditView`
- `MyModelBulkDeleteView`
- `MyModelBulkRenameView` (if present)

Also remove the panel class from `netbox/<app>/ui/panels.py` and any `layout` references using it.

If there is a model-specific HTML template (`netbox/templates/<app>/mymodel.html` or similar), delete it.

## 9. Remove Table

**File:** `netbox/<app>/tables/<module>.py`

Remove the `MyModelTable` class. If it is the sole table in the module, delete the file and clean up the `__init__.py` re-export.

**File:** `netbox/<app>/tables/__init__.py`

Remove the corresponding `from .<module> import *` or named import.

## 10. Remove Forms

Remove in dependency order (bulk forms depend on the model form):

1. **`netbox/<app>/forms/bulk_import.py`** — remove `MyModelImportForm`.
2. **`netbox/<app>/forms/bulk_edit.py`** — remove `MyModelBulkEditForm`.
3. **`netbox/<app>/forms/filtersets.py`** — remove `MyModelFilterForm`.
4. **`netbox/<app>/forms/model_forms.py`** — remove `MyModelForm`.
5. **`netbox/<app>/forms/__init__.py`** — remove all re-exports of the deleted form classes.

## 11. Remove FilterSet

**File:** `netbox/<app>/filtersets.py`

Remove the `MyModelFilterSet` class. Also remove any imports of `MyModel` or related models that were only used by this filterset.

## 12. Remove Choices

**File:** `netbox/<app>/choices.py`

Remove any `ChoiceSet` subclasses that were defined exclusively for this model (e.g. `MyModelStatusChoices`). Leave choices that are shared with other models.

## 13. Remove the Model

**File:** `netbox/<app>/models/<module>.py` (or `models.py`)

1. Delete the `MyModel` class.
2. Remove `'MyModel'` from `__all__` in the module.
3. Remove the import line in `netbox/<app>/models/__init__.py` if this was the last model in the submodule (or remove just the `MyModel` name from a `from .<module> import ...` line).
4. Remove any now-unused imports in the model file itself.

## 14. Generate the Migration

**Do NOT write migrations manually.** Tell the user to run:

```bash
cd netbox/
python manage.py makemigrations <app> -n remove_mymodel --no-header
```

Set `DEVELOPER = True` in `configuration.py` if the command is blocked.

Review the generated migration before applying — it should only contain a `DeleteModel` operation (plus any `RemoveField` operations for FKs on other models if Django detected them). Apply with:

```bash
python manage.py migrate
```

## Common Gotchas

- **Remove consumers before providers** — tests, docs, GraphQL schema, API viewset, URL routes, and views all reference the model; remove them before removing the model itself to avoid import errors.
- **FK cleanup** — Django will detect FKs pointing at the deleted model and auto-add `RemoveField` operations to the migration. Verify the migration is correct before running it.
- **ContentType cleanup** — after migrating, `ContentType` rows for the old model linger in the database. They are harmless but can be cleaned up with `python manage.py remove_stale_contenttypes`.
- **`__all__` entries** — grep all `__init__.py` files for the model name after removing the class; dangling re-exports cause `ImportError` at startup.
- **Serializer references** — other serializers may have a nested `MyModelSerializer(nested=True)` field. Search for the serializer class name as well as the model name.
- **`manage.py` lives in `netbox/`**, not the repo root.
- **No `ruff format`** on existing files — use `ruff check` only.

## Summary Checklist

| # | File(s) | Action |
|---|---|---|
| 1 | `tests/test_*.py` | Remove test classes for this model |
| 2 | `docs/models/<app>/<model>.md`, `mkdocs.yml`, `docs/development/models.md` | Delete doc page; remove nav entries |
| 3 | `netbox/netbox/navigation/menu.py` | Remove `get_model_item(...)` line |
| 4 | `<app>/search.py` | Remove `SearchIndex` class |
| 5 | `<app>/graphql/schema.py`, `types.py`, `filters.py` | Remove query fields, type, filter |
| 6 | `<app>/api/urls.py`, `views.py`, `serializers_/<module>.py` | Remove router entry, viewset, serializer |
| 7 | `<app>/urls.py` | Remove `get_model_urls(...)` paths |
| 8 | `<app>/views.py`, `<app>/ui/panels.py` | Remove all view classes and panel |
| 9 | `<app>/tables/<module>.py`, `tables/__init__.py` | Remove table class and re-export |
| 10 | `<app>/forms/*.py`, `forms/__init__.py` | Remove all four form classes and re-exports |
| 11 | `<app>/filtersets.py` | Remove `FilterSet` class |
| 12 | `<app>/choices.py` | Remove model-specific `ChoiceSet` subclasses |
| 13 | `<app>/models/<module>.py`, `models/__init__.py` | Remove model class and `__all__` entry |
| 14 | (user runs) | `makemigrations <app> -n remove_mymodel --no-header` then `migrate` |

## References

- Model base classes: `netbox/netbox/models/__init__.py`
- Navigation menu: `netbox/netbox/navigation/menu.py`
- `add-model` skill: `.claude/skills/add-model/SKILL.md` (reverse of this skill)
