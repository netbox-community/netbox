from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from core.choices import ManagedFileRootPathChoices
from extras import filtersets
from extras.jobs import ScriptJob
from extras.models import *
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired, TokenWritePermission
from netbox.api.features import SyncedDataMixin
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import BaseViewSet, NetBoxModelViewSet
from netbox.api.viewsets.mixins import ObjectValidationMixin
from users.models import Token
from utilities.exceptions import RQWorkerNotRunningException
from utilities.request import copy_safe_request
from utilities.rqworker import any_workers_for_queue

from . import serializers
from .mixins import ConfigTemplateRenderMixin, SharedObjectQuerySetMixin


class ExtrasRootView(APIRootView):
    """
    Extras API root view
    """
    def get_view_name(self):
        return 'Extras'


#
# EventRules
#

class EventRuleViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = EventRule.objects.all()
    serializer_class = serializers.EventRuleSerializer
    filterset_class = filtersets.EventRuleFilterSet


#
# Webhooks
#

class WebhookViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Webhook.objects.all()
    serializer_class = serializers.WebhookSerializer
    filterset_class = filtersets.WebhookFilterSet


#
# Custom fields
#

class CustomFieldViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = CustomField.objects.select_related('choice_set')
    serializer_class = serializers.CustomFieldSerializer
    filterset_class = filtersets.CustomFieldFilterSet


class CustomFieldChoiceSetViewSet(NetBoxModelViewSet):
    queryset = CustomFieldChoiceSet.objects.all()
    serializer_class = serializers.CustomFieldChoiceSetSerializer
    filterset_class = filtersets.CustomFieldChoiceSetFilterSet

    @action(detail=True)
    def choices(self, request, pk):
        """
        Provides an endpoint to iterate through each choice in a set.
        """
        choiceset = get_object_or_404(self.queryset, pk=pk)
        choices = choiceset.choices

        # Enable filtering
        if q := request.GET.get('q'):
            q = q.lower()
            choices = [c for c in choices if q in c[0].lower() or q in c[1].lower()]

        # Paginate data
        if page := self.paginate_queryset(choices):
            data = [
                {'id': c[0], 'display': c[1]} for c in page
            ]
        else:
            data = []

        return self.get_paginated_response(data)


#
# Custom links
#

class CustomLinkViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = CustomLink.objects.all()
    serializer_class = serializers.CustomLinkSerializer
    filterset_class = filtersets.CustomLinkFilterSet


#
# Export templates
#

