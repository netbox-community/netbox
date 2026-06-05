---
name: add-model
description: Step-by-step guide for adding a new model to NetBox, including all required components (model, filterset, serializer, views, forms, tables, GraphQL, tests, docs, navigation). Use when the user asks to add a new model or object type to NetBox.
---

# Adding a New Model to NetBox

Adding a model requires wiring up ~12 components. Work through them in order — each builds on the previous. If the user hasn't specified which app to place the model in, ask first.

## 0. Before You Start

Decide on:
- **App**: which existing app owns this model (`dcim`, `ipam`, `extras`, etc.)
- **Base class**: see the hierarchy below
- **URL slug**: the kebab-case name used in URLs (e.g. `virtual-chassis`)
- **Model name**: PascalCase (e.g. `VirtualChassis`)
- **Verbose names**: for `Meta.verbose_name` / `verbose_name_plural`

### Base Class Hierarchy

| Class | Use when                                                                            |
|---|-------------------------------------------------------------------------------------|
| `PrimaryModel` | Real infrastructure objects with description, comments, and owner. Most new models. |
| `OrganizationalModel` | Purely organizational/grouping objects (roles, types, categories).                  |
| `NestedGroupModel` | Hierarchical tree objects (regions, locations). Uses MPTT.                          |
| `ChangeLoggedModel` | Lightweight ancillary objects; no custom fields, tags, etc.                         |
| `AdminModel` | Administrative resources (no change-logging in the user-facing changelog).          |
| `NetBoxModel` | Direct subclass of the feature set — use only when no other class fits.             |

All of these live in `netbox/netbox/models/__init__.py`. The remainder of this skill assumes `PrimaryModel`; substitute the matching `Organizational…` / `NestedGroup…` / `ChangeLogged…` base classes (filterset, form, table, serializer, GraphQL) where appropriate.

## 1. Define the Model

**File:** `netbox/<app>/models/<module>.py` (or `models.py` for smaller apps)

```python
class MyModel(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        db_collation='natural_sort',  # for alphabetic-aware sorting
    )
    some_fk = models.ForeignKey(
        to='app.RelatedModel',
        on_delete=models.PROTECT,
        related_name='my_models',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('my model')
        verbose_name_plural = _('my models')

    def __str__(self):
        return self.name
```

- Add the model to `__all__` in the models module's `__init__.py`.
- `db_collation='natural_sort'` on name fields enables natural sort order; omit if not needed.
- Use `models.PROTECT` for FK `on_delete` unless cascade deletion is explicitly desired.
- `PrimaryModel` already provides `description`, `comments`, and `owner` — don't redeclare them.

**Do NOT run `makemigrations` yourself.** Tell the user to run the following when finished:

```bash
python netbox/manage.py makemigrations
```

## 2. Define Field Choices (if needed)

**File:** `netbox/<app>/choices.py`

```python
class MyModelStatusChoices(ChoiceSet):
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'

    CHOICES = [
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
    ]
```

Reference with `choices=MyModelStatusChoices` on the model field and `choices=MyModelStatusChoices.CHOICES` in forms.

## 3. Create the FilterSet

**File:** `netbox/<app>/filtersets.py`

```python
class MyModelFilterSet(PrimaryModelFilterSet):
    some_fk = django_filters.ModelMultipleChoiceFilter(
        field_name='some_fk__name',
        queryset=RelatedModel.objects.all(),
        to_field_name='name',
        label=_('Related model (name)'),
    )
    some_fk_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RelatedModel.objects.all(),
        label=_('Related model (ID)'),
    )

    class Meta:
        model = MyModel
        fields = ('id', 'name', 'description')
```

**Critical:** Always add both `<field>` (name/slug lookup) and `<field>_id` (PK lookup) for every FK. Do not rely on `Meta.fields` to auto-generate `_id` variants — it won't work correctly.

Match the base class to the model: `PrimaryModelFilterSet`, `OrganizationalModelFilterSet`, `NetBoxModelFilterSet`, or `ChangeLoggedModelFilterSet`.

## 4. Create Forms

**File:** `netbox/<app>/forms/model_forms.py`

```python
class MyModelForm(PrimaryModelForm):
    fieldsets = (
        FieldSet('name', 'some_fk', name=_('My Model')),
        FieldSet('description', 'tags', name=_('Other')),
    )

    class Meta:
        model = MyModel
        fields = ('name', 'some_fk', 'description', 'owner', 'comments', 'tags')
```

