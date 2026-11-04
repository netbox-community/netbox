from collections.abc import MutableMapping
from copy import deepcopy

from django import forms
from django.forms.widgets import ChoiceWidget
from django_filters.widgets import BaseCSVWidget, BooleanWidget, LinkWidget, QueryArrayWidget, SuffixedMultiWidget

__all__ = (
    'FilterDict',
    'FilterIndex',
    'LazyFilters',
    'get_data_keys',
)

# Widget classes whose value_from_datadict() reads only the key matching the field's name
SINGLE_KEY_WIDGETS = (
    forms.CheckboxInput,
    forms.MultipleHiddenInput,
    forms.NullBooleanSelect,
    forms.SelectMultiple,
    forms.Widget,
    ChoiceWidget,
    BaseCSVWidget,
    BooleanWidget,
    LinkWidget,
)


def get_field_attr(filter_, attr):
    """
    Return an attribute (e.g. "required") of the given filter's form field, without building the field if it hasn't
    been already.
    """
    # Filter.field caches the field as _field once built, after which changes to the filter's extra don't apply
    if (field := vars(filter_).get('_field')) is not None:
        return getattr(field, attr)
    return filter_.extra.get(attr)


def get_data_keys(name, filter_):
    """
    Return the keys of request data from which the given filter reads its value, or None if they can't be determined.
    """
    widget = get_field_attr(filter_, 'widget') or getattr(filter_.field_class, 'widget', None)
    widget_class = widget if isinstance(widget, type) else type(widget)
    # The keys read depend on which class implements value_from_datadict()
    reader = next((klass for klass in widget_class.__mro__ if 'value_from_datadict' in vars(klass)), None)
    if reader is QueryArrayWidget:
        return [name, f'{name}[]']
    if reader is SuffixedMultiWidget:
        return [f'{name}_{suffix}' if suffix else name for suffix in widget.suffixes]
    if reader is forms.MultiWidget:
        return [f'{name}{suffix}' for suffix in deepcopy(filter_).field.widget.widgets_names]
    if reader in SINGLE_KEY_WIDGETS:
        return [name]
    return None


def is_unconditional(filter_, data_keys):
    """
    Return True if the given filter is cleaned even when absent from the request data: if it's required or disabled,
    or if the keys it reads (data_keys) can't be determined.
    """
    return data_keys is None or bool(get_field_attr(filter_, 'required') or get_field_attr(filter_, 'disabled'))


class FilterIndex:
    """
    The filters of a FilterSet class, indexed for resolving request data.

    Attributes:
        filters: The class's filters, keyed by name in declaration order; shared by all instances of the FilterSet
        positions: The position of each filter in declaration order, keyed by name
        data_keys: Maps each request data key read by a filter of a different name (e.g. "created_after") to the
            names of the filters which read it
        unconditional: The names of filters which are cleaned even when absent from the request data: those which
            are required or disabled, or whose data keys can't be determined
    """
    def __init__(self, filters):
        self.filters = filters
        self.positions = {name: i for i, name in enumerate(filters)}
        self.data_keys = {}
        self.unconditional = []
        for name, filter_ in filters.items():
            keys = get_data_keys(name, filter_)
            if is_unconditional(filter_, keys):
                self.unconditional.append(name)
            for key in keys or ():
                if key != name:
                    self.data_keys.setdefault(key, []).append(name)


class LazyFilters:
    """
    Filters built by calling a loader once a filter whose name begins with the given prefix is requested.

    Attributes:
        prefix: The prefix of the names of the filters the loader returns (e.g. "cf_")
        loader: A callable which returns the filters, keyed by name
        names: The names of the filters which the loader added, or None until it has been called
    """
    def __init__(self, prefix, loader):
        self.prefix = prefix
        self.loader = loader
        self.names = None


class FilterDict(MutableMapping):
    """
    The filters of a FilterSet instance. Each of the class's filters is copied on first access, so that a request
    copies only the filters it uses.

    Attributes:
        filterset: The FilterSet instance to which the filters belong
        index: The FilterIndex of the FilterSet's class
        filters: The filters copied from the index, added, or loaded for this instance, keyed by name. Any of these may
            have been changed since, so the request data each reads is determined only once the request is evaluated.
        removed: The names of class filters removed from this instance
        extra: The names of filters added to this instance, and its LazyFilters, in the order added
    """
    def __init__(self, filterset, index):
        self.filterset = filterset
        self.index = index
        self.filters = {}
        self.removed = set()
        self.extra = []

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

    def copy(self):
        """
        Return the filters as a dict.
        """
        return dict(self)

    def add_lazy(self, prefix, loader):
        """
        Register a callable which returns filters named with the given prefix, to be called once one is needed.
        """
        self.extra.append(LazyFilters(prefix, loader))

    def get_evaluated(self, keys):
        """
        Return the names of the filters to clean for request data with the given keys: those which read any of the
        keys, and those which are cleaned even when absent from the request data.
        """
        keys = set(keys)
        # Look up each key first, which loads any lazy filters it names
        names = {key for key in keys if key in self}
        for key in keys:
            names.update(name for name in self.index.data_keys.get(key, ()) if self._is_indexed(name))
        names.update(name for name in self.index.unconditional if self._is_indexed(name))
        # The index doesn't reflect changes to the filters held by this instance, so examine each of them
        for name, filter_ in self.filters.items():
            data_keys = get_data_keys(name, filter_)
            if is_unconditional(filter_, data_keys) or not keys.isdisjoint(data_keys):
                names.add(name)
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

    def _is_indexed(self, name):
        # A class filter which this instance hasn't copied, replaced, or removed
        return name not in self.filters and self._is_class_filter(name)

    def _extra_names(self):
        names = []
        for entry in self.extra:
            if isinstance(entry, LazyFilters):
                names.extend(entry.names or [])
            else:
                names.append(entry)
        return names

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
                self.filters[filter_name] = filter_
        return name is not None and name in self.filters
