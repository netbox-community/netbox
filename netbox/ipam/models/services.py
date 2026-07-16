from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.choices import *
from ipam.constants import *
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

    class Meta:
        abstract = True

    def __str__(self):
        if self.port_mappings:
            return f'{self.name} ({self.port_list})'
        return self.name

    def clean(self):
        super().clean()
        self._apply_bulk_port_mapping_modifiers()
        validate_port_mappings(self.port_mappings)
        if not self.port_mappings:
            raise ValidationError({'port_mappings': _("At least one port mapping is required.")})

    def _apply_bulk_port_mapping_modifiers(self):
        """
        Fold bulk-edit add/remove deltas into ``port_mappings`` before validation.

        The generic ``BulkEditView`` has no per-object pre-save hook, but it does assign the
        ``add_port_mappings`` / ``remove_port_mappings`` bulk-edit form values onto the instance ahead
        of ``full_clean()`` (its "form field used to modify a field" handling). Consuming them here keeps
        the change within the single bulk-edit save (one change-log entry). This is a no-op everywhere
        else, since those attributes are only present during a bulk edit.
        """
        add = getattr(self, 'add_port_mappings', None)
        remove = getattr(self, 'remove_port_mappings', None)
        if add is None and remove is None:
            return

        # Consume the transient attributes so a repeated clean() can't re-apply the delta
        for attr in ('add_port_mappings', 'remove_port_mappings'):
            try:
                delattr(self, attr)
            except AttributeError:
                pass

        mappings = list(self.port_mappings)
        if add:
            mappings += [mapping for mapping in add if mapping not in mappings]
        if remove:
            mappings = [mapping for mapping in mappings if mapping not in remove]
        self.port_mappings = mappings

    @property
    def port_list(self):
        # Group ports by protocol for a compact display, e.g. "TCP/80,443, UDP/53". Ports are sorted
        # numerically within each protocol so the display is stable regardless of stored order.
        grouped = {}
        for mapping in self.port_mappings:
            protocol, _sep, port = mapping.partition('/')
            grouped.setdefault(protocol, []).append(port)
        return ', '.join(
            f'{protocol.upper()}/{",".join(sorted(ports, key=int))}'
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

    clone_fields = ('port_mappings', 'description')

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
        'port_mappings', 'description', 'parent_object_type', 'parent_object_id', 'ipaddresses',
    )

    class Meta:
        indexes = (
            models.Index(fields=('name', 'id')),  # Default ordering
            models.Index(fields=('parent_object_type', 'parent_object_id')),
        )
        ordering = ('name', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')
