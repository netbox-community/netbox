from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
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
    protocol = models.CharField(
        verbose_name=_('protocol'),
        max_length=50,
        choices=ServiceProtocolChoices
    )
    ports = ArrayField(
        base_field=models.PositiveIntegerField(
            validators=[
                MinValueValidator(SERVICE_PORT_MIN),
                MaxValueValidator(SERVICE_PORT_MAX)
            ]
        ),
        verbose_name=_('port numbers')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} ({self.get_protocol_display()}/{self.port_list})'

    @property
    def port_list(self):
        return array_to_string(self.ports)


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
    _min_port = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    clone_fields = (
        'protocol', 'ports', 'description', 'parent_object_type', 'parent_object_id', 'ipaddresses',
    )

    def save(self, *args, **kwargs):
        # On saving find the smallest port and save for default ordering
        if self.ports:
            self._min_port = min(self.ports)
        else:
            self._min_port = None

        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            models.Index(fields=('name', 'protocol', '_min_port', 'id')),  # Default ordering
            models.Index(fields=('parent_object_type', 'parent_object_id')),
        )
        ordering = ('name', 'protocol', '_min_port', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')
