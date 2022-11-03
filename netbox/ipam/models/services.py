from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from ipam.choices import *
from ipam.constants import *
from netbox.models import PrimaryModel
from utilities.utils import array_to_string


__all__ = (
    'Service',
    'ServiceTemplate',
)


class ServiceBase(models.Model):
    protocol = models.CharField(
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
        verbose_name='Port numbers'
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
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('ipam:servicetemplate', args=[self.pk])


class Service(ServiceBase, PrimaryModel):
    """
    A Service represents a layer-four service (e.g. HTTP or SSH) running on a Device or VirtualMachine. A Service may
    optionally be tied to one or more specific IPAddresses belonging to its parent.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='device',
        null=True,
        blank=True
    )
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=100
    )
    ipaddresses = models.ManyToManyField(
        to='ipam.IPAddress',
        related_name='services',
        blank=True,
        verbose_name='IP addresses'
    )

    clone_fields = ['protocol', 'ports', 'description', 'device', 'virtual_machine', 'ipaddresses', ]

    class Meta:
        ordering = ('protocol', 'ports', 'pk')  # (protocol, port) may be non-unique

    def get_absolute_url(self):
        return reverse('ipam:service', args=[self.pk])

    @property
    def parent(self):
        return self.device or self.virtual_machine

    def clean(self):
        super().clean()

        # A Service must belong to a Device *or* to a VirtualMachine
        if self.device and self.virtual_machine:
            raise ValidationError("A service cannot be associated with both a device and a virtual machine.")
        if not self.device and not self.virtual_machine:
            raise ValidationError("A service must be associated with either a device or a virtual machine.")
