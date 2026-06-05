---
name: add-model-field
description: Step-by-step checklist for adding a new field to an existing NetBox model, covering all required touch points (model, migration, validation, serializer, forms, filterset, table, panel/template, search, GraphQL, tests, docs). Use when the user asks to add a field or attribute to an existing model.
---

# Adding a Field to an Existing NetBox Model

Adding a field to an existing model touches many files. The scope depends on the field type and how it will be used. Work through the checklist below in order — each section builds on the previous.

## Before You Start

Determine upfront:
- **Field type**: scalar (CharField, IntegerField, etc.), FK/M2M, GenericForeignKey, or a special type like JSONField
- **Nullable/optional?** Most new fields should be `blank=True, null=True` unless there's a strong reason otherwise
- **Searchable?** Should it appear in global search results?
- **Filterable?** Should it be exposed in the FilterSet?
- **Displayable in list view?** Should it be a column in the object table?
- **Displayable in detail view?** Should it appear in the detail panel?

## 1. Add the Field to the Model

**File:** `netbox/<app>/models/<module>.py`

```python
class MyModel(PrimaryModel):
    # ... existing fields ...
    new_field = models.CharField(
        verbose_name=_('new field'),
        max_length=100,
        blank=True,
    )
    # FK example:
    related_thing = models.ForeignKey(
        to='app.RelatedModel',
        on_delete=models.PROTECT,
        related_name='my_models',
        blank=True,
        null=True,
    )
```

The `related_name` of a ForeignKey field should generally be the verbose form of the related model's name (e.g. `books` rather than the default `book_set`).

**Special cases:**

- **GenericForeignKey**: If this is a non-unique GFK, add a composite index in `Meta`:
  ```python
  class Meta:
      indexes = (
          models.Index(fields=('object_type', 'object_id')),
      )
  ```

- **`clone_fields`**: If the field should be pre-filled when cloning an object, add it to `clone_fields` on the model class:
  ```python
  clone_fields = ('existing_field', 'new_field')
  ```

- **Validation**: If the new field introduces cross-field constraints, add logic to `clean()`:
  ```python
  def clean(self):
      super().clean()
      if self.new_field and not self.related_field:
          raise ValidationError({'new_field': _('...')})
  ```

## 2. Generate the Migration

**Do NOT write migrations manually.** Tell the user to run:

```bash
python netbox/manage.py makemigrations <app> -n <short_descriptive_name> --no-header
```

Set `DEVELOPER = True` in `configuration.py` if the command is blocked.

For FK fields, also run:
```bash
python netbox/manage.py migrate
```
before continuing, so the DB is in sync for manual testing.

## 3. Update the API Serializer