**File:** `netbox/<app>/forms/filtersets.py` (for the filter form)

```python
class MyModelFilterForm(PrimaryModelFilterSetForm):
    model = MyModel
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('some_fk_id', name=_('Related')),
    )
    some_fk_id = DynamicModelMultipleChoiceField(
        queryset=RelatedModel.objects.all(),
        required=False,
        label=_('Related Model'),
    )
    tag = TagFilterField(model)
```

Match the form base class to the model's base: `PrimaryModelFilterSetForm`, `OrganizationalModelFilterSetForm`, `NestedGroupModelFilterSetForm`, or `NetBoxModelFilterSetForm` (all in `netbox.forms`).

### Bulk Edit Form — `netbox/<app>/forms/bulk_edit.py`

```python
class MyModelBulkEditForm(PrimaryModelBulkEditForm):
    model = MyModel
    description = forms.CharField(max_length=200, required=False)
    some_fk = DynamicModelChoiceField(queryset=RelatedModel.objects.all(), required=False)

    fieldsets = (
        FieldSet('some_fk', 'description', name=_('My Model')),
    )
    nullable_fields = ('description', 'some_fk')
```

### Bulk Import Form — `netbox/<app>/forms/bulk_import.py`

```python
class MyModelImportForm(PrimaryModelImportForm):
    some_fk = CSVModelChoiceField(
        queryset=RelatedModel.objects.all(),
        to_field_name='name',
        required=False,
    )

    class Meta:
        model = MyModel
        fields = ('name', 'some_fk', 'description', 'comments', 'tags')
```

Use the matching `Primary…` / `Organizational…` / `NestedGroup…` / `NetBoxModel…` variants of `…ImportForm` and `…BulkEditForm` for non-PrimaryModel bases.

Export each new form from `netbox/<app>/forms/__init__.py`.

## 5. Create the Table

**File:** `netbox/<app>/tables/<module>.py`

```python
class MyModelTable(PrimaryModelTable):
    name = tables.Column(linkify=True)
    some_fk = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name='<app>:mymodel_list')

    class Meta(PrimaryModelTable.Meta):
        model = MyModel
        fields = ('pk', 'id', 'name', 'some_fk', 'description', 'tags', 'created', 'last_updated')
        default_columns = ('pk', 'name', 'some_fk', 'description')
```

Use custom columns provided by NetBox where appropriate. Otherwise, export from the tables package's `__init__.py`.

## 6. Add Views

**File:** `netbox/<app>/views.py`

Common imports:

```python
from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import layout
from netbox.ui.panels import CommentsPanel
from netbox.views import generic
from utilities.views import register_model_view
```

```python
@register_model_view(MyModel, 'list', path='', detail=False)
class MyModelListView(generic.ObjectListView):
    queryset = MyModel.objects.all()
    table = tables.MyModelTable
    filterset = filtersets.MyModelFilterSet
    filterset_form = forms.MyModelFilterForm

@register_model_view(MyModel)
class MyModelView(generic.ObjectView):
    queryset = MyModel.objects.all()
    template_name = 'generic/object.html'  # opt out of model-specific template lookup
    layout = layout.SimpleLayout(
        left_panels=[panels.MyModelPanel(), TagsPanel(), CustomFieldsPanel()],
        right_panels=[CommentsPanel()],
    )

@register_model_view(MyModel, 'add', detail=False)
@register_model_view(MyModel, 'edit')
class MyModelEditView(generic.ObjectEditView):
    queryset = MyModel.objects.all()
    form = forms.MyModelForm

@register_model_view(MyModel, 'delete')
class MyModelDeleteView(generic.ObjectDeleteView):
    queryset = MyModel.objects.all()

@register_model_view(MyModel, 'bulk_import', path='import', detail=False)
class MyModelBulkImportView(generic.BulkImportView):
    queryset = MyModel.objects.all()
    model_form = forms.MyModelImportForm

@register_model_view(MyModel, 'bulk_edit', path='edit', detail=False)
class MyModelBulkEditView(generic.BulkEditView):
    queryset = MyModel.objects.all()
    filterset = filtersets.MyModelFilterSet
    table = tables.MyModelTable
    form = forms.MyModelBulkEditForm

@register_model_view(MyModel, 'bulk_delete', path='delete', detail=False)
class MyModelBulkDeleteView(generic.BulkDeleteView):
    queryset = MyModel.objects.all()
    filterset = filtersets.MyModelFilterSet
    table = tables.MyModelTable
```

