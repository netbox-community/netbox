from rest_framework import serializers

from core.api.serializers import JobSerializer
from ndx.choices import ImportRecordSourceChoices
from ndx.models import Enrichment, ImportRecord, Provenance
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import BaseModelSerializer

__all__ = (
    'CatalogImportRequestSerializer',
    'CatalogImportResultSerializer',
    'EnrichmentSerializer',
    'ImportRecordSerializer',
    'ProvenanceSerializer',
    'SyncStatusSerializer',
)


class ProvenanceSerializer(BaseModelSerializer):

    class Meta:
        model = Provenance
        fields = [
            'id', 'display', 'field', 'source', 'type', 'confidence', 'retrieved', 'note', 'created', 'last_updated',
        ]
        read_only_fields = fields
        brief_fields = ('id', 'display', 'field', 'source', 'confidence')


class EnrichmentSerializer(BaseModelSerializer):
    import_record = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    provenance = ProvenanceSerializer(
        many=True,
        read_only=True,
        nested=True,
        fields=('id', 'field', 'source', 'type', 'confidence', 'retrieved', 'note')
    )

    class Meta:
        model = Enrichment
        fields = [
            'id', 'url', 'display', 'import_record', 'tdp_watts', 'airflow_cfm', 'cooling_type',
            'ga_date', 'eol_announced', 'eos_date', 'eosw_date', 'eosec_date', 'last_support_date',
            'max_operating_temp_c', 'min_operating_temp_c', 'max_operating_humidity', 'min_operating_humidity',
            'max_operating_altitude_m', 'ingress_protection', 'mtbf_hours', 'typical_power_draw_watts',
            'max_power_draw_watts', 'noise_level_dba', 'power_capacity_watts', 'nos', 'nos_family', 'api_types',
            'snmp_sys_object_id', 'snmp_vendor_oid_prefix', 'has_lifecycle', 'has_thermal', 'has_environmental',
            'has_operational', 'has_platform', 'has_snmp', 'extensions', 'provenance', 'created', 'last_updated',
        ]
        read_only_fields = fields
        brief_fields = ('id', 'url', 'display', 'import_record')


class ImportRecordSerializer(BaseModelSerializer):
    object_type = ContentTypeField(
        read_only=True
    )
    object = GFKSerializerField(
        read_only=True,
        allow_missing_serializer=True
    )
    source = ChoiceField(
        choices=ImportRecordSourceChoices,
        read_only=True
    )
    enrichment = EnrichmentSerializer(
        nested=True,
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ImportRecord
        fields = [
            'id', 'url', 'display_url', 'display', 'object_type', 'object_id', 'object', 'ndx_id', 'entry_type',
            'vendor_slug', 'source', 'checksum', 'update_available', 'last_imported', 'enrichment', 'created',
            'last_updated',
        ]
        read_only_fields = fields
        brief_fields = ('id', 'url', 'display', 'ndx_id', 'object_type', 'object_id', 'update_available')


#
# Catalog operations
#

class CatalogImportRequestSerializer(serializers.Serializer):
    ndx_ids = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        help_text='Catalog entries to import, identified as "<vendor_slug>/<slug>"'
    )


class CatalogImportResultSerializer(serializers.Serializer):
    ndx_id = serializers.CharField()
    entry_type = serializers.CharField()
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=('created', 'updated', 'skipped', 'failed'))
    object_type = serializers.CharField(allow_null=True)
    object_id = serializers.IntegerField(allow_null=True)
    message = serializers.CharField()
    errors = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())
    component_errors = serializers.ListField(child=serializers.CharField())
    image_errors = serializers.ListField(child=serializers.CharField())


class SyncStatusSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    imported_count = serializers.IntegerField()
    updates_available = serializers.IntegerField()
    last_sync = JobSerializer(nested=True, allow_null=True, fields=(
        'id', 'url', 'display', 'status', 'created', 'completed', 'data', 'error',
    ))
