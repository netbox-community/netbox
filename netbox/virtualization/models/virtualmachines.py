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

from ..choices import *

__all__ = (
    'VMInterface',
    'VirtualDisk',
    'VirtualMachine',
    'VirtualMachineType',
)


class VirtualMachineType(ImageAttachmentsMixin, PrimaryModel):
    """
    A type defining default attributes (platform, vCPUs, memory, etc.) for virtual machines.
    """

    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True,
    )
    default_platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name=_('default platform'),
    )
    default_vcpus = models.DecimalField(
        verbose_name=_('default vCPUs'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=(MinValueValidator(decimal.Decimal('0.01')),),
    )
    default_memory = models.PositiveIntegerField(
        verbose_name=_('default memory (MB)'),
        blank=True,
        null=True,
    )

    # Counter fields
    virtual_machine_count = CounterCacheField(
        to_model='virtualization.VirtualMachine',
        to_field='virtual_machine_type',
    )

    clone_fields = (
        'default_platform',
        'default_vcpus',
        'default_memory',
    )

    class Meta:
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                Lower('name'),
                name='%(app_label)s_%(class)s_unique_name',
                violation_error_message=_('Virtual machine type name must be unique.'),
            ),
        )
        indexes = (
            models.Index(fields=('name',)),  # Default ordering
        )
        verbose_name = _('virtual machine type')
        verbose_name_plural = _('virtual machine types')

    def __str__(self):
        return self.name


