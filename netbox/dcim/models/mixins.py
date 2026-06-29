from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfaceTypeChoices
from dcim.constants import NONCONNECTABLE_IFACE_TYPES, VIRTUAL_IFACE_TYPES, WIRELESS_IFACE_TYPES
from netbox.choices import *
from utilities.conversion import (
    to_celsius,
    to_kilopascals,
    to_liters_per_minute,
    to_millimeters,
)

__all__ = (
    'CachedScopeMixin',
    'CoolingTemperatureMixin',
    'DiameterMixin',
    'FlowRateMixin',
    'InterfaceValidationMixin',
    'MaximumFlowMixin',
    'PressureMixin',
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
        return None


class CachedScopeMixin(models.Model):
    """
    Mixin for adding a GenericForeignKey scope to a model that can point to a Region, SiteGroup, Site, or Location.
    Includes cached fields for each to allow efficient filtering. Appropriate validation must be done in the clean()
    method as this does not have any as validation is generally model-specific.
    """
    scope_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
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

    _location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    _site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    # SET_NULL, not CASCADE: these cache an ancestor of the actual scope, so deleting that
    # ancestor must not delete this object. Deletion of a Region/SiteGroup that *is* the
    # actual scope is handled independently via its GenericRelation to this model.
    _region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    _site_group = models.ForeignKey(
        to='dcim.SiteGroup',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def clean(self):
        if self.scope_type and not (self.scope or self.scope_id):
            scope_type = self.scope_type.model_class()
            raise ValidationError(
                _("Please select a {scope_type}.").format(scope_type=scope_type._meta.model_name)
            )
        super().clean()

    def save(self, *args, **kwargs):
        # Cache objects associated with the terminating object (for filtering)
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self):
        self._region = self._site_group = self._site = self._location = None
        if self.scope_type:
            scope_type = self.scope_type.model_class()
            if scope_type == apps.get_model('dcim', 'region'):
                self._region = self.scope
            elif scope_type == apps.get_model('dcim', 'sitegroup'):
                self._site_group = self.scope
            elif scope_type == apps.get_model('dcim', 'site'):
                self._region = self.scope.region
                self._site_group = self.scope.group
                self._site = self.scope
            elif scope_type == apps.get_model('dcim', 'location'):
                self._region = self.scope.site.region
                self._site_group = self.scope.site.group
                self._site = self.scope.site
                self._location = self.scope
    cache_related_objects.alters_data = True


class InterfaceValidationMixin:

    def clean(self):
        super().clean()

        # An interface cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': _("An interface cannot be its own parent.")})

        # Only virtual and channel interfaces may have a parent interface
        if self.parent_id and self.type not in (InterfaceTypeChoices.TYPE_VIRTUAL, InterfaceTypeChoices.TYPE_CHANNEL):
            raise ValidationError({
                'parent': _("Only virtual and channel interfaces may be assigned to a parent interface.")
            })

        # Only one layer of channelization is permitted: an interface cannot be both channelized and a channel
        if self.channels and self.channel_id:
            raise ValidationError(
                _("An interface cannot be both channelized and bound to a channel on a parent interface.")
            )

        # Only physical interfaces may be channelized
        if self.channels and self.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'channels': _("{display_type} interfaces cannot be channelized.").format(
                    display_type=self.get_type_display()
                )
            })

        # The channel type and channel_id are mutually dependent. The channel_id requirement is relaxed for a
        # replication base (bulk creation), where each channel_id is supplied per-instance during expansion.
        is_channel = self.type == InterfaceTypeChoices.TYPE_CHANNEL
        if is_channel and self.channel_id is None and not getattr(self, '_replicated_base', False):
            raise ValidationError({
                'channel_id': _("Channel interfaces must have a channel ID assigned.")
            })
        if self.channel_id is not None and not is_channel:
            raise ValidationError({
                'channel_id': _("A channel ID can be assigned only to a channel-type interface.")
            })

        # A channel subinterface must be bound to a channelized parent interface
        if is_channel:
            if self.parent is None:
                raise ValidationError({
                    'parent': _("Channel interfaces must be assigned to a parent interface.")
                })
            if not self.parent.channels:
                raise ValidationError({
                    'parent': _("The parent interface ({interface}) is not channelized.").format(
                        interface=self.parent
                    )
                })
            if self.channel_id and self.channel_id > self.parent.channels:
                raise ValidationError({
                    'channel_id': _(
                        "Invalid channel ID ({channel_id}): the parent interface provides only {channels} channels."
                    ).format(channel_id=self.channel_id, channels=self.parent.channels)
                })

        # Reducing or clearing the channel count cannot orphan an existing channel subinterface bound to a higher
        # channel (clearing channelization entirely would orphan every bound subinterface). Gated on the current or
        # original channel count so the child lookup stays off the hot path for ordinary (never-channelized) interfaces.
        if self.pk and (self.channels or self._original_channels):
            max_child_channel_id = self.child_interfaces.filter(
                channel_id__gt=self.channels or 0
            ).aggregate(models.Max('channel_id'))['channel_id__max']
            if max_child_channel_id is not None:
                if self.channels:
                    message = _(
                        "Cannot set channels to {channels}: a channel subinterface is bound to channel "
                        "{channel_id}. Delete or reassign the affected subinterface(s) first."
                    ).format(channels=self.channels, channel_id=max_child_channel_id)
                else:
                    message = _(
                        "Cannot remove channelization: a channel subinterface is bound to channel {channel_id}. "
                        "Delete or reassign the affected subinterface(s) first."
                    ).format(channel_id=max_child_channel_id)
                raise ValidationError({'channels': message})

        # An interface cannot be bridged to itself
        if self.pk and self.bridge_id == self.pk:
            raise ValidationError({'bridge': _("An interface cannot be bridged to itself.")})

        # Only physical interfaces may have a PoE mode/type assigned
        if self.poe_mode and self.type in VIRTUAL_IFACE_TYPES:
            raise ValidationError({
                'poe_mode': _("Virtual interfaces cannot have a PoE mode.")
            })
        if self.poe_type and self.type in VIRTUAL_IFACE_TYPES:
            raise ValidationError({
                'poe_type': _("Virtual interfaces cannot have a PoE type.")
            })

        # An interface with a PoE type set must also specify a mode
        if self.poe_type and not self.poe_mode:
            raise ValidationError({
                'poe_type': _("Must specify PoE mode when designating a PoE type.")
            })

        # RF role may be set only for wireless interfaces
        if self.rf_role and self.type not in WIRELESS_IFACE_TYPES:
            raise ValidationError({'rf_role': _("Wireless role may be set only on wireless interfaces.")})


