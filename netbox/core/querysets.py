from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.utils import ProgrammingError

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ObjectChangeQuerySet',
)


class ObjectChangeQuerySet(RestrictedQuerySet):

    def valid_models(self):
        # Exclude any change records which refer to an instance of a model that's no longer installed. This
        # can happen when a plugin is removed but its data remains in the database, for example.
        try:
            content_types = ContentType.objects.get_for_models(*apps.get_models()).values()
        except ProgrammingError:
            # Handle the case where the database schema has not yet been initialized
            content_types = ContentType.objects.none()

        content_type_ids = set(
            ct.pk for ct in content_types
        )
        return self.filter(changed_object_type_id__in=content_type_ids)
