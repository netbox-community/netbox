from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.models import OrganizationalModel, PrimaryModel
from netbox.models.features import ContactsMixin
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
    class Meta:
        ordering = ('name',)
        verbose_name = _('cluster type')
        verbose_name_plural = _('cluster types')

    def get_absolute_url(self):
        return reverse('virtualization:clustertype', args=[self.pk])


class ClusterGroup(ContactsMixin, OrganizationalModel):
    """
    An organizational group of Clusters.
    """
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster_group'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('cluster group')
        verbose_name_plural = _('cluster groups')

    def get_absolute_url(self):
        return reverse('virtualization:clustergroup', args=[self.pk])


class Cluster(ContactsMixin, PrimaryModel):
    """
    A cluster of VirtualMachines. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    type = models.ForeignKey(
        verbose_name=_('type'),
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
        verbose_name=_('status'),
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
        verbose_name = _('cluster')
        verbose_name_plural = _('clusters')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])

    def get_status_color(self):
        return ClusterStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if not self._state.adding and self.site:
            if nonsite_devices := Device.objects.filter(cluster=self).exclude(site=self.site).count():
                raise ValidationError({
                    'site': _(
                        "{count} devices are assigned as hosts for this cluster but are not in site {site}"
                    ).format(count=nonsite_devices, site=self.site)
                })
