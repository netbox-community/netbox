from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from django_rq.queues import get_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rq import Worker

from core.models import ObjectType
from extras import filtersets
from extras.models import *
from extras.jobs import ScriptJob
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.features import SyncedDataMixin
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.exceptions import RQWorkerNotRunningException
from utilities.request import copy_safe_request
from . import serializers
from .mixins import ConfigTemplateRenderMixin


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

class SavedFilterViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = SavedFilter.objects.all()
    serializer_class = serializers.SavedFilterSerializer
    filterset_class = filtersets.SavedFilterFilterSet


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

    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer, TextRenderer])
    def render(self, request, pk):
        """
        Render a ConfigTemplate using the context data provided (if any). If the client requests "text/plain" data,
        return the raw rendered content, rather than serialized JSON.
        """
        configtemplate = self.get_object()
        context = request.data

        return self.render_configtemplate(request, configtemplate, context)


#
# Scripts
#

class ScriptViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    queryset = Script.objects.prefetch_related('jobs')
    serializer_class = serializers.ScriptSerializer
    filterset_class = filtersets.ScriptFilterSet

    _ignore_model_permissions = True
    lookup_value_regex = '[^/]+'  # Allow dots

    def _get_script(self, pk):
        # If pk is numeric, retrieve script by ID
        if pk.isnumeric():
            return get_object_or_404(self.queryset, pk=pk)

        # Default to retrieval by module & name
        try:
            module_name, script_name = pk.split('.', maxsplit=1)
        except ValueError:
            raise Http404
        return get_object_or_404(self.queryset, module__file_path=f'{module_name}.py', name=script_name)

    def retrieve(self, request, pk):
        script = self._get_script(pk)
        serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

        return Response(serializer.data)

    def post(self, request, pk):
        """
        Run a Script identified by its numeric PK or module & name and return the pending Job as the result
        """
        if not request.user.has_perm('extras.run_script'):
            raise PermissionDenied("This user does not have permission to run scripts.")

        script = self._get_script(pk)
        input_serializer = serializers.ScriptInputSerializer(
            data=request.data,
            context={'script': script}
        )

        # Check that at least one RQ worker is running
        if not Worker.count(get_connection('default')):
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
                interval=input_serializer.validated_data.get('interval')
            )
            serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

            return Response(serializer.data)

        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# Object types
#

class ObjectTypeViewSet(ReadOnlyModelViewSet):
    """
    Read-only list of ObjectTypes.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    queryset = ObjectType.objects.order_by('app_label', 'model')
    serializer_class = serializers.ObjectTypeSerializer
    filterset_class = filtersets.ObjectTypeFilterSet


#
# User dashboard
#

class DashboardView(RetrieveUpdateDestroyAPIView):
    queryset = Dashboard.objects.all()
    serializer_class = serializers.DashboardSerializer

    def get_object(self):
        return Dashboard.objects.filter(user=self.request.user).first()
