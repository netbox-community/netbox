# Database Models

## Creating Models

If your plugin introduces a new type of object in NetBox, you'll probably want to create a [Django model](https://docs.djangoproject.com/en/stable/topics/db/models/) for it. A model is essentially a Python representation of a database table, with attributes that represent individual columns. Model instances can be created, manipulated, and deleted using [queries](https://docs.djangoproject.com/en/stable/topics/db/queries/). Models must be defined within a file named `models.py`.

Below is an example `models.py` file containing a model with two character fields:

```python
from django.db import models

class Animal(models.Model):
    name = models.CharField(max_length=50)
    sound = models.CharField(max_length=50)

    def __str__(self):
        return self.name
```

### Migrations

Once you have defined the model(s) for your plugin, you'll need to create the database schema migrations. A migration file is essentially a set of instructions for manipulating the PostgreSQL database to support your new model, or to alter existing models. Creating migrations can usually be done automatically using Django's `makemigrations` management command.

!!! note
    A plugin must be installed before it can be used with Django management commands. If you skipped this step above, run `python setup.py develop` from the plugin's root directory.

```no-highlight
$ ./manage.py makemigrations netbox_animal_sounds 
Migrations for 'netbox_animal_sounds':
  /home/jstretch/animal_sounds/netbox_animal_sounds/migrations/0001_initial.py
    - Create model Animal
```

Next, we can apply the migration to the database with the `migrate` command:

```no-highlight
$ ./manage.py migrate netbox_animal_sounds
Operations to perform:
  Apply all migrations: netbox_animal_sounds
Running migrations:
  Applying netbox_animal_sounds.0001_initial... OK
```

For more background on schema migrations, see the [Django documentation](https://docs.djangoproject.com/en/stable/topics/migrations/).

## Enabling NetBox Features

Plugin models can leverage certain NetBox features by inheriting from NetBox's `BaseModel` class. This class extends the plugin model to enable numerous feature, including:

* Change logging
* Custom fields
* Custom links
* Custom validation
* Export templates
* Journaling
* Tags
* Webhooks

This class performs two crucial functions:

1. Apply any fields, methods, or attributes necessary to the operation of these features
2. Register the model with NetBox as utilizing these feature

Simply subclass BaseModel when defining a model in your plugin:

```python
# models.py
from django.db import models
from netbox.models import NetBoxModel

class MyModel(NetBoxModel):
    foo = models.CharField()
    ...
```

### Enabling Features Individually

If you prefer instead to enable only a subset of these features for a plugin model, NetBox provides a discrete "mix-in" class for each feature. You can subclass each of these individually when defining your model. (You will also need to inherit from Django's built-in `Model` class.)

```python
# models.py
from django.db import models
from netbox.models.features import ExportTemplatesMixin, TagsMixin

class MyModel(ExportTemplatesMixin, TagsMixin, models.Model):
    foo = models.CharField()
    ...
```

The example above will enable export templates and tags, but no other NetBox features. A complete list of available feature mixins is included below. (Inheriting all the available mixins is essentially the same as subclassing `BaseModel`.)

## Feature Mixins Reference

!!! note
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `features` module, they are not yet supported for use by plugins.

::: netbox.models.features.ChangeLoggingMixin

::: netbox.models.features.CustomLinksMixin

::: netbox.models.features.CustomFieldsMixin

::: netbox.models.features.CustomValidationMixin

::: netbox.models.features.ExportTemplatesMixin

::: netbox.models.features.JournalingMixin

::: netbox.models.features.TagsMixin

::: netbox.models.features.WebhooksMixin
