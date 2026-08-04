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
    to_liters_per_minute,
    to_millimeters,
)

__all__ = (
    'CachedScopeMixin',
    'CoolingLoopValidationMixin',
    'DiameterMixin',
    'InterfaceValidationMixin',
    'MaxFlowMixin',
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


class CoolingLoopValidationMixin:
    """
    Adds loop detection to the coolant chain formed by cooling intakes and outflows. A CoolingIntake is supplied
    by an upstream CoolingOutflow (via `cooling_outflow`), which may in turn be supplied by an upstream
    CoolingIntake on the same device (via `cooling_intake`), and so on; this chain must remain acyclic.

    Each concrete model declares `upstream_field`, the name of its foreign key to the next component upstream.
    The chain alternates between the two models, so the walk simply follows each visited component's own
    upstream field in turn. (The field is resolved by name rather than referencing the models directly, as this
    module is imported by the ones defining them.)
    """
    upstream_field = None

    @classmethod
    def _get_upstream_field(cls):
        return cls._meta.get_field(cls.upstream_field)

    def validate_cooling_loop(self):
        """
        Raise a ValidationError if this component's upstream assignment forms a loop.

        Each hop resolves only the next foreign key ID (a single indexed column lookup) rather than loading
        full related objects, and the `seen` set of (model, pk) pairs guarantees termination.
        """
        seen = set()
        if self.pk:
            seen.add((type(self), self.pk))

        # Seed the walk from this (possibly unsaved) component's in-memory foreign key
        field = self._get_upstream_field()
        model, pk = field.related_model, getattr(self, field.attname)

        while pk is not None:
            if (model, pk) in seen:
                raise ValidationError(_("Cooling intake and outflow assignments cannot form a loop."))
            seen.add((model, pk))

            # Advance to the component upstream of the one just visited
            field = model._get_upstream_field()
            pk = model.objects.filter(pk=pk).values_list(field.attname, flat=True).first()
            model = field.related_model


class DiameterMixin(models.Model):
    diameter = models.DecimalField(
        verbose_name=_('diameter'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
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

    def normalize_diameter(self):
        """
        Store the given diameter (if any) in millimeters for use in database ordering. Called by save(), and
        directly by component instantiation, which bypasses save() via bulk_create().
        """
        if self.diameter is not None and self.diameter_unit:
            self._abs_diameter = to_millimeters(self.diameter, self.diameter_unit)
        else:
            self._abs_diameter = None
        if self.diameter is None:
            self.diameter_unit = None
    normalize_diameter.alters_data = True

    def save(self, *args, **kwargs):
        self.normalize_diameter()

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate diameter and diameter_unit
        if self.diameter is not None and not self.diameter_unit:
            raise ValidationError(_("Must specify a unit when setting a diameter"))


class MaxFlowMixin(models.Model):
    """
    Adds the maximum rate of coolant flow supported by an object, held as a value plus its unit alongside a
    normalized column (in liters per minute) so that ordering and filtering work across mixed units.
    """
    max_flow = models.DecimalField(
        verbose_name=_('max flow'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
    )
    max_flow_unit = models.CharField(
        verbose_name=_('max flow unit'),
        max_length=50,
        choices=FlowRateUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized max flow (in liters per minute) for database ordering
    _abs_max_flow = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_max_flow(self):
        # Public alias for _abs_max_flow; Django templates cannot access underscore-prefixed attributes.
        return self._abs_max_flow

    def normalize_max_flow(self):
        """
        Store the given max flow (if any) in liters per minute for use in database ordering. Called by save(),
        and directly by component instantiation, which bypasses save() via bulk_create().
        """
        if self.max_flow is not None and self.max_flow_unit:
            self._abs_max_flow = to_liters_per_minute(self.max_flow, self.max_flow_unit)
        else:
            self._abs_max_flow = None
        if self.max_flow is None:
            self.max_flow_unit = None
    normalize_max_flow.alters_data = True

    def save(self, *args, **kwargs):
        self.normalize_max_flow()

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate max_flow and max_flow_unit
        if self.max_flow is not None and not self.max_flow_unit:
            raise ValidationError(_("Must specify a unit when setting a maximum flow"))
