import json
from typing import Dict, List, Tuple

from django import forms
from django.conf import settings

__all__ = (
    'APISelect',
    'APISelectMultiple',
)


class APISelect(forms.Select):
    """
    A select widget populated via an API call

    :param api_url: API endpoint URL. Required if not set automatically by the parent field.
    """
    template_name = 'widgets/apiselect.html'
    option_template_name = 'widgets/select_option.html'
    dynamic_params: Dict[str, str]
    static_params: Dict[str, List[str]]

    def __init__(self, api_url=None, full=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['class'] = 'api-select'
        self.dynamic_params: Dict[str, List[str]] = {}
        self.static_params: Dict[str, List[str]] = {}

        if api_url:
            self.attrs['data-url'] = '/{}{}'.format(settings.BASE_PATH, api_url.lstrip('/'))  # Inject BASE_PATH

    def __deepcopy__(self, memo):
        """Reset `static_params` and `dynamic_params` when APISelect is deepcopied."""
        result = super().__deepcopy__(memo)
        result.dynamic_params = {}
        result.static_params = {}
        return result

    def _process_query_param(self, key, value) -> None:
        """
        Based on query param value's type and value, update instance's dynamic/static params.
        """
        if isinstance(value, str):
            # Coerce `True` boolean.
            if value.lower() == 'true':
                value = True
            # Coerce `False` boolean.
            elif value.lower() == 'false':
                value = False
            # Query parameters cannot have a `None` (or `null` in JSON) type, convert
            # `None` types to `'null'` so that ?key=null is used in the query URL.
            elif value is None:
                value = 'null'

        # Check type of `value` again, since it may have changed.
        if isinstance(value, str):
            if value.startswith('$'):
                # A value starting with `$` indicates a dynamic query param, where the
                # initial value is unknown and will be updated at the JavaScript layer
                # as the related form field's value changes.
                field_name = value.strip('$')
                self.dynamic_params[field_name] = key
            else:
                # A value _not_ starting with `$` indicates a static query param, where
                # the value is already known and should not be changed at the JavaScript
                # layer.
                if key in self.static_params:
                    current = self.static_params[key]
                    self.static_params[key] = [v for v in set([*current, value])]
                else:
                    self.static_params[key] = [value]
        else:
            # Any non-string values are passed through as static query params, since
            # dynamic query param values have to be a string (in order to start with
            # `$`).
            if key in self.static_params:
                current = self.static_params[key]
                self.static_params[key] = [v for v in set([*current, value])]
            else:
                self.static_params[key] = [value]

    def _process_query_params(self, query_params):
        """
        Process an entire query_params dictionary, and handle primitive or list values.
        """
        for key, value in query_params.items():
            if isinstance(value, (List, Tuple)):
                # If value is a list/tuple, iterate through each item.
                for item in value:
                    self._process_query_param(key, item)
            else:
                self._process_query_param(key, value)

    def _serialize_params(self, key, params):
        """
        Serialize dynamic or static query params to JSON and add the serialized value to
        the widget attributes by `key`.
        """
        # Deserialize the current serialized value from the widget, using an empty JSON
        # array as a fallback in the event one is not defined.
        current = json.loads(self.attrs.get(key, '[]'))

        # Combine the current values with the updated values and serialize the result as
        # JSON. Note: the `separators` kwarg effectively removes extra whitespace from
        # the serialized JSON string, which is ideal since these will be passed as
        # attributes to HTML elements and parsed on the client.
        self.attrs[key] = json.dumps([*current, *params], separators=(',', ':'))

    def _add_dynamic_params(self):
        """
        Convert post-processed dynamic query params to data structure expected by front-
        end, serialize the value to JSON, and add it to the widget attributes.
        """
        key = 'data-dynamic-params'
        if len(self.dynamic_params) > 0:
            try:
                update = [{'fieldName': f, 'queryParam': q} for (f, q) in self.dynamic_params.items()]
                self._serialize_params(key, update)
            except IndexError as error:
                raise RuntimeError(f"Missing required value for dynamic query param: '{self.dynamic_params}'") from error

    def _add_static_params(self):
        """
        Convert post-processed static query params to data structure expected by front-
        end, serialize the value to JSON, and add it to the widget attributes.
        """
        key = 'data-static-params'
        if len(self.static_params) > 0:
            try:
                update = [{'queryParam': k, 'queryValue': v} for (k, v) in self.static_params.items()]
                self._serialize_params(key, update)
            except IndexError as error:
                raise RuntimeError(f"Missing required value for static query param: '{self.static_params}'") from error

    def add_query_params(self, query_params):
        """
        Proccess & add a dictionary of URL query parameters to the widget attributes.
        """
        # Process query parameters. This populates `self.dynamic_params` and `self.static_params`.
        self._process_query_params(query_params)
        # Add processed dynamic parameters to widget attributes.
        self._add_dynamic_params()
        # Add processed static parameters to widget attributes.
        self._add_static_params()

    def add_query_param(self, key, value) -> None:
        """
        Process & add a key/value pair of URL query parameters to the widget attributes.
        """
        self.add_query_params({key: value})


class APISelectMultiple(APISelect, forms.SelectMultiple):
    pass
