import decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from dcim.models import BaseInterface
from dcim.models.mixins import RenderConfigMixin
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from netbox.config import get_config
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from netbox.models.mixins import OwnerMixin
from utilities.fields import CounterCacheField, NaturalOrderingField
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from utilities.tracking import TrackingModelMixin
from virtualization.choices import *

__all__ = (
    'VMInterface',
    'VirtualDisk',
    'VirtualMachine',
)


class VirtualMachine(ContactsMixin, ImageAttachmentsMixin, RenderConfigMixin, ConfigContextModel, PrimaryModel):
    """
    A virtual machine which runs inside a Cluster.
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
        db_collation="natural_sort"
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualMachineStatusChoices,
        default=VirtualMachineStatusChoices.STATUS_ACTIVE,
        verbose_name=_('status')
    )
    start_on_boot = models.CharField(
        max_length=32,
        choices=VirtualMachineStartOnBootChoices,
        default=VirtualMachineStartOnBootChoices.STATUS_OFF,
        verbose_name=_('start on boot'),
    )
    role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name=_('primary IPv4')
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name=_('primary IPv6')
    )
    vcpus = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('vCPUs'),
        validators=(
            MinValueValidator(decimal.Decimal(0.01)),
        )
    )
    memory = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('memory')
    )
    disk = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('disk')
    )
    serial = models.CharField(
        verbose_name=_('serial number'),
        blank=True,
        max_length=50
    )
    services = GenericRelation(
        to='ipam.Service',
        content_type_field='parent_object_type',
        object_id_field='parent_object_id',
        related_query_name='virtual_machine',
    )

    # Counter fields
    interface_count = CounterCacheField(
        to_model='virtualization.VMInterface',
        to_field='virtual_machine'
    )
    virtual_disk_count = CounterCacheField(
        to_model='virtualization.VirtualDisk',
        to_field='virtual_machine'
    )

    objects = ConfigContextModelQuerySet.as_manager()

    clone_fields = (
        'site', 'cluster', 'device', 'tenant', 'platform', 'status', 'role', 'vcpus', 'memory', 'disk',
    )
    prerequisite_models = (
        'virtualization.Cluster',
    )

    class Meta:
        ordering = ('name', 'pk')  # Name may be non-unique
        constraints = (
            models.UniqueConstraint(
                Lower('name'), 'cluster', 'tenant',
                name='%(app_label)s_%(class)s_unique_name_cluster_tenant'
            ),
            models.UniqueConstraint(
                Lower('name'), 'cluster',
                name='%(app_label)s_%(class)s_unique_name_cluster',
                condition=Q(tenant__isnull=True),
                violation_error_message=_("Virtual machine name must be unique per cluster.")
            ),
        )
        verbose_name = _('virtual machine')
        verbose_name_plural = _('virtual machines')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def get_status_color(self):
        return VirtualMachineStatusChoices.colors.get(self.status)

    def get_start_on_boot_color(self):
        return VirtualMachineStartOnBootChoices.colors.get(self.start_on_boot)

    @property
    def primary_ip(self):
        if get_config().PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        if self.primary_ip6:
            return self.primary_ip6
        if self.primary_ip4:
            return self.primary_ip4
        return None


#
# VM components
#


class ComponentModel(OwnerMixin, NetBoxModel):
    """
    An abstract model inherited by any model which has a parent VirtualMachine.
    """
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
        db_collation="natural_sort"
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('virtual_machine', 'name'),
                name='%(app_label)s_%(class)s_unique_virtual_machine_name'
            ),
        )

    def __str__(self):
        return self.name

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.virtual_machine
        return objectchange

    @property
    def parent_object(self):
        return self.virtual_machine


class VMInterface(ComponentModel, BaseInterface, TrackingModelMixin):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
    )
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='interfaces'  # Override ComponentModel
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vminterface'
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.SET_NULL,
        related_name='vminterfaces',
        null=True,
        blank=True,
        verbose_name=_('VRF')
    )
    fhrp_group_assignments = GenericRelation(
        to='ipam.FHRPGroupAssignment',
        content_type_field='interface_type',
        object_id_field='interface_id',
        related_query_name='+'
    )
    tunnel_terminations = GenericRelation(
        to='vpn.TunnelTermination',
        content_type_field='termination_type',
        object_id_field='termination_id',
        related_query_name='vminterface',
    )
    l2vpn_terminations = GenericRelation(
        to='vpn.L2VPNTermination',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vminterface',
    )
    mac_addresses = GenericRelation(
        to='dcim.MACAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vminterface'
    )

    class Meta(ComponentModel.Meta):
        verbose_name = _('interface')
        verbose_name_plural = _('interfaces')
        ordering = ('virtual_machine', CollateAsChar('_name'))

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    @property
    def l2vpn_termination(self):
        return self.l2vpn_terminations.first()


class VirtualDisk(ComponentModel, TrackingModelMixin):
    size = models.PositiveIntegerField(
        verbose_name=_('size'),
    )

    class Meta(ComponentModel.Meta):
        verbose_name = _('virtual disk')
        verbose_name_plural = _('virtual disks')
        ordering = ('virtual_machine', 'name')
