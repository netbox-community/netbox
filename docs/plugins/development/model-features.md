# Model Features

Plugin models can leverage certain NetBox features by inheriting from designated Python classes (documented below), defined in `netbox.models.features`. These classes perform two crucial functions:

1. Apply any fields, methods, or attributes necessary to the operation of the feature
2. Register the model with NetBox as utilizing the feature

For example, to enable support for tags in a plugin model, it should inherit from `TagsMixin`:

```python
# models.py
from django.db.models import models
from netbox.models.features import TagsMixin

class MyModel(TagsMixin, models.Model):
    foo = models.CharField()
    ...
```

This will ensure that TaggableManager is applied to the model, and that the model is registered with NetBox as taggable.

!!! note
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `features` module, they are not yet supported for use by plugins.

::: netbox.models.features.CustomLinksMixin

::: netbox.models.features.CustomFieldsMixin

::: netbox.models.features.ExportTemplatesMixin

::: netbox.models.features.JobResultsMixin

::: netbox.models.features.JournalingMixin

::: netbox.models.features.TagsMixin

::: netbox.models.features.WebhooksMixin
