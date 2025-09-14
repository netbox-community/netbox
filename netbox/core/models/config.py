from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ConfigRevision',
)


class ConfigRevision(models.Model):
    """
    An atomic revision of NetBox's configuration.
    """
    active = models.BooleanField(
        default=False
    )
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    comment = models.CharField(
        verbose_name=_('comment'),
        max_length=200,
        blank=True
    )
    data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('configuration data')
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['-created']
        verbose_name = _('config revision')
        verbose_name_plural = _('config revisions')
        constraints = [
            models.UniqueConstraint(
                fields=('active',),
                condition=models.Q(active=True),
                name='unique_active_config_revision',
            )
        ]

    def __str__(self):
        if not self.pk:
            return gettext('Default configuration')
        if self.is_active:
            return gettext('Current configuration')
        return gettext('Config revision #{id}').format(id=self.pk)

    def __getattr__(self, item):
        if self.data and item in self.data:
            return self.data[item]
        return super().__getattribute__(item)

    def get_absolute_url(self):
        if not self.pk:
            return reverse('core:config')  # Default config view
        return reverse('core:configrevision', args=[self.pk])

    def activate(self):
        """
        Cache the configuration data.
        """
        cache.set('config', self.data, None)
        cache.set('config_version', self.pk, None)

        # Set all instances of ConfigRevision to false and set this instance to true
        ConfigRevision.objects.all().update(active=False)
        ConfigRevision.objects.filter(pk=self.pk).update(active=True)

    activate.alters_data = True

    @property
    def is_active(self):
        return self.active
