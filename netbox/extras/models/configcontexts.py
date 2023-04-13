from django.conf import settings
from django.core.validators import ValidationError
from django.db import models
from django.urls import reverse

from extras.querysets import ConfigContextQuerySet
from netbox.models import ChangeLoggedModel
from netbox.models.features import CloningMixin, WebhooksMixin
from utilities.utils import deepmerge


__all__ = (
    'ConfigContext',
    'ConfigContextModel',
)


#
# Config contexts
#

class ConfigContext(CloningMixin, WebhooksMixin, ChangeLoggedModel):
    """
    A ConfigContext represents a set of arbitrary data available to any Device or VirtualMachine matching its assigned
    qualifiers (region, site, etc.). For example, the data stored in a ConfigContext assigned to site A and tenant B
    will be available to a Device in site A assigned to tenant B. Data is stored in JSON format.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    weight = models.PositiveSmallIntegerField(
        default=1000
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
    )
    regions = models.ManyToManyField(
        to='dcim.Region',
        related_name='+',
        blank=True
    )
    site_groups = models.ManyToManyField(
        to='dcim.SiteGroup',
        related_name='+',
        blank=True
    )
    sites = models.ManyToManyField(
        to='dcim.Site',
        related_name='+',
        blank=True
    )
    locations = models.ManyToManyField(
        to='dcim.Location',
        related_name='+',
        blank=True
    )
    device_types = models.ManyToManyField(
        to='dcim.DeviceType',
        related_name='+',
        blank=True
    )
    roles = models.ManyToManyField(
        to='dcim.DeviceRole',
        related_name='+',
        blank=True
    )
    platforms = models.ManyToManyField(
        to='dcim.Platform',
        related_name='+',
        blank=True
    )
    cluster_types = models.ManyToManyField(
        to='virtualization.ClusterType',
        related_name='+',
        blank=True
    )
    cluster_groups = models.ManyToManyField(
        to='virtualization.ClusterGroup',
        related_name='+',
        blank=True
    )
    clusters = models.ManyToManyField(
        to='virtualization.Cluster',
        related_name='+',
        blank=True
    )
    tenant_groups = models.ManyToManyField(
        to='tenancy.TenantGroup',
        related_name='+',
        blank=True
    )
    tenants = models.ManyToManyField(
        to='tenancy.Tenant',
        related_name='+',
        blank=True
    )
    tags = models.ManyToManyField(
        to='extras.Tag',
        related_name='+',
        blank=True
    )
    data = models.JSONField()

    objects = ConfigContextQuerySet.as_manager()

    clone_fields = (
        'weight', 'is_active', 'regions', 'site_groups', 'sites', 'locations', 'device_types',
        'roles', 'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups',
        'tenants', 'tags', 'data',
    )

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:configcontext', kwargs={'pk': self.pk})

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/configcontext/'

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if type(self.data) is not dict:
            raise ValidationError(
                {'data': 'JSON data must be in object form. Example: {"foo": 123}'}
            )


class ConfigContextModel(models.Model):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    ConfigContexts.
    """
    local_context_data = models.JSONField(
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def get_config_context(self):
        """
        Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs.
        Return the rendered configuration context for a device or VM.
        """
        data = {}

        if not hasattr(self, 'config_context_data'):
            # The annotation is not available, so we fall back to manually querying for the config context objects
            config_context_data = ConfigContext.objects.get_for_object(self, aggregate_data=True)
        else:
            # The attribute may exist, but the annotated value could be None if there is no config context data
            config_context_data = self.config_context_data or []

        for context in config_context_data:
            data = deepmerge(data, context)

        # If the object has local config context data defined, merge it last
        if self.local_context_data:
            data = deepmerge(data, self.local_context_data)

        return data

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if self.local_context_data and type(self.local_context_data) is not dict:
            raise ValidationError(
                {'local_context_data': 'JSON data must be in object form. Example: {"foo": 123}'}
            )
