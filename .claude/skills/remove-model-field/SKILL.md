---
name: remove-model-field
description: Step-by-step checklist for removing a field from an existing NetBox model, covering all required touch points (model, migration, serializer, forms, filterset, table, panel/template, search, GraphQL, tests, docs). Use when the user asks to remove or delete a field or attribute from an existing model.
---

# Removing a Field from an Existing NetBox Model

Removing a field touches many files. Work through the checklist below in order — remove outer consumers first (tests, docs, GraphQL, API, forms) before touching the model definition itself.

## Before You Start

Determine upfront:
- **Field name** and which **model/app** owns it
- **Field type**: scalar, FK/M2M, GenericForeignKey, or special (JSONField, etc.)
- **All references** — run a broad grep before touching anything:

```bash
grep -r 'new_field\|related_thing' netbox/ --include='*.py' -l
grep -r 'new_field\|related_thing' docs/ -l
```

For FK/M2M fields, also check for FilterSet `_id` companions and GraphQL lazy annotations referencing this field.

**Check dependents**: if other models or code use this field (e.g. ordering, constraints, signal handlers), those references must be cleaned up too.

## 1. Update Tests

Update test files to remove references to the field being deleted. Specifically:

- **`tests/test_filtersets.py`** — remove `test_<field>` and `test_<field>_id` methods; remove the field from `setUpTestData` test objects.
- **`tests/test_api.py`** — remove the field from `setUpTestData`, `create_data`, and `bulk_update_data`; remove any `test_list_objects_by_<field>` methods.
- **`tests/test_views.py`** — remove the field from `form_data`, `bulk_edit_data`, and `csv_data` in `setUpTestData`.
- **`tests/test_models.py`** — remove any `test_clean_<field>` or constraint tests specific to this field.

## 2. Update Documentation

**File:** `docs/models/<app>/<modelname>.md`

Remove the field's entry from the `## Fields` section. If the field had any cross-references in other doc pages, remove those too.

## 3. Update GraphQL

### Filter — `graphql/filters.py`

Remove the filter field declaration(s) for the deleted field:

```python
# Remove lines like:
new_field: StrFilterLookup[str] | None = strawberry_django.filter_field()

# Or for FK:
related_thing: Annotated[...] | None = strawberry_django.filter_field()
related_thing_id: ID | None = strawberry_django.filter_field()
```

### Type — `graphql/types.py`

For simple fields, `fields='__all__'` means no change is needed — the field disappears automatically once removed from the model.

For FK fields with an explicit annotation, remove the annotation line:

```python
# Remove:
related_thing: Annotated['RelatedThingType', strawberry.lazy('<app>.graphql.types')] | None
```

If the field was in an `exclude` list, remove it from the exclude list (it no longer exists to exclude).

## 4. Update the API Serializer

**File:** `netbox/<app>/api/serializers_/<module>.py`

- **Simple field**: remove the field name from `Meta.fields` (and `brief_fields` if present).
- **FK field**: remove the serializer field declaration and its name from `Meta.fields`:

```python
# Remove:
related_thing = RelatedThingSerializer(nested=True, required=False, allow_null=True)
# And remove 'related_thing' from Meta.fields
```

## 5. Update Forms

There are typically up to four forms to update. Find them under `netbox/<app>/forms/`.

### 5a. Filter form — `forms/filtersets.py`

- Remove the field from `fieldsets`.
- Remove the filter field declaration (e.g. `new_field = forms.CharField(...)` or the `DynamicModelMultipleChoiceField`).

### 5b. Bulk edit form — `forms/bulk_edit.py`

- Remove the field from `fieldsets` and `Meta.fields` (if present).
- Remove the field declaration.
- Remove from `nullable_fields` if listed there.

### 5c. Bulk import form — `forms/bulk_import.py`

- Remove from `Meta.fields`.
- Remove any explicit field declaration.

### 5d. Model form — `model_forms.py`

- Remove from `fieldsets`.
- Remove from `Meta.fields`.
- Remove any explicit field declaration (e.g. a `DynamicModelChoiceField`).

## 6. Update the FilterSet

**File:** `netbox/<app>/filtersets.py`

- **Simple field**: remove from `Meta.fields`.
- **FK field**: remove both the `<field>` and `<field>_id` explicit filter declarations.
- **`search()` method**: if the field was included in the `Q(...)` chain, remove that clause.
- Remove any now-unused imports (e.g. the related model import if it was only used by this filter).

## 7. Update the Table

**File:** `netbox/<app>/tables/<module>.py`

- Remove the column declaration (e.g. `related_thing = tables.Column(linkify=True)`).
- Remove the field from `Meta.fields`.
- Remove from `default_columns` if listed there.

## 8. Update the Detail View Panel

**File:** `netbox/<app>/ui/panels.py`

