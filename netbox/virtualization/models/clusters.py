from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from dcim.models.mixins import CachedScopeMixin
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


class Cluster(ContactsMixin, CachedScopeMixin, PrimaryModel):
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

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster'
    )

    clone_fields = (
        'scope_type', 'scope_id', 'type', 'group', 'status', 'tenant',
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
                fields=('_site', 'name'),
                name='%(app_label)s_%(class)s_unique__site_name'
            ),
        )
        verbose_name = _('cluster')
        verbose_name_plural = _('clusters')

    def __str__(self):
        return self.name

    def get_status_color(self):
        return ClusterStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        site = location = None
        if self.scope_type:
            scope_type = self.scope_type.model_class()
            if scope_type == apps.get_model('dcim', 'site'):
                site = self.scope
            elif scope_type == apps.get_model('dcim', 'location'):
                location = self.scope
                site = location.site

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if not self._state.adding:
            if site:
                if nonsite_devices := Device.objects.filter(cluster=self).exclude(site=site).count():
                    raise ValidationError({
                        'scope': _(
                            "{count} devices are assigned as hosts for this cluster but are not in site {site}"
                        ).format(count=nonsite_devices, site=site)
                    })
            if location:
                if nonlocation_devices := Device.objects.filter(cluster=self).exclude(location=location).count():
                    raise ValidationError({
                        'scope': _(
                            "{count} devices are assigned as hosts for this cluster but are not in location {location}"
                        ).format(count=nonlocation_devices, location=location)
                    })
