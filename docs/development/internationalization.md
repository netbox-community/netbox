# Internationalization

Beginning with NetBox v4.0, NetBox will leverage [Django's automatic translation](https://docs.djangoproject.com/en/stable/topics/i18n/translation/) to support languages other than English. This page details the areas of the project which require special attention to ensure functioning translation support. Briefly, these include:

* The `verbose_name` and `verbose_name_plural` Meta attributes for each model
* The `verbose_name` and (if defined) `help_text` for each model field
* The `label` for each form field
* Headers for `fieldsets` on each form class
* The `verbose_name` for each table column
* All human-readable strings within templates must be wrapped with `{% trans %}` or `{% blocktrans %}`

The rest of this document elaborates on each of the items above.

## General Guidance

* Wrap human-readable strings with Django's `gettext()` or `gettext_lazy()` utility functions to enable automatic translation. Generally, `gettext_lazy()` is preferred (and sometimes required) to defer translation until the string is displayed.

* By convention, the preferred translation function is typically imported as an underscore (`_`) to minimize boilerplate code. Thus, you will often see translation as e.g. `_("Some text")`. It is still an option to import and use alternative translation functions (e.g. `pgettext()` and `ngettext()`) normally as needed.

* Avoid passing markup and other non-natural language where possible. Everything wrapped by a translation function gets exported to a messages file for translation by a human.

* Where the intended meaning of the translated string may not be obvious, use `pgettext()` or `pgettext_lazy()` to include assisting context for the translator. For example:

    ```python
    # Context, string
    pgettext("month name", "May")
    ```

* **Format strings do not support translation.** Avoid "f" strings for messages that must support translation. Instead, use `format()` to accomplish variable replacement:

    ```python
    # Translation will not work
    f"There are {count} objects"
    
    # Do this instead
    "There are {count} objects".format(count=count)
    ```

## Models

1. Import `gettext_lazy` as `_`.
2. Ensure both `verbose_name` and `verbose_name_plural` are defined under the model's `Meta` class and wrapped with the `gettext_lazy()` shortcut.
3. Ensure each model field specifies a `verbose_name` wrapped with `gettext_lazy()`.
4. Ensure any `help_text` attributes on model fields are also wrapped with `gettext_lazy()`.

```python
from django.utils.translation import gettext_lazy as _

class Circuit(PrimaryModel):
    commit_rate = models.PositiveIntegerField(
        ...
        verbose_name=_('commit rate (Kbps)'),
        help_text=_("Committed rate")
    )

    class Meta:
        verbose_name = _('circuit')
        verbose_name_plural = _('circuits')
```

## Forms

1. Import `gettext_lazy` as `_`.
2. All form fields must specify a `label` wrapped with `gettext_lazy()`.
3. The name of each FieldSet on a form must be wrapped with `gettext_lazy()`.

```python
from django.utils.translation import gettext_lazy as _
from utilities.forms.rendering import FieldSet

class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        ...
    )

    fieldsets = (
        FieldSet('provider', 'type', 'status', 'description', name=_('Circuit')),
    )
```

## Tables

1. Import `gettext_lazy` as `_`.
2. All table columns must specify a `verbose_name` wrapped with `gettext_lazy()`.

```python
from django.utils.translation import gettext_lazy as _

class CircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    provider = tables.Column(
        verbose_name=_('Provider'),
        ...
    )
```

## Templates

1. Ensure translation support is enabled by including `{% load i18n %}` at the top of the template.
2. Use the [`{% trans %}`](https://docs.djangoproject.com/en/stable/topics/i18n/translation/#translate-template-tag) tag (short for "translate") to wrap short strings.
3. Longer strings may be enclosed between [`{% blocktrans %}`](https://docs.djangoproject.com/en/stable/topics/i18n/translation/#blocktranslate-template-tag) and `{% endblocktrans %}` tags to improve readability and to enable variable replacement. (Remember to include the `trimmed` argument to trim whitespace between the tags.)
4. Avoid passing HTML within translated strings where possible, as this can complicate the work needed of human translators to develop message maps.

```
{% load i18n %}

{# A short string #}
<h5 class="card-header">{% trans "Circuit List" %}</h5>

{# A longer string with a context variable #}
{% blocktrans trimmed with count=object.circuits.count %}
  There are {count} circuits. Would you like to continue?
{% endblocktrans %}
```

!!! warning
    The `{% blocktrans %}` tag supports only **limited variable replacement**, comparable to the `format()` method on Python strings. It does not permit access to object attributes or the use of other template tags or filters inside it. Ensure that any necessary context is passed as simple variables.

!!! info
    The `{% trans %}` and `{% blocktrans %}` support the inclusion of contextual hints for translators using the `context` argument:

    ```nohighlight
    {% trans "May" context "month name" %}
    ```
