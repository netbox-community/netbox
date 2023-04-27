# Templates

Templates are used to render HTML content generated from a set of context data. NetBox provides a set of built-in templates suitable for use in plugin views. Plugin authors can extend these templates to minimize the work needed to create custom templates while ensuring that the content they produce matches NetBox's layout and style. These templates are all written in the [Django Template Language (DTL)](https://docs.djangoproject.com/en/stable/ref/templates/language/).

## Template File Structure

Plugin templates should live in the `templates/<plugin-name>/` path within the plugin root. For example if your plugin's name is `my_plugin` and you create a template named `foo.html`, it should be saved to `templates/my_plugin/foo.html`. (You can of course use subdirectories below this point as well.) This ensures that Django's template engine can locate the template for rendering.

## Standard Blocks

The following template blocks are available on all templates.

| Name           | Required | Description                                                         |
|----------------|----------|---------------------------------------------------------------------|
| `title`        | Yes      | Page title                                                          |
| `content`      | Yes      | Page content                                                        |
| `head`         | -        | Content to include in the HTML `<head>` element                     |
| `footer`       | -        | Page footer content                                                 |
| `footer_links` | -        | Links section of the page footer                                    |
| `javascript`   | -        | Javascript content included at the end of the HTML `<body>` element |

!!! note
    For more information on how template blocks work, consult the [Django documentation](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#block).

## Base Templates

### layout.html

Path: `base/layout.html`

NetBox provides a base template to ensure a consistent user experience, which plugins can extend with their own content. This is a general-purpose template that can be used when none of the function-specific templates below are suitable.

#### Blocks

| Name      | Required | Description                |
|-----------|----------|----------------------------|
| `header`  | -        | Page header                |
| `tabs`    | -        | Horizontal navigation tabs |
| `modals`  | -        | Bootstrap 5 modal elements |

#### Example

An example of a plugin template which extends `layout.html` is included below.

```jinja2
{% extends 'base/layout.html' %}

{% block header %}
  <h1>My Custom Header</h1>
{% endblock header %}

{% block content %}
  <p>{{ some_plugin_context_var }}</p>
{% endblock content %}
```

The first line of the template instructs Django to extend the NetBox base template, and the `block` sections inject our custom content within its `header` and `content` blocks.

!!! note
    Django renders templates with its own custom [template language](https://docs.djangoproject.com/en/stable/topics/templates/#the-django-template-language). This is very similar to Jinja2, however there are some important distinctions of which authors should be aware. Be sure to familiarize yourself with Django's template language before attempting to create new templates.

## Generic View Templates

### object.html

Path: `generic/object.html`

This template is used by the `ObjectView` generic view to display a single object.

#### Blocks

| Name                | Required | Description                                  |
|---------------------|----------|----------------------------------------------|
| `breadcrumbs`       | -        | Breadcrumb list items (HTML `<li>` elements) |
| `object_identifier` | -        | A unique identifier (string) for the object  |
| `extra_controls`    | -        | Additional action buttons to display         |

#### Context

| Name     | Required | Description                      |
|----------|----------|----------------------------------|
| `object` | Yes      | The object instance being viewed |

### object_edit.html

Path: `generic/object_edit.html`

This template is used by the `ObjectEditView` generic view to create or modify a single object.

#### Blocks

| Name             | Required | Description                                           |
|------------------|----------|-------------------------------------------------------|
| `form`           | -        | Custom form content (within the HTML `<form>` element |
| `buttons`        | -        | Form submission buttons                               |

#### Context

| Name         | Required | Description                                                     |
|--------------|----------|-----------------------------------------------------------------|
| `object`     | Yes      | The object instance being modified (or none, if creating)       |
| `form`       | Yes      | The form class for creating/modifying the object                |
| `return_url` | Yes      | The URL to which the user is redirect after submitting the form |

### object_delete.html

Path: `generic/object_delete.html`

This template is used by the `ObjectDeleteView` generic view to delete a single object.

#### Blocks

None

#### Context

| Name         | Required | Description                                                     |
|--------------|----------|-----------------------------------------------------------------|
| `object`     | Yes      | The object instance being deleted                               |
| `form`       | Yes      | The form class for confirming the object's deletion             |
| `return_url` | Yes      | The URL to which the user is redirect after submitting the form |

### object_list.html

Path: `generic/object_list.html`

This template is used by the `ObjectListView` generic view to display a filterable list of multiple objects.

#### Blocks

| Name             | Required | Description                                                        |
|------------------|----------|--------------------------------------------------------------------|
| `extra_controls` | -        | Additional action buttons                                          |
| `bulk_buttons`   | -        | Additional bulk action buttons to display beneath the objects list |

#### Context

| Name          | Required | Description                                                                                 |
|---------------|----------|---------------------------------------------------------------------------------------------|
| `model`       | Yes      | The object class                                                                            |
| `table`       | Yes      | The table class used for rendering the list of objects                                      |
| `permissions` | Yes      | A mapping of add, change, and delete permissions for the current user                       |
| `actions`     | Yes      | A list of buttons to display (`add`, `import`, `export`, `bulk_edit`, and/or `bulk_delete`) |
| `filter_form` | -        | The bound filterset form for filtering the objects list                                     |
| `return_url`  | -        | The return URL to pass when submitting a bulk operation form                                |

### bulk_import.html

Path: `generic/bulk_import.html`

This template is used by the `BulkImportView` generic view to import multiple objects at once from CSV data.

#### Blocks

None

#### Context

| Name         | Required | Description                                                  |
|--------------|----------|--------------------------------------------------------------|
| `model`      | Yes      | The object class                                             |
| `form`       | Yes      | The CSV import form class                                    |
| `return_url` | -        | The return URL to pass when submitting a bulk operation form |
| `fields`     | -        | A dictionary of form fields, to display import options       |

### bulk_edit.html

Path: `generic/bulk_edit.html`

This template is used by the `BulkEditView` generic view to modify multiple objects simultaneously.

#### Blocks

None

#### Context

| Name         | Required | Description                                                     |
|--------------|----------|-----------------------------------------------------------------|
| `model`      | Yes      | The object class                                                |
| `form`       | Yes      | The bulk edit form class                                        |
| `table`      | Yes      | The table class used for rendering the list of objects          |
| `return_url` | Yes      | The URL to which the user is redirect after submitting the form |

### bulk_delete.html

Path: `generic/bulk_delete.html`

This template is used by the `BulkDeleteView` generic view to delete multiple objects simultaneously.

#### Blocks

| Name            | Required | Description                           |
|-----------------|----------|---------------------------------------|
| `message_extra` | -        | Supplementary warning message content |

#### Context

| Name         | Required | Description                                                     |
|--------------|----------|-----------------------------------------------------------------|
| `model`      | Yes      | The object class                                                |
| `form`       | Yes      | The bulk delete form class                                      |
| `table`      | Yes      | The table class used for rendering the list of objects          |
| `return_url` | Yes      | The URL to which the user is redirect after submitting the form |

## Tags

The following custom template tags are available in NetBox.

!!! info
    These are loaded automatically by the template backend: You do _not_ need to include a `{% load %}` tag in your template to activate them.

::: utilities.templatetags.builtins.tags.badge

::: utilities.templatetags.builtins.tags.checkmark

::: utilities.templatetags.builtins.tags.customfield_value

::: utilities.templatetags.builtins.tags.tag

## Filters

The following custom template filters are available in NetBox.

!!! info
    These are loaded automatically by the template backend: You do _not_ need to include a `{% load %}` tag in your template to activate them.

::: utilities.templatetags.builtins.filters.bettertitle

::: utilities.templatetags.builtins.filters.content_type

::: utilities.templatetags.builtins.filters.content_type_id

::: utilities.templatetags.builtins.filters.linkify

::: utilities.templatetags.builtins.filters.meta

::: utilities.templatetags.builtins.filters.placeholder

::: utilities.templatetags.builtins.filters.render_json

::: utilities.templatetags.builtins.filters.render_markdown

::: utilities.templatetags.builtins.filters.render_yaml

::: utilities.templatetags.builtins.filters.split

::: utilities.templatetags.builtins.filters.tzoffset
