from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels
from utilities.data import resolve_attr_path

__all__ = (
    'EnrichmentEnvironmentalPanel',
    'EnrichmentExtensionsPanel',
    'EnrichmentLifecyclePanel',
    'EnrichmentPlatformPanel',
    'EnrichmentPowerThermalPanel',
    'ImportRecordAttributesPanel',
    'ImportRecordPanel',
)


class ImportRecordAttributesPanel(panels.ObjectAttributesPanel):
    title = _('Import Record')
    object = attrs.GenericForeignKeyAttr('object', linkify=True)
    ndx_id = attrs.TextAttr('ndx_id', label=_('NDX ID'), style='font-monospace', copy_button=True)
    entry_type = attrs.TextAttr('entry_type', label=_('Entry type'))
    vendor_slug = attrs.TextAttr('vendor_slug', label=_('Vendor slug'))
    source = attrs.ChoiceAttr('source')
    checksum = attrs.TextAttr('checksum', style='font-monospace')
    update_available = attrs.BooleanAttr('update_available', label=_('Update available'))
    last_imported = attrs.DateTimeAttr('last_imported', label=_('Last imported'))


class EnrichmentPanel(panels.ObjectAttributesPanel):
    """
    Base class for panels displaying an import record's enrichment data (if any).
    """
    accessor = 'object.enrichment'

    def get_context(self, context):
        if resolve_attr_path(context, self.accessor) is None:
            return {'object': None}
        return super().get_context(context)

    def should_render(self, context):
        return context.get('object') is not None


class EnrichmentLifecyclePanel(EnrichmentPanel):
    title = _('Lifecycle')
    ga_date = attrs.TextAttr('ga_date', label=_('General availability'))
    eol_announced = attrs.TextAttr('eol_announced', label=_('End of life announced'))
    eos_date = attrs.TextAttr('eos_date', label=_('End of sale'))
    eosw_date = attrs.TextAttr('eosw_date', label=_('End of software maintenance'))
    eosec_date = attrs.TextAttr('eosec_date', label=_('End of security updates'))
    last_support_date = attrs.TextAttr('last_support_date', label=_('Last date of support'))


class EnrichmentPowerThermalPanel(EnrichmentPanel):
    title = _('Power & Thermal')
    typical_power_draw_watts = attrs.NumericAttr('typical_power_draw_watts', label=_('Typical power draw (W)'))
    max_power_draw_watts = attrs.NumericAttr('max_power_draw_watts', label=_('Maximum power draw (W)'))
    power_capacity_watts = attrs.NumericAttr('power_capacity_watts', label=_('Power capacity (W)'))
    tdp_watts = attrs.NumericAttr('tdp_watts', label=_('TDP (W)'))
    airflow_cfm = attrs.NumericAttr('airflow_cfm', label=_('Airflow (CFM)'))
    cooling_type = attrs.TextAttr('cooling_type', label=_('Cooling type'))
    noise_level_dba = attrs.NumericAttr('noise_level_dba', label=_('Noise level (dBA)'))


class EnrichmentEnvironmentalPanel(EnrichmentPanel):
    title = _('Environmental')
    min_operating_temp_c = attrs.NumericAttr('min_operating_temp_c', label=_('Minimum temperature (°C)'))
    max_operating_temp_c = attrs.NumericAttr('max_operating_temp_c', label=_('Maximum temperature (°C)'))
    min_operating_humidity = attrs.NumericAttr('min_operating_humidity', label=_('Minimum humidity (%)'))
    max_operating_humidity = attrs.NumericAttr('max_operating_humidity', label=_('Maximum humidity (%)'))
    max_operating_altitude_m = attrs.NumericAttr('max_operating_altitude_m', label=_('Maximum altitude (m)'))
    ingress_protection = attrs.TextAttr('ingress_protection', label=_('Ingress protection'))
    mtbf_hours = attrs.NumericAttr('mtbf_hours', label=_('MTBF (hours)'))


class EnrichmentPlatformPanel(EnrichmentPanel):
    title = _('Platform')
    nos = attrs.TextAttr('nos', label=_('Network OS'))
    nos_family = attrs.TextAttr('nos_family', label=_('Network OS family'))
    api_types = attrs.ArrayAttr('api_types', label=_('API types'))
    snmp_sys_object_id = attrs.TextAttr(
        'snmp_sys_object_id', label=_('SNMP sysObjectID'), style='font-monospace', copy_button=True
    )
    snmp_vendor_oid_prefix = attrs.TextAttr(
        'snmp_vendor_oid_prefix', label=_('SNMP vendor OID prefix'), style='font-monospace'
    )


class EnrichmentExtensionsPanel(panels.JSONPanel):
    """
    Displays the protocol extension data (if any) of an import record's enrichment.
    """
    def __init__(self, **kwargs):
        super().__init__('extensions', accessor='object.enrichment', title=_('Extensions'), **kwargs)

    def should_render(self, context):
        return bool(context.get('data'))


class ImportRecordPanel(panels.ObjectPanel):
    """
    Summarizes the NDX import record (if any) for an object such as a device type.
    """
    template_name = 'ndx/panels/import_record.html'
    title = _('NetBox Data Exchange')

    def get_context(self, context):
        from ndx.constants import UPGRADE_URL
        from ndx.jobs import get_last_sync_job
        from ndx.models import ImportRecord
        from ndx.utils import get_web_url, is_enabled

        ctx = super().get_context(context)
        obj = ctx['object']
        record = ImportRecord.objects.restrict(ctx['request'].user, 'view').filter(
            object_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
        ).select_related('enrichment').first() if obj is not None else None
        # The token's tier is determined by the most recent catalog sync
        tier = None
        if record is not None and is_enabled() and (job := get_last_sync_job()) and isinstance(job.data, dict):
            tier = job.data.get('tier')
        return {
            **ctx,
            'record': record,
            'enrichment': getattr(record, 'enrichment', None) if record else None,
            'ndx_web_url': get_web_url(),
            'free_tier': tier == 'free',
            'upgrade_url': UPGRADE_URL,
        }

    def should_render(self, context):
        return context.get('record') is not None
