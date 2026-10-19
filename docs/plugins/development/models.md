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

Every model includes by default a numeric primary key. This value is generated automatically by the database (unless supplied by a [primary key allocator](#primary-key-allocators)), and can be referenced as `pk` or `id`.

!!! note
    Model names should adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/#class-names) standards and be CapWords (no underscores).  Using underscores in model names will result in problems with permissions.

## Enabling NetBox Features

Plugin models can leverage certain [model features](../../development/models.md#features-matrix) (such as tags, custom fields, event rules, etc.) by inheriting from NetBox's `NetBoxModel` class. This class performs two crucial functions:

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

### Additional Models

In addition to the base NetBoxModel class, the following additional classes are provided for convenience.

!!! info "These model classes were added to the plugins API in NetBox v4.5."

#### PrimaryModel

PrimaryModel is the go-to class for most object types. It extends NetBoxModel with `description` and `comments` fields, and it introduces support for ownership assignment.

| Field         | Required | Unique | Description                                 |
|---------------|----------|--------|---------------------------------------------|
| `owner`       | No       | No     | The object's owner                          |
| `description` | No       | No     | A human-friendly description for the object |
| `comments`    | No       | No     | General comments                            |

#### OrganizationalModel

OrganizationalModel is used by object types whose function is primarily the organization of other objects.

| Field         | Required | Unique | Description                                 |
|---------------|----------|--------|---------------------------------------------|
| `name`        | Yes      | Yes    | The name of the object                      |
| `slug`        | Yes      | Yes    | A unique URL-friendly identifier            |
| `owner`       | No       | No     | The object's owner                          |
| `description` | No       | No     | A human-friendly description for the object |

#### NestedGroupModel

NestedGroupModel is used for objects which arrange into a recursive hierarchy (like regions and locations) via its self-referential `parent` foreign key.

| Field         | Required | Unique | Description                                                     |
|---------------|----------|--------|-----------------------------------------------------------------|
| `name`        | Yes      | Yes    | The name of the object                                          |
| `slug`        | Yes      | Yes    | A unique URL-friendly identifier                                |
| `parent`      | No       | No     | The object (of the same type) under which this object is nested |
| `owner`       | No       | No     | The object's owner                                              |
| `description` | No       | No     | A human-friendly description for the object                     |
| `comments`    | No       | No     | General comments                                                |

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

::: netbox.models.features.ContactsMixin

::: netbox.models.features.CustomLinksMixin

::: netbox.models.features.CustomFieldsMixin

::: netbox.models.features.CustomValidationMixin

::: netbox.models.features.EventRulesMixin

::: netbox.models.features.ExportTemplatesMixin

::: netbox.models.features.JobsMixin

::: netbox.models.features.JournalingMixin

::: netbox.models.features.TagsMixin

## Custom Model Features

In addition to utilizing the model features provided natively by NetBox (listed above), plugins can register their own model features. This is done using the `register_model_feature()` function from `netbox.utils`. This function takes two arguments: a feature name, and a callable which accepts a model class. The callable must return a boolean value indicting whether the given model supports the named feature.

This function can be used as a decorator:

```python
@register_model_feature('foo')
def supports_foo(model):
    # Your logic here
```

Or it can be called directly:

```python
register_model_feature('foo', supports_foo)
```

!!! tip
    Consider performing feature registration inside your PluginConfig's `ready()` method.

## Dependent Objects

Some models maintain dependent objects from their `save()` method: saving a cable, for example, traces and records its cable paths. Callers which write objects directly to the database bypass `save()` — replaying serialized changes, restoring deleted objects, or importing data — and those dependent objects are never created.

A model can implement `update_dependent_objects()` to expose that work to such a caller:

```python
# models.py
class MyModel(NetBoxModel):

    def update_dependent_objects(self):
        # Recreate any objects derived from this one
        ...
    update_dependent_objects.alters_data = True
```

The method is optional; callers should check for its presence before calling it. NetBox never calls it during a normal save.

Two constraints apply to an implementation:

* It must derive its work entirely from the database. The in-memory state a normal `save()` relies on (which fields changed, for instance) is not available to a caller replaying serialized data.
* It must be idempotent and safe to call when nothing needs to change, as a caller will generally invoke it for every object it has written.

Exceptions raised by an implementation propagate to the caller unchanged: `Cable.update_dependent_objects()` raises `UnsupportedCablePath` where `Cable.save()` converts it to `AbortRequest`. The hook is not tied to a request, so it is for the caller to decide how a failure is handled.

The caller is responsible for calling the method only once every related object is in place: `Cable.update_dependent_objects()` retraces the cable's paths, which requires its `CableTermination` objects to exist.

## Primary Key Allocators

!!! info "This feature was introduced in NetBox v4.8."

By default, the database assigns each new object's primary key from its table's sequence. A plugin can instead supply primary keys by registering a primary key allocator with the `register_pk_allocator()` decorator from `netbox.utils`. An allocator is a callable which accepts a model class and a count. It returns either a list of exactly that many primary keys for the model, or `None` to defer to the next allocator.

```python
from netbox.utils import register_pk_allocator

@register_pk_allocator
def my_allocator(model, count):
    if not handles_model(model):
        return None
    return reserve_pks(model, count)
```

Allocators are consulted in the order in which they were registered. If no allocator supplies primary keys, the database assigns them as usual.

NetBox consults allocators whenever an object without a primary key is created via the ORM, from both `save()` and `bulk_create()`. A few things to keep in mind when writing an allocator:

* It is called for every model which supports allocation, including core models, other plugins' models, and the auto-created through models of many-to-many relationships. It should return `None` promptly for any model it doesn't handle.
* It is called once for each object, including within `bulk_create()`. An allocator which obtains primary keys from a remote source may wish to fetch them in blocks and hand them out from a local cache.
* It is not told which database the object is being written to; it must decide whether to supply primary keys from its own context.
* Under multi-table inheritance, it receives the parent model, which owns the primary key column.

!!! tip
    Consider registering allocators inside your PluginConfig's `ready()` method.

### Model Support

Allocators apply to models whose primary key is a `NetBoxAutoField`. This is a subclass of Django's `BigAutoField`, and is NetBox's [`DEFAULT_AUTO_FIELD`](https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field), so plugin models which don't declare a primary key use it automatically. A plugin which sets `default_auto_field` on its PluginConfig, or which declares a primary key explicitly, should use `NetBoxAutoField` to support allocators:

```python
# __init__.py
class MyPluginConfig(PluginConfig):
    default_auto_field = 'utilities.fields.NetBoxAutoField'
```

```python
# models.py
from utilities.fields import NetBoxAutoField

class MyModel(NetBoxModel):
    id = NetBoxAutoField(primary_key=True)
```

`NetBoxAutoField` presents itself to migrations as a `BigAutoField`, so switching an existing primary key to it generates no migrations.

!!! note
    Because `NetBoxAutoField` reports a default, saving a new (unsaved) instance whose primary key is set to that of an existing row (e.g. `MyModel(pk=5).save()`) attempts an `INSERT` and fails on the duplicate key, rather than updating the existing row. To update an existing row, fetch the object first, or call `save(force_update=True)`. Raw saves, such as when loading fixtures or deserialized objects, are not affected.

### Inserting Rows Outside the ORM

Code which inserts rows directly, for example using raw SQL or PostgreSQL's `COPY`, bypasses the ORM and with it any registered allocators. Such code should call `allocate_pks()` from `netbox.utils` to obtain primary keys for the new rows, and insert them explicitly. This function returns a list of primary keys from the first allocator which supplies them, or `None` if the database should assign them.

```python
from netbox.utils import allocate_pks

pks = allocate_pks(MyModel, count=len(rows))
if pks is None:
    # Omit the primary key column and let the database assign values
    ...
```

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
