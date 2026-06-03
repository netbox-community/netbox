import traceback

import jsonschema
from django.conf import settings
from django.core.validators import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from jinja2.exceptions import TemplateError
from jsonschema.exceptions import ValidationError as JSONValidationError

from extras.models.mixins import RenderTemplateMixin
from extras.querysets import ConfigContextQuerySet
from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import CloningMixin, CustomLinksMixin, ExportTemplatesMixin, SyncedDataMixin, TagsMixin
from netbox.models.mixins import OwnerMixin
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


class ConfigContext(SyncedDataMixin, CloningMixin, CustomLinksMixin, OwnerMixin, ChangeLoggedModel):
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
        indexes = (
            models.Index(fields=('weight', 'name')),  # Default ordering
        )
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

    def get_affected_objects(self):
        """
        Return a (device_qs, vm_qs) tuple of all Devices and VirtualMachines that fall within this
        ConfigContext's scope. This is the inverse of ConfigContextQuerySet.get_for_object().
        Used to determine which pre-rendered context caches must be invalidated when this
        ConfigContext changes.
        """
        from dcim.models import Device
        from virtualization.models import VirtualMachine

        device_q, vm_q = self._get_affected_object_filters()
        return (
            Device.objects.filter(device_q),
            VirtualMachine.objects.filter(vm_q),
        )

    def _get_affected_object_filters(self):
        """
        Build the Q expressions matching Devices and VirtualMachines in this context's scope.
        Returns (device_q, vm_q). Does NOT consider `is_active` — callers that need that should
        check it separately. For invalidation purposes, we want the scope set regardless of
        whether the context is currently active (toggling is_active also requires invalidation).
        """
        from extras.models.tags import TaggedItem

        def _mptt_descendants(m2m):
            # Return the PKs of all descendants (incl. self) of the items in this MPTT m2m,
            # or None if the m2m is empty (meaning: no scope restriction).
            scope_pks = list(m2m.values_list('pk', flat=True))
            if not scope_pks:
                return None
            return list(
                m2m.model.objects.filter(pk__in=scope_pks)
                .get_descendants(include_self=True)
                .values_list('pk', flat=True)
            )

        def _direct_pks(m2m):
            pks = list(m2m.values_list('pk', flat=True))
            return pks or None

        # Shared filters (applicable to both Device and VirtualMachine)
        shared = Q()

        region_pks = _mptt_descendants(self.regions)
        if region_pks is not None:
            shared &= Q(site__region__in=region_pks)

        site_group_pks = _mptt_descendants(self.site_groups)
        if site_group_pks is not None:
            shared &= Q(site__group__in=site_group_pks)

        role_pks = _mptt_descendants(self.roles)
        if role_pks is not None:
            shared &= Q(role__in=role_pks)

        platform_pks = _mptt_descendants(self.platforms)
        if platform_pks is not None:
            shared &= Q(platform__in=platform_pks)

        for m2m, path in (
            (self.sites, 'site'),
            (self.cluster_types, 'cluster__type'),
            (self.cluster_groups, 'cluster__group'),
            (self.clusters, 'cluster'),
            (self.tenant_groups, 'tenant__group'),
            (self.tenants, 'tenant'),
        ):
            pks = _direct_pks(m2m)
            if pks is not None:
                shared &= Q(**{f'{path}__in': pks})

        # Tag-scoped contexts: object must be tagged with at least one of the context's tags
        tag_pks = _direct_pks(self.tags)

        device_q = Q(shared)
        vm_q = Q(shared)

        # Device-only filters: location (MPTT) and device_type (direct)
        location_pks = _mptt_descendants(self.locations)
        if location_pks is not None:
            device_q &= Q(location__in=location_pks)
        device_type_pks = _direct_pks(self.device_types)
        if device_type_pks is not None:
            device_q &= Q(device_type__in=device_type_pks)
        # For VMs, locations and device_types must be empty for the context to apply
        if location_pks is not None or device_type_pks is not None:
            vm_q &= Q(pk__in=())

        if tag_pks is not None:
            device_tagged = TaggedItem.objects.filter(
                tag_id__in=tag_pks,
                content_type__app_label='dcim',
                content_type__model='device',
            ).values_list('object_id', flat=True)
            vm_tagged = TaggedItem.objects.filter(
                tag_id__in=tag_pks,
                content_type__app_label='virtualization',
                content_type__model='virtualmachine',
            ).values_list('object_id', flat=True)
            device_q &= Q(pk__in=device_tagged)
            vm_q &= Q(pk__in=vm_tagged)

        return device_q, vm_q


class ConfigContextModel(models.Model):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    ConfigContexts.
    """
    # Pre-rendered config context cache. NULL means "invalidated; render on demand". Populated by
    # extras.jobs.RenderConfigContextJob in the background.
    _config_context_data = models.JSONField(
        blank=True,
        null=True,
        editable=False,
    )
    # Monotonic counter bumped each time the cache is invalidated. The background renderer captures
    # this value before rendering and only writes the result back if it is unchanged, so a fresh
    # invalidation that lands mid-render is never overwritten by a stale value (compare-and-set).
    _config_context_generation = models.PositiveBigIntegerField(
        default=0,
        editable=False,
    )
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
        Return the merged config context for this object. If a pre-rendered cache is present
        (`_config_context_data`), return it directly. Otherwise, fall back to rendering on demand.
        """
        cached = getattr(self, '_config_context_data', None)
        if cached is not None:
            return cached
        return self.render_config_context()

    def render_config_context(self):
        """
        Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs.
        Return the rendered configuration context for a device or VM. This bypasses the pre-rendered cache
        (`_config_context_data`); use get_config_context() for the cached read path.
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

    def serialize_object(self, exclude=None):
        # Exclude the pre-rendered cache and its generation counter from change-log snapshots;
        # they are derived fields and would otherwise produce noisy diffs.
        exclude = list(exclude or [])
        for field in ('_config_context_data', '_config_context_generation'):
            if field not in exclude:
                exclude.append(field)
        return super().serialize_object(exclude=exclude)


#
# Config templates
#

class ConfigTemplate(
    RenderTemplateMixin,
    SyncedDataMixin,
    CustomLinksMixin,
    ExportTemplatesMixin,
    OwnerMixin,
    TagsMixin,
    ChangeLoggedModel,
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
    debug = models.BooleanField(
        verbose_name=_('debug'),
        default=False,
        help_text=_(
            'Enable verbose error output when rendering this template. Not recommended for production use.'
        )
    )

    class Meta:
        ordering = ('name',)
        indexes = (
            models.Index(fields=('name',)),  # Default ordering
        )
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

    def format_render_error(self, exc):
        """
        Return a formatted error string for a rendering exception. When debug is enabled, the full
        traceback for the provided exception is returned. Otherwise, a concise, user-facing message
        is returned.
        """
        if self.debug:
            return ''.join(traceback.format_exception(exc))
        if isinstance(exc, TemplateError):
            parts = [f"{type(exc).__name__}: {exc}"]
            if getattr(exc, 'name', None):
                parts.append(_("Template: {name}").format(name=exc.name))
            if getattr(exc, 'lineno', None):
                parts.append(_("Line: {lineno}").format(lineno=exc.lineno))
            return "\n".join(parts)
        return f"{type(exc).__name__}: {exc}"