`path='import'`/`'edit'`/`'delete'` keep URLs short and match existing apps. If the model has a `name` field amenable to find/replace, also register a `bulk_rename` view (`generic.BulkRenameView`, `path='rename'`).

Define `MyModelPanel` as an `ObjectAttributesPanel` subclass in `netbox/<app>/ui/panels.py` (see `netbox/dcim/ui/panels.py` for examples and the field summary in `add-model-field`).

## 7. Add URL Routes

**File:** `netbox/<app>/urls.py`

```python
from utilities.urls import get_model_urls

urlpatterns = [
    # ...existing routes...
    path('my-models/', include(get_model_urls('<app>', 'mymodel', detail=False))),
    path('my-models/<int:pk>/', include(get_model_urls('<app>', 'mymodel'))),
]
```

`get_model_urls()` auto-generates routes for all registered views. `detail=False` covers the list/create routes; the second `path` covers detail/edit/delete routes.

## 8. REST API

### Serializer

Each app has a `netbox/<app>/api/serializers_/` package (note the trailing underscore — it's a directory). Add a new module like `mymodel.py` and re-export from `serializers_/__init__.py` (`netbox/<app>/api/serializers.py` star-imports each submodule).

```python
class MyModelSerializer(PrimaryModelSerializer):
    some_fk = RelatedModelSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = MyModel
        fields = [
            'id', 'url', 'display_url', 'display',
            'name', 'some_fk',
            'description', 'owner', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
```

NetBox serializers use a single FK field with `nested=True` — no separate `_id` companion. Pass `nested=True` when the related serializer is referenced by another serializer; the framework renders it as a brief representation when reading and accepts a primary key (or brief object) when writing. Match the base class to the model: `PrimaryModelSerializer`, `OrganizationalModelSerializer`, `NestedGroupModelSerializer`, `NetBoxModelSerializer`.

### ViewSet

**File:** `netbox/<app>/api/views.py`

```python
class MyModelViewSet(NetBoxModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = serializers.MyModelSerializer
    filterset_class = filtersets.MyModelFilterSet
```

Skip `prefetch_related()` on the queryset — `NetBoxModelViewSet` resolves prefetches dynamically based on the serializer.

### API URL Route

**File:** `netbox/<app>/api/urls.py`

```python
router.register('my-models', views.MyModelViewSet)
```

## 9. GraphQL

### Filter

**File:** `netbox/<app>/graphql/filters.py`

```python
@strawberry_django.filter_type(models.MyModel, lookups=True)
class MyModelFilter(PrimaryModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    some_fk: Annotated['RelatedModelFilter', strawberry.lazy('<app>.graphql.filters')] | None = strawberry_django.filter_field()
    some_fk_id: ID | None = strawberry_django.filter_field()
```

Add `'MyModelFilter'` to `__all__` at the top of the file.

### Type

**File:** `netbox/<app>/graphql/types.py`

```python
@strawberry_django.type(
    models.MyModel,
    fields='__all__',
    filters=MyModelFilter,
    pagination=True,
)
class MyModelType(PrimaryObjectType):
    some_fk: Annotated['RelatedModelType', strawberry.lazy('<app>.graphql.types')] | None
```

Add `'MyModelType'` to `__all__`.

### Schema

**File:** `netbox/<app>/graphql/schema.py`

```python
@strawberry.type
class MyAppQuery:
    # ...existing fields...
    my_model: MyModelType = strawberry_django.field()
    my_model_list: list[MyModelType] = strawberry_django.field()
```

> **Note:** GraphQL unit tests may fail citing null values on a non-nullable field if related objects are prefetched. Fix by using `= strawberry_django.field(select_related=['some_fk'])` instead.

## 10. Register in Search

**File:** `netbox/<app>/search.py`

```python
@register_search
class MyModelIndex(SearchIndex):
    model = models.MyModel
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('some_fk', 'description')
```

Field weights: lower = higher priority in results. Typical: name=100, description=500, comments=5000.

## 11. Add Navigation Menu Entry

**File:** `netbox/netbox/navigation/menu.py`

Find the relevant `MenuGroup` and add:

```python
get_model_item('<app>', 'mymodel', _('My Models')),
```

The model name must be lowercase (not the URL slug). This auto-links to the list view.

## 12. Add Documentation

**File:** `docs/models/<app>/<modelname>.md` (filename is the lowercase model name with no separators, e.g. `virtualchassis.md`).

Include at minimum:
- A description of what the model represents
- A `## Fields` section with a subsection per field (see `docs/models/dcim/site.md` for the canonical structure)

Then register the page in two indexes:

- `mkdocs.yml` — add a line under the appropriate `nav:` group (e.g. `- MyModel: 'models/<app>/mymodel.md'`)
- `docs/development/models.md` — add to the relevant model-type list under "Models Index" (Primary, Organizational, Nested Group, etc.)

There is no per-app `index.md` under `docs/models/` — `mkdocs.yml` is the single source of truth for navigation.

## 13. Write Tests

### API Tests

**File:** `netbox/<app>/tests/test_api.py`

```python
class MyModelTest(APIViewTestCases.APIViewTestCase):
    model = MyModel
    brief_fields = ['description', 'display', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        # Create 3+ instances for list/bulk tests
        my_models = (
            MyModel(name='My Model 1', ...),
            MyModel(name='My Model 2', ...),
            MyModel(name='My Model 3', ...),
        )
        MyModel.objects.bulk_create(my_models)

        cls.create_data = [
            {'name': 'My Model 4', ...},
            {'name': 'My Model 5', ...},
            {'name': 'My Model 6', ...},
        ]
```

### View Tests

**File:** `netbox/<app>/tests/test_views.py`

```python
class MyModelTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = MyModel

    @classmethod
    def setUpTestData(cls):
        my_models = (
            MyModel(name='My Model 1', ...),
            MyModel(name='My Model 2', ...),
            MyModel(name='My Model 3', ...),
        )
        MyModel.objects.bulk_create(my_models)

        cls.form_data = {
            'name': 'My Model X',
            # all required form fields
        }
        cls.bulk_edit_data = {
            'description': 'New description',
        }
        cls.csv_data = (
            'name',
            'My Model 4',
            'My Model 5',
            'My Model 6',
        )
```

### FilterSet Tests

**File:** `netbox/<app>/tests/test_filtersets.py`

```python
from utilities.testing import ChangeLoggedFilterSetTests

class MyModelFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = MyModel.objects.all()
    filterset = MyModelFilterSet

    @classmethod
    def setUpTestData(cls):
        # Create diverse test data

    def test_name(self):
        params = {'name': ['My Model 1', 'My Model 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_some_fk(self):
        # Test FK and FK_id filters
```

`ChangeLoggedFilterSetTests` provides standard tests for `id`, `created`, `last_updated`, `q` search, etc. Always mix it in.

## Common Gotchas

- **Never write migrations manually.** Always run `python netbox/manage.py makemigrations` and let Django generate them. Set `DEVELOPER = True` in `configuration.py` to enable this.
- **FK filters need explicit `_id` variants** in FilterSets. `Meta.fields` does not auto-generate them.
- **`manage.py` lives in `netbox/`**, not the repo root.
- **Brief fields** in API serializers must be declared explicitly via `brief_fields` on the `Meta` class; they are used for nested representations.
- **GraphQL null prefetch failures**: if tests fail on non-nullable fields, add `select_related=[...]` to the `strawberry_django.field()` call.
- **Template**: by default `generic.ObjectView` auto-resolves to `<app>/<model>.html`. If you only define a panel-driven `layout`, set `template_name = 'generic/object.html'` on the view to opt out of that lookup. Add a real per-model template only when you need markup that panels can't express.
- **Serializer FK fields**: write a single field like `some_fk = RelatedModelSerializer(nested=True, ...)` — do **not** add a separate `some_fk_id` companion. The framework accepts a PK or brief object on write.
- **Modern pattern check**: cargo-culting older nested serializer code (`NestedFooSerializer(read_only=True)` plus `_id` field) is wrong for new code — use the `nested=True` form.
- **`PrimaryModel`** already has `description`, `comments`, `owner`. Don't re-add them.
- **No `ruff format`** on existing files. Use ruff check only.

## References

- Model base classes: `netbox/netbox/models/__init__.py`
- Concrete example (VirtualChassis): `netbox/dcim/models/devices.py`, `netbox/dcim/filtersets.py`, `netbox/dcim/api/`, `netbox/dcim/graphql/`, `netbox/dcim/tests/`
- Contributing guide: `docs/development/adding-models.md`
- Navigation menu: `netbox/netbox/navigation/menu.py`
