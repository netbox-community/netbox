from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from dcim.constants import *
from dcim.managers import InterfaceManager
from extras.models import ObjectChange
from utilities.managers import NaturalOrderingManager
from utilities.utils import serialize_object


class ComponentTemplateModel(models.Model):

    class Meta:
        abstract = True

    def log_change(self, user, request_id, action):
        """
        Log an ObjectChange including the parent DeviceType.
        """
        ObjectChange(
            user=user,
            request_id=request_id,
            changed_object=self,
            related_object=self.device_type,
            action=action,
            object_data=serialize_object(self)
        ).save()


class ConsolePortTemplate(ComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='consoleport_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class ConsoleServerPortTemplate(ComponentTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='consoleserverport_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class PowerPortTemplate(ComponentTemplateModel):
    """
    A template for a PowerPort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='powerport_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class PowerOutletTemplate(ComponentTemplateModel):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='poweroutlet_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class InterfaceTemplate(ComponentTemplateModel):
    """
    A template for a physical data interface on a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='interface_templates'
    )
    name = models.CharField(
        max_length=64
    )
    form_factor = models.PositiveSmallIntegerField(
        choices=IFACE_FF_CHOICES,
        default=IFACE_FF_10GE_SFP_PLUS
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only'
    )

    objects = InterfaceManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class FrontPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPortTemplate',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = [
            ['device_type', 'name'],
            ['rear_port', 'rear_port_position'],
        ]

    def __str__(self):
        return self.name

    def clean(self):

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


class RearPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the rear of a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='rearport_templates'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class DeviceBayTemplate(ComponentTemplateModel):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='device_bay_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name
