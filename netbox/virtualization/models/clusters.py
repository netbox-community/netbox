from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from dcim.models import Device
from netbox.models import OrganizationalModel, PrimaryModel
from virtualization.choices import *

__all__ = (
    'Cluster',
    'ClusterGroup',
    'ClusterType',
)


class ClusterType(OrganizationalModel):
    """
    A type of Cluster.
    """
    def get_absolute_url(self):
        return reverse('virtualization:clustertype', args=[self.pk])


class ClusterGroup(OrganizationalModel):
    """
    An organizational group of Clusters.
    """
    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster_group'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    def get_absolute_url(self):
        return reverse('virtualization:clustergroup', args=[self.pk])


class Cluster(PrimaryModel):
    """
    A cluster of VirtualMachines. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        max_length=100
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
    status = models.CharField(
        max_length=50,
        choices=ClusterStatusChoices,
        default=ClusterStatusChoices.STATUS_ACTIVE
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

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = (
        'type', 'group', 'status', 'tenant', 'site',
    )
    prerequisite_models = (
        'virtualization.ClusterType',
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name'
            ),
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name'
            ),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])

    def get_status_color(self):
        return ClusterStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if self.pk and self.site:
            nonsite_devices = Device.objects.filter(cluster=self).exclude(site=self.site).count()
            if nonsite_devices:
                raise ValidationError({
                    'site': "{} devices are assigned as hosts for this cluster but are not in site {}".format(
                        nonsite_devices, self.site
                    )
                })
