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

# Fixed protocol value -> label map, built once (the choice set is static per process) rather than
# rebuilt on every port_mappings_list render.
SERVICE_PROTOCOL_LABELS = dict(ServiceProtocolChoices)


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

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # validate_port_mappings returns the canonical form (integer ports), so storing its result
        # normalizes any entry that bypassed the form field (e.g. a raw REST payload of 'tcp/080'). Key
        # its errors to the field — it raises unkeyed, which full_clean() would otherwise file as a
        # non-field (__all__) error rather than against port_mappings.
        try:
            self.port_mappings = validate_port_mappings(self.port_mappings)
        except ValidationError as e:
            raise ValidationError({'port_mappings': e.messages})
        if not self.port_mappings:
            raise ValidationError({'port_mappings': _("At least one port mapping is required.")})

    @staticmethod
    def _normalize_mapping(mapping):
        # Normalize a stored/incoming mapping's port to an integer so a non-canonical value (e.g. a
        # raw-DB 'tcp/080') compares equal to its canonical form ('tcp/80').
        protocol, port = split_port_mapping(mapping)
        return f'{protocol}/{int(port)}' if port.isdigit() else mapping

    def _add_port_mappings(self, mappings):
        """
        Add the given canonical ``protocol/port`` strings to ``port_mappings``, skipping any already
        present (matched by normalized form). The merged list is left for ``clean()`` to validate.

        Internal helper called from the Service/ServiceTemplate bulk-edit view's pre_save_operations()
        hook, so the merge is part of the single bulk-edit save (one change-log entry) and the model
        stays unaware of the bulk-edit form. Underscore-prefixed to keep it out of the way of the
        identically-named ``add_port_mappings`` bulk-edit form field (which the generic bulk-edit view
        assigns onto the object).
        """
        existing = {self._normalize_mapping(mapping) for mapping in self.port_mappings}
        self.port_mappings = list(self.port_mappings) + [
            mapping for mapping in mappings if self._normalize_mapping(mapping) not in existing
        ]

    def _remove_port_mappings(self, mappings):
        """
        Remove the given canonical ``protocol/port`` strings from ``port_mappings`` (matched by
        normalized form). The result is left for ``clean()`` to validate (range, duplicates, and the
        at-least-one rule). Internal helper called from the bulk-edit view's pre_save_operations() hook
        (see ``_add_port_mappings``).
        """
        remove = {self._normalize_mapping(mapping) for mapping in mappings}
        self.port_mappings = [
            mapping for mapping in self.port_mappings if self._normalize_mapping(mapping) not in remove
        ]

    # Read-only legacy accessors mirroring the deprecated REST/GraphQL protocol/ports fields, retained
    # for backward compatibility with code that read the old single-protocol fields. A multi-protocol
    # service has no single-protocol form, so both return None (ports=[] when there are no mappings).
    # TODO: Remove in v5.0 once backward compatibility is dropped.
    @property
    def _legacy_protocol_ports(self):
        # Recomputed on access (grouping a handful of strings is cheap) rather than cached, so a mutation
        # of port_mappings — e.g. via _add_port_mappings()/_remove_port_mappings() — is always reflected
        # by the protocol/ports accessors, with no cache to invalidate.
        return legacy_protocol_and_ports(self.port_mappings)

    # Return types are annotated so drf-spectacular can resolve these properties when it builds the
    # write-side serializer schema (without them it warns and falls back to string).
    @property
    def protocol(self) -> str | None:
        return self._legacy_protocol_ports[0]

    @property
    def ports(self) -> list[int] | None:
        return self._legacy_protocol_ports[1]

    @property
    def port_mappings_list(self):
        # List each protocol/port pair individually for display, e.g. "TCP/80, TCP/443, UDP/53". Each
        # protocol is rendered via its defined label (falling back to the stored value if unknown); the
        # port is taken verbatim from the stored mapping, so no reformatting of the raw data is needed.
        return ', '.join(
            f'{SERVICE_PROTOCOL_LABELS.get(protocol, protocol)}/{port}'
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
            # Supports exact protocol/port lookups (port_mappings && ['tcp/80']). Protocol-only and
            # range lookups can't use an array index at all (GIN array_ops supports only =, &&, @>, <@)
            # and are served by a correlated scan instead — see ipam.utils.PortMappingMatch.
            GinIndex(fields=('port_mappings',)),
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
            # Supports exact protocol/port lookups (port_mappings && ['tcp/80']). Protocol-only and
            # range lookups can't use an array index at all (GIN array_ops supports only =, &&, @>, <@)
            # and are served by a correlated scan instead — see ipam.utils.PortMappingMatch.
            GinIndex(fields=('port_mappings',)),
        )
        ordering = ('name', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')