The serializer lives under `netbox/<app>/api/serializers_/` (note the trailing underscore — it's a directory of submodules star-imported by `serializers.py`). Find the submodule that owns the model and edit the serializer there.

- **Simple field**: just add the field name to `fields` in `Meta`:
  ```python
  class Meta:
      fields = [..., 'new_field', ...]
  ```

- **FK field**: add a single serializer field with `nested=True`. NetBox does not use a separate `_id` companion field — the framework accepts a primary key (or brief object) when writing:
  ```python
  related_thing = RelatedThingSerializer(
      nested=True,
      required=False,
      allow_null=True,
  )
  # Add 'related_thing' to Meta.fields
  ```

- **`brief_fields`**: only add to `brief_fields` if the field is truly essential for compact/nested representations.

## 4. Update Forms

There are typically up to four forms to update. Find them under `netbox/<app>/forms/`.

### 4a. Model form (create/edit) — `model_forms.py`

Add the field to the `fieldsets` tuple and to `Meta.fields`:

```python
class MyModelForm(PrimaryModelForm):
    fieldsets = (
        FieldSet('name', 'new_field', 'related_thing', name=_('My Model')),
        ...
    )
    class Meta:
        model = MyModel
        fields = ('name', 'new_field', 'related_thing', ...)
```

For FK fields, use `DynamicModelChoiceField`:
```python
related_thing = DynamicModelChoiceField(
    queryset=RelatedModel.objects.all(),
    required=False,
)
```

### 4b. Bulk edit form — `bulk_edit.py`

Add the field as optional (so it can be blanked):
```python
new_field = forms.CharField(required=False)
# or for FK:
related_thing = DynamicModelChoiceField(queryset=..., required=False)
nullable_fields = ('new_field', 'related_thing')  # if it can be set to null
```
Add to `fieldsets` and `Meta.fields` here too.

### 4c. Bulk import form — `bulk_import.py`

If the field should be importable via CSV, add it to the import form:
```python
class MyModelImportForm(NetBoxModelImportForm):
    new_field = forms.CharField(required=False)
    class Meta:
        model = MyModel
        fields = ('name', 'new_field', ...)
```

### 4d. Filter form — `filtersets.py` (the forms version)

The base class should match the model's base (`PrimaryModelFilterSetForm`, `OrganizationalModelFilterSetForm`, `NestedGroupModelFilterSetForm`, or `NetBoxModelFilterSetForm`). Add the new entries to the existing `fieldsets` and declare the filter field:

```python
class MyModelFilterForm(PrimaryModelFilterSetForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('new_field', 'related_thing_id', name=_('Attributes')),
    )
    new_field = forms.CharField(required=False)
    related_thing_id = DynamicModelMultipleChoiceField(
        queryset=RelatedModel.objects.all(),
        required=False,
        label=_('Related Thing'),
    )
```

## 5. Update the FilterSet

**File:** `netbox/<app>/filtersets.py`

- **Simple scalar field**: add to `Meta.fields` if a basic exact/contains filter suffices.
- **FK field**: add both `<field>` (name lookup) and `<field>_id` (PK lookup) explicitly — do not rely on `Meta.fields` to generate them:

```python
class MyModelFilterSet(PrimaryModelFilterSet):
    related_thing = django_filters.ModelMultipleChoiceFilter(
        field_name='related_thing__name',
        queryset=RelatedModel.objects.all(),
        to_field_name='name',
        label=_('Related thing (name)'),
    )
    related_thing_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RelatedModel.objects.all(),
        label=_('Related thing (ID)'),
    )

    class Meta:
        model = MyModel
        fields = ('id', 'name', 'new_field', ...)  # add new_field here for simple fields
```

If the field should be searchable from the search box (`q=`), add it to the `search()` method:
```python
def search(self, queryset, name, value):
    return queryset.filter(
        Q(name__icontains=value) |
        Q(new_field__icontains=value) |  # add here
        ...
    )
```

## 6. Update the Table

**File:** `netbox/<app>/tables/<module>.py`

- **Simple field**: just add the field name to `Meta.fields`. Add to `default_columns` if it should show by default.
- **FK field** (linking to another object):
  ```python
  related_thing = tables.Column(linkify=True)
  ```
  Add `related_thing` to both `Meta.fields` and `default_columns` if appropriate.
- **Choice field**: display just works if the model uses `get_<field>_display()`; no custom column needed.
- **Traversed FK** (field accessed through another relation):
  ```python
  related_thing = tables.Column(
      accessor=tables.A('some_fk__related_thing'),
      linkify=True,
  )
  ```

## 7. Update the Detail View Panel

The detail view display is controlled by a panel class (not an HTML template), defined under `netbox/<app>/ui/panels.py`.

Find the panel for the model and add a new attribute declaration:

```python
from netbox.ui import attrs, panels

class MyModelPanel(panels.ObjectAttributesPanel):
    existing_field = attrs.TextAttr('existing_field')
    new_field = attrs.TextAttr('new_field')               # simple text
    related_thing = attrs.RelatedObjectAttr('related_thing', linkify=True)  # FK
    status = attrs.ChoiceAttr('status')                   # choice field with badge
    is_active = attrs.BooleanAttr('is_active')            # boolean
    color = attrs.ColorAttr('color')                      # color swatch
```

**Available attr types** (from `netbox.ui.attrs`):

| Class | Use for |
|---|---|
| `TextAttr` | Plain text / CharField |
| `NumericAttr` | Numbers, optionally with a unit |
| `ChoiceAttr` | Choice fields (renders a colored badge) |
| `BooleanAttr` | Boolean fields |
| `ColorAttr` | Color hex fields |
| `RelatedObjectAttr` | Direct ForeignKey |
| `NestedObjectAttr` | ForeignKey on a nested/hierarchical model (e.g. region.parent) |
| `RelatedObjectListAttr` | ManyToMany or reverse FK list |
| `GenericForeignKeyAttr` | GenericForeignKey |
| `DateTimeAttr` | DateTimeField |
| `TimezoneAttr` | Timezone fields |
| `AddressAttr` | Address text (optionally with map link) |
| `TemplatedAttr` | Custom per-field HTML template |

If the model uses a legacy HTML template (under `netbox/templates/<app>/`) rather than a declarative panel, add a `<tr>` row to the relevant `<table>` in that template instead.

## 8. Update the SearchIndex (if applicable)

**File:** `netbox/<app>/search.py`

If the new field should be indexed for global search, add it to the model's `SearchIndex`:

```python
@register_search
class MyModelIndex(SearchIndex):
    model = models.MyModel
    fields = (
        ('name', 100),
        ('new_field', 300),   # add here with an appropriate weight
        ('description', 500),
        ('comments', 5000),
    )
```

Weight guide: lower = higher search priority. Name fields ~100, short descriptors ~300–500, long-form comments ~5000.

## 9. Update GraphQL

### Filter — `graphql/filters.py`

Add a filter field to the model's `Filter` class:

```python
@strawberry_django.filter_type(models.MyModel, lookups=True)
class MyModelFilter(PrimaryModelFilter):
    # simple field (lookups=True auto-generates eq/icontains/etc.)
    new_field: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # FK field:
    related_thing: Annotated['RelatedThingFilter', strawberry.lazy('<app>.graphql.filters')] | None = strawberry_django.filter_field()
    related_thing_id: ID | None = strawberry_django.filter_field()
```

### Type — `graphql/types.py`

For simple fields, `fields='__all__'` on the type decorator will pick up the new field automatically. No change needed unless:

- The field is in an `exclude` list on the type — remove it.
- The field requires a custom type annotation (e.g. a lazy FK reference or a special scalar):
  ```python
  @strawberry_django.type(models.MyModel, fields='__all__', ...)
  class MyModelType(PrimaryObjectType):
      related_thing: Annotated['RelatedThingType', strawberry.lazy('<app>.graphql.types')] | None
  ```

> **Prefetch null failures:** If GraphQL unit tests fail citing null values on a non-nullable field, change the field definition to use `select_related`:
> ```python
> related_thing: ... = strawberry_django.field(select_related=['related_thing'])
> ```

## 10. Write Tests

### FilterSet tests — `tests/test_filtersets.py`

Add test methods for any new FilterSet fields:

```python
def test_new_field(self):
    params = {'new_field': ['value1', 'value2']}
    self.assertEqual(self.filterset(params, self.queryset).qs.count(), expected)

def test_related_thing(self):
    # Test both name and _id variants
    related = RelatedModel.objects.filter(...)
    params = {'related_thing_id': [related[0].pk]}
    self.assertEqual(self.filterset(params, self.queryset).qs.count(), expected)
    params = {'related_thing': [related[0].name]}
    self.assertEqual(self.filterset(params, self.queryset).qs.count(), expected)
```

Ensure `setUpTestData` creates test objects with diverse values for the new field.

### API tests — `tests/test_api.py`

- Update `setUpTestData` to populate the new field in test instances.
- Update `create_data` and (if applicable) `bulk_update_data` to include the new field.
- If the field is filterable via the API, add a `test_list_objects_by_<field>` test.

### View tests — `tests/test_views.py`

- Update `form_data` in `setUpTestData` to include the new field.
- Update `bulk_edit_data` if the field is bulk-editable.
- Update `csv_data` if the field is importable.

### Model tests — `tests/test_models.py` (if validation was added)

Add a test for any custom `clean()` logic:

```python
def test_clean_new_field_validation(self):
    instance = MyModel(new_field='invalid_value', ...)
    with self.assertRaises(ValidationError):
        instance.clean()
```

## 11. Update Documentation

**File:** `docs/models/<app>/<modelname>.md`

Add the new field to the model's documentation page. Include:
- The field name and description
- Valid values (for choice fields)
- Any constraints or dependencies

## Summary Checklist

| # | File(s) | Action |
|---|---|---|
| 1 | `models/<module>.py` | Add field; add to `clone_fields`; add `clean()` validation |
| 2 | (user runs) | `makemigrations <app> -n <name> --no-header` |
| 3 | `api/serializers_/<module>.py` | Add field to `fields`; for FK use a single `Serializer(nested=True)` field (no `_id` companion) |
| 4a | `forms/model_forms.py` | Add to `fieldsets` and `Meta.fields` |
| 4b | `forms/bulk_edit.py` | Add as optional; add to `nullable_fields` if nullable |
| 4c | `forms/bulk_import.py` | Add if CSV-importable |
| 4d | `forms/filtersets.py` | Add filter field and to `fieldsets` |
| 5 | `filtersets.py` | Add to FilterSet; add FK + FK_id pair; update `search()` |
| 6 | `tables/<module>.py` | Add column; add to `Meta.fields`; update `default_columns` |
| 7 | `<app>/ui/panels.py` | Add attr to the model's panel class |
| 8 | `search.py` | Add to SearchIndex `fields` tuple with appropriate weight |
| 9 | `graphql/filters.py`, `types.py` | Add filter field; update type if excluded or needs custom annotation |
| 10 | `tests/test_*.py` | Update filterset, API, view, and model tests |
| 11 | `docs/models/<app>/<model>.md` | Document the new field |

## Common Gotchas

- **FilterSets need explicit `_id` variants for FK fields** — `Meta.fields` does not auto-generate them. (This is FilterSet-only — API serializers do **not** add a parallel `_id` field; see below.)
- **Serializer FK fields use `nested=True`, not a parallel `_id`.** Older code that defines both `foo = NestedFooSerializer(read_only=True)` and `foo_id = serializers.PrimaryKeyRelatedField(...)` is the legacy pattern; new code uses a single `foo = FooSerializer(nested=True, ...)` field.
- **Migrations must be generated, not written manually.** If `makemigrations` is blocked, ensure `DEVELOPER = True` is set in `configuration.py`.
- **List views and API serializers don't need manual `prefetch_related()`** — this is handled dynamically. Only add explicit prefetches in a viewset if required for a custom endpoint.
- **`clone_fields` must be declared explicitly** on the model. Fields not in this list are not copied when cloning an object.
- **`brief_fields` on serializers is explicit** — just listing a field in `Meta.fields` does not include it in brief/nested representations.
- **Panel attrs, not HTML templates** — new models use `ObjectAttributesPanel` subclasses in `<app>/ui/panels.py`. Only fall back to editing `templates/<app>/` HTML files if the model predates the declarative layout system.
- **GraphQL `fields='__all__'`** picks up simple new fields automatically; only explicit overrides needed for FKs, excluded fields, or special scalars.
- **No `ruff format`** on existing files — use `ruff check` only.

## References

- Real example (adding FK filter field): `git show 87b17ff26` — adds `profile`/`profile_id` to the Module filterset, filter form, table, template, and tests
- Real example (adding a JSONField): `git show 5f802bb18` — adds `choice_colors` to CustomFieldChoiceSet across model, forms, filterset, serializer, GraphQL, and tests
- Panel attrs reference: `netbox/netbox/ui/attrs.py`
- Panel classes: `netbox/<app>/ui/panels.py`
- Base filterset classes: `netbox/netbox/filtersets.py`
- Contributing guide: `docs/development/extending-models.md`
