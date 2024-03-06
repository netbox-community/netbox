from datetime import datetime, timezone
from itertools import chain

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey, ManyToManyField, ManyToManyRel, ManyToOneRel, OneToOneRel
from django.utils.module_loading import import_string
from taggit.managers import TaggableManager

from core.models import ObjectType

__all__ = (
    'BaseFilterSetTests',
    'ChangeLoggedFilterSetTests',
)

IGNORE_MODELS = (
    ('core', 'AutoSyncRecord'),
    ('core', 'ManagedFile'),
    ('core', 'ObjectType'),
    ('dcim', 'CablePath'),
    ('extras', 'Branch'),
    ('extras', 'CachedValue'),
    ('extras', 'Dashboard'),
    ('extras', 'ScriptModule'),
    ('extras', 'StagedChange'),
    ('extras', 'TaggedItem'),
    ('users', 'UserConfig'),
)

IGNORE_FIELDS = (
    'comments',
    'custom_field_data',
    'level',    # MPTT
    'lft',      # MPTT
    'rght',     # MPTT
    'tree_id',  # MPTT
)


class BaseFilterSetTests:
    queryset = None
    filterset = None
    ignore_fields = tuple()

    def test_id(self):
        """
        Test filtering for two PKs from a set of >2 objects.
        """
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertGreater(self.queryset.count(), 2)
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_missing_filters(self):
        """
        Check for any model fields which do not have the required filter(s) defined.
        """
        app_label = self.__class__.__module__.split('.')[0]
        model = self.queryset.model
        model_name = model.__name__

        # Skip ignored models
        if (app_label, model_name) in IGNORE_MODELS:
            return

        # Import the FilterSet class & sanity check it
        filterset = import_string(f'{app_label}.filtersets.{model_name}FilterSet')
        self.assertEqual(model, filterset.Meta.model, "FilterSet model does not match!")

        filterset_fields = sorted(filterset.get_filters())

        # Check for missing filters
        for model_field in model._meta.get_fields():

            # Skip private fields
            if model_field.name.startswith('_'):
                continue

            # Skip ignored fields
            if model_field.name in chain(self.ignore_fields, IGNORE_FIELDS):
                continue

            # One-to-one & one-to-many relationships
            if issubclass(model_field.__class__, ForeignKey) or type(model_field) is OneToOneRel:
                if model_field.related_model is ContentType:
                    # Relationships to ContentType (used as part of a GFK) do not need a filter
                    continue
                elif model_field.related_model is ObjectType:
                    # Filters to ObjectType use 'app.model' rather than numeric PK, so we omit the _id suffix
                    filter_name = model_field.name
                else:
                    filter_name = f'{model_field.name}_id'
                self.assertIn(filter_name, filterset_fields, f'No filter found for {model_field.name}!')

            # TODO: Many-to-one & many-to-many relationships
            elif type(model_field) in (ManyToOneRel, ManyToManyField, ManyToManyRel):
                continue

            # TODO: Generic relationships
            elif type(model_field) in (GenericForeignKey, GenericRelation):
                continue

            # Tags
            elif type(model_field) is TaggableManager:
                self.assertIn('tag', filterset_fields, f'No filter found for {model_field.name}!')

            # All other fields
            else:
                self.assertIn(
                    model_field.name,
                    filterset_fields,
                    f'No filter found for {model_field.name} ({type(model_field)})!'
                )


class ChangeLoggedFilterSetTests(BaseFilterSetTests):

    def test_created(self):
        pk_list = self.queryset.values_list('pk', flat=True)[:2]
        self.queryset.filter(pk__in=pk_list).update(created=datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        params = {'created': ['2021-01-01T00:00:00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_last_updated(self):
        pk_list = self.queryset.values_list('pk', flat=True)[:2]
        self.queryset.filter(pk__in=pk_list).update(last_updated=datetime(2021, 1, 2, 0, 0, 0, tzinfo=timezone.utc))
        params = {'last_updated': ['2021-01-02T00:00:00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