class VirtualMachine(
    ContactsMixin, ImageAttachmentsMixin, RenderConfigMixin, ConfigContextModel, TrackingModelMixin, PrimaryModel
):
    """
    A virtual machine which runs on a Cluster or a standalone Device.

    Each VM must be placed in at least one of three ways:

    1. Assigned to a Site alone (e.g. for logical grouping without a specific host).
    2. Assigned to a Cluster and optionally pinned to a host Device within that cluster.
    3. Assigned directly to a standalone Device (one that does not belong to any cluster).

    When a Cluster or Device is set, the Site is automatically inherited if not explicitly provided.
    If a Device belongs to a Cluster, the Cluster must also be specified on the VM.
    """

    virtual_machine_type = models.ForeignKey(
        to='virtualization.VirtualMachineType',
        on_delete=models.PROTECT,
        related_name='instances',
        verbose_name=_('type'),
        blank=True,
        null=True,
    )
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
        'virtual_machine_type', 'site', 'cluster', 'device', 'tenant', 'platform', 'status', 'role', 'vcpus', 'memory',
        'disk',
    )

    class Meta:
        ordering = ('name', 'pk')  # Name may be non-unique
        indexes = (
            models.Index(fields=('name', 'id')),  # Default ordering
        )
        constraints = (
            models.UniqueConstraint(
                Lower('name'), 'cluster', 'tenant',
                name='%(app_label)s_%(class)s_unique_name_cluster_tenant',
                violation_error_message=_('Virtual machine name must be unique per cluster and tenant.')
            ),
            models.UniqueConstraint(
                Lower('name'), 'cluster',
                name='%(app_label)s_%(class)s_unique_name_cluster',
                condition=Q(tenant__isnull=True),
                violation_error_message=_('Virtual machine name must be unique per cluster.')
            ),
            models.UniqueConstraint(
                Lower('name'), 'device', 'tenant',
                name='%(app_label)s_%(class)s_unique_name_device_tenant',
                condition=Q(cluster__isnull=True, device__isnull=False),
                violation_error_message=_('Virtual machine name must be unique per device and tenant.')
            ),
            models.UniqueConstraint(
                Lower('name'), 'device',
                name='%(app_label)s_%(class)s_unique_name_device',
                condition=Q(cluster__isnull=True, device__isnull=False, tenant__isnull=True),
                violation_error_message=_('Virtual machine name must be unique per device.')
            ),
        )
        verbose_name = _('virtual machine')
        verbose_name_plural = _('virtual machines')
        permissions = [
            ('render_config', 'Render configuration'),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Must be assigned to a site, cluster, and/or device
        if not self.site and not self.cluster and not self.device:
            raise ValidationError(
                _('A virtual machine must be assigned to a site, cluster, or device.')
            )

        # Validate site for cluster & VM
        if self.cluster and self.site and self.cluster._site and self.cluster._site != self.site:
            raise ValidationError({
                'cluster': _(
                    'The selected cluster ({cluster}) is not assigned to this site ({site}).'
                ).format(cluster=self.cluster, site=self.site)
            })

        # Validate site for the device & VM (when the device is standalone)
        if self.device and self.site and self.device.site and self.device.site != self.site:
            raise ValidationError({
                'site': _(
                    'The selected device ({device}) is not assigned to this site ({site}).'
                ).format(device=self.device, site=self.site)
            })

        # Direct device assignment is only for standalone hosts. If the selected
        # device already belongs to a cluster, require that cluster explicitly.
        if self.device and not self.cluster and self.device.cluster:
            raise ValidationError({
                'cluster': _(
                    "Must specify the assigned device's cluster ({cluster}) when assigning host device {device}."
                ).format(cluster=self.device.cluster, device=self.device)
            })

        # Validate assigned cluster device
        if self.device and self.cluster and self.device.cluster_id != self.cluster_id:
            raise ValidationError({
                'device': _(
                    "The selected device ({device}) is not assigned to this cluster ({cluster})."
                ).format(device=self.device, cluster=self.cluster)
            })

        # Validate aggregate disk size
        if not self._state.adding:
            total_disk = self.virtualdisks.aggregate(Sum('size', default=0))['size__sum']
            if total_disk and self.disk is None:
                self.disk = total_disk
            elif total_disk and self.disk != total_disk:
                raise ValidationError({
                    'disk': _(
                        "The specified disk size ({size}) must match the aggregate size of assigned virtual disks "
                        "({total_size})."
                    ).format(size=self.disk, total_size=total_disk)
                })

        # Validate primary IP addresses
        interfaces = self.interfaces.all() if self.pk else None
        for family in (4, 6):
            field = f'primary_ip{family}'
            ip = getattr(self, field)
            if ip is not None:
                if ip.address.version != family:
                    raise ValidationError({
                        field: _(
                            "Must be an IPv{family} address. ({ip} is an IPv{version} address.)"
                        ).format(family=family, ip=ip, version=ip.address.version)
                    })
                if ip.assigned_object in interfaces:
                    pass
                elif ip.nat_inside is not None and ip.nat_inside.assigned_object in interfaces:
                    pass
                else:
                    raise ValidationError({
                        field: _("The specified IP address ({ip}) is not assigned to this VM.").format(ip=ip),
                    })

    def save(self, *args, **kwargs):
        # Assign a site from a cluster or device if not set
        if not self.site:
            if self.cluster and self.cluster._site:
                self.site = self.cluster._site
            elif self.device and self.device.site:
                self.site = self.device.site

        if self._state.adding:
            self.apply_type_defaults()

        super().save(*args, **kwargs)

    def apply_type_defaults(self):
        """
        Populate any empty fields with defaults from the assigned VirtualMachineType.
        """
        if not self.virtual_machine_type_id:
            return

        defaults = {
            'platform_id': 'default_platform_id',
            'vcpus': 'default_vcpus',
            'memory': 'default_memory',
        }
        for field, default_field in defaults.items():
            if getattr(self, field) is None:
                default_value = getattr(self.virtual_machine_type, default_field)
                if default_value is not None:
                    setattr(self, field, default_value)

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

        # Parent validation

        # An interface cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': _("An interface cannot be its own parent.")})

        # An interface's parent must belong to the same virtual machine
        if self.parent and self.parent.virtual_machine != self.virtual_machine:
            raise ValidationError({
                'parent': _(
                    "The selected parent interface ({parent}) belongs to a different virtual machine "
                    "({virtual_machine})."
                ).format(parent=self.parent, virtual_machine=self.parent.virtual_machine)
            })

        # Bridge validation

        # An interface cannot be bridged to itself
        if self.pk and self.bridge_id == self.pk:
            raise ValidationError({'bridge': _("An interface cannot be bridged to itself.")})

        # A bridged interface belong to the same virtual machine
        if self.bridge and self.bridge.virtual_machine != self.virtual_machine:
            raise ValidationError({
                'bridge': _(
                    "The selected bridge interface ({bridge}) belongs to a different virtual machine "
                    "({virtual_machine})."
                ).format(bridge=self.bridge, virtual_machine=self.bridge.virtual_machine)
            })

        # VLAN validation

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.virtual_machine.site, None]:
            raise ValidationError({
                'untagged_vlan': _(
                    "The untagged VLAN ({untagged_vlan}) must belong to the same site as the interface's parent "
                    "virtual machine, or it must be global."
                ).format(untagged_vlan=self.untagged_vlan)
            })

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
