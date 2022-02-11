import platform
import sys

from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.utils import formatting

from netbox.api.exceptions import GraphQLTypeNotFound, SerializerNotFound
from .utils import dynamic_import


def get_serializer_for_model(model, prefix=''):
    """
    Dynamically resolve and return the appropriate serializer for a model.
    """
    app_name, model_name = model._meta.label.split('.')
    # Serializers for Django's auth models are in the users app
    if app_name == 'auth':
        app_name = 'users'
    serializer_name = f'{app_name}.api.serializers.{prefix}{model_name}Serializer'
    try:
        return dynamic_import(serializer_name)
    except AttributeError:
        raise SerializerNotFound(
            f"Could not determine serializer for {app_name}.{model_name} with prefix '{prefix}'"
        )


def get_graphql_type_for_model(model):
    """
    Return the GraphQL type class for the given model.
    """
    app_name, model_name = model._meta.label.split('.')
    # Object types for Django's auth models are in the users app
    if app_name == 'auth':
        app_name = 'users'
    class_name = f'{app_name}.graphql.types.{model_name}Type'
    try:
        return dynamic_import(class_name)
    except AttributeError:
        raise GraphQLTypeNotFound(f"Could not find GraphQL type for {app_name}.{model_name}")


def is_api_request(request):
    """
    Return True of the request is being made via the REST API.
    """
    api_path = reverse('api-root')

    return request.path_info.startswith(api_path) and request.content_type == 'application/json'


def get_view_name(view, suffix=None):
    """
    Derive the view name from its associated model, if it has one. Fall back to DRF's built-in `get_view_name`.
    """
    if hasattr(view, 'queryset'):
        # Determine the model name from the queryset.
        name = view.queryset.model._meta.verbose_name
        name = ' '.join([w[0].upper() + w[1:] for w in name.split()])  # Capitalize each word

    else:
        # Replicate DRF's built-in behavior.
        name = view.__class__.__name__
        name = formatting.remove_trailing_string(name, 'View')
        name = formatting.remove_trailing_string(name, 'ViewSet')
        name = formatting.camelcase_to_spaces(name)

    if suffix:
        name += ' ' + suffix

    return name


def rest_api_server_error(request, *args, **kwargs):
    """
    Handle exceptions and return a useful error message for REST API requests.
    """
    type_, error, traceback = sys.exc_info()
    data = {
        'error': str(error),
        'exception': type_.__name__,
        'netbox_version': settings.VERSION,
        'python_version': platform.python_version(),
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
