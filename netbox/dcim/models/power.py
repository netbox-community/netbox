from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from netbox.config import ConfigItem
from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from utilities.validators import ExclusionValidator
from .device_components import CabledObjectModel, PathEndpoint

__all__ = (
    'PowerFeed',
    'PowerPanel',
)


#
# Power
#

class PowerPanel(ContactsMixin, ImageAttachmentsMixin, PrimaryModel):
    """
    A distribution point for electrical power; e.g. a data center RPP.
    """
    site = models.ForeignKey(
        to='Site',
        on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        db_collation="natural_sort"
    )

    prerequisite_models = (
        'dcim.Site',
    )

    class Meta:
        ordering = ['site', 'name']
        constraints = (
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name'
            ),
        )
        verbose_name = _('power panel')
        verbose_name_plural = _('power panels')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Location must belong to assigned Site
        if self.location and self.location.site != self.site:
            raise ValidationError(
                _("Location {location} ({location_site}) is in a different site than {site}").format(
                    location=self.location, location_site=self.location.site, site=self.site)
            )


class PowerFeed(PrimaryModel, PathEndpoint, CabledObjectModel):
    """
    An electrical circuit delivered from a PowerPanel.
    """
    power_panel = models.ForeignKey(
        to='PowerPanel',
        on_delete=models.PROTECT,
        related_name='powerfeeds'
    )
    rack = models.ForeignKey(
        to='Rack',
        on_delete=models.PROTECT,
        related_name='powerfeeds',
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        db_collation="natural_sort"
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=PowerFeedStatusChoices,
        default=PowerFeedStatusChoices.STATUS_ACTIVE
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PowerFeedTypeChoices,
        default=PowerFeedTypeChoices.TYPE_PRIMARY
    )
    supply = models.CharField(
        verbose_name=_('supply'),
        max_length=50,
        choices=PowerFeedSupplyChoices,
        default=PowerFeedSupplyChoices.SUPPLY_AC
    )
    phase = models.CharField(
        verbose_name=_('phase'),
        max_length=50,
        choices=PowerFeedPhaseChoices,
        default=PowerFeedPhaseChoices.PHASE_SINGLE
    )
    voltage = models.SmallIntegerField(
        verbose_name=_('voltage'),
        default=ConfigItem('POWERFEED_DEFAULT_VOLTAGE'),
        validators=[ExclusionValidator([0])]
    )
    amperage = models.PositiveSmallIntegerField(
        verbose_name=_('amperage'),
        validators=[MinValueValidator(1)],
        default=ConfigItem('POWERFEED_DEFAULT_AMPERAGE')
    )
    max_utilization = models.PositiveSmallIntegerField(
        verbose_name=_('max utilization'),
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=ConfigItem('POWERFEED_DEFAULT_MAX_UTILIZATION'),
        help_text=_("Maximum permissible draw (percentage)")
    )
    available_power = models.PositiveIntegerField(
        verbose_name=_('available power'),
        default=0,
        editable=False
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='power_feeds',
        blank=True,
        null=True
    )

    clone_fields = (
        'power_panel', 'rack', 'status', 'type', 'mark_connected', 'supply', 'phase', 'voltage', 'amperage',
        'max_utilization', 'tenant',
    )
    prerequisite_models = (
        'dcim.PowerPanel',
    )

    class Meta:
        ordering = ['power_panel', 'name']
        constraints = (
            models.UniqueConstraint(
                fields=('power_panel', 'name'),
                name='%(app_label)s_%(class)s_unique_power_panel_name'
            ),
        )
        verbose_name = _('power feed')
        verbose_name_plural = _('power feeds')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Rack must belong to same Site as PowerPanel
        if self.rack and self.rack.site != self.power_panel.site:
            raise ValidationError(_(
                "Rack {rack} ({rack_site}) and power panel {powerpanel} ({powerpanel_site}) are in different sites."
            ).format(
                rack=self.rack,
                rack_site=self.rack.site,
                powerpanel=self.power_panel,
                powerpanel_site=self.power_panel.site
            ))

        # AC voltage cannot be negative
        if self.voltage < 0 and self.supply == PowerFeedSupplyChoices.SUPPLY_AC:
            raise ValidationError({
                "voltage": _("Voltage cannot be negative for AC supply")
            })

    def save(self, *args, **kwargs):

        # Cache the available_power property on the instance
        kva = abs(self.voltage) * self.amperage * (self.max_utilization / 100)
        if self.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)

        super().save(*args, **kwargs)

    @property
    def parent_object(self):
        return self.power_panel

    def get_type_color(self):
        return PowerFeedTypeChoices.colors.get(self.type)

    def get_status_color(self):
        return PowerFeedStatusChoices.colors.get(self.status)
