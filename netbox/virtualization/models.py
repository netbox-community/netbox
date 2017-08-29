from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible

from dcim.fields import MACAddressField
from extras.models import CustomFieldModel, CustomFieldValue
from utilities.models import CreatedUpdatedModel


#
# Cluster types
#

@python_2_unicode_compatible
class ClusterType(models.Model):
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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?type={}".format(reverse('virtualization:cluster_list'), self.slug)


#
# Cluster groups
#

@python_2_unicode_compatible
class ClusterGroup(models.Model):
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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group={}".format(reverse('virtualization:cluster_list'), self.slug)


#
# Clusters
#

@python_2_unicode_compatible
class Cluster(CreatedUpdatedModel, CustomFieldModel):
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
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to=CustomFieldValue,
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])


#
# Virtual machines
#

@python_2_unicode_compatible
class VirtualMachine(CreatedUpdatedModel, CustomFieldModel):
    """
    A virtual machine which runs inside a Cluster.
    """
    cluster = models.ForeignKey(
        to=Cluster,
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
        to=CustomFieldValue,
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])
