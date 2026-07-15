from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.choices import *
from ipam.constants import *
from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import ContactsMixin
from utilities.data import array_to_string

__all__ = (
    'Service',
    'ServicePortMapping',
    'ServiceTemplate',
    'ServiceTemplatePortMapping',
)


class ServiceBase(models.Model):
    """
    Shared behavior for Service and ServiceTemplate. The protocol/port data now lives in the related
    port mapping models (one row per protocol), accessible via the ``port_mappings`` reverse relation.
    """

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def port_list(self):
        # Summarize the related port mappings, e.g. "TCP/80,443, UDP/53"
        return ', '.join(str(mapping) for mapping in self.port_mappings.all())


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
        'description', 'parent_object_type', 'parent_object_id', 'ipaddresses',
    )

    class Meta:
        indexes = (
            models.Index(fields=('name', 'id')),  # Default ordering
            models.Index(fields=('parent_object_type', 'parent_object_id')),
        )
        ordering = ('name', 'id')
        verbose_name = _('application service')
        verbose_name_plural = _('application services')


class ServicePortMappingBase(ChangeLoggedModel):
    """
    A single protocol paired with one or more port numbers, belonging to a Service or ServiceTemplate.
    """
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
        ordering = ('protocol',)

    def __str__(self):
        return f'{self.get_protocol_display()}/{self.port_list}'

    @property
    def port_list(self):
        return array_to_string(self.ports)


class ServicePortMapping(ServicePortMappingBase):
    service = models.ForeignKey(
        to='ipam.Service',
        on_delete=models.CASCADE,
        related_name='port_mappings'
    )

    clone_fields = ('protocol', 'ports')

    class Meta:
        ordering = ('protocol',)
        constraints = (
            models.UniqueConstraint(
                fields=('service', 'protocol'),
                name='%(app_label)s_%(class)s_unique_service_protocol'
            ),
        )
        verbose_name = _('service port mapping')
        verbose_name_plural = _('service port mappings')

    def get_absolute_url(self):
        return self.service.get_absolute_url()


class ServiceTemplatePortMapping(ServicePortMappingBase):
    service_template = models.ForeignKey(
        to='ipam.ServiceTemplate',
        on_delete=models.CASCADE,
        related_name='port_mappings'
    )

    clone_fields = ('protocol', 'ports')

    class Meta:
        ordering = ('protocol',)
        constraints = (
            models.UniqueConstraint(
                fields=('service_template', 'protocol'),
                name='%(app_label)s_%(class)s_unique_servicetemplate_protocol'
            ),
        )
        verbose_name = _('service template port mapping')
        verbose_name_plural = _('service template port mappings')

    def get_absolute_url(self):
        return self.service_template.get_absolute_url()