class ExportTemplateViewSet(SyncedDataMixin, NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = ExportTemplate.objects.all()
    serializer_class = serializers.ExportTemplateSerializer
    filterset_class = filtersets.ExportTemplateFilterSet


#
# Saved filters
#

class SavedFilterViewSet(SharedObjectQuerySetMixin, NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = SavedFilter.objects.all()
    serializer_class = serializers.SavedFilterSerializer
    filterset_class = filtersets.SavedFilterFilterSet


#
# Table Configs
#

class TableConfigViewSet(SharedObjectQuerySetMixin, NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = TableConfig.objects.all()
    serializer_class = serializers.TableConfigSerializer
    filterset_class = filtersets.TableConfigFilterSet


#
# Bookmarks
#

class BookmarkViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Bookmark.objects.all()
    serializer_class = serializers.BookmarkSerializer
    filterset_class = filtersets.BookmarkFilterSet


#
# Notifications & subscriptions
#

class NotificationViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer


class NotificationGroupViewSet(NetBoxModelViewSet):
    queryset = NotificationGroup.objects.all()
    serializer_class = serializers.NotificationGroupSerializer


class SubscriptionViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer


#
# Tags
#

class TagViewSet(NetBoxModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filterset_class = filtersets.TagFilterSet


class TaggedItemViewSet(RetrieveModelMixin, ListModelMixin, BaseViewSet):
    queryset = TaggedItem.objects.prefetch_related(
        'content_type', 'content_object', 'tag'
    ).order_by('tag__weight', 'tag__name')
    serializer_class = serializers.TaggedItemSerializer
    filterset_class = filtersets.TaggedItemFilterSet


#
# Image attachments
#

class ImageAttachmentViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = ImageAttachment.objects.all()
    serializer_class = serializers.ImageAttachmentSerializer
    filterset_class = filtersets.ImageAttachmentFilterSet


#
# Journal entries
#

class JournalEntryViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = JournalEntry.objects.all()
    serializer_class = serializers.JournalEntrySerializer
    filterset_class = filtersets.JournalEntryFilterSet


#
# Config contexts
#

class ConfigContextProfileViewSet(SyncedDataMixin, NetBoxModelViewSet):
    queryset = ConfigContextProfile.objects.all()
    serializer_class = serializers.ConfigContextProfileSerializer
    filterset_class = filtersets.ConfigContextProfileFilterSet


class ConfigContextViewSet(SyncedDataMixin, NetBoxModelViewSet):
    queryset = ConfigContext.objects.all()
    serializer_class = serializers.ConfigContextSerializer
    filterset_class = filtersets.ConfigContextFilterSet


#
# Config templates
#

class ConfigTemplateViewSet(SyncedDataMixin, ConfigTemplateRenderMixin, NetBoxModelViewSet):
    queryset = ConfigTemplate.objects.all()
    serializer_class = serializers.ConfigTemplateSerializer
    filterset_class = filtersets.ConfigTemplateFilterSet

    def get_permissions(self):
        # For render action, check only token write ability (not model permissions)
        if self.action == 'render':
            return [TokenWritePermission()]
        return super().get_permissions()

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiResponse(
                response=serializers.RenderedConfigSerializer,
                description=_(
                    "The rendered config template. When the client requests `text/plain`, the raw "
                    "rendered content is returned in place of the JSON object."
                ),
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description=_("An error occurred while rendering the config template."),
            ),
        },
    )
    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer, TextRenderer])
    def render(self, request, pk):
        """
        Render a ConfigTemplate using the context data provided (if any). The request body should be a
        mapping of context variables to make available to the template. If the client requests "text/plain"
        data, return the raw rendered content, rather than serialized JSON.
        """
        # Override restrict() on the default queryset to enforce the render & view actions
        self.queryset = self.queryset.model.objects.restrict(request.user, 'render').restrict(request.user, 'view')
        configtemplate = self.get_object()

        context = request.data

        return self.render_configtemplate(request, configtemplate, context)


#
# Scripts
#

