import django_filters
from copy import deepcopy
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django_filters.exceptions import FieldLookupError
from django_filters.utils import get_model_field, resolve_field
from django.utils.translation import gettext as _

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from extras.choices import CustomFieldFilterLogicChoices
from extras.filters import TagFilter
from extras.models import CustomField, SavedFilter
from utilities.constants import (
    FILTER_CHAR_BASED_LOOKUP_MAP, FILTER_NEGATION_LOOKUP_MAP, FILTER_TREENODE_NEGATION_LOOKUP_MAP,
    FILTER_NUMERIC_BASED_LOOKUP_MAP
)
from utilities.forms.fields import MACAddressField
from utilities import filters

__all__ = (
    'BaseFilterSet',
    'ChangeLoggedModelFilterSet',
    'NetBoxModelFilterSet',
    'OrganizationalModelFilterSet',
)


#
# FilterSets
#

class BaseFilterSet(django_filters.FilterSet):
    """
    A base FilterSet which provides some enhanced functionality over django-filter2's FilterSet class.
    """
    FILTER_DEFAULTS = deepcopy(django_filters.filterset.FILTER_FOR_DBFIELD_DEFAULTS)
    FILTER_DEFAULTS.update({
        models.AutoField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.CharField: {
            'filter_class': filters.MultiValueCharFilter
        },
        models.DateField: {
            'filter_class': filters.MultiValueDateFilter
        },
        models.DateTimeField: {
            'filter_class': filters.MultiValueDateTimeFilter
        },
        models.DecimalField: {
            'filter_class': filters.MultiValueDecimalFilter
        },
        models.EmailField: {
            'filter_class': filters.MultiValueCharFilter
        },
        models.FloatField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.IntegerField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.PositiveIntegerField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.PositiveSmallIntegerField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.SlugField: {
            'filter_class': filters.MultiValueCharFilter
        },
        models.SmallIntegerField: {
            'filter_class': filters.MultiValueNumberFilter
        },
        models.TimeField: {
            'filter_class': filters.MultiValueTimeFilter
        },
        models.URLField: {
            'filter_class': filters.MultiValueCharFilter
        },
        MACAddressField: {
            'filter_class': filters.MultiValueMACAddressFilter
        },
    })

    def __init__(self, data=None, *args, **kwargs):
        # bit of a hack for #9231 - extras.lookup.Empty is registered in apps.ready
        # however FilterSet Factory is setup before this which creates the
        # initial filters.  This recreates the filters so Empty is picked up correctly.
        self.base_filters = self.__class__.get_filters()

        # Apply any referenced SavedFilters
        if data and ('filter' in data or 'filter_id' in data):
            data = data.copy()  # Get a mutable copy
            saved_filters = SavedFilter.objects.filter(
                Q(slug__in=data.pop('filter', [])) |
                Q(pk__in=data.pop('filter_id', []))
            )
            for sf in saved_filters:
                for key, value in sf.parameters.items():
                    # QueryDicts are... fun
                    if type(value) not in (list, tuple):
                        value = [value]
                    if key in data:
                        for v in value:
                            data.appendlist(key, v)
                    else:
                        data.setlist(key, value)

        super().__init__(data, *args, **kwargs)

    @staticmethod
    def _get_filter_lookup_dict(existing_filter):
        # Choose the lookup expression map based on the filter type
        if isinstance(existing_filter, (
            django_filters.NumberFilter,
            filters.MultiValueDateFilter,
            filters.MultiValueDateTimeFilter,
            filters.MultiValueNumberFilter,
            filters.MultiValueDecimalFilter,
            filters.MultiValueTimeFilter
        )):
            return FILTER_NUMERIC_BASED_LOOKUP_MAP

        elif isinstance(existing_filter, (
            filters.TreeNodeMultipleChoiceFilter,
        )):
            # TreeNodeMultipleChoiceFilter only support negation but must maintain the `in` lookup expression
            return FILTER_TREENODE_NEGATION_LOOKUP_MAP

        elif isinstance(existing_filter, (
            django_filters.ModelChoiceFilter,
            django_filters.ModelMultipleChoiceFilter,
            TagFilter
        )):
            # These filter types support only negation
            return FILTER_NEGATION_LOOKUP_MAP

        elif isinstance(existing_filter, (
            django_filters.filters.CharFilter,
            django_filters.MultipleChoiceFilter,
            filters.MultiValueCharFilter,
            filters.MultiValueMACAddressFilter
        )):
            return FILTER_CHAR_BASED_LOOKUP_MAP

        return None

    @classmethod
    def get_additional_lookups(cls, existing_filter_name, existing_filter):
        new_filters = {}

        # Skip on abstract models
        if not cls._meta.model:
            return {}

        # Skip nonstandard lookup expressions
        if existing_filter.method is not None or existing_filter.lookup_expr not in ['exact', 'iexact', 'in']:
            return {}

        # Choose the lookup expression map based on the filter type
        lookup_map = cls._get_filter_lookup_dict(existing_filter)
        if lookup_map is None:
            # Do not augment this filter type with more lookup expressions
            return {}

        # Get properties of the existing filter for later use
        field_name = existing_filter.field_name
        field = get_model_field(cls._meta.model, field_name)

        # Create new filters for each lookup expression in the map
        for lookup_name, lookup_expr in lookup_map.items():
            new_filter_name = f'{existing_filter_name}__{lookup_name}'
            existing_filter_extra = deepcopy(existing_filter.extra)

            try:
                if existing_filter_name in cls.declared_filters:
                    # The filter field has been explicitly defined on the filterset class so we must manually
                    # create the new filter with the same type because there is no guarantee the defined type
                    # is the same as the default type for the field
                    resolve_field(field, lookup_expr)  # Will raise FieldLookupError if the lookup is invalid
                    filter_cls = type(existing_filter)
                    if lookup_expr == 'empty':
                        filter_cls = django_filters.BooleanFilter
                        for param_to_remove in ('choices', 'null_value'):
                            existing_filter_extra.pop(param_to_remove, None)
                    new_filter = filter_cls(
                        field_name=field_name,
                        lookup_expr=lookup_expr,
                        label=existing_filter.label,
                        exclude=existing_filter.exclude,
                        distinct=existing_filter.distinct,
                        **existing_filter_extra
                    )
                elif hasattr(existing_filter, 'custom_field'):
                    # Filter is for a custom field
                    custom_field = existing_filter.custom_field
                    new_filter = custom_field.to_filter(lookup_expr=lookup_expr)
                else:
                    # The filter field is listed in Meta.fields so we can safely rely on default behaviour
                    # Will raise FieldLookupError if the lookup is invalid
                    new_filter = cls.filter_for_field(field, field_name, lookup_expr)
            except FieldLookupError:
                # The filter could not be created because the lookup expression is not supported on the field
                continue

            if lookup_name.startswith('n'):
                # This is a negation filter which requires a queryset.exclude() clause
                # Of course setting the negation of the existing filter's exclude attribute handles both cases
                new_filter.exclude = not existing_filter.exclude

            new_filters[new_filter_name] = new_filter

        return new_filters

    @classmethod
    def get_filters(cls):
        """
        Override filter generation to support dynamic lookup expressions for certain filter types.

        For specific filter types, new filters are created based on defined lookup expressions in
        the form `<field_name>__<lookup_expr>`
        """
        filters = super().get_filters()

        additional_filters = {}
        for existing_filter_name, existing_filter in filters.items():
            additional_filters.update(cls.get_additional_lookups(existing_filter_name, existing_filter))

        filters.update(additional_filters)

        return filters

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):

        if lookup_type == 'empty':
            return django_filters.BooleanFilter, {}

        return super().filter_for_lookup(field, lookup_type)


