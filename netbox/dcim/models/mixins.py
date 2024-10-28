from django.apps import apps
from django.db import models

__all__ = (
    'CachedScopeMixin',
    'RenderConfigMixin',
)


class RenderConfigMixin(models.Model):
    config_template = models.ForeignKey(
        to='extras.ConfigTemplate',
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def get_config_template(self):
        """
        Return the appropriate ConfigTemplate (if any) for this Device.
        """
        if self.config_template:
            return self.config_template
        if self.role and self.role.config_template:
            return self.role.config_template
        if self.platform and self.platform.config_template:
            return self.platform.config_template


class CachedScopeMixin(models.Model):
    """
    Cached associations for scope to enable efficient filtering - must define scope and scope_type on model
    """
    _location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.CASCADE,
        related_name='_%(class)ss',
        blank=True,
        null=True
    )
    _site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='_%(class)ss',
        blank=True,
        null=True
    )
    _region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.CASCADE,
        related_name='_%(class)ss',
        blank=True,
        null=True
    )
    _sitegroup = models.ForeignKey(
        to='dcim.SiteGroup',
        on_delete=models.CASCADE,
        related_name='_%(class)ss',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

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
