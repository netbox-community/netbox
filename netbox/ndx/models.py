from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ndx.choices import ImportRecordSourceChoices
from netbox.models import ChangeLoggedModel

__all__ = (
    'Enrichment',
    'ImportRecord',
    'Provenance',
)


class ImportRecord(ChangeLoggedModel):
    """
    Tracks an object (such as a device type) which was imported from the NDX catalog.
    """
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE,
        related_name='+'
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    ndx_id = models.CharField(
        verbose_name=_('NDX ID'),
        max_length=255,
        unique=True,
        help_text=_('Catalog identifier (<vendor slug>/<slug>)')
    )
    entry_type = models.CharField(
        verbose_name=_('entry type'),
        max_length=50,
        help_text=_('Catalog entry type (e.g. device-type)')
    )
    vendor_slug = models.CharField(
        verbose_name=_('vendor slug'),
        max_length=100,
        db_index=True
    )
    source = models.CharField(
        verbose_name=_('source'),
        max_length=50,
        choices=ImportRecordSourceChoices,
        blank=True
    )
    checksum = models.CharField(
        verbose_name=_('checksum'),
        max_length=64,
        blank=True,
        help_text=_("The vendor's catalog checksum at the time of import")
    )
    update_available = models.BooleanField(
        verbose_name=_('update available'),
        default=False
    )
    last_imported = models.DateTimeField(
        verbose_name=_('last imported')
    )

    class Meta:
        ordering = ('ndx_id',)
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        permissions = (
            ('sync', 'Synchronize with the NDX catalog'),
        )
        verbose_name = _('NDX import record')
        verbose_name_plural = _('NDX import records')

    def __str__(self):
        return self.ndx_id

    def get_absolute_url(self):
        return reverse('ndx:importrecord', args=[self.pk])

    def get_source_color(self):
        return ImportRecordSourceChoices.colors.get(self.source)

    @property
    def slug(self):
        return self.ndx_id.split('/', 1)[-1]


