from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from dcim.choices import *
from dcim.constants import *
from extras.utils import extras_features
from netbox.models import ChangeLoggedModel
from utilities.fields import NaturalOrderingField
from utilities.querysets import RestrictedQuerySet
from utilities.ordering import naturalize_interface
from .device_components import (
    ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface, PowerOutlet, PowerPort, RearPort,
)


__all__ = (
    'ConsolePortTemplate',
    'ConsoleServerPortTemplate',
    'DeviceBayTemplate',
    'FrontPortTemplate',
    'InterfaceTemplate',
    'PowerOutletTemplate',
    'PowerPortTemplate',
    'RearPortTemplate',
)


class ComponentTemplateModel(ChangeLoggedModel):
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text="Physical label"
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        if self.label:
            return f"{self.name} ({self.label})"
        return self.name

    def instantiate(self, device):
        """
        Instantiate a new component on the specified Device.
        """
        raise NotImplementedError()

    def to_objectchange(self, action):
        # Annotate the parent DeviceType
        try:
            device_type = self.device_type
        except ObjectDoesNotExist:
            # The parent DeviceType has already been deleted
            device_type = None
        return super().to_objectchange(action, related_object=device_type)


@extras_features('webhooks')
class ConsolePortTemplate(ComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return ConsolePort(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type
        )


@extras_features('webhooks')
class ConsoleServerPortTemplate(ComponentTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return ConsoleServerPort(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type
        )


@extras_features('webhooks')
class PowerPortTemplate(ComponentTemplateModel):
    """
    A template for a PowerPort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated power draw (watts)"
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return PowerPort(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type,
            maximum_draw=self.maximum_draw,
            allocated_draw=self.allocated_draw
        )

    def clean(self):
        super().clean()

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': f"Allocated draw cannot exceed the maximum draw ({self.maximum_draw}W)."
                })


@extras_features('webhooks')
class PowerOutletTemplate(ComponentTemplateModel):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPortTemplate',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlet_templates'
    )
    feed_leg = models.CharField(
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        help_text="Phase (for three-phase feeds)"
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def clean(self):
        super().clean()

        # Validate power port assignment
        if self.power_port and self.power_port.device_type != self.device_type:
            raise ValidationError(
                "Parent power port ({}) must belong to the same device type".format(self.power_port)
            )

    def instantiate(self, device):
        if self.power_port:
            power_port = PowerPort.objects.get(device=device, name=self.power_port.name)
        else:
            power_port = None
        return PowerOutlet(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type,
            power_port=power_port,
            feed_leg=self.feed_leg
        )


@extras_features('webhooks')
class InterfaceTemplate(ComponentTemplateModel):
    """
    A template for a physical data interface on a new Device.
    """
    # Override ComponentTemplateModel._name to specify naturalize_interface function
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only'
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return Interface(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type,
            mgmt_only=self.mgmt_only
        )


@extras_features('webhooks')
class FrontPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPortTemplate',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = (
            ('device_type', 'name'),
            ('rear_port', 'rear_port_position'),
        )

    def clean(self):
        super().clean()

        # Validate rear port assignment
        if self.rear_port.device_type != self.device_type:
            raise ValidationError(
                "Rear port ({}) must belong to the same device type".format(self.rear_port)
            )

        # Validate rear port position assignment
        if self.rear_port_position > self.rear_port.positions:
            raise ValidationError(
                "Invalid rear port position ({}); rear port {} has only {} positions".format(
                    self.rear_port_position, self.rear_port.name, self.rear_port.positions
                )
            )

    def instantiate(self, device):
        if self.rear_port:
            rear_port = RearPort.objects.get(device=device, name=self.rear_port.name)
        else:
            rear_port = None
        return FrontPort(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type,
            rear_port=rear_port,
            rear_port_position=self.rear_port_position
        )


@extras_features('webhooks')
class RearPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the rear of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return RearPort(
            device=device,
            name=self.name,
            label=self.label,
            type=self.type,
            positions=self.positions
        )


@extras_features('webhooks')
class DeviceBayTemplate(ComponentTemplateModel):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    class Meta:
        ordering = ('device_type', '_name')
        unique_together = ('device_type', 'name')

    def instantiate(self, device):
        return DeviceBay(
            device=device,
            name=self.name,
            label=self.label
        )

    def clean(self):
        if self.device_type and self.device_type.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
            raise ValidationError(
                f"Subdevice role of device type ({self.device_type}) must be set to \"parent\" to allow device bays."
            )
