from functools import cached_property

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.choices import *
from ipam.constants import *
from ipam.utils import legacy_protocol_and_ports, split_port_mapping
from ipam.validators import validate_port_mappings
from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin

__all__ = (
    'Service',
    'ServiceTemplate',
)


class ServiceBase(models.Model):
    """
    Shared behavior for Service and ServiceTemplate. Protocol/port data is stored as a single array of
    ``protocol/port`` strings (e.g. ``['tcp/80', 'tcp/443', 'udp/53']``), allowing a service to expose
    the same port on multiple protocols.
    """
    port_mappings = ArrayField(
        base_field=models.CharField(max_length=63),
        verbose_name=_('port mappings'),
        help_text=_("Protocol/port pairs, e.g. tcp/80"),
        blank=True,
        default=list,
    )
    # Denormalized set of the distinct protocols present in port_mappings, maintained by a PostgreSQL
    # trigger (see the migration) so a protocol-only filter can hit a GIN index (_protocols @> ['tcp'])
    # instead of scanning a computed string form of port_mappings. Ports are unbounded, so only protocols
    # are denormalized; port and protocol+port filters query port_mappings directly.
    _protocols = ArrayField(
        base_field=models.CharField(max_length=63),
        blank=True,
        default=list,
        editable=False,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # validate_port_mappings returns the canonical form (integer ports), so storing its result
        # normalizes any entry that bypassed the form field (e.g. a raw REST payload of 'tcp/080').
        self.port_mappings = validate_port_mappings(self.port_mappings)
        self.__dict__.pop('_legacy_protocol_ports', None)  # invalidate the cached legacy view
        if not self.port_mappings:
            raise ValidationError({'port_mappings': _("At least one port mapping is required.")})

    def apply_port_mapping_delta(self, add=None, remove=None):
        """
        Merge bulk-edit add/remove port-mapping deltas into ``port_mappings``. ``add``/``remove`` hold
        canonical ``protocol/port`` strings; existing entries are normalized for the comparison so a
        non-canonical stored value (e.g. a raw-DB 'tcp/080') is still matched by a 'tcp/80' remove. The
        merged list is left for ``clean()`` to validate (range, duplicates, and the at-least-one rule).

        Called from the Service/ServiceTemplate bulk-edit views' pre_save_operations() hook, so the
        merge is part of the single bulk-edit save (one change-log entry) and the model stays unaware of
        the bulk-edit form.
        """
        def _normalize(mapping):
            protocol, port = split_port_mapping(mapping)
            return f'{protocol}/{int(port)}' if port.isdigit() else mapping

        mappings = list(self.port_mappings)
        remove = {_normalize(mapping) for mapping in (remove or [])}
        if add:
            existing = {_normalize(mapping) for mapping in mappings}
            mappings += [mapping for mapping in add if _normalize(mapping) not in existing]
        if remove:
            mappings = [mapping for mapping in mappings if _normalize(mapping) not in remove]
        self.port_mappings = mappings

    # Read-only legacy accessors mirroring the deprecated REST/GraphQL protocol/ports fields, retained
    # for backward compatibility with code that read the old single-protocol fields. A multi-protocol
    # service has no single-protocol form, so both return None (ports=[] when there are no mappings).
    # TODO: Remove in v5.0 once backward compatibility is dropped.
    @cached_property
    def _legacy_protocol_ports(self):
        # Derived once per instance and shared by the protocol/ports accessors (and the GraphQL
        # resolvers, which read these properties), so selecting both doesn't re-group port_mappings twice.
        return legacy_protocol_and_ports(self.port_mappings)

    @property
    def protocol(self):
        return self._legacy_protocol_ports[0]

    @property
    def ports(self):
        return self._legacy_protocol_ports[1]

    @property
    def port_list(self):
        # List each protocol/port pair individually for display, e.g. "TCP/80, TCP/443, UDP/53". Each
        # protocol is rendered via its defined label (falling back to the stored value if unknown); the
        # port is taken verbatim from the stored mapping, so no reformatting of the raw data is needed.
        protocol_labels = dict(ServiceProtocolChoices)
        return ', '.join(
            f'{protocol_labels.get(protocol, protocol)}/{port}'
            for protocol, port in (split_port_mapping(mapping) for mapping in self.port_mappings)
        )


class ServiceTemplate(ServiceBase, PrimaryModel):
    """
    A template for a Service to be applied to a device or virtual machine.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )

    clone_fields = ('port_mappings', 'description')

    class Meta:
        indexes = (
            # Supports exact protocol/port containment lookups (port_mappings @> ['tcp/80'])
            GinIndex(fields=('port_mappings',)),
            # Supports protocol-only containment lookups (_protocols @> ['tcp'])
            GinIndex(fields=('_protocols',)),
        )
        ordering = ('name',)
        verbose_name = _('application service template')
        verbose_name_plural = _('application service templates')


class Service(ContactsMixin, ServiceBase, PrimaryModel):
    """
    A Service represents a layer-four service (e.g. HTTP or SSH) running on a Device or VirtualMachine. A Service may
    optionally be tied to one or more specific IPAddresses belonging to its parent.
    """
    parent_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+',
    )
    parent_object_id = models.PositiveBigIntegerField()
    parent = GenericForeignKey(
        ct_field='parent_object_type',
        fk_field='parent_object_id'
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('name')
    )
    ipaddresses = models.ManyToManyField(
        to='ipam.IPAddress',
        related_name='services',
        blank=True,
        verbose_name=_('IP addresses'),
        help_text=_("The specific IP addresses (if any) to which this application service is bound")
    )

    clone_fields = (
        'port_mappings', 'description', 'parent', 'ipaddresses',
    )

    class Meta:
        indexes = (
            models.Index(fields=('name', 'id')),  # Default ordering
            models.Index(fields=('parent_object_type', 'parent_object_id')),
            # Supports exact protocol/port containment lookups (port_mappings @> ['tcp/80'])
            GinIndex(fields=('port_mappings',)),
            # Supports protocol-only containment lookups (_protocols @> ['tcp'])
            GinIndex(fields=('_protocols',)),
        )
        ordering = ('name', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')
