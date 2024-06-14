import django_filters
from datetime import datetime, timezone
from itertools import chain
from mptt.models import MPTTModel

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey, ManyToManyField, ManyToManyRel, ManyToOneRel, OneToOneRel
from django.utils.module_loading import import_string
from taggit.managers import TaggableManager

from extras.filters import TagFilter
from utilities.filters import ContentTypeFilter, TreeNodeMultipleChoiceFilter

from core.models import ObjectType

__all__ = (
    'BaseFilterSetTests',
    'ChangeLoggedFilterSetTests',
)

EXEMPT_MODEL_FIELDS = (
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

    def get_m2m_filter_name(self, field):
        """
        Given a ManyToManyField, determine the correct name for its corresponding Filter. Individual test
        cases may override this method to prescribe deviations for specific fields.
        """
        related_model_name = field.related_model._meta.verbose_name
        return related_model_name.lower().replace(' ', '_')

    def get_filters_for_model_field(self, field):
        """
        Given a model field, return an iterable of (name, class) for each filter that should be defined on
        the model's FilterSet class. If the appropriate filter class cannot be determined, it will be None.
        """
        # ForeignKey & OneToOneField
        if issubclass(field.__class__, ForeignKey) or type(field) is OneToOneRel:

            # Relationships to ContentType (used as part of a GFK) do not need a filter
            if field.related_model is ContentType:
                return [(None, None)]

            # ForeignKeys to ObjectType need two filters: 'app.model' & PK
            if field.related_model is ObjectType:
                return [
                    (field.name, ContentTypeFilter),
                    (f'{field.name}_id', django_filters.ModelMultipleChoiceFilter),
                ]

            # ForeignKey to an MPTT-enabled model
            if issubclass(field.related_model, MPTTModel) and field.model is not field.related_model:
                return [(f'{field.name}_id', TreeNodeMultipleChoiceFilter)]

            return [(f'{field.name}_id', django_filters.ModelMultipleChoiceFilter)]

        # Many-to-many relationships (forward & backward)
        elif type(field) in (ManyToManyField, ManyToManyRel):
            filter_name = self.get_m2m_filter_name(field)

            # ManyToManyFields to ObjectType need two filters: 'app.model' & PK
            if field.related_model is ObjectType:
                return [
                    (filter_name, ContentTypeFilter),
                    (f'{filter_name}_id', django_filters.ModelMultipleChoiceFilter),
                ]

            return [(f'{filter_name}_id', django_filters.ModelMultipleChoiceFilter)]

        # Tag manager
        if type(field) is TaggableManager:
            return [('tag', TagFilter)]

        # Unable to determine the correct filter class
        return [(field.name, None)]

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

        # Import the FilterSet class & sanity check it
        filterset = import_string(f'{app_label}.filtersets.{model_name}FilterSet')
        self.assertEqual(model, filterset.Meta.model, "FilterSet model does not match!")

        filters = filterset.get_filters()

        # Check for missing filters
        for model_field in model._meta.get_fields():

            # Skip private fields
            if model_field.name.startswith('_'):
                continue

            # Skip ignored fields
            if model_field.name in chain(self.ignore_fields, EXEMPT_MODEL_FIELDS):
                continue

            # Skip reverse ForeignKey relationships
            if type(model_field) is ManyToOneRel:
                continue

            # Skip generic relationships
            if type(model_field) in (GenericForeignKey, GenericRelation):
                continue

            for filter_name, filter_class in self.get_filters_for_model_field(model_field):

                if filter_name is None:
                    # Field is exempt
                    continue

                # Check that the filter is defined
                self.assertIn(
                    filter_name,
                    filters.keys(),
                    f'No filter defined for {filter_name} ({model_field.name})!'
                )

                # Check that the filter class is correct
                filter = filters[filter_name]
                if filter_class is not None:
                    self.assertIs(
                        type(filter),
                        filter_class,
                        f"Invalid filter class {type(filter)} for {filter_name} (should be {filter_class})!"
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
