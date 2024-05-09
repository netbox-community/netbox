# Forms

## Form Classes

NetBox provides several base form classes for use by plugins.

| Form Class                 | Purpose                              |
|----------------------------|--------------------------------------|
| `NetBoxModelForm`          | Create/edit individual objects       |
| `NetBoxModelImportForm`    | Bulk import objects from CSV data    |
| `NetBoxModelBulkEditForm`  | Edit multiple objects simultaneously |
| `NetBoxModelFilterSetForm` | Filter objects within a list view   |

### `NetBoxModelForm`

This is the base form for creating and editing NetBox models. It extends Django's ModelForm to add support for tags and custom fields.

| Attribute   | Description                                                                           |
|-------------|---------------------------------------------------------------------------------------|
| `fieldsets` | A tuple of `FieldSet` instances which control how form fields are rendered (optional) |

**Example**

```python
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from .models import MyModel

class MyModelForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all()
    )
    comments = CommentField()
    fieldsets = (
        FieldSet('name', 'status', 'site', 'tags', name=_('Model Stuff')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = MyModel
        fields = ('name', 'status', 'site', 'comments', 'tags')
```

!!! tip "Comment fields"
    If your form has a `comments` field, there's no need to list it; this will always appear last on the page.

### `NetBoxModelImportForm`

This form facilitates the bulk import of new objects from CSV, JSON, or YAML data. As with model forms, you'll need to declare a `Meta` subclass specifying the associated `model` and `fields`. NetBox also provides several form fields suitable for import various types of CSV data, listed below.

**Example**

```python
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelImportForm
from utilities.forms import CSVModelChoiceField
from .models import MyModel


class MyModelImportForm(NetBoxModelImportForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text=_('Assigned site')
    )

    class Meta:
        model = MyModel
        fields = ('name', 'status', 'site', 'comments')
```

### `NetBoxModelBulkEditForm`

This form facilitates editing multiple objects in bulk. Unlike a model form, this form does not have a child `Meta` class, and must explicitly define each field. All fields in a bulk edit form are generally declared with `required=False`.

| Attribute         | Description                                                                                 |
|-------------------|---------------------------------------------------------------------------------------------|
| `model`           | The model of object being edited                                                            |
| `fieldsets`       | A tuple of `FieldSet` instances which control how form fields are rendered (optional)       |
| `nullable_fields` | A tuple of fields which can be nullified (set to empty) using the bulk edit form (optional) |

**Example**

```python
from django import forms
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelImportForm
from utilities.forms import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from .models import MyModel, MyModelStatusChoices


class MyModelEditForm(NetBoxModelImportForm):
    name = forms.CharField(
        required=False
    )
    status = forms.ChoiceField(
        choices=MyModelStatusChoices,
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    comments = CommentField()

    model = MyModel
    fieldsets = (
        FieldSet('name', 'status', 'site', name=_('Model Stuff')),
    )
    nullable_fields = ('site', 'comments')
```

### `NetBoxModelFilterSetForm`

This form class is used to render a form expressly for filtering a list of objects. Its fields should correspond to filters defined on the model's filter set.

| Attribute   | Description                                                                           |
|-------------|---------------------------------------------------------------------------------------|
| `model`     | The model of object being edited                                                      |
| `fieldsets` | A tuple of `FieldSet` instances which control how form fields are rendered (optional) |

**Example**

```python
from dcim.models import Site
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import DynamicModelMultipleChoiceField, MultipleChoiceField
from .models import MyModel, MyModelStatusChoices

class MyModelFilterForm(NetBoxModelFilterSetForm):
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    status = MultipleChoiceField(
        choices=MyModelStatusChoices,
        required=False
    )

    model = MyModel
```

## General Purpose Fields

In addition to the [form fields provided by Django](https://docs.djangoproject.com/en/stable/ref/forms/fields/), NetBox provides several field classes for use within forms to handle specific types of data. These can be imported from `utilities.forms.fields` and are documented below.

::: utilities.forms.fields.ColorField
    options:
      members: false

::: utilities.forms.fields.CommentField
    options:
      members: false

::: utilities.forms.fields.JSONField
    options:
      members: false

::: utilities.forms.fields.MACAddressField
    options:
      members: false

::: utilities.forms.fields.SlugField
    options:
      members: false

## Dynamic Object Fields

::: utilities.forms.fields.DynamicModelChoiceField
    options:
      members: false

::: utilities.forms.fields.DynamicModelMultipleChoiceField
    options:
      members: false

## Content Type Fields

::: utilities.forms.fields.ContentTypeChoiceField
    options:
      members: false

::: utilities.forms.fields.ContentTypeMultipleChoiceField
    options:
      members: false

## CSV Import Fields

::: utilities.forms.fields.CSVChoiceField
    options:
      members: false

::: utilities.forms.fields.CSVMultipleChoiceField
    options:
      members: false

::: utilities.forms.fields.CSVModelChoiceField
    options:
      members: false

::: utilities.forms.fields.CSVContentTypeField
    options:
      members: false

::: utilities.forms.fields.CSVMultipleContentTypeField
    options:
      members: false

## Form Rendering

::: utilities.forms.rendering.FieldSet

::: utilities.forms.rendering.InlineFields

::: utilities.forms.rendering.TabbedGroups

::: utilities.forms.rendering.ObjectAttribute
