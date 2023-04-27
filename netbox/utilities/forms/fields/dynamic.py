import django_filters
from django import forms
from django.conf import settings
from django.forms import BoundField
from django.urls import reverse

from utilities.forms import widgets
from utilities.utils import get_viewname

__all__ = (
    'DynamicModelChoiceField',
    'DynamicModelMultipleChoiceField',
)


class DynamicModelChoiceMixin:
    """
    Override `get_bound_field()` to avoid pre-populating field choices with a SQL query. The field will be
    rendered only with choices set via bound data. Choices are populated on-demand via the APISelect widget.

    Attributes:
        query_params: A dictionary of additional key/value pairs to attach to the API request
        initial_params: A dictionary of child field references to use for selecting a parent field's initial value
        null_option: The string used to represent a null selection (if any)
        disabled_indicator: The name of the field which, if populated, will disable selection of the
            choice (optional)
        fetch_trigger: The event type which will cause the select element to
            fetch data from the API. Must be 'load', 'open', or 'collapse'. (optional)
        selector: Include an advanced object selection widget to assist the user in identifying the desired object
    """
    filter = django_filters.ModelChoiceFilter
    widget = widgets.APISelect

    def __init__(
            self,
            queryset,
            *,
            query_params=None,
            initial_params=None,
            null_option=None,
            disabled_indicator=None,
            fetch_trigger=None,
            empty_label=None,
            selector=False,
            **kwargs
    ):
        self.model = queryset.model
        self.query_params = query_params or {}
        self.initial_params = initial_params or {}
        self.null_option = null_option
        self.disabled_indicator = disabled_indicator
        self.fetch_trigger = fetch_trigger
        self.selector = selector

        # to_field_name is set by ModelChoiceField.__init__(), but we need to set it early for reference
        # by widget_attrs()
        self.to_field_name = kwargs.get('to_field_name')
        self.empty_option = empty_label or ""

        super().__init__(queryset, **kwargs)

    def widget_attrs(self, widget):
        attrs = {
            'data-empty-option': self.empty_option
        }

        # Set value-field attribute if the field specifies to_field_name
        if self.to_field_name:
            attrs['value-field'] = self.to_field_name

        # Set the string used to represent a null option
        if self.null_option is not None:
            attrs['data-null-option'] = self.null_option

        # Set the disabled indicator, if any
        if self.disabled_indicator is not None:
            attrs['disabled-indicator'] = self.disabled_indicator

        # Set the fetch trigger, if any.
        if self.fetch_trigger is not None:
            attrs['data-fetch-trigger'] = self.fetch_trigger

        # Attach any static query parameters
        if (len(self.query_params) > 0):
            widget.add_query_params(self.query_params)

        # Include object selector?
        if self.selector:
            attrs['selector'] = self.model._meta.label_lower

        return attrs

    def get_bound_field(self, form, field_name):
        bound_field = BoundField(form, self, field_name)

        # Set initial value based on prescribed child fields (if not already set)
        if not self.initial and self.initial_params:
            filter_kwargs = {}
            for kwarg, child_field in self.initial_params.items():
                value = form.initial.get(child_field.lstrip('$'))
                if value:
                    filter_kwargs[kwarg] = value
            if filter_kwargs:
                self.initial = self.queryset.filter(**filter_kwargs).first()

        # Modify the QuerySet of the field before we return it. Limit choices to any data already bound: Options
        # will be populated on-demand via the APISelect widget.
        data = bound_field.value()

        if data:
            # When the field is multiple choice pass the data as a list if it's not already
            if isinstance(bound_field.field, DynamicModelMultipleChoiceField) and not type(data) is list:
                data = [data]

            field_name = getattr(self, 'to_field_name') or 'pk'
            filter = self.filter(field_name=field_name)
            try:
                self.queryset = filter.filter(self.queryset, data)
            except (TypeError, ValueError):
                # Catch any error caused by invalid initial data passed from the user
                self.queryset = self.queryset.none()
        else:
            self.queryset = self.queryset.none()

        # Set the data URL on the APISelect widget (if not already set)
        widget = bound_field.field.widget
        if not widget.attrs.get('data-url'):
            viewname = get_viewname(self.queryset.model, action='list', rest_api=True)
            widget.attrs['data-url'] = reverse(viewname)

        return bound_field


class DynamicModelChoiceField(DynamicModelChoiceMixin, forms.ModelChoiceField):
    """
    Dynamic selection field for a single object, backed by NetBox's REST API.
    """
    def clean(self, value):
        """
        When null option is enabled and "None" is sent as part of a form to be submitted, it is sent as the
        string 'null'.  This will check for that condition and gracefully handle the conversion to a NoneType.
        """
        if self.null_option is not None and value == settings.FILTERS_NULL_CHOICE_VALUE:
            return None
        return super().clean(value)


class DynamicModelMultipleChoiceField(DynamicModelChoiceMixin, forms.ModelMultipleChoiceField):
    """
    A multiple-choice version of `DynamicModelChoiceField`.
    """
    filter = django_filters.ModelMultipleChoiceFilter
    widget = widgets.APISelectMultiple

    def clean(self, value):
        value = value or []

        # When null option is enabled and "None" is sent as part of a form to be submitted, it is sent as the
        # string 'null'.  This will check for that condition and gracefully handle the conversion to a NoneType.
        if self.null_option is not None and settings.FILTERS_NULL_CHOICE_VALUE in value:
            value = [v for v in value if v != settings.FILTERS_NULL_CHOICE_VALUE]
            return [None, *value]

        return super().clean(value)
