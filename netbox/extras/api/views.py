from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django_rq.queues import get_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rq import Worker

from extras import filtersets
from extras.choices import JobResultStatusChoices
from extras.models import *
from extras.models import CustomField
from extras.reports import get_report, run_report
from extras.scripts import get_script, run_script
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.features import SyncedDataMixin
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.exceptions import RQWorkerNotRunningException
from utilities.utils import copy_safe_request, count_related
from . import serializers
from .mixins import ConfigTemplateRenderMixin


class ExtrasRootView(APIRootView):
    """
    Extras API root view
    """
    def get_view_name(self):
        return 'Extras'


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
    queryset = CustomField.objects.all()
    serializer_class = serializers.CustomFieldSerializer
    filterset_class = filtersets.CustomFieldFilterSet


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
    queryset = ExportTemplate.objects.prefetch_related('data_source', 'data_file')
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
# Tags
#

class TagViewSet(NetBoxModelViewSet):
    queryset = Tag.objects.annotate(
        tagged_items=count_related(TaggedItem, 'tag')
    )
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
    queryset = ConfigContext.objects.prefetch_related(
        'regions', 'site_groups', 'sites', 'locations', 'roles', 'platforms', 'tenant_groups', 'tenants', 'data_source',
        'data_file',
    )
    serializer_class = serializers.ConfigContextSerializer
    filterset_class = filtersets.ConfigContextFilterSet


#
# Config templates
#

class ConfigTemplateViewSet(SyncedDataMixin, ConfigTemplateRenderMixin, NetBoxModelViewSet):
    queryset = ConfigTemplate.objects.prefetch_related('data_source', 'data_file')
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
# Reports
#

class ReportViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    _ignore_model_permissions = True
    exclude_from_schema = True
    lookup_value_regex = '[^/]+'  # Allow dots

    def _retrieve_report(self, pk):

        # Read the PK as "<module>.<report>"
        if '.' not in pk:
            raise Http404
        module_name, report_name = pk.split('.', maxsplit=1)

        # Raise a 404 on an invalid Report module/name
        report = get_report(module_name, report_name)
        if report is None:
            raise Http404

        return report

    def list(self, request):
        """
        Compile all reports and their related results (if any). Result data is deferred in the list view.
        """
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=report_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('name', '-created').distinct('name').defer('data')
        }

        report_list = []
        for report_module in ReportModule.objects.restrict(request.user):
            report_list.extend([report() for report in report_module.reports.values()])

        # Attach JobResult objects to each report (if any)
        for report in report_list:
            report.result = results.get(report.full_name, None)

        serializer = serializers.ReportSerializer(report_list, many=True, context={
            'request': request,
        })

        return Response(serializer.data)

    def retrieve(self, request, pk):
        """
        Retrieve a single Report identified as "<module>.<report>".
        """

        # Retrieve the Report and JobResult, if any.
        report = self._retrieve_report(pk)
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        report.result = JobResult.objects.filter(
            obj_type=report_content_type,
            name=report.full_name,
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        serializer = serializers.ReportDetailSerializer(report, context={
            'request': request
        })

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def run(self, request, pk):
        """
        Run a Report identified as "<module>.<script>" and return the pending JobResult as the result
        """
        # Check that the user has permission to run reports.
        if not request.user.has_perm('extras.run_report'):
            raise PermissionDenied("This user does not have permission to run reports.")

        # Check that at least one RQ worker is running
        if not Worker.count(get_connection('default')):
            raise RQWorkerNotRunningException()

        # Retrieve and run the Report. This will create a new JobResult.
        report = self._retrieve_report(pk)
        input_serializer = serializers.ReportInputSerializer(data=request.data)

        if input_serializer.is_valid():
            job_result = JobResult.enqueue_job(
                run_report,
                name=report.full_name,
                obj_type=ContentType.objects.get_for_model(Report),
                user=request.user,
                job_timeout=report.job_timeout,
                schedule_at=input_serializer.validated_data.get('schedule_at'),
                interval=input_serializer.validated_data.get('interval')
            )
            report.result = job_result

            serializer = serializers.ReportDetailSerializer(report, context={'request': request})

            return Response(serializer.data)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# Scripts
#

class ScriptViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    _ignore_model_permissions = True
    exclude_from_schema = True
    lookup_value_regex = '[^/]+'  # Allow dots

    def _get_script(self, pk):
        module_name, script_name = pk.split('.', maxsplit=1)
        script = get_script(module_name, script_name)
        if script is None:
            raise Http404
        return script

    def list(self, request):

        script_content_type = ContentType.objects.get(app_label='extras', model='script')
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=script_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('name', '-created').distinct('name').defer('data')
        }

        script_list = []
        for script_module in ScriptModule.objects.restrict(request.user):
            script_list.extend(script_module.scripts.values())

        # Attach JobResult objects to each script (if any)
        for script in script_list:
            script.result = results.get(script.full_name, None)

        serializer = serializers.ScriptSerializer(script_list, many=True, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk):
        script = self._get_script(pk)
        script_content_type = ContentType.objects.get(app_label='extras', model='script')
        script.result = JobResult.objects.filter(
            obj_type=script_content_type,
            name=script.full_name,
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).first()
        serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

        return Response(serializer.data)

    def post(self, request, pk):
        """
        Run a Script identified as "<module>.<script>" and return the pending JobResult as the result
        """

        if not request.user.has_perm('extras.run_script'):
            raise PermissionDenied("This user does not have permission to run scripts.")

        script = self._get_script(pk)()
        input_serializer = serializers.ScriptInputSerializer(data=request.data)

        # Check that at least one RQ worker is running
        if not Worker.count(get_connection('default')):
            raise RQWorkerNotRunningException()

        if input_serializer.is_valid():
            job_result = JobResult.enqueue_job(
                run_script,
                name=script.full_name,
                obj_type=ContentType.objects.get_for_model(Script),
                user=request.user,
                data=input_serializer.data['data'],
                request=copy_safe_request(request),
                commit=input_serializer.data['commit'],
                job_timeout=script.job_timeout,
                schedule_at=input_serializer.validated_data.get('schedule_at'),
                interval=input_serializer.validated_data.get('interval')
            )
            script.result = job_result
            serializer = serializers.ScriptDetailSerializer(script, context={'request': request})

            return Response(serializer.data)

        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# Change logging
#

class ObjectChangeViewSet(ReadOnlyModelViewSet):
    """
    Retrieve a list of recent changes.
    """
    metadata_class = ContentTypeMetadata
    queryset = ObjectChange.objects.prefetch_related('user')
    serializer_class = serializers.ObjectChangeSerializer
    filterset_class = filtersets.ObjectChangeFilterSet


#
# Job Results
#

class JobResultViewSet(ReadOnlyModelViewSet):
    """
    Retrieve a list of job results
    """
    queryset = JobResult.objects.prefetch_related('user')
    serializer_class = serializers.JobResultSerializer
    filterset_class = filtersets.JobResultFilterSet


#
# ContentTypes
#

class ContentTypeViewSet(ReadOnlyModelViewSet):
    """
    Read-only list of ContentTypes. Limit results to ContentTypes pertinent to NetBox objects.
    """
    permission_classes = (IsAuthenticated,)
    queryset = ContentType.objects.order_by('app_label', 'model')
    serializer_class = serializers.ContentTypeSerializer
    filterset_class = filtersets.ContentTypeFilterSet


#
# User dashboard
#

class DashboardView(RetrieveUpdateDestroyAPIView):
    queryset = Dashboard.objects.all()
    serializer_class = serializers.DashboardSerializer

    def get_object(self):
        return Dashboard.objects.filter(user=self.request.user).first()
