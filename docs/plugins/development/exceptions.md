# Exceptions

The exception classes listed here may be raised by a plugin to alter NetBox's default behavior in various scenarios.

## `AbortRequest`

NetBox provides several [generic views](./views.md) and [REST API viewsets](./rest-api.md) which facilitate the creation, modification, and deletion of objects, either individually or in bulk. Under certain conditions, it may be desirable for a plugin to interrupt these actions and cleanly abort the request, reporting an error message to the end user or API consumer.

For example, a plugin may prohibit the creation of a site with a prohibited name by connecting a receiver to Django's `pre_save` signal for the Site model:

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from dcim.models import Site
from utilities.exceptions import AbortRequest

PROHIBITED_NAMES = ('foo', 'bar', 'baz')

@receiver(pre_save, sender=Site)
def test_abort_request(instance, **kwargs):
    if instance.name.lower() in PROHIBITED_NAMES:
        raise AbortRequest(f"Site name can't be {instance.name}!")
```

An error message must be supplied when raising `AbortRequest`. This will be conveyed to the user and should clearly explain the reason for which the request was aborted, as well as any potential remedy.

!!! tip "Consider custom validation rules"
    This exception is intended to be used for handling complex evaluation logic and should be used sparingly. For simple object validation (such as the contrived example above), consider using [custom validation rules](../../customization/custom-validation.md) instead.
