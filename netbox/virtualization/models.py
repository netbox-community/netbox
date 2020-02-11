from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from dcim.models import Device
from extras.models import ConfigContextModel, CustomFieldModel, TaggedItem
from utilities.models import ChangeLoggedModel
from .choices import *


__all__ = (
    'Cluster',
    'ClusterGroup',
    'ClusterType',
    'VirtualMachine',
)


#
# Cluster types
#

class ClusterType(ChangeLoggedModel):
    """
    A type of Cluster.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?type={}".format(reverse('virtualization:cluster_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
        )


#
# Cluster groups
#

class ClusterGroup(ChangeLoggedModel):
    """
    An organizational group of Clusters.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group={}".format(reverse('virtualization:cluster_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
        )


#
# Clusters
#

class Cluster(ChangeLoggedModel, CustomFieldModel):
    """
    A cluster of VirtualMachines. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    type = models.ForeignKey(
        to=ClusterType,
        on_delete=models.PROTECT,
        related_name='clusters'
    )
    group = models.ForeignKey(
        to=ClusterGroup,
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['name', 'type', 'group', 'site', 'comments']
    clone_fields = [
        'type', 'group', 'tenant', 'site',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])

    def clean(self):

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if self.pk and self.site:
            nonsite_devices = Device.objects.filter(cluster=self).exclude(site=self.site).count()
            if nonsite_devices:
                raise ValidationError({
                    'site': "{} devices are assigned as hosts for this cluster but are not in site {}".format(
                        nonsite_devices, self.site
                    )
                })

    def to_csv(self):
        return (
            self.name,
            self.type.name,
            self.group.name if self.group else None,
            self.site.name if self.site else None,
            self.tenant.name if self.tenant else None,
            self.comments,
        )


#
# Virtual machines
#

class VirtualMachine(ChangeLoggedModel, ConfigContextModel, CustomFieldModel):
    """
    A virtual machine which runs inside a Cluster.
    """
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.PROTECT,
        related_name='virtual_machines'
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
        max_length=64
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualMachineStatusChoices,
        default=VirtualMachineStatusChoices.STATUS_ACTIVE,
        verbose_name='Status'
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
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    vcpus = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='vCPUs'
    )
    memory = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Memory (MB)'
    )
    disk = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Disk (GB)'
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'name', 'status', 'role', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments',
    ]
    clone_fields = [
        'cluster', 'tenant', 'platform', 'status', 'role', 'vcpus', 'memory', 'disk',
    ]

    STATUS_CLASS_MAP = {
        VirtualMachineStatusChoices.STATUS_ACTIVE: 'success',
        VirtualMachineStatusChoices.STATUS_OFFLINE: 'danger',
        VirtualMachineStatusChoices.STATUS_STAGED: 'primary',
        VirtualMachineStatusChoices.STATUS_DECOMMISSIONING: 'warning',
    }

    class Meta:
        ordering = ('name', 'pk')  # Name may be non-unique
        unique_together = [
            ['cluster', 'tenant', 'name']
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])

    def validate_unique(self, exclude=None):

        # Check for a duplicate name on a VM assigned to the same Cluster and no Tenant. This is necessary
        # because Django does not consider two NULL fields to be equal, and thus will not trigger a violation
        # of the uniqueness constraint without manual intervention.
        if self.tenant is None and VirtualMachine.objects.exclude(pk=self.pk).filter(
                name=self.name, tenant__isnull=True
        ):
            raise ValidationError({
                'name': 'A virtual machine with this name already exists.'
            })

        super().validate_unique(exclude)

    def clean(self):

        super().clean()

        # Validate primary IP addresses
        interfaces = self.interfaces.all()
        for field in ['primary_ip4', 'primary_ip6']:
            ip = getattr(self, field)
            if ip is not None:
                if ip.interface in interfaces:
                    pass
                elif self.primary_ip4.nat_inside is not None and self.primary_ip4.nat_inside.interface in interfaces:
                    pass
                else:
                    raise ValidationError({
                        field: "The specified IP address ({}) is not assigned to this VM.".format(ip),
                    })

    def to_csv(self):
        return (
            self.name,
            self.get_status_display(),
            self.role.name if self.role else None,
            self.cluster.name,
            self.tenant.name if self.tenant else None,
            self.platform.name if self.platform else None,
            self.vcpus,
            self.memory,
            self.disk,
            self.comments,
        )

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)

    @property
    def primary_ip(self):
        if settings.PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    @property
    def site(self):
        return self.cluster.site
