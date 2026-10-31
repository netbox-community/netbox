import json
from collections.abc import MutableMapping
from copy import deepcopy

import django_filters
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.forms.utils import ErrorDict, ErrorList
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext as _
from django_filters.exceptions import FieldLookupError
from django_filters.utils import get_model_field, resolve_field
from django_filters.widgets import SuffixedMultiWidget

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from extras.choices import CustomFieldFilterLogicChoices
from extras.filters import TagFilter, TagIDFilter
from extras.models import CustomField, SavedFilter
from users.filterset_mixins import OwnerFilterMixin
from utilities import filters
from utilities.constants import (
    FILTER_ARRAY_BASED_LOOKUP_MAP,
    FILTER_CHAR_BASED_LOOKUP_MAP,
    FILTER_EMPTY_LOOKUP_MAP,
    FILTER_NEGATION_LOOKUP_MAP,
    FILTER_NUMERIC_BASED_LOOKUP_MAP,
    FILTER_TAG_LOOKUP_MAP,
    FILTER_TREENODE_NEGATION_LOOKUP_MAP,
)
from utilities.forms.fields import MACAddressField

__all__ = (
    'AttributeFiltersMixin',
    'BaseFilterSet',
    'ChangeLoggedModelFilterSet',
    'NestedGroupModelFilterSet',
    'NetBoxModelFilterSet',
    'OrganizationalModelFilterSet',
    'PrimaryModelFilterSet',
)

STANDARD_LOOKUPS = (
    'exact',
    'iexact',
    'in',
    'contains',
)

# Lookup expressions which take a boolean value
BOOLEAN_LOOKUPS = (
    'empty',
    'isnull',
)


#
# Filter resolution
#

def get_data_keys(name, filter_):
    """
    Return the keys of request data from which the given filter reads its value.
    """
    widget = filter_.extra.get('widget') or getattr(filter_.field_class, 'widget', None)
    widget_class = widget if isinstance(widget, type) else type(widget)
    if not issubclass(widget_class, forms.MultiWidget):
        return [name]
    if issubclass(widget_class, SuffixedMultiWidget):
        return [f'{name}_{suffix}' if suffix else name for suffix in widget.suffixes]
    return [f'{name}{suffix}' for suffix in deepcopy(filter_).field.widget.widgets_names]


class FilterIndex:
    """
    The filters of a FilterSet class, indexed for resolving request data.
    """
    def __init__(self, filters):
        self.filters = filters
        self.positions = {name: i for i, name in enumerate(filters)}
        # Data keys which differ from the name of the filter reading them (e.g. "created_after")
        self.data_keys = {
            key: name
            for name, filter_ in filters.items()
            for key in get_data_keys(name, filter_)
            if key != name
        }
        self.required = [name for name, filter_ in filters.items() if filter_.extra.get('required')]


class LazyFilters:
    """
    Filters built by calling a loader once a filter whose name begins with the given prefix is requested.
    """
    def __init__(self, prefix, loader):
        self.prefix = prefix
        self.loader = loader
        self.names = None