class DiameterMixin(models.Model):
    diameter = models.DecimalField(
        verbose_name=_('diameter'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    diameter_unit = models.CharField(
        verbose_name=_('diameter unit'),
        max_length=50,
        choices=DiameterUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized diameter (in millimeters) for database ordering
    _abs_diameter = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_diameter(self):
        # Public alias for _abs_diameter; Django templates cannot access underscore-prefixed attributes.
        return self._abs_diameter

    def save(self, *args, **kwargs):
        # Store the given diameter (if any) in millimeters for use in database ordering
        if self.diameter is not None and self.diameter_unit:
            self._abs_diameter = to_millimeters(self.diameter, self.diameter_unit)
        else:
            self._abs_diameter = None

        # Clear diameter_unit if no diameter is defined
        if self.diameter is None:
            self.diameter_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate diameter and diameter_unit
        if self.diameter is not None and not self.diameter_unit:
            raise ValidationError(_("Must specify a unit when setting a diameter"))


class FlowRateMixin(models.Model):
    flow_rate = models.DecimalField(
        verbose_name=_('flow rate'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    flow_rate_unit = models.CharField(
        verbose_name=_('flow rate unit'),
        max_length=50,
        choices=FlowRateUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized flow rate (in liters per minute) for database ordering
    _abs_flow_rate = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_flow_rate(self):
        # Public alias for _abs_flow_rate; Django templates cannot access underscore-prefixed attributes.
        return self._abs_flow_rate

    def save(self, *args, **kwargs):
        # Store the given flow rate (if any) in liters per minute for use in database ordering
        if self.flow_rate is not None and self.flow_rate_unit:
            self._abs_flow_rate = to_liters_per_minute(self.flow_rate, self.flow_rate_unit)
        else:
            self._abs_flow_rate = None

        # Clear flow_rate_unit if no flow rate is defined
        if self.flow_rate is None:
            self.flow_rate_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate flow_rate and flow_rate_unit
        if self.flow_rate is not None and not self.flow_rate_unit:
            raise ValidationError(_("Must specify a unit when setting a flow rate"))


class MaximumFlowMixin(models.Model):
    maximum_flow = models.DecimalField(
        verbose_name=_('maximum flow'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    maximum_flow_unit = models.CharField(
        verbose_name=_('maximum flow unit'),
        max_length=50,
        choices=FlowRateUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized maximum flow (in liters per minute) for database ordering
    _abs_maximum_flow = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_maximum_flow(self):
        # Public alias for _abs_maximum_flow; Django templates cannot access underscore-prefixed attributes.
        return self._abs_maximum_flow

    def save(self, *args, **kwargs):
        # Store the given maximum flow (if any) in liters per minute for use in database ordering
        if self.maximum_flow is not None and self.maximum_flow_unit:
            self._abs_maximum_flow = to_liters_per_minute(self.maximum_flow, self.maximum_flow_unit)
        else:
            self._abs_maximum_flow = None

        # Clear maximum_flow_unit if no maximum flow is defined
        if self.maximum_flow is None:
            self.maximum_flow_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate maximum_flow and maximum_flow_unit
        if self.maximum_flow is not None and not self.maximum_flow_unit:
            raise ValidationError(_("Must specify a unit when setting a maximum flow"))


class PressureMixin(models.Model):
    pressure = models.DecimalField(
        verbose_name=_('pressure'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    pressure_unit = models.CharField(
        verbose_name=_('pressure unit'),
        max_length=50,
        choices=PressureUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized pressure (in kilopascals) for database ordering
    _abs_pressure = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_pressure(self):
        # Public alias for _abs_pressure; Django templates cannot access underscore-prefixed attributes.
        return self._abs_pressure

    def save(self, *args, **kwargs):
        # Store the given pressure (if any) in kilopascals for use in database ordering
        if self.pressure is not None and self.pressure_unit:
            self._abs_pressure = to_kilopascals(self.pressure, self.pressure_unit)
        else:
            self._abs_pressure = None

        # Clear pressure_unit if no pressure is defined
        if self.pressure is None:
            self.pressure_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate pressure and pressure_unit
        if self.pressure is not None and not self.pressure_unit:
            raise ValidationError(_("Must specify a unit when setting a pressure"))


class CoolingTemperatureMixin(models.Model):
    """
    Adds supply/return temperatures sharing a single unit, with normalized (°C) fields for ordering.
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
