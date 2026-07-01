from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.choices import *
from ipam.constants import *
from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin
from utilities.data import array_to_string

__all__ = (
    'Service',
    'ServiceTemplate',
)


class ServiceBase(models.Model):
    port_assignments = models.JSONField(
        verbose_name=_('port assignments'),
        default=list,
        blank=True,
        help_text=_('A list of protocol/port assignments, e.g. [{"protocol": "tcp", "port": 53}]')
    )
    _ports_lowest = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Compose port_assignments from any deprecated protocol/ports values assigned directly
        self._recompose_port_assignments()
        # On saving find the smallest port and save for default ordering
        self._ports_lowest = min(
            (assignment['port'] for assignment in self.port_assignments), default=None
        )
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and '_ports_lowest' not in update_fields:
            kwargs['update_fields'] = list(update_fields) + ['_ports_lowest']
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.port_list})'

    def clean(self):
        super().clean()

        # Compose port_assignments from any deprecated protocol/ports values assigned directly
        self._recompose_port_assignments()

        if not self.port_assignments:
            raise ValidationError({
                'port_assignments': _("At least one protocol/port assignment must be defined.")
            })

        valid_protocols = ServiceProtocolChoices.values()
        for assignment in self.port_assignments:
            if not isinstance(assignment, dict) or set(assignment) != {'protocol', 'port'}:
                raise ValidationError({
                    'port_assignments': _("Each assignment must define exactly a protocol and a port.")
                })
            if assignment['protocol'] not in valid_protocols:
                raise ValidationError({
                    'port_assignments': _("Invalid protocol: {protocol}").format(protocol=assignment['protocol'])
                })
            port = assignment['port']
            if not isinstance(port, int) or not SERVICE_PORT_MIN <= port <= SERVICE_PORT_MAX:
                raise ValidationError({
                    'port_assignments': _("Invalid port number: {port}").format(port=port)
                })

    @property
    def protocol(self):
        """
        Deprecated backward-compatibility accessor. Returns the single protocol shared by all port
        assignments, or None if the service mixes protocols (or has no assignments).
        """
        protocols = {assignment['protocol'] for assignment in self.port_assignments}
        return protocols.pop() if len(protocols) == 1 else None

    @protocol.setter
    def protocol(self, value):
        # Deprecated: buffer the value for recomposition into port_assignments (see save()/clean())
        self._legacy_protocol = value

    @property
    def ports(self):
        """
        Deprecated backward-compatibility accessor. Returns a sorted list of all assigned port numbers.
        """
        return sorted({assignment['port'] for assignment in self.port_assignments})

    @ports.setter
    def ports(self, value):
        # Deprecated: buffer the value for recomposition into port_assignments (see save()/clean())
        self._legacy_ports = list(value) if value else []

    def _recompose_port_assignments(self):
        """
        If deprecated protocol and/or ports values were assigned directly (e.g. via bulk edit),
        rebuild port_assignments as the cartesian product of the effective protocols and ports.
        Missing values fall back to those already present in port_assignments.
        """
        has_protocol = hasattr(self, '_legacy_protocol')
        has_ports = hasattr(self, '_legacy_ports')
        if not (has_protocol or has_ports):
            return

        if has_protocol and self._legacy_protocol:
            protocols = [self._legacy_protocol]
        else:
            protocols = sorted({assignment['protocol'] for assignment in self.port_assignments})
        if has_ports:
            ports = self._legacy_ports
        else:
            ports = sorted({assignment['port'] for assignment in self.port_assignments})

        self.port_assignments = [
            {'protocol': protocol, 'port': port}
            for port in ports
            for protocol in protocols
        ]

        if has_protocol:
            del self._legacy_protocol
        if has_ports:
            del self._legacy_ports

    @property
    def port_list(self):
        # Group ports by protocol for compact display, e.g. "TCP/80, 443; UDP/53"
        protocol_labels = dict(ServiceProtocolChoices)
        grouped = {}
        for assignment in self.port_assignments:
            grouped.setdefault(assignment['protocol'], []).append(assignment['port'])
        return '; '.join(
            f'{protocol_labels.get(protocol, protocol)}/{array_to_string(sorted(ports))}'
            for protocol, ports in grouped.items()
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

    class Meta:
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
        'port_assignments', 'description', 'parent', 'ipaddresses',
    )

    class Meta:
        indexes = (
            models.Index(fields=('_ports_lowest', 'id')),  # Default ordering
            models.Index(fields=('parent_object_type', 'parent_object_id')),
        )
        ordering = ('_ports_lowest', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')
