import jsonschema
from collections import defaultdict
from jsonschema.exceptions import ValidationError as JSONValidationError

from django.conf import settings
from django.core.validators import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from extras.models.mixins import RenderTemplateMixin
from extras.querysets import ConfigContextQuerySet
from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import CloningMixin, CustomLinksMixin, ExportTemplatesMixin, SyncedDataMixin, TagsMixin
from utilities.data import deepmerge
from utilities.jsonschema import validate_schema

__all__ = (
    'ConfigContext',
    'ConfigContextModel',
    'ConfigContextProfile',
    'ConfigTemplate',
)


#
# Config contexts
#

class ConfigContextProfile(SyncedDataMixin, PrimaryModel):
    """
    A profile which can be used to enforce parameters on a ConfigContext.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    schema = models.JSONField(
        blank=True,
        null=True,
        validators=[validate_schema],
        verbose_name=_('schema'),
        help_text=_('A JSON schema specifying the structure of the context data for this profile')
    )

    clone_fields = ('schema',)

    class Meta:
        ordering = ('name',)
        verbose_name = _('config context profile')
        verbose_name_plural = _('config context profiles')

    def __str__(self):
        return self.name

    def sync_data(self):
        """
        Synchronize schema from the designated DataFile (if any).
        """
        self.schema = self.data_file.get_data()
    sync_data.alters_data = True


class ConfigContext(SyncedDataMixin, CloningMixin, CustomLinksMixin, ChangeLoggedModel):
    """
    A ConfigContext represents a set of arbitrary data available to any Device or VirtualMachine matching its assigned
    qualifiers (region, site, etc.). For example, the data stored in a ConfigContext assigned to site A and tenant B
    will be available to a Device in site A assigned to tenant B. Data is stored in JSON format.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    profile = models.ForeignKey(
        to='extras.ConfigContextProfile',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='config_contexts',
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=1000
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
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
        'weight', 'profile', 'is_active', 'regions', 'site_groups', 'sites', 'locations', 'device_types', 'roles',
        'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'tags', 'data',
    )

    class Meta:
        ordering = ['weight', 'name']
        verbose_name = _('config context')
        verbose_name_plural = _('config contexts')

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
                {'data': _('JSON data must be in object form. Example:') + ' {"foo": 123}'}
            )

        # Validate config data against the assigned profile's schema (if any)
        if self.profile and self.profile.schema:
            try:
                jsonschema.validate(self.data, schema=self.profile.schema)
            except JSONValidationError as e:
                raise ValidationError(_("Data does not conform to profile schema: {error}").format(error=e))

    def sync_data(self):
        """
        Synchronize context data from the designated DataFile (if any).
        """
        self.data = self.data_file.get_data()
    sync_data.alters_data = True


class ConfigContextModel(models.Model):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    ConfigContexts.
    """
    local_context_data = models.JSONField(
        blank=True,
        null=True,
        help_text=_(
            "Local config context data takes precedence over source contexts in the final rendered config context"
        )
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
            config_context_data = ConfigContext.objects.get_for_object(self, aggregate_data=True) or []
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
        if self.local_context_data is not None and type(self.local_context_data) is not dict:
            raise ValidationError(
                {'local_context_data': _('JSON data must be in object form. Example:') + ' {"foo": 123}'}
            )


#
# Config templates
#

class ConfigTemplate(
    RenderTemplateMixin, SyncedDataMixin, CustomLinksMixin, ExportTemplatesMixin, TagsMixin, ChangeLoggedModel
):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('config template')
        verbose_name_plural = _('config templates')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:configtemplate', args=[self.pk])

    def sync_data(self):
        """
        Synchronize template content from the designated DataFile (if any).
        """
        self.template_code = self.data_file.data_as_string
    sync_data.alters_data = True

    def get_context(self, context=None, queryset=None):
        _context = defaultdict(dict)

        # Populate all public models for reference within the template
        for object_type in ObjectType.objects.public():
            if model := object_type.model_class():
                _context[object_type.app_label][model.__name__] = model

        # Apply the provided context data, if any
        if context is not None:
            _context.update(context)

        return _context
