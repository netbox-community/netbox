from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework.viewsets import ViewSet

from core.api.serializers import JobSerializer
from ndx import filtersets
from ndx.catalog import annotate_entries
from ndx.client import DISABLED, NOT_FOUND, RATE_LIMITED, NDXError, error_of, get_client
from ndx.constants import CATALOG_MAX_PAGE_SIZE, IMPORT_BACKGROUND_THRESHOLD
from ndx.importers import get_vendor_checksums, import_entries
from ndx.jobs import ImportJob, SyncJob, get_active_sync_job, get_last_sync_job
from ndx.models import Enrichment, ImportRecord
from ndx.utils import is_enabled
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from users.models import Token

from . import serializers

__all__ = (
    'CatalogViewSet',
    'EnrichmentViewSet',
    'ImportRecordViewSet',
    'NDXRootView',
    'SyncViewSet',
)

CATALOG_DEFAULT_PAGE_SIZE = 50

# Entry fields retained when ?brief is specified
CATALOG_BRIEF_FIELDS = ('vendor_slug', 'slug', 'ndx_id', 'manufacturer', 'model', 'part_number', 'type')


class NDXRootView(APIRootView):
    """
    NDX API root view
    """
    def get_view_name(self):
        return 'NDX'


#
# Viewsets
#

class ImportRecordViewSet(NetBoxModelViewSet):
    # Import records are created and updated only by importing catalog entries
    http_method_names = ['get', 'delete', 'head', 'options', 'trace']
    queryset = ImportRecord.objects.all()
    serializer_class = serializers.ImportRecordSerializer
    filterset_class = filtersets.ImportRecordFilterSet


class EnrichmentViewSet(NetBoxReadOnlyModelViewSet):
    queryset = Enrichment.objects.all()
    serializer_class = serializers.EnrichmentSerializer
    filterset_class = filtersets.EnrichmentFilterSet


#
# Catalog operations
#

class NDXPermission(BasePermission):
    """
    Permit users who may view NDX import records. Unsafe requests made with a token require it to be write-enabled.
    """
    def has_permission(self, request, view):
        if isinstance(request.auth, Token) and request.method not in SAFE_METHODS and not request.auth.write_enabled:
            return False
        return request.user.is_authenticated and request.user.has_perm('ndx.view_importrecord')


def error_response(error):
    """
    Return an API response for a failed NDX API request. Errors which reflect the instance's configuration or
    connectivity (rather than the client's request) are reported as 503.
    """
    status_code = {
        NOT_FOUND: status.HTTP_404_NOT_FOUND,
        RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
    }.get(error.kind, status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'detail': str(error.message)}, status=status_code)


def get_int_param(request, name, default):
    try:
        return max(int(request.query_params.get(name, default)), 0)
    except ValueError:
        return default


def select_fields(request, entry):
    """
    Apply the fields, omit, or brief query parameters to a catalog entry.
    """
    params = request.query_params
    if fields := params.get('fields'):
        return {k: v for k, v in entry.items() if k in fields.split(',')}
    if omit := params.get('omit'):
        return {k: v for k, v in entry.items() if k not in omit.split(',')}
    if params.get('brief', '').lower() in ('true', '1'):
        return {k: v for k, v in entry.items() if k in CATALOG_BRIEF_FIELDS}
    return entry


def serialize_entry(entry):
    """
    Replace the import record annotated on a catalog entry with its ID.
    """
    record = entry.pop('import_record', None)
    entry['import_record_id'] = record.pk if record else None
    return entry


