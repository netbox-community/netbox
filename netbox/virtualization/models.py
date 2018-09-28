from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from taggit.managers import TaggableManager

from dcim.models import Device
from extras.models import ConfigContextModel, CustomFieldModel
from utilities.models import ChangeLoggedModel
from .constants import DEVICE_STATUS_ACTIVE, VM_STATUS_CHOICES, VM_STATUS_CLASSES


#
# Cluster types
#

@python_2_unicode_compatible
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

@python_2_unicode_compatible
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

@python_2_unicode_compatible
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

    tags = TaggableManager()

    csv_headers = ['name', 'type', 'group', 'site', 'comments']

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
            self.comments,
        )


#
# Virtual machines
#

@python_2_unicode_compatible
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
        max_length=64,
        unique=True
    )
    status = models.PositiveSmallIntegerField(
        choices=VM_STATUS_CHOICES,
        default=DEVICE_STATUS_ACTIVE,
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

    tags = TaggableManager()

    csv_headers = [
        'name', 'status', 'role', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])

    def clean(self):

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
        return VM_STATUS_CLASSES[self.status]

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
