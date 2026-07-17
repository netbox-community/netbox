from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from netbox.choices import FlowRateUnitChoices
from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from utilities.conversion import to_liters_per_minute

__all__ = (
    'CoolingFeed',
    'CoolingSource',
)


#
# Cooling
#

class CoolingSource(ContactsMixin, ImageAttachmentsMixin, PrimaryModel):
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
        help_text=_('Total rated cooling capacity (kW)')
    )

    clone_fields = (
        'site', 'location', 'type', 'status', 'fluid_type', 'cooling_capacity',
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


class CoolingFeed(PrimaryModel):
    """
    A coolant loop delivered from a CoolingSource to a rack or CDU. A single feed represents the entire
    loop (both the supply and return paths). A CoolingFeed supplies one or more CoolingIntakes
    (referenced via CoolingIntake.cooling_feed) rather than being cabled.

    Rated flow rate is a design specification (the intended operating envelope), not live telemetry;
    runtime readings belong in an external monitoring system.
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
    cooling_capacity = models.DecimalField(
        verbose_name=_('cooling capacity'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Rated cooling capacity (kW)')
    )
    rated_flow_rate = models.DecimalField(
        verbose_name=_('rated flow rate'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Rated (design) flow rate')
    )
    rated_flow_rate_unit = models.CharField(
        verbose_name=_('rated flow rate unit'),
        max_length=50,
        choices=FlowRateUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized rated flow rate (in liters per minute) for database ordering
    _abs_rated_flow_rate = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='cooling_feeds',
        blank=True,
        null=True
    )

    clone_fields = (
        'cooling_source', 'rack', 'status', 'cooling_capacity', 'rated_flow_rate',
        'rated_flow_rate_unit', 'tenant',
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

    def save(self, *args, **kwargs):
        # Store the given rated flow rate (if any) in liters per minute for use in database ordering
        if self.rated_flow_rate is not None and self.rated_flow_rate_unit:
            self._abs_rated_flow_rate = to_liters_per_minute(self.rated_flow_rate, self.rated_flow_rate_unit)
        else:
            self._abs_rated_flow_rate = None

        # Clear rated_flow_rate_unit if no rated flow rate is defined
        if self.rated_flow_rate is None:
            self.rated_flow_rate_unit = None

        super().save(*args, **kwargs)

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

        # A rated flow rate unit is required when a rated flow rate is set
        if self.rated_flow_rate is not None and not self.rated_flow_rate_unit:
            raise ValidationError(_("Must specify a unit when setting a rated flow rate"))

    @property
    def abs_rated_flow_rate(self):
        # Public alias for _abs_rated_flow_rate; Django templates cannot access underscore-prefixed attributes.
        return self._abs_rated_flow_rate

    @property
    def parent_object(self):
        return self.cooling_source

    def get_status_color(self):
        return CoolingFeedStatusChoices.colors.get(self.status)
