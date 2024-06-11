import decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dcim.models import BaseInterface
from dcim.models.mixins import RenderConfigMixin
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from netbox.config import get_config
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from utilities.fields import CounterCacheField, NaturalOrderingField
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from utilities.tracking import TrackingModelMixin
from virtualization.choices import *

__all__ = (
    'VirtualDisk',
    'VirtualMachine',
    'VMInterface',
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
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualMachineStatusChoices,
        default=VirtualMachineStatusChoices.STATUS_ACTIVE,
        verbose_name=_('status')
    )
    role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        limit_choices_to={'vm_role': True},
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
        verbose_name=_('memory (MB)')
    )
    disk = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('disk (MB)')
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
        ordering = ('_name', 'pk')  # Name may be non-unique
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

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])

    def clean(self):
        super().clean()

        # Must be assigned to a site and/or cluster
        if not self.site and not self.cluster:
            raise ValidationError({
                'cluster': _('A virtual machine must be assigned to a site and/or cluster.')
            })

        # Validate site for cluster & device
        if self.cluster and self.site and self.cluster.site != self.site:
            raise ValidationError({
                'cluster': _(
                    'The selected cluster ({cluster}) is not assigned to this site ({site}).'
                ).format(cluster=self.cluster, site=self.site)
            })

        # Validate assigned cluster device
        if self.device and not self.cluster:
            raise ValidationError({
                'device': _('Must specify a cluster when assigning a host device.')
            })
        if self.device and self.device not in self.cluster.devices.all():
            raise ValidationError({
                'device': _(
                    "The selected device ({device}) is not assigned to this cluster ({cluster})."
                ).format(device=self.device, cluster=self.cluster)
            })

        # Validate aggregate disk size
        if self.pk:
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

        # Assign site from cluster if not set
        if self.cluster and not self.site:
            self.site = self.cluster.site

        super().save(*args, **kwargs)

    def get_status_color(self):
        return VirtualMachineStatusChoices.colors.get(self.status)

    @property
    def primary_ip(self):
        if get_config().PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None


#
# VM components
#


class ComponentModel(NetBoxModel):
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
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ('virtual_machine', CollateAsChar('_name'))
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
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='interfaces'  # Override ComponentModel
    )
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='vminterfaces_as_untagged',
        null=True,
        blank=True,
        verbose_name=_('untagged VLAN')
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='vminterfaces_as_tagged',
        blank=True,
        verbose_name=_('tagged VLANs')
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

    class Meta(ComponentModel.Meta):
        verbose_name = _('interface')
        verbose_name_plural = _('interfaces')

    def get_absolute_url(self):
        return reverse('virtualization:vminterface', kwargs={'pk': self.pk})

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
        verbose_name=_('size (GB)'),
    )

    class Meta(ComponentModel.Meta):
        verbose_name = _('virtual disk')
        verbose_name_plural = _('virtual disks')

    def get_absolute_url(self):
        return reverse('virtualization:virtualdisk', args=[self.pk])