class ChangeLoggedModelFilterSet(BaseFilterSet):
    """
    Base FilterSet for ChangeLoggedModel classes.
    """
    created = filters.MultiValueDateTimeFilter()
    last_updated = filters.MultiValueDateTimeFilter()
    created_by_request = django_filters.UUIDFilter(
        method='filter_by_request'
    )
    updated_by_request = django_filters.UUIDFilter(
        method='filter_by_request'
    )
    modified_by_request = django_filters.UUIDFilter(
        method='filter_by_request'
    )

    def filter_by_request(self, queryset, name, value):
        content_type = ContentType.objects.get_for_model(self.Meta.model)
        action = {
            'created_by_request': Q(action=ObjectChangeActionChoices.ACTION_CREATE),
            'updated_by_request': Q(action=ObjectChangeActionChoices.ACTION_UPDATE),
            'modified_by_request': Q(action__in=[ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE]),
        }.get(name)
        request_id = value
        pks = ObjectChange.objects.filter(
            action,
            changed_object_type=content_type,
            request_id=request_id,
        ).values_list('changed_object_id', flat=True)
        return queryset.filter(pk__in=pks)


class NetBoxModelFilterSet(ChangeLoggedModelFilterSet):
    """
    Provides additional filtering functionality (e.g. tags, custom fields) for core NetBox models.
    """
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    tag = TagFilter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically add a Filter for each CustomField applicable to the parent model
        custom_fields = CustomField.objects.filter(
            object_types=ContentType.objects.get_for_model(self._meta.model)
        ).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )

        custom_field_filters = {}
        for custom_field in custom_fields:
            filter_name = f'cf_{custom_field.name}'
            filter_instance = custom_field.to_filter()
            if filter_instance:
                custom_field_filters[filter_name] = filter_instance

                # Add relevant additional lookups
                additional_lookups = self.get_additional_lookups(filter_name, filter_instance)
                custom_field_filters.update(additional_lookups)

        self.filters.update(custom_field_filters)

    def search(self, queryset, name, value):
        """
        Override this method to apply a general-purpose search logic.
        """
        return queryset


class OrganizationalModelFilterSet(NetBoxModelFilterSet):
    """
    A base class for adding the search method to models which only expose the `name` and `slug` fields
    """
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(slug__icontains=value) |
            models.Q(description__icontains=value)
        )
