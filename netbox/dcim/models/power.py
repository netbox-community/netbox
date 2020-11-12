from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from dcim.choices import *
from dcim.constants import *
from extras.models import ChangeLoggedModel, CustomFieldModel, TaggedItem
from extras.utils import extras_features
from utilities.querysets import RestrictedQuerySet
from utilities.validators import ExclusionValidator
from .device_components import CableTermination, PathEndpoint

__all__ = (
    'PowerFeed',
    'PowerPanel',
)


#
# Power
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class PowerPanel(ChangeLoggedModel, CustomFieldModel):
    """
    A distribution point for electrical power; e.g. a data center RPP.
    """
    site = models.ForeignKey(
        to='Site',
        on_delete=models.PROTECT
    )
    rack_group = models.ForeignKey(
        to='RackGroup',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=100
    )
    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['site', 'rack_group', 'name']

    class Meta:
        ordering = ['site', 'name']
        unique_together = ['site', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerpanel', args=[self.pk])

    def to_csv(self):
        return (
            self.site.name,
            self.rack_group.name if self.rack_group else None,
            self.name,
        )

    def clean(self):
        super().clean()

        # RackGroup must belong to assigned Site
        if self.rack_group and self.rack_group.site != self.site:
            raise ValidationError("Rack group {} ({}) is in a different site than {}".format(
                self.rack_group, self.rack_group.site, self.site
            ))


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class PowerFeed(ChangeLoggedModel, PathEndpoint, CableTermination, CustomFieldModel):
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
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=100
    )
    status = models.CharField(
        max_length=50,
        choices=PowerFeedStatusChoices,
        default=PowerFeedStatusChoices.STATUS_ACTIVE
    )
    type = models.CharField(
        max_length=50,
        choices=PowerFeedTypeChoices,
        default=PowerFeedTypeChoices.TYPE_PRIMARY
    )
    supply = models.CharField(
        max_length=50,
        choices=PowerFeedSupplyChoices,
        default=PowerFeedSupplyChoices.SUPPLY_AC
    )
    phase = models.CharField(
        max_length=50,
        choices=PowerFeedPhaseChoices,
        default=PowerFeedPhaseChoices.PHASE_SINGLE
    )
    voltage = models.SmallIntegerField(
        default=POWERFEED_VOLTAGE_DEFAULT,
        validators=[ExclusionValidator([0])]
    )
    amperage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=POWERFEED_AMPERAGE_DEFAULT
    )
    max_utilization = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=POWERFEED_MAX_UTILIZATION_DEFAULT,
        help_text="Maximum permissible draw (percentage)"
    )
    available_power = models.PositiveIntegerField(
        default=0,
        editable=False
    )
    comments = models.TextField(
        blank=True
    )
    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'site', 'power_panel', 'rack_group', 'rack', 'name', 'status', 'type', 'supply', 'phase', 'voltage',
        'amperage', 'max_utilization', 'comments',
    ]
    clone_fields = [
        'power_panel', 'rack', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization',
        'available_power',
    ]

    class Meta:
        ordering = ['power_panel', 'name']
        unique_together = ['power_panel', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerfeed', args=[self.pk])

    def to_csv(self):
        return (
            self.power_panel.site.name,
            self.power_panel.name,
            self.rack.group.name if self.rack and self.rack.group else None,
            self.rack.name if self.rack else None,
            self.name,
            self.get_status_display(),
            self.get_type_display(),
            self.get_supply_display(),
            self.get_phase_display(),
            self.voltage,
            self.amperage,
            self.max_utilization,
            self.comments,
        )

    def clean(self):
        super().clean()

        # Rack must belong to same Site as PowerPanel
        if self.rack and self.rack.site != self.power_panel.site:
            raise ValidationError("Rack {} ({}) and power panel {} ({}) are in different sites".format(
                self.rack, self.rack.site, self.power_panel, self.power_panel.site
            ))

        # AC voltage cannot be negative
        if self.voltage < 0 and self.supply == PowerFeedSupplyChoices.SUPPLY_AC:
            raise ValidationError({
                "voltage": "Voltage cannot be negative for AC supply"
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
    def parent(self):
        return self.power_panel

    def get_type_class(self):
        return PowerFeedTypeChoices.CSS_CLASSES.get(self.type)

    def get_status_class(self):
        return PowerFeedStatusChoices.CSS_CLASSES.get(self.status)