class FilterDict(MutableMapping):
    """
    The filters of a FilterSet instance. Each of the class's filters is copied on first access, so that a request
    copies only the filters it uses.
    """
    def __init__(self, filterset, index):
        self.filterset = filterset
        self.index = index
        self.filters = {}  # Filters copied or added for this instance
        self.removed = set()  # Names of class filters removed from this instance
        self.extra = []  # Names of added filters, and LazyFilters, in order
        self.extra_data_keys = {}

    def __getitem__(self, name):
        if name not in self.filters:
            if self._is_class_filter(name):
                filter_ = deepcopy(self.index.filters[name])
                filter_.model = self.filterset.queryset.model
                filter_.parent = self.filterset
                self.filters[name] = filter_
            elif not self._load(name):
                raise KeyError(name)
        return self.filters[name]

    def __setitem__(self, name, filter_):
        if name not in self:
            self.extra.append(name)
            self._add_data_keys(name, filter_)
        self.filters[name] = filter_

    def __delitem__(self, name):
        if name not in self:
            raise KeyError(name)
        self.filters.pop(name, None)
        if self._is_class_filter(name):
            self.removed.add(name)
        elif name in self.extra:
            self.extra.remove(name)
        else:
            for entry in self.extra:
                if isinstance(entry, LazyFilters) and name in (entry.names or []):
                    entry.names.remove(name)
        self.extra_data_keys = {key: value for key, value in self.extra_data_keys.items() if value != name}

    def __iter__(self):
        self._load()
        for name in self.index.filters:
            if name not in self.removed:
                yield name
        yield from self._extra_names()

    def __len__(self):
        self._load()
        return len(self.index.filters) - len(self.removed) + len(self._extra_names())

    def __contains__(self, name):
        return name in self.filters or self._is_class_filter(name) or self._load(name)

    def add_lazy(self, prefix, loader):
        """
        Register a callable which returns filters named with the given prefix, to be called once one is needed.
        """
        self.extra.append(LazyFilters(prefix, loader))

    def get_names(self, key):
        """
        Return the names of the filters which read the given key of the request data.
        """
        names = [key] if key in self else []
        name = self.extra_data_keys.get(key) or self.index.data_keys.get(key)
        if name is not None and name != key and name in self:
            names.append(name)
        return names

    def position(self, name):
        """
        Return the position of the named filter in declaration order.
        """
        if self._is_class_filter(name):
            return self.index.positions[name]
        return len(self.index.positions) + self._extra_names().index(name)

    def _is_class_filter(self, name):
        return name in self.index.filters and name not in self.removed

    def _extra_names(self):
        names = []
        for entry in self.extra:
            if isinstance(entry, LazyFilters):
                names.extend(entry.names or [])
            else:
                names.append(entry)
        return names

    def _add_data_keys(self, name, filter_):
        for key in get_data_keys(name, filter_):
            if key != name:
                self.extra_data_keys[key] = name

    def _load(self, name=None):
        """
        Call any pending loaders for the given filter name (or all of them). Return True if the name now exists.
        """
        for entry in self.extra:
            if not isinstance(entry, LazyFilters) or entry.names is not None:
                continue
            if name is not None and not name.startswith(entry.prefix):
                continue
            entry.names = []
            for filter_name, filter_ in entry.loader().items():
                if filter_name not in self.filters and not self._is_class_filter(filter_name):
                    entry.names.append(filter_name)
                    self._add_data_keys(filter_name, filter_)
                self.filters[filter_name] = filter_
        return name is not None and name in self.filters


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
        models.BigIntegerField: {
            'filter_class': filters.MultiValueBigNumberFilter
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

    # Set to True to evaluate every filter on each request, as before NetBox v4.8 (to be revisited in v5.0)
    legacy_evaluation = False

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        # Apply any referenced SavedFilters
        if data and ('filter' in data or 'filter_id' in data):
            data = data.copy()  # Get a mutable copy

            # Coerce filter_id values to integers, ignoring any which are not valid (see #22568)
            filter_ids = []
            for f_id in data.pop('filter_id', []):
                try:
                    filter_ids.append(int(f_id))
                except (ValueError, TypeError):
                    pass

            # Only apply SavedFilters the requesting user is permitted to see (#22790). Fall back to
            # anonymous visibility (shared filters only) when no request is available.
            user = request.user if request else AnonymousUser()
            saved_filters = SavedFilter.objects.restrict_to_shared(user).filter(
                Q(slug__in=data.pop('filter', [])) |
                Q(pk__in=filter_ids)
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

        if self.legacy_evaluation or prefix is not None or self._has_custom_form():
            # bit of a hack for #9231 - extras.lookup.Empty is registered in apps.ready
            # however FilterSet Factory is setup before this which creates the
            # initial filters.  This recreates the filters so Empty is picked up correctly.
            self.base_filters = self.__class__.get_filters()
            super().__init__(data, queryset, request=request, prefix=prefix)
            return

        # Copy each filter only once it's used, rather than deep-copying all of them as django-filter does
        if queryset is None:
            queryset = self._meta.model._default_manager.all()
        self.is_bound = data is not None
        self.data = data or QueryDict()
        self.queryset = queryset
        self.request = request
        self.form_prefix = prefix
        self.filters = FilterDict(self, self._get_filter_index())

    @classmethod
    def _get_filter_index(cls):
        """
        Return the class's filters, generated on first use (after Empty has been registered; see #9231). A class
        which overrides get_filters() regenerates them on every call.
        """
        if cls.get_filters.__func__ is not BaseFilterSet.get_filters.__func__:
            return FilterIndex(cls.get_filters())
        if '_filter_index' not in cls.__dict__:
            cls._filter_index = FilterIndex(cls.get_filters())
        return cls._filter_index

    @classmethod
    def _has_custom_form(cls):
        return cls._meta.form is not forms.Form or cls.get_form_class is not django_filters.FilterSet.get_form_class

    @property
    def _lazy(self):
        # False under legacy evaluation, or if the filters have been replaced
        return isinstance(self.filters, FilterDict)

    @property
    def form(self):
        form = super().form
        if self._lazy and self.is_bound:
            # Evaluation no longer validates the form, so validate it here for code which reads its cleaned_data
            form.is_valid()
        return form

    @property
    def errors(self):
        if not self._lazy:
            return super().errors
        self._clean()
        return self._errors

    def is_valid(self):
        return self.is_bound and not self.errors

    @property
    def cleaned_data(self):
        """
        The cleaned values of the filters for which the request supplies data. For internal use only.
        """
        if not self._lazy:
            self.form.is_valid()
            return getattr(self.form, 'cleaned_data', {})
        self._clean()
        return self._cleaned_data

    def filter_queryset(self, queryset):
        if not self._lazy:
            return super().filter_queryset(queryset)
        for name, value in self.cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(queryset, models.QuerySet), (
                f"Expected '{type(self).__name__}.{name}' to return a QuerySet, but got a "
                f"{type(queryset).__name__} instead."
            )
        return queryset

    def _clean(self):
        """
        Clean the request's value for each filter it supplies, in declaration order.
        """
        if hasattr(self, '_cleaned_data'):
            return
        self._cleaned_data = {}
        self._errors = ErrorDict()
        if not self.is_bound:
            return
        names = {name for name in self.filters.index.required if name in self.filters}
        for key in self.data.keys():
            names.update(self.filters.get_names(key))
        files = MultiValueDict()
        for name in sorted(names, key=self.filters.position):
            field = self.filters[name].field
            try:
                self._cleaned_data[name] = field.clean(field.widget.value_from_datadict(self.data, files, name))
            except ValidationError as e:
                self._errors[name] = ErrorList(e.error_list)

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

        if isinstance(existing_filter, (
            filters.TreeNodeMultipleChoiceFilter,
        )):
            # TreeNodeMultipleChoiceFilter only support negation but must maintain the `in` lookup expression
            return FILTER_TREENODE_NEGATION_LOOKUP_MAP

        if isinstance(existing_filter, (TagFilter, TagIDFilter)):
            # Tags additionally support an "any of" (OR) mode, unlike other model choice filters
            return FILTER_TAG_LOOKUP_MAP

        if isinstance(existing_filter, (
            django_filters.ModelChoiceFilter,
            django_filters.ModelMultipleChoiceFilter,
        )):
            # These filter types support only negation
            return FILTER_NEGATION_LOOKUP_MAP

        if isinstance(existing_filter, (
            filters.MultiValueArrayFilter,
        )):
            # Must precede the char-based branch below, which would otherwise shadow this subclass
            return FILTER_ARRAY_BASED_LOOKUP_MAP

        if isinstance(existing_filter, (
            django_filters.filters.CharFilter,
            django_filters.ChoiceFilter,
            django_filters.MultipleChoiceFilter,
            filters.MultiValueCharFilter,
        )):
            return FILTER_CHAR_BASED_LOOKUP_MAP

        if isinstance(existing_filter, django_filters.BooleanFilter) and hasattr(existing_filter, 'custom_field'):
            # A boolean custom field may hold no value at all, so it supports only the empty lookup
            return FILTER_EMPTY_LOOKUP_MAP

        return None

    @classmethod
    def get_additional_lookups(cls, existing_filter_name, existing_filter):
        new_filters = {}

        # Skip on abstract models
        if not cls._meta.model:
            return {}

        # Skip nonstandard lookup expressions
        if existing_filter.method is not None or existing_filter.lookup_expr not in STANDARD_LOOKUPS:
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

            try:
                if existing_filter_name in cls.declared_filters:
                    # The filter field has been explicitly defined on the filterset class so we must manually
                    # create the new filter with the same type because there is no guarantee the defined type
                    # is the same as the default type for the field
                    if field is None:
                        raise ValueError('Invalid field name/lookup on {}: {}'.format(existing_filter_name, field_name))
                    resolve_field(field, lookup_expr)  # Will raise FieldLookupError if the lookup is invalid
                    if lookup_expr in BOOLEAN_LOOKUPS:
                        # Boolean lookups take a true/false value regardless of the declared filter's type. The
                        # declared filter's extra kwargs (e.g. min_value, max_digits) don't apply to a BooleanFilter.
                        filter_cls = django_filters.BooleanFilter
                        existing_filter_extra = {}
                    else:
                        filter_cls = type(existing_filter)
                        existing_filter_extra = deepcopy(existing_filter.extra)
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

            if lookup_name == 'any' and isinstance(new_filter, (TagFilter, TagIDFilter)):
                # "Any of" is an OR match, whereas TagFilter/TagIDFilter default to AND (conjoined=True)
                new_filter.conjoined = False

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
            'modified_by_request': Q(
                action__in=[ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE]
            ),
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
    tag_id = TagIDFilter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.filters, FilterDict):
            # Build custom field filters only once one is needed
            self.filters.add_lazy('cf_', self._get_custom_field_filters)
        else:
            self.filters.update(self._get_custom_field_filters())

    def _get_custom_field_filters(self):
        """
        Return filters for the model's custom fields, including their additional lookups.
        """
        custom_field_filters = {}
        for custom_field in CustomField.objects.get_for_model(self._meta.model):
            if custom_field.filter_logic == CustomFieldFilterLogicChoices.FILTER_DISABLED:
                # Skip disabled fields
                continue
            if filter_instance := custom_field.to_filter():
                filter_name = f'cf_{custom_field.name}'
                custom_field_filters[filter_name] = filter_instance

                # Add relevant additional lookups
                additional_lookups = self.get_additional_lookups(filter_name, filter_instance)
                custom_field_filters.update(additional_lookups)

        return custom_field_filters

    def search(self, queryset, name, value):
        """
        Override this method to apply a general-purpose search logic.
        """
        return queryset


class PrimaryModelFilterSet(OwnerFilterMixin, NetBoxModelFilterSet):
    """
    Base filterset for models inheriting from PrimaryModel.
    """
    pass


class OrganizationalModelFilterSet(OwnerFilterMixin, NetBoxModelFilterSet):
    """
    Base filterset for models inheriting from OrganizationalModel.
    """
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(slug__icontains=value) |
            models.Q(description__icontains=value)
        )


class NestedGroupModelFilterSet(OwnerFilterMixin, NetBoxModelFilterSet):
    """
    Base filterset for models inheriting from NestedGroupModel.
    """
    def search(self, queryset, name, value):
        if value.strip():
            queryset = queryset.filter(
                models.Q(name__icontains=value) |
                models.Q(slug__icontains=value) |
                models.Q(description__icontains=value) |
                models.Q(comments__icontains=value)
            )

        return queryset


class AttributeFiltersMixin:
    attributes_field_name = 'attribute_data'
    attribute_filter_prefix = 'attr_'

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self.attr_filters = {}

        # Extract JSONField-based filters from the incoming data
        if data is not None:
            for key, value in data.items():
                if field := self._get_field_lookup(key):
                    # Attempt to cast the value to a native JSON type
                    try:
                        self.attr_filters[field] = json.loads(value)
                    except (ValueError, json.JSONDecodeError):
                        self.attr_filters[field] = value

        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

    def _get_field_lookup(self, key):
        if not key.startswith(self.attribute_filter_prefix):
            return None
        lookup = key.split(self.attribute_filter_prefix, 1)[1]  # Strip prefix
        return f'{self.attributes_field_name}__{lookup}'

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(**self.attr_filters)