class CatalogViewSet(ViewSet):
    """
    Search the NDX catalog and import entries from it.
    """
    permission_classes = [NDXPermission]
    lookup_url_kwarg = 'ndx_id'
    lookup_value_regex = r'[^/]+/[^/]+'

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.client = get_client()

    def check_enabled(self):
        if not is_enabled():
            return error_response(NDXError(kind=DISABLED))
        return None

    @extend_schema(
        operation_id='ndx_catalog_list',
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, description='Search terms'),
            OpenApiParameter('vendor', OpenApiTypes.STR, description='Vendor slug'),
            OpenApiParameter('type', OpenApiTypes.STR, description='Entry type (e.g. device-type)'),
            OpenApiParameter('has_lifecycle', OpenApiTypes.BOOL),
            OpenApiParameter('has_thermal', OpenApiTypes.BOOL),
            OpenApiParameter('limit', OpenApiTypes.INT, description=(
                f'Number of results to return per page (maximum {CATALOG_MAX_PAGE_SIZE})'
            )),
            OpenApiParameter('offset', OpenApiTypes.INT, description='The initial index from which to return results'),
            OpenApiParameter('brief', OpenApiTypes.BOOL),
            OpenApiParameter('fields', OpenApiTypes.STR),
            OpenApiParameter('omit', OpenApiTypes.STR),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def list(self, request):
        if response := self.check_enabled():
            return response

        params = request.query_params
        limit = min(get_int_param(request, 'limit', CATALOG_DEFAULT_PAGE_SIZE) or CATALOG_DEFAULT_PAGE_SIZE,
                    CATALOG_MAX_PAGE_SIZE)
        offset = get_int_param(request, 'offset', 0)
        filters = {
            name: 'true' for name in ('has_lifecycle', 'has_thermal')
            if params.get(name, '').lower() in ('true', '1')
        }
        results = self.client.search(
            q=params.get('q') or None,
            vendor=params.get('vendor') or None,
            entry_type=params.get('type') or None,
            offset=offset,
            limit=limit,
            **filters,
        )
        if error := error_of(results):
            return error_response(error)

        count = results.get('total') or 0
        url = request.build_absolute_uri()
        next_url = None
        if offset + limit < count:
            next_url = replace_query_param(replace_query_param(url, 'limit', limit), 'offset', offset + limit)
        previous_url = None
        if offset > 0:
            if offset - limit <= 0:
                previous_url = remove_query_param(url, 'offset')
            else:
                previous_url = replace_query_param(url, 'offset', offset - limit)

        entries = annotate_entries(results.get('results') or [], request.user)
        return Response({
            'count': count,
            'next': next_url,
            'previous': previous_url,
            'results': [select_fields(request, serialize_entry(entry)) for entry in entries],
        })

    @extend_schema(
        operation_id='ndx_catalog_retrieve',
        parameters=[
            OpenApiParameter(
                'ndx_id', OpenApiTypes.STR, OpenApiParameter.PATH, description='Catalog entry ("<vendor_slug>/<slug>")'
            ),
            OpenApiParameter('brief', OpenApiTypes.BOOL),
            OpenApiParameter('fields', OpenApiTypes.STR),
            OpenApiParameter('omit', OpenApiTypes.STR),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def retrieve(self, request, ndx_id):
        if response := self.check_enabled():
            return response

        vendor_slug, slug = ndx_id.split('/', 1)
        entry = self.client.get_entry(vendor_slug, slug)
        if error := error_of(entry):
            return error_response(error)
        if not entry:
            return error_response(NDXError(kind=NOT_FOUND))
        entry = annotate_entries([dict(entry)], request.user)[0]
        return Response(select_fields(request, serialize_entry(entry)))

    @extend_schema(
        operation_id='ndx_catalog_import',
        request=serializers.CatalogImportRequestSerializer,
        parameters=[
            OpenApiParameter('background', OpenApiTypes.BOOL, description=(
                f'Import the entries in a background job (always the case for more than '
                f'{IMPORT_BACKGROUND_THRESHOLD} entries)'
            )),
        ],
        responses={
            200: serializers.CatalogImportResultSerializer(many=True),
            202: JobSerializer,
        },
    )
    @action(detail=False, methods=['post'], url_path='import')
    def run_import(self, request):
        """
        Import entries from the catalog. Entries are imported immediately, unless the `background` query parameter
        is set or the number of entries exceeds IMPORT_BACKGROUND_THRESHOLD, in which case a background job is
        queued.
        """
        if response := self.check_enabled():
            return response

        serializer = serializers.CatalogImportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ndx_ids = serializer.validated_data['ndx_ids']

        background = request.query_params.get('background', '').lower() in ('true', '1')
        if background or len(ndx_ids) > IMPORT_BACKGROUND_THRESHOLD:
            job = ImportJob.enqueue_for(request._request, ndx_ids)
            return Response(
                JobSerializer(job, context={'request': request}).data,
                status=status.HTTP_202_ACCEPTED
            )

        checksums, error = get_vendor_checksums(self.client)
        if error is not None:
            return error_response(error)
        results = import_entries(ndx_ids, request.user, client=self.client, checksums=checksums)

        return Response([result.serialize() for result in results])


class SyncViewSet(ViewSet):
    """
    Retrieve the status of catalog synchronization, or queue a sync job.
    """
    permission_classes = [NDXPermission]

    @extend_schema(operation_id='ndx_sync_status', responses={200: serializers.SyncStatusSerializer})
    def list(self, request):
        records = ImportRecord.objects.restrict(request.user, 'view')
        job = get_last_sync_job()
        return Response({
            'enabled': is_enabled(),
            'imported_count': records.count(),
            'updates_available': records.filter(update_available=True).count(),
            'last_sync': JobSerializer(
                job,
                nested=True,
                fields=('id', 'url', 'display', 'status', 'created', 'completed', 'data', 'error'),
                context={'request': request},
            ).data if job else None,
        })

    @extend_schema(operation_id='ndx_sync_create', request=None, responses={202: JobSerializer})
    def create(self, request):
        if not is_enabled():
            return error_response(NDXError(kind=DISABLED))
        if not request.user.has_perm('ndx.sync_importrecord'):
            raise PermissionDenied(_("This user does not have permission to synchronize with the NDX catalog."))
        # Return the sync job already in progress, if any
        job = get_active_sync_job() or SyncJob.enqueue(user=request.user)
        return Response(JobSerializer(job, context={'request': request}).data, status=status.HTTP_202_ACCEPTED)
