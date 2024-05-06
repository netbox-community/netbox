import json

from django.db import models

from extras.utils import is_taggable


class CloningUserMixin(models.Model):
    """
    Provides the clone() method used to prepare a copy of existing objects.
    The same code from netbox/users/models/features.py (CloningMixin) is used here.
    It was necessary to avoid circular imports.
    """
    class Meta:
        abstract = True

    def clone(self):
        """
        Returns a dictionary of attributes suitable for creating a copy of the current instance. This is used for pre-
        populating an object creation form in the UI. By default, this method will replicate any fields listed in the
        model's `clone_fields` list (if defined), but it can be overridden to apply custom logic.

        ```python
        class MyModel(NetBoxModel):
            def clone(self):
                attrs = super().clone()
                attrs['extra-value'] = 123
                return attrs
        ```
        """
        attrs = {}

        for field_name in getattr(self, 'clone_fields', []):
            field = self._meta.get_field(field_name)
            field_value = field.value_from_object(self)
            if field_value and isinstance(field, models.ManyToManyField):
                attrs[field_name] = [v.pk for v in field_value]
            elif field_value and isinstance(field, models.JSONField):
                attrs[field_name] = json.dumps(field_value)
            elif field_value not in (None, ''):
                attrs[field_name] = field_value

        # Include tags (if applicable)
        if is_taggable(self):
            attrs['tags'] = [tag.pk for tag in self.tags.all()]

        # Include any cloneable custom fields
        if hasattr(self, 'custom_fields'):
            for field in self.custom_fields:
                if field.is_cloneable:
                    attrs[f'cf_{field.name}'] = self.custom_field_data.get(field.name)

        return attrs
