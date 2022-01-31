# Forms

## Form Classes

NetBox provides several base form classes for use by plugins. These are documented below.

* `NetBoxModelForm`
* `NetBoxModelCSVForm`
* `NetBoxModelBulkEditForm`
* `NetBoxModelFilterSetForm`

### TODO: Include forms reference

In addition to the [form fields provided by Django](https://docs.djangoproject.com/en/stable/ref/forms/fields/), NetBox provides several field classes for use within forms to handle specific types of data. These can be imported from `utilities.forms.fields` and are documented below.

## General Purpose Fields

::: utilities.forms.ColorField
    selection:
      members: false

::: utilities.forms.CommentField
    selection:
      members: false

::: utilities.forms.JSONField
    selection:
      members: false

::: utilities.forms.MACAddressField
    selection:
      members: false

::: utilities.forms.SlugField
    selection:
      members: false

## Dynamic Object Fields

::: utilities.forms.DynamicModelChoiceField
    selection:
      members: false

::: utilities.forms.DynamicModelMultipleChoiceField
    selection:
      members: false

## Content Type Fields

::: utilities.forms.ContentTypeChoiceField
    selection:
      members: false

::: utilities.forms.ContentTypeMultipleChoiceField
    selection:
      members: false

## CSV Import Fields

::: utilities.forms.CSVChoiceField
    selection:
      members: false

::: utilities.forms.CSVMultipleChoiceField
    selection:
      members: false

::: utilities.forms.CSVModelChoiceField
    selection:
      members: false

::: utilities.forms.CSVContentTypeField
    selection:
      members: false

::: utilities.forms.CSVMultipleContentTypeField
    selection:
      members: false
