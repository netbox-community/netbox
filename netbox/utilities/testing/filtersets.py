from datetime import UTC, datetime
from itertools import chain

import django_filters
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey, ManyToManyField, ManyToManyRel, ManyToOneRel, OneToOneRel
from django.db.models.constants import LOOKUP_SEP
from django.utils.module_loading import import_string
from taggit.managers import TaggableManager

from extras.filters import TagFilter
from netbox.models.ltree import LtreeModel
from utilities.filters import MultiValueContentTypeFilter, TreeNodeMultipleChoiceFilter

__all__ = (
    'BaseFilterSetTestMixin',
    'ChangeLoggedFilterSetTestMixin',
)

EXEMPT_MODEL_FIELDS = (
    'comments',
    'custom_field_data',
    'path',      # ltree, trigger-maintained
    'sort_path',  # ltree, trigger-maintained
)


def get_filter_target(model, field_name):
    """
    Return a (model, field) tuple for a filter's field_name, or (None, None) if it cannot be resolved (e.g. an
    annotation or GFK). A path ending in a relation (e.g. site) targets the related model; a path ending in a scalar
    field (e.g. site__slug) targets the model which owns that field. In either case, field is the final field in the
    path.
    """
    field = None
    for part in field_name.split(LOOKUP_SEP):
        if part == 'pk':
            return model, model._meta.pk
        try:
            field = model._meta.get_field(part)
        except FieldDoesNotExist:
            return None, None
        if not field.is_relation:
            return model, field
        if field.related_model is None:
            return None, None
        model = field.related_model
    return model, field


class BaseFilterSetTestMixin:
    queryset = None
    filterset = None
    ignore_fields = tuple()
    filter_name_map = {}

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

        filter_name_map provides a mechanism for developers to provide an actual field name for the
        filter that is being resolved, given the field's actual name.
        """
        # If an alias is not present in filter_name_map, then use field.name
        filter_name = self.filter_name_map.get(field.name, field.name)

        # ForeignKey & OneToOneField
        if issubclass(field.__class__, ForeignKey) or type(field) is OneToOneRel:

            # Relationships to ContentType (used as part of a GFK) do not need a filter
            if field.related_model is ContentType:
                return [(None, None)]

            # ForeignKey to an ltree-backed hierarchical model
            if issubclass(field.related_model, LtreeModel) and field.model is not field.related_model:
                return [(f'{filter_name}_id', TreeNodeMultipleChoiceFilter)]

            return [(f'{filter_name}_id', django_filters.ModelMultipleChoiceFilter)]

        # Many-to-many relationships (forward & backward)
        if type(field) in (ManyToManyField, ManyToManyRel):
            filter_name = self.get_m2m_filter_name(field)
            filter_name = self.filter_name_map.get(filter_name, filter_name)

            # ManyToManyFields to ContentType need two filters: 'app.model' & PK
            if field.related_model is ContentType:
                # Standardize on object_type for filter name even though it's technically a ContentType
                filter_name = 'object_type'
                return [
                    (filter_name, MultiValueContentTypeFilter),
                    (f'{filter_name}_id', django_filters.ModelMultipleChoiceFilter),
                ]

            return [(f'{filter_name}_id', django_filters.ModelMultipleChoiceFilter)]

        # Tag manager
        if isinstance(field, TaggableManager):
            return [('tag', TagFilter)]

        # Unable to determine the correct filter class
        return [(filter_name, None)]

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
                    self.assertIsInstance(
                        filter,
                        filter_class,
                        f"Invalid filter class {type(filter)} for {filter_name} (should be {filter_class})!"
                    )

    def test_model_choice_filters(self):
        """
        Check that each model choice filter's queryset and to_field_name are consistent with its field_name.
        """
        model = self.filterset.Meta.model

        for filter_name, filter in self.filterset.base_filters.items():
            if not isinstance(filter, (django_filters.ModelChoiceFilter, django_filters.ModelMultipleChoiceFilter)):
                continue
            queryset = filter.extra.get('queryset')
            if queryset is None or callable(queryset):
                continue
            queryset_model = queryset.model

            with self.subTest(filter=filter_name):
                to_field_name = filter.extra.get('to_field_name')
                if to_field_name and to_field_name != 'pk':
                    try:
                        queryset_model._meta.get_field(to_field_name)
                    except FieldDoesNotExist:
                        self.fail(
                            f"Invalid to_field_name '{to_field_name}' for {filter_name} "
                            f"({queryset_model.__name__} has no such field)!"
                        )

                # Filters with a custom method may use any queryset
                if filter.method is not None:
                    continue
                target_model, target_field = get_filter_target(model, filter.field_name)
                if target_model is None:
                    continue
                self.assertTrue(
                    issubclass(queryset_model, target_model) or
                    queryset_model._meta.concrete_model is target_model._meta.concrete_model,
                    f"Invalid queryset model {queryset_model.__name__} for {filter_name} "
                    f"(field_name '{filter.field_name}' targets {target_model.__name__})!"
                )

                if target_field.is_relation:
                    # Tree filters match descendants by queryset rather than by to_field_name value
                    if isinstance(filter, TreeNodeMultipleChoiceFilter) or type(target_field) is GenericRelation:
                        continue
                    # Only multiple-choice filters with an explicit to_field_name pass that attribute's value to the
                    # lookup; single-choice filters and those without to_field_name pass the model instance itself
                    if not isinstance(filter, django_filters.ModelMultipleChoiceFilter) or to_field_name is None:
                        continue
                    # A field_name ending in a relation is matched against the relation's target field
                    expected_field = target_field.target_field
                    msg = f"to_field_name for {filter_name} must match the target field of '{filter.field_name}'!"
                else:
                    # A field_name ending in a scalar field is matched against the to_field_name value
                    self.assertIsInstance(
                        filter,
                        django_filters.ModelMultipleChoiceFilter,
                        f"ModelChoiceFilter {filter_name} cannot use a scalar field_name '{filter.field_name}'!"
                    )
                    expected_field = target_field
                    msg = f"to_field_name for {filter_name} must match field_name '{filter.field_name}'!"

                # to_field_name defaults to 'pk', which may also be given explicitly (or by its actual name)
                if to_field_name in (None, 'pk'):
                    self.assertTrue(expected_field.primary_key, msg)
                else:
                    self.assertEqual(to_field_name, expected_field.name, msg)


class ChangeLoggedFilterSetTestMixin(BaseFilterSetTestMixin):

    def test_created(self):
        pk_list = self.queryset.values_list('pk', flat=True)[:2]
        self.queryset.filter(pk__in=pk_list).update(created=datetime(2021, 1, 1, 0, 0, 0, tzinfo=UTC))
        params = {'created': ['2021-01-01T00:00:00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_last_updated(self):
        pk_list = self.queryset.values_list('pk', flat=True)[:2]
        self.queryset.filter(pk__in=pk_list).update(last_updated=datetime(2021, 1, 2, 0, 0, 0, tzinfo=UTC))
        params = {'last_updated': ['2021-01-02T00:00:00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
