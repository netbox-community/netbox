from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.models import OrganizationalModel, PrimaryModel
from netbox.models.features import ContactsMixin
from virtualization.choices import *
from virtualization.constants import CLUSTER_SCOPE_TYPES

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
    scope_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        limit_choices_to=models.Q(model__in=CLUSTER_SCOPE_TYPES),
        related_name='+',
        blank=True,
        null=True
    )
    scope_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    scope = GenericForeignKey(
        ct_field='scope_type',
        fk_field='scope_id'
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster'
    )

    # Cached associations to enable efficient filtering
    _location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.CASCADE,
        related_name='_clusters',
        blank=True,
        null=True
    )
    _site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='_clusters',
        blank=True,
        null=True
    )
    _region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.CASCADE,
        related_name='_clusters',
        blank=True,
        null=True
    )
    _sitegroup = models.ForeignKey(
        to='dcim.SiteGroup',
        on_delete=models.CASCADE,
        related_name='_clusters',
        blank=True,
        null=True
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
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name'
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

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if not self._state.adding and self.site:
            if nonsite_devices := Device.objects.filter(cluster=self).exclude(site=self.site).count():
                raise ValidationError({
                    'site': _(
                        "{count} devices are assigned as hosts for this cluster but are not in site {site}"
                    ).format(count=nonsite_devices, site=self.site)
                })

    def save(self, *args, **kwargs):
        # Cache objects associated with the terminating object (for filtering)
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self):
        self._region = self._sitegroup = self._site = self._location = None
        if self.scope_type:
            scope_type = self.scope_type.model_class()
            if scope_type == apps.get_model('dcim', 'region'):
                self._region = self.scope
            elif scope_type == apps.get_model('dcim', 'sitegroup'):
                self._sitegroup = self.scope
            elif scope_type == apps.get_model('dcim', 'site'):
                self._region = self.scope.region
                self._sitegroup = self.scope.group
                self._site = self.scope
            elif scope_type == apps.get_model('dcim', 'location'):
                self._region = self.scope.site.region
                self._sitegroup = self.scope.site.group
                self._site = self.scope.site
                self._location = self.scope
    cache_related_objects.alters_data = True