class ScriptModuleViewSet(ObjectValidationMixin, CreateModelMixin, UpdateModelMixin, BaseViewSet):
    queryset = ScriptModule.objects.filter(file_root=ManagedFileRootPathChoices.SCRIPTS)
    serializer_class = serializers.ScriptModuleSerializer
    lookup_value_regex = '[^/]+'  # Allow dots

    def get_object(self):
        """
        Retrieve a ScriptModule by numeric ID or by file name (e.g. my_script.py).
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, '')

        # Support lookup by numeric PK or by file_path. Treat all-decimal values as PKs
        # to preserve normal detail-route behavior; otherwise resolve the value as a
        # script module filename, e.g. "myscript.py".
        if lookup.isdecimal():
            obj = get_object_or_404(queryset, pk=int(lookup))
        else:
            obj = get_object_or_404(queryset, file_path=lookup)

        self.check_object_permissions(self.request, obj)
        return obj


class ScriptViewSet(ListModelMixin, RetrieveModelMixin, BaseViewSet):
    # Individual scripts are created, modified, and deleted through their module (see ScriptModuleViewSet),
    # so the standard write actions are intentionally omitted here. Only listing/retrieving a script (GET)
    # and running one (POST to the detail route) are supported.
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    queryset = Script.objects.all()
    serializer_class = serializers.ScriptSerializer
    filterset_class = filtersets.ScriptFilterSet

    lookup_value_regex = '[^/]+'  # Allow dots

    def get_serializer(self, *args, **kwargs):
        # A POST to the detail route runs the script, taking ScriptInputSerializer as its request body.
        # (This is keyed on the request method rather than on self.action, which is unset when generating
        # OPTIONS metadata.) ScriptInputSerializer is instantiated directly rather than via BaseViewSet,
        # which would pass it the fields/omit kwargs supported only by BaseModelSerializer.
        if getattr(self.request, 'method', None) == 'POST':
            kwargs.setdefault('context', self.get_serializer_context())
            return serializers.ScriptInputSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # ScriptInputSerializer resolves its field defaults and validates scheduling against the script
        # being run (set by run() below).
        context['script'] = getattr(self, 'script', None)

        return context

    def _get_script(self, pk):
        # Retrieve the script by ID if the PK is all decimal digits. (isdecimal() rather than isnumeric(),
        # as the latter also matches characters which cannot be cast to an integer.)
        if pk.isdecimal():
            try:
                pk = int(pk)
            except ValueError:
                raise Http404
            return get_object_or_404(self.queryset, pk=pk)

        # Default to retrieval by module & name
        try:
            module_name, script_name = pk.split('.', maxsplit=1)
        except ValueError:
            raise Http404

        return get_object_or_404(self.queryset, module__file_path=f'{module_name}.py', name=script_name)

    def retrieve(self, request, pk, **kwargs):
        script = self._get_script(pk)
        serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

        return Response(serializer.data)

    @extend_schema(
        operation_id='extras_scripts_run',
        request=serializers.ScriptInputSerializer,
        responses={
            200: OpenApiResponse(
                response=serializers.ScriptDetailSerializer,
                description=_("The script has been enqueued for execution."),
            ),
        },
    )
    def run(self, request, pk, **kwargs):
        """
        Run a Script identified by its numeric PK or module & name and return the pending Job as the result
        """
        # Bound to POST on the detail route by ScriptRouter

        # Reject read-only tokens before resolving the script, so that an insufficient token is always
        # reported as such. (Not via TokenWritePermission, which permits token auth only.)
        if isinstance(request.auth, Token) and not request.auth.write_enabled:
            raise PermissionDenied(_("This token does not permit write operations (running a script)."))

        # An unauthenticated user can never run a script; report that explicitly, as restrict() below would
        # match no scripts and yield a misleading 404.
        if not request.user.is_authenticated:
            raise PermissionDenied(_("This user does not have permission to run this script."))

        # Running a script is a 'run' operation (not the 'add' that BaseViewSet maps to POST), so restrict
        # the QuerySet on 'run' before resolving the script. A script the user cannot run yields a 404.
        self.queryset = self.queryset.model.objects.restrict(request.user, 'run')
        self.script = script = self._get_script(pk)

        # A script whose Python class cannot be resolved (e.g. its module has been modified or the script has
        # been deleted, retaining the record for its jobs) cannot be run
        if not script.is_executable or script.python_class is None:
            raise ValidationError(_("This script is not currently executable."))

        input_serializer = self.get_serializer(data=request.data)

        # Check that at least one RQ worker is running
        if not any_workers_for_queue('default'):
            raise RQWorkerNotRunningException()

        if input_serializer.is_valid():
            ScriptJob.enqueue(
                instance=script,
                user=request.user,
                data=input_serializer.data['data'],
                request=copy_safe_request(request),
                commit=input_serializer.data['commit'],
                job_timeout=script.python_class.job_timeout,
                schedule_at=input_serializer.validated_data.get('schedule_at'),
                interval=input_serializer.validated_data.get('interval'),
                notifications=input_serializer.validated_data.get('notifications'),
            )
            serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

            return Response(serializer.data)

        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# User dashboard
#

class DashboardView(RetrieveUpdateDestroyAPIView):
    queryset = Dashboard.objects.all()
    serializer_class = serializers.DashboardSerializer

    def get_object(self):
        return Dashboard.objects.filter(user=self.request.user).first()
