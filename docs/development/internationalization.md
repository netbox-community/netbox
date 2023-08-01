# Internationalization

NetBox follows the [Django translation guide](https://docs.djangoproject.com/en/4.2/topics/i18n/translation/) to mark translatable strings.

## General Guidance

* In models, forms and tables wrap strings with gettext_lazy function.
* In templates wrap strings with the **{% trans %}** tag.

!!! f-strings
    Python f-strings are great, but do not work with internationalization.  If a parameterized strings needs to be displayed (for example a help_string) it will need to use .format method instead of f-strings.

## Models

1. Import gettext_lazy.
2. Make sure all model fields have a verbose_name defined.
3. Wrap all verbose_name and help_text fields with the gettext_lazy shortcut.

```
from django.utils.translation import gettext_lazy as _

class Circuit(PrimaryModel):
    commit_rate = models.PositiveIntegerField(
        ...
        verbose_name=_('commit rate (Kbps)'),
        help_text=_("Committed rate")
    )

```
**Note:** The Django docs specifically state for internationalization: "It is recommended to always provide explicit verbose_name and verbose_name_plural options"

## Forms

1. Import gettext_lazy
2. Make sure all form-fields have a lable defined
3. Wrap all lable and fieldsets headers wtih the gettext_lazy shorcut

```
from django.utils.translation import gettext_lazy as _

class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        ...
    )

    fieldsets = (
        (_('Circuit'), ('provider', 'type', 'status', 'description')),
    )

```

## Tables

1. Import gettext_lazy
2. Make sure all table-fields have a verbose_name defined

```
from django.utils.translation import gettext_lazy as _

class CircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    provider = tables.Column(
        verbose_name=_('Provider'),
        ...
    )
```

## Templates

1. Add **{% load i18n %}** at the top of the template files
2. Wrap displayable strings with the **trans** tag

```
{% load i18n %}
    <h5 class="card-header">{% trans "Circuit" %}</h5>
```

!!! note
    These just cover the most standard use cases, please read over the [Django translation guide](https://docs.djangoproject.com/en/4.2/topics/i18n/translation/#standard-translation) for dealing with pluralization, model methods, time display and other specialized cases.
