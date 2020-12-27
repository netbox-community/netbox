import logging
import platform
from collections import OrderedDict

from django import __version__ as DJANGO_VERSION
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django_rq.queues import get_connection
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rq.worker import Worker

from netbox.api import BulkOperationSerializer
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.exceptions import SerializerNotFound
from utilities.api import get_serializer_for_model

HTTP_ACTIONS = {
    'GET': 'view',
    'OPTIONS': None,
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


#
# Mixins
#

class BulkUpdateModelMixin:
    """
    Support bulk modification of objects using the list endpoint for a model. Accepts a PATCH action with a list of one
    or more JSON objects, each specifying the numeric ID of an object to be updated as well as the attributes to be set.
    For example:

    PATCH /api/dcim/sites/
    [
        {
            "id": 123,
            "name": "New name"
        },
        {
            "id": 456,
            "status": "planned"
        }
    ]
    """
    def bulk_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        # Map update data by object ID
        update_data = {
            obj.pop('id'): obj for obj in request.data
        }

        data = self.perform_bulk_update(qs, update_data, partial=partial)

        return Response(data, status=status.HTTP_200_OK)

    def perform_bulk_update(self, objects, update_data, partial):
        with transaction.atomic():
            data_list = []
            for obj in objects:
                data = update_data.get(obj.id)
                serializer = self.get_serializer(obj, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                data_list.append(serializer.data)

            return data_list

    def bulk_partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.bulk_update(request, *args, **kwargs)


class BulkDestroyModelMixin:
    """
    Support bulk deletion of objects using the list endpoint for a model. Accepts a DELETE action with a list of one
    or more JSON objects, each specifying the numeric ID of an object to be deleted. For example:

    DELETE /api/dcim/sites/
    [
        {"id": 123},
        {"id": 456}
    ]
    """
    def bulk_destroy(self, request, *args, **kwargs):
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        self.perform_bulk_destroy(qs)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, objects):
        with transaction.atomic():
            for obj in objects:
                self.perform_destroy(obj)


#
# Viewsets
#

class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   BulkUpdateModelMixin,
                   BulkDestroyModelMixin,
                   GenericViewSet):
    """
    Accept either a single object or a list of objects to create.
    """
    def get_serializer(self, *args, **kwargs):

        # If a list of objects has been provided, initialize the serializer with many=True
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        logger = logging.getLogger('netbox.api.views.ModelViewSet')

        # If 'brief' has been passed as a query param, find and return the nested serializer for this model, if one
        # exists
        request = self.get_serializer_context()['request']
        if request.query_params.get('brief'):
            logger.debug("Request is for 'brief' format; initializing nested serializer")
            try:
                serializer = get_serializer_for_model(self.queryset.model, prefix='Nested')
                logger.debug(f"Using serializer {serializer}")
                return serializer
            except SerializerNotFound:
                pass

        # Fall back to the hard-coded serializer class
        logger.debug(f"Using serializer {self.serializer_class}")
        return self.serializer_class

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return

        # Restrict the view's QuerySet to allow only the permitted objects
        action = HTTP_ACTIONS[request.method]
        if action:
            self.queryset = self.queryset.restrict(request.user, action)

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger('netbox.api.views.ModelViewSet')

        try:
            return super().dispatch(request, *args, **kwargs)
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            msg = f'Unable to delete object. {len(protected_objects)} dependent objects were found: '
            msg += ', '.join([f'{obj} ({obj.pk})' for obj in protected_objects])
            logger.warning(msg)
            return self.finalize_response(
                request,
                Response({'detail': msg}, status=409),
                *args,
                **kwargs
            )

    def _validate_objects(self, instance):
        """
        Check that the provided instance or list of instances are matched by the current queryset. This confirms that
        any newly created or modified objects abide by the attributes granted by any applicable ObjectPermissions.
        """
        if type(instance) is list:
            # Check that all instances are still included in the view's queryset
            conforming_count = self.queryset.filter(pk__in=[obj.pk for obj in instance]).count()
            if conforming_count != len(instance):
                raise ObjectDoesNotExist
        else:
            # Check that the instance is matched by the view's queryset
            self.queryset.get(pk=instance.pk)

    def perform_create(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Creating new {model._meta.verbose_name}")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    def perform_update(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Updating {model._meta.verbose_name} {serializer.instance} (PK: {serializer.instance.pk})")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    def perform_destroy(self, instance):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Deleting {model._meta.verbose_name} {instance} (PK: {instance.pk})")

        return super().perform_destroy(instance)


#
# Views
#

class APIRootView(APIView):
    """
    This is the root of NetBox's REST API. API endpoints are arranged by app and model name; e.g. `/api/dcim/sites/`.
    """
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

    def get_view_name(self):
        return "API Root"

    def get(self, request, format=None):

        return Response(OrderedDict((
            ('circuits', reverse('circuits-api:api-root', request=request, format=format)),
            ('dcim', reverse('dcim-api:api-root', request=request, format=format)),
            ('extras', reverse('extras-api:api-root', request=request, format=format)),
            ('ipam', reverse('ipam-api:api-root', request=request, format=format)),
            ('plugins', reverse('plugins-api:api-root', request=request, format=format)),
            ('secrets', reverse('secrets-api:api-root', request=request, format=format)),
            ('status', reverse('api-status', request=request, format=format)),
            ('tenancy', reverse('tenancy-api:api-root', request=request, format=format)),
            ('users', reverse('users-api:api-root', request=request, format=format)),
            ('virtualization', reverse('virtualization-api:api-root', request=request, format=format)),
        )))


class StatusView(APIView):
    """
    A lightweight read-only endpoint for conveying NetBox's current operational status.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    def get(self, request):
        # Gather the version numbers from all installed Django apps
        installed_apps = {}
        for app_config in apps.get_app_configs():
            app = app_config.module
            version = getattr(app, 'VERSION', getattr(app, '__version__', None))
            if version:
                if type(version) is tuple:
                    version = '.'.join(str(n) for n in version)
                installed_apps[app_config.name] = version
        installed_apps = {k: v for k, v in sorted(installed_apps.items())}

        # Gather installed plugins
        plugins = {}
        for plugin_name in settings.PLUGINS:
            plugin_name = plugin_name.rsplit('.', 1)[-1]
            plugin_config = apps.get_app_config(plugin_name)
            plugins[plugin_name] = getattr(plugin_config, 'version', None)
        plugins = {k: v for k, v in sorted(plugins.items())}

        return Response({
            'django-version': DJANGO_VERSION,
            'installed-apps': installed_apps,
            'netbox-version': settings.VERSION,
            'plugins': plugins,
            'python-version': platform.python_version(),
            'rq-workers-running': Worker.count(get_connection('default')),
        })
