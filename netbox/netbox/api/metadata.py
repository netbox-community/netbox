from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_str
from rest_framework import exceptions
from rest_framework.metadata import SimpleMetadata
from rest_framework.request import clone_request

from netbox.api.fields import ContentTypeField


class BulkOperationMetadata(SimpleMetadata):

    def determine_actions(self, request, view):
        """
        Replace the stock determine_actions() method to assess object permissions only
        when viewing a specific object. This is necessary to support OPTIONS requests
        with bulk update in place (see #5470).
        """
        actions = {}
        for method in {'PUT', 'POST'} & set(view.allowed_methods):
            view.request = clone_request(request, method)
            try:
                # Test global permissions
                if hasattr(view, 'check_permissions'):
                    view.check_permissions(view.request)
                # Test object permissions (if viewing a specific object)
                if method == 'PUT' and view.lookup_url_kwarg and hasattr(view, 'get_object'):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions


class ContentTypeMetadata(BulkOperationMetadata):

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if hasattr(field, 'queryset') and not field_info.get('read_only') and isinstance(field, ContentTypeField):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_str(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]
            field_info['choices'].sort(key=lambda item: item['display_name'])
        return field_info
