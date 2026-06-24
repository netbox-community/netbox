from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from netbox.choices import TemperatureUnitChoices
from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from netbox.models.mixins import FlowRateMixin, PressureMixin
from utilities.conversion import to_celsius

from .device_components import CabledObjectModel, PathEndpoint

__all__ = (
    'CoolingFeed',
    'CoolingSource',
)


#
# Cooling
#

class CoolingTemperatureMixin(models.Model):
    """
    Adds design supply/return temperatures sharing a single unit, with normalized (°C) fields for ordering.
    """
    supply_temperature = models.DecimalField(
        verbose_name=_('supply temperature'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Supply (cold) temperature')
    )
    return_temperature = models.DecimalField(
        verbose_name=_('return temperature'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Return (warm) temperature')
    )
    temperature_unit = models.CharField(
        verbose_name=_('temperature unit'),
        max_length=50,
        choices=TemperatureUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized temperatures (in degrees Celsius) for database ordering
    _abs_supply_temperature = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True
    )
    _abs_return_temperature = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_supply_temperature(self):
        # Public alias for _abs_supply_temperature; Django templates cannot access underscore-prefixed attributes.
        return self._abs_supply_temperature

    @property
    def abs_return_temperature(self):
        # Public alias for _abs_return_temperature; Django templates cannot access underscore-prefixed attributes.
        return self._abs_return_temperature

    def save(self, *args, **kwargs):
        # Store the given temperatures (if any) in degrees Celsius for use in database ordering
        if self.temperature_unit:
            self._abs_supply_temperature = (
                to_celsius(self.supply_temperature, self.temperature_unit)
                if self.supply_temperature is not None else None
            )
            self._abs_return_temperature = (
                to_celsius(self.return_temperature, self.temperature_unit)
                if self.return_temperature is not None else None
            )
        else:
            self._abs_supply_temperature = None
            self._abs_return_temperature = None

        # Clear temperature_unit if no temperatures are defined
        if self.supply_temperature is None and self.return_temperature is None:
            self.temperature_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # A temperature unit is required when a temperature is set
        if (self.supply_temperature is not None or self.return_temperature is not None) and not self.temperature_unit:
            raise ValidationError(_("Must specify a unit when setting a temperature"))


class CoolingSource(CoolingTemperatureMixin, ContactsMixin, ImageAttachmentsMixin, PrimaryModel):
    """
    A facility-level source of cooling; e.g. a chiller, cooling tower, or dry cooler.
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
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CoolingSourceTypeChoices
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=CoolingSourceStatusChoices,
        default=CoolingSourceStatusChoices.STATUS_ACTIVE
    )
    cooling_capacity = models.DecimalField(
        verbose_name=_('cooling capacity'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Total cooling capacity (kW)')
    )
    # supply_temperature, return_temperature, temperature_unit, _abs_* provided by CoolingTemperatureMixin

    clone_fields = (
        'site', 'location', 'type', 'status', 'cooling_capacity', 'supply_temperature', 'return_temperature',
        'temperature_unit',
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
        verbose_name = _('cooling source')
        verbose_name_plural = _('cooling sources')

    def __str__(self):
        return self.name

    def get_status_color(self):
        return CoolingSourceStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        # Location must belong to assigned Site
        if self.location and self.location.site != self.site:
            raise ValidationError(
                _("Location {location} ({location_site}) is in a different site than {site}").format(
                    location=self.location, location_site=self.location.site, site=self.site)
            )


class CoolingFeed(CoolingTemperatureMixin, FlowRateMixin, PressureMixin, PrimaryModel, PathEndpoint, CabledObjectModel):
    """
    A coolant loop delivered from a CoolingSource to a rack or CDU. Supply and return loops are
    represented as separate feeds so each can be traced independently.
    """
    cooling_source = models.ForeignKey(
        to='CoolingSource',
        on_delete=models.PROTECT,
        related_name='cooling_feeds'
    )
    rack = models.ForeignKey(
        to='Rack',
        on_delete=models.PROTECT,
        related_name='cooling_feeds',
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
        choices=CoolingFeedStatusChoices,
        default=CoolingFeedStatusChoices.STATUS_ACTIVE
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CoolingFeedTypeChoices,
        default=CoolingFeedTypeChoices.TYPE_SUPPLY
    )
    fluid_type = models.CharField(
        verbose_name=_('fluid type'),
        max_length=50,
        choices=FluidTypeChoices,
        blank=True,
        null=True
    )
    cooling_capacity = models.DecimalField(
        verbose_name=_('cooling capacity'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Cooling capacity (kW)')
    )
    # flow_rate, flow_rate_unit, _abs_flow_rate provided by FlowRateMixin
    # pressure, pressure_unit, _abs_pressure provided by PressureMixin
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='cooling_feeds',
        blank=True,
        null=True
    )

    clone_fields = (
        'cooling_source', 'rack', 'status', 'type', 'mark_connected', 'fluid_type', 'cooling_capacity', 'flow_rate',
        'flow_rate_unit', 'pressure', 'pressure_unit', 'supply_temperature', 'return_temperature', 'temperature_unit',
        'tenant',
    )
    prerequisite_models = (
        'dcim.CoolingSource',
    )

    class Meta:
        ordering = ['cooling_source', 'name']
        constraints = (
            models.UniqueConstraint(
                fields=('cooling_source', 'name'),
                name='%(app_label)s_%(class)s_unique_cooling_source_name'
            ),
        )
        verbose_name = _('cooling feed')
        verbose_name_plural = _('cooling feeds')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Rack must belong to same Site as CoolingSource
        if self.rack and self.rack.site != self.cooling_source.site:
            raise ValidationError(_(
                "Rack {rack} ({rack_site}) and cooling source {source} ({source_site}) are in different sites."
            ).format(
                rack=self.rack,
                rack_site=self.rack.site,
                source=self.cooling_source,
                source_site=self.cooling_source.site
            ))

    @property
    def parent_object(self):
        return self.cooling_source

    def get_type_color(self):
        return CoolingFeedTypeChoices.colors.get(self.type)

    def get_status_color(self):
        return CoolingFeedStatusChoices.colors.get(self.status)