class Enrichment(ChangeLoggedModel):
    """
    Supplementary data (lifecycle, thermal, etc.) provided by the NDX catalog for an imported object.
    """
    import_record = models.OneToOneField(
        to='ndx.ImportRecord',
        on_delete=models.CASCADE,
        related_name='enrichment'
    )

    # Thermal
    tdp_watts = models.IntegerField(
        verbose_name=_('TDP (W)'),
        blank=True,
        null=True
    )
    airflow_cfm = models.FloatField(
        verbose_name=_('airflow (CFM)'),
        blank=True,
        null=True
    )
    cooling_type = models.CharField(
        verbose_name=_('cooling type'),
        max_length=50,
        blank=True
    )

    # Lifecycle (stored as strings because the catalog may provide partial dates)
    ga_date = models.CharField(
        verbose_name=_('general availability'),
        max_length=20,
        blank=True
    )
    eol_announced = models.CharField(
        verbose_name=_('end of life announced'),
        max_length=20,
        blank=True
    )
    eos_date = models.CharField(
        verbose_name=_('end of sale'),
        max_length=20,
        blank=True
    )
    eosw_date = models.CharField(
        verbose_name=_('end of software maintenance'),
        max_length=20,
        blank=True
    )
    eosec_date = models.CharField(
        verbose_name=_('end of security updates'),
        max_length=20,
        blank=True
    )
    last_support_date = models.CharField(
        verbose_name=_('last date of support'),
        max_length=20,
        blank=True
    )

    # Environmental
    max_operating_temp_c = models.FloatField(
        verbose_name=_('maximum operating temperature (°C)'),
        blank=True,
        null=True
    )
    min_operating_temp_c = models.FloatField(
        verbose_name=_('minimum operating temperature (°C)'),
        blank=True,
        null=True
    )
    max_operating_humidity = models.IntegerField(
        verbose_name=_('maximum operating humidity (%)'),
        blank=True,
        null=True
    )
    min_operating_humidity = models.IntegerField(
        verbose_name=_('minimum operating humidity (%)'),
        blank=True,
        null=True
    )
    max_operating_altitude_m = models.IntegerField(
        verbose_name=_('maximum operating altitude (m)'),
        blank=True,
        null=True
    )
    ingress_protection = models.CharField(
        verbose_name=_('ingress protection'),
        max_length=10,
        blank=True
    )
    mtbf_hours = models.IntegerField(
        verbose_name=_('MTBF (hours)'),
        blank=True,
        null=True
    )

    # Operational
    typical_power_draw_watts = models.IntegerField(
        verbose_name=_('typical power draw (W)'),
        blank=True,
        null=True
    )
    max_power_draw_watts = models.IntegerField(
        verbose_name=_('maximum power draw (W)'),
        blank=True,
        null=True
    )
    noise_level_dba = models.FloatField(
        verbose_name=_('noise level (dBA)'),
        blank=True,
        null=True
    )
    power_capacity_watts = models.IntegerField(
        verbose_name=_('power capacity (W)'),
        blank=True,
        null=True,
        help_text=_('Rated capacity of a power distribution unit')
    )

    # Platform
    nos = models.CharField(
        verbose_name=_('network OS'),
        max_length=100,
        blank=True
    )
    nos_family = models.CharField(
        verbose_name=_('network OS family'),
        max_length=100,
        blank=True
    )
    api_types = models.JSONField(
        verbose_name=_('API types'),
        default=list,
        blank=True
    )

    # SNMP
    snmp_sys_object_id = models.CharField(
        verbose_name=_('SNMP sysObjectID'),
        max_length=255,
        blank=True
    )
    snmp_vendor_oid_prefix = models.CharField(
        verbose_name=_('SNMP vendor OID prefix'),
        max_length=255,
        blank=True
    )

    # Availability flags (indicate which data the catalog holds, regardless of entitlement)
    has_lifecycle = models.BooleanField(
        verbose_name=_('has lifecycle data'),
        default=False
    )
    has_thermal = models.BooleanField(
        verbose_name=_('has thermal data'),
        default=False
    )
    has_environmental = models.BooleanField(
        verbose_name=_('has environmental data'),
        default=False
    )
    has_operational = models.BooleanField(
        verbose_name=_('has operational data'),
        default=False
    )
    has_platform = models.BooleanField(
        verbose_name=_('has platform data'),
        default=False
    )
    has_snmp = models.BooleanField(
        verbose_name=_('has SNMP data'),
        default=False
    )

    # Protocol extensions (Modbus, BACnet, Redfish, IPMI, gNMI, NETCONF, etc.)
    extensions = models.JSONField(
        verbose_name=_('extensions'),
        default=dict,
        blank=True
    )

    class Meta:
        ordering = ('import_record',)
        verbose_name = _('NDX enrichment')
        verbose_name_plural = _('NDX enrichments')

    def __str__(self):
        return str(self.import_record)

    def get_absolute_url(self):
        return self.import_record.get_absolute_url()

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.import_record
        return objectchange


class Provenance(ChangeLoggedModel):
    """
    The source of an individual enrichment field.
    """
    enrichment = models.ForeignKey(
        to='ndx.Enrichment',
        on_delete=models.CASCADE,
        related_name='provenance'
    )
    field = models.CharField(
        verbose_name=_('field'),
        max_length=100,
        help_text=_('Dotted field path (e.g. lifecycle.ga_date)')
    )
    source = models.CharField(
        verbose_name=_('source'),
        max_length=500,
        blank=True
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        blank=True
    )
    confidence = models.CharField(
        verbose_name=_('confidence'),
        max_length=20,
        blank=True
    )
    retrieved = models.DateField(
        verbose_name=_('retrieved'),
        blank=True,
        null=True
    )
    note = models.TextField(
        verbose_name=_('note'),
        blank=True
    )

    _netbox_private = True

    class Meta:
        ordering = ('enrichment', 'field')
        constraints = (
            models.UniqueConstraint(
                fields=('enrichment', 'field'),
                name='%(app_label)s_%(class)s_unique_enrichment_field'
            ),
        )
        verbose_name = _('NDX provenance entry')
        verbose_name_plural = _('NDX provenance entries')

    def __str__(self):
        return self.field

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.enrichment.import_record
        return objectchange
