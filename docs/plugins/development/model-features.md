# Model Features

## Enabling NetBox Features

Plugin models can leverage certain NetBox features by inheriting from NetBox's `BaseModel` class. This class extends the plugin model to enable numerous feature, including:

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
from netbox.models import BaseModel

class MyModel(BaseModel):
    foo = models.CharField()
    ...
```

## Enabling Features Individually

If you prefer instead to enable only a subset of these features for a plugin model, NetBox provides a discrete "mix-in" class for each feature. You can subclass each of these individually when defining your model. (You will also need to inherit from Django's built-in `Model` class.)

```python
# models.py
from django.db.models import models
from netbox.models.features import ExportTemplatesMixin, TagsMixin

class MyModel(ExportTemplatesMixin, TagsMixin, models.Model):
    foo = models.CharField()
    ...
```

The example above will enable export templates and tags, but no other NetBox features. A complete list of available feature mixins is included below. (Inheriting all the available mixins is essentially the same as subclassing `BaseModel`.)

## Feature Mixins Reference

!!! note
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `features` module, they are not yet supported for use by plugins.

::: netbox.models.features.CustomLinksMixin

::: netbox.models.features.CustomFieldsMixin

::: netbox.models.features.CustomValidationMixin

::: netbox.models.features.ExportTemplatesMixin

::: netbox.models.features.JournalingMixin

::: netbox.models.features.TagsMixin

::: netbox.models.features.WebhooksMixin