Find the panel class for the model and remove the attribute declaration:

```python
# Remove:
new_field = attrs.TextAttr('new_field')
related_thing = attrs.RelatedObjectAttr('related_thing', linkify=True)
```

If the model uses a legacy HTML template (`netbox/templates/<app>/`) rather than a declarative panel, remove the corresponding `<tr>` row from that template instead.

## 9. Update the SearchIndex

**File:** `netbox/<app>/search.py`

If the field was indexed for global search, remove it from the `fields` tuple:

```python
# Remove:
('new_field', 300),
```

## 10. Remove the Field from the Model

**File:** `netbox/<app>/models/<module>.py`

1. Delete the field declaration.
2. If the field was in `clone_fields`, remove it from that tuple.
3. If `clean()` had validation logic specific to this field, remove those clauses. If `clean()` becomes empty, remove the override entirely.
4. For FK fields: remove the `related_name` on the target model is automatic (Django handles it). If the FK was the only reason a related model was imported, remove that import too.
5. Check `Meta` for references to the field:
   - `ordering` — if the field appears in the ordering tuple, remove it (or replace with a remaining field if ordering would otherwise become empty).
   - `constraints` — remove any `UniqueConstraint` or `CheckConstraint` whose `fields` list includes this field; if only this field remains, remove the constraint entirely; if other fields remain, remove just this field from the list.
   - `indexes` — remove any `models.Index` that includes this field.
6. For GenericForeignKey fields: if this was the only GFK, also remove the `object_type` ContentType FK and `object_id` integer field, and remove the `models.Index(fields=('object_type', 'object_id'))` from `Meta`.

## 11. Generate the Migration

**Do NOT write migrations manually.** Tell the user to run:

```bash
cd netbox/
python manage.py makemigrations <app> -n remove_<field>_from_<model> --no-header
```

Set `DEVELOPER = True` in `configuration.py` if the command is blocked.

Review the generated migration — it should contain only a `RemoveField` operation (plus any index removal for GFK fields). Apply with:

```bash
python manage.py migrate
```

## Summary Checklist

| # | File(s) | Action |
|---|---|---|
| 1 | `tests/test_*.py` | Remove field from test data, filter tests, API tests, view tests |
| 2 | `docs/models/<app>/<model>.md` | Remove field from `## Fields` section |
| 3 | `graphql/filters.py`, `types.py` | Remove filter field; remove FK annotation if explicit |
| 4 | `api/serializers_/<module>.py` | Remove from `Meta.fields`; remove FK serializer field |
| 5a | `forms/filtersets.py` | Remove from `fieldsets`; remove filter field declaration |
| 5b | `forms/bulk_edit.py` | Remove from `fieldsets`, `Meta.fields`, `nullable_fields` |
| 5c | `forms/bulk_import.py` | Remove from `Meta.fields` and field declaration |
| 5d | `forms/model_forms.py` | Remove from `fieldsets`, `Meta.fields`, and field declaration |
| 6 | `filtersets.py` | Remove from `Meta.fields`; remove FK + FK_id pair; update `search()` |
| 7 | `tables/<module>.py` | Remove column declaration and from `Meta.fields`, `default_columns` |
| 8 | `<app>/ui/panels.py` | Remove attr declaration from panel class |
| 9 | `search.py` | Remove from SearchIndex `fields` tuple |
| 10 | `models/<module>.py` | Remove field; clean up `clone_fields`, `clean()`, `Meta` ordering/constraints/indexes, imports |
| 11 | (user runs) | `makemigrations <app> -n remove_<field>_from_<model> --no-header` then `migrate` |

## Common Gotchas

- **Work outside-in** — remove tests, docs, GraphQL, and API references before touching the model, to avoid import errors during the process.
- **FK fields leave no `_id` companion in serializers** — the modern pattern uses a single `field = Serializer(nested=True)`. Grep for the field name and the serializer class name.
- **FilterSets have both `<field>` and `<field>_id`** — both must be removed; they are explicit declarations, not auto-generated.
- **`clone_fields`** must be updated if the field was listed there.
- **`search()` in filtersets** — if the field was in the `Q(...)` chain of the `search()` method, that clause must be removed to avoid a `FieldError` at runtime.
- **`brief_fields` in serializers** — remove explicitly if the field was listed.
- **`makemigrations` must be run**, not written manually. If blocked, set `DEVELOPER = True` in `configuration.py`.
- **No `ruff format`** on existing files — use `ruff check` only.

## References

- Panel attrs reference: `netbox/netbox/ui/attrs.py`
- Panel classes: `netbox/<app>/ui/panels.py`
- Base filterset classes: `netbox/netbox/filtersets.py`
- `add-model-field` skill: `.claude/skills/add-model-field/SKILL.md` (reverse of this skill)
- Contributing guide: `docs/development/extending-models.md`
