# Database Models

## Creating Models

If your plugin introduces a new type of object in NetBox, you'll probably want to create a [Django model](https://docs.djangoproject.com/en/stable/topics/db/models/) for it. A model is essentially a Python representation of a database table, with attributes that represent individual columns. Instances of a model (objects) can be created, manipulated, and deleted using [queries](https://docs.djangoproject.com/en/stable/topics/db/queries/). Models must be defined within a file named `models.py`.

Below is an example `models.py` file containing a model with two character (text) fields:

```python
from django.db import models

class MyModel(models.Model):
    foo = models.CharField(max_length=50)
    bar = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.foo} {self.bar}'
```

Every model includes by default a numeric primary key. This value is generated automatically by the database, and can be referenced as `pk` or `id`.

!!! note
    Model names should adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/#class-names) standards and be CapWords (no underscores).  Using underscores in model names will result in problems with permissions.

## Enabling NetBox Features

Plugin models can leverage certain NetBox features by inheriting from NetBox's `NetBoxModel` class. This class extends the plugin model to enable features unique to NetBox, including:

* Bookmarks
* Change logging
* Cloning
* Custom fields
* Custom links
* Custom validation
* Export templates
* Journaling
* Tags
* Webhooks

This class performs two crucial functions:

1. Apply any fields, methods, and/or attributes necessary to the operation of these features
2. Register the model with NetBox as utilizing these features

Simply subclass NetBoxModel when defining a model in your plugin:

```python
# models.py
from django.db import models
from netbox.models import NetBoxModel

class MyModel(NetBoxModel):
    foo = models.CharField()
    ...
```

### NetBoxModel Properties

#### `docs_url`

This attribute specifies the URL at which the documentation for this model can be reached. By default, it will return `/static/docs/models/<app_label>/<model_name>/`. Plugin models can override this to return a custom URL. For example, you might direct the user to your plugin's documentation hosted on [ReadTheDocs](https://readthedocs.org/).

#### `_netbox_private`

By default, any model introduced by a plugin will appear in the list of available object types e.g. when creating a custom field or certain dashboard widgets. If your model is intended only for "behind the scenes use" and should not be exposed to end users, set `_netbox_private` to True. This will omit it from the list of general-purpose object types.

### Enabling Features Individually

If you prefer instead to enable only a subset of these features for a plugin model, NetBox provides a discrete "mix-in" class for each feature. You can subclass each of these individually when defining your model. (Your model will also need to inherit from Django's built-in `Model` class.)

For example, if we wanted to support only tags and export templates, we would inherit from NetBox's `ExportTemplatesMixin` and `TagsMixin` classes, and from Django's `Model` class. (Inheriting _all_ the available mixins is essentially the same as subclassing `NetBoxModel`.)

```python
# models.py
from django.db import models
from netbox.models.features import ExportTemplatesMixin, TagsMixin

class MyModel(ExportTemplatesMixin, TagsMixin, models.Model):
    foo = models.CharField()
    ...
```

## Database Migrations

Once you have completed defining the model(s) for your plugin, you'll need to create the database schema migrations. A migration file is essentially a set of instructions for manipulating the PostgreSQL database to support your new model, or to alter existing models. Creating migrations can usually be done automatically using Django's `makemigrations` management command. (Ensure that your plugin has been installed and enabled first, otherwise it won't be found.)

!!! note Enable Developer Mode
    NetBox enforces a safeguard around the `makemigrations` command to protect regular users from inadvertently creating erroneous schema migrations. To enable this command for plugin development, set `DEVELOPER=True` in `configuration.py`.

```no-highlight
$ ./manage.py makemigrations my_plugin 
Migrations for 'my_plugin':
  /home/jstretch/animal_sounds/my_plugin/migrations/0001_initial.py
    - Create model MyModel
```

Next, we can apply the migration to the database with the `migrate` command:

```no-highlight
$ ./manage.py migrate my_plugin
Operations to perform:
  Apply all migrations: my_plugin
Running migrations:
  Applying my_plugin.0001_initial... OK
```

For more information about database migrations, see the [Django documentation](https://docs.djangoproject.com/en/stable/topics/migrations/).

## Feature Mixins Reference

!!! warning
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `features` module, they are not yet supported for use by plugins.

::: netbox.models.features.BookmarksMixin

::: netbox.models.features.ChangeLoggingMixin

::: netbox.models.features.CloningMixin

::: netbox.models.features.CustomLinksMixin

::: netbox.models.features.CustomFieldsMixin

::: netbox.models.features.CustomValidationMixin

::: netbox.models.features.EventRulesMixin

!!! note
    `EventRulesMixin` was renamed from `WebhooksMixin` in NetBox v3.7.

::: netbox.models.features.ExportTemplatesMixin

::: netbox.models.features.JobsMixin

::: netbox.models.features.JournalingMixin

::: netbox.models.features.TagsMixin

## Choice Sets

For model fields which support the selection of one or more values from a predefined list of choices, NetBox provides the `ChoiceSet` utility class. This can be used in place of a regular choices tuple to provide enhanced functionality, namely dynamic configuration and colorization. (See [Django's documentation](https://docs.djangoproject.com/en/stable/ref/models/fields/#choices) on the `choices` parameter for supported model fields.)

To define choices for a model field, subclass `ChoiceSet` and define a tuple named `CHOICES`, of which each member is a two- or three-element tuple. These elements are:

* The database value
* The corresponding human-friendly label
* The assigned color (optional)

A complete example is provided below.

!!! note
    Authors may find it useful to declare each of the database values as constants on the class, and reference them within `CHOICES` members. This convention allows the values to be referenced from outside the class, however it is not strictly required.

### Dynamic Configuration

Some model field choices in NetBox can be configured by an administrator. For example, the default values for the Site model's `status` field can be replaced or supplemented with custom choices. To enable dynamic configuration for a ChoiceSet subclass, define its `key` as a string specifying the model and field name to which it applies. For example:

```python
from utilities.choices import ChoiceSet

class StatusChoices(ChoiceSet):
    key = 'MyModel.status'
```

To extend or replace the default values for this choice set, a NetBox administrator can then reference it under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter. For example, the `status` field on `MyModel` in `my_plugin` would be referenced as:

```python
FIELD_CHOICES = {
    'my_plugin.MyModel.status': (
        # Custom choices
    )
}
```

### Example

```python
# choices.py
from utilities.choices import ChoiceSet

class StatusChoices(ChoiceSet):
    key = 'MyModel.status'

    STATUS_FOO = 'foo'
    STATUS_BAR = 'bar'
    STATUS_BAZ = 'baz'

    CHOICES = [
        (STATUS_FOO, 'Foo', 'red'),
        (STATUS_BAR, 'Bar', 'green'),
        (STATUS_BAZ, 'Baz', 'blue'),
    ]
```

!!! warning
    For dynamic configuration to work properly, `CHOICES` must be a mutable list, rather than a tuple.

```python
# models.py
from django.db import models
from .choices import StatusChoices

class MyModel(models.Model):
    status = models.CharField(
        max_length=50,
        choices=StatusChoices,
        default=StatusChoices.STATUS_FOO
    )
```
