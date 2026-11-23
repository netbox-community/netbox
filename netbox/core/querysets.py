from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.utils import ProgrammingError

from netbox.registry import registry
from utilities.querysets import RestrictedQuerySet

from .choices import JobAccessChoices

__all__ = (
    'JobQuerySet',
    'ObjectChangeQuerySet',
)


class JobQuerySet(RestrictedQuerySet):

    def restrict(self, user, action='view'):
        """
        Additionally limit the jobs returned to those permitted by each job's access class (see JobAccessChoices).
        """
        queryset = super().restrict(user, action)

        # Superusers can access all jobs, and there's nothing left to filter if the user has no permission
        if (user and user.is_active and user.is_superuser) or queryset.query.is_empty():
            return queryset

        access = Q(access=JobAccessChoices.ACCESS_SHARED)
        if user is not None and user.is_authenticated:
            access |= Q(access=JobAccessChoices.ACCESS_REQUESTER, user=user)

        # Object jobs are limited to those whose assigned object the user can view. A job assigned to a model which
        # is no longer installed (e.g. that of a removed plugin) can't be evaluated, and is excluded.
        supports_jobs = registry['model_features']['jobs']
        for model in apps.get_models():
            if not supports_jobs(model):
                continue
            objects = model._default_manager.all()
            if not hasattr(objects, 'restrict'):
                continue
            objects = objects.restrict(user, 'view')
            if objects.query.is_empty():
                continue
            access |= Q(
                access=JobAccessChoices.ACCESS_OBJECT,
                object_type=ContentType.objects.get_for_model(model, for_concrete_model=False),
                object_id__in=objects.values('pk'),
            )

        return queryset.filter(access)


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
