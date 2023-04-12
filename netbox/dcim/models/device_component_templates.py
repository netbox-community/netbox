from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext as _
from mptt.models import MPTTModel, TreeForeignKey

from dcim.choices import *
from dcim.constants import *
from netbox.models import ChangeLoggedModel
from netbox.models.features import WebhooksMixin
from utilities.fields import ColorField, NaturalOrderingField
from utilities.mptt import TreeManager
from utilities.ordering import naturalize_interface
from .device_components import (
    ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface, InventoryItem, ModuleBay, PowerOutlet, PowerPort,
    RearPort,
)


__all__ = (
    'ConsolePortTemplate',
    'ConsoleServerPortTemplate',
    'DeviceBayTemplate',
    'FrontPortTemplate',
    'InterfaceTemplate',
    'InventoryItemTemplate',
    'ModuleBayTemplate',
    'PowerOutletTemplate',
    'PowerPortTemplate',
    'RearPortTemplate',
)


class ComponentTemplateModel(WebhooksMixin, ChangeLoggedModel):
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        max_length=64,
        help_text="""
        {module} is accepted as a substitution for the module bay position when attached to a module type.
        """
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Physical label")
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ('device_type', '_name')
        constraints = (
            models.UniqueConstraint(
                fields=('device_type', 'name'),
                name='%(app_label)s_%(class)s_unique_device_type_name'
            ),
        )

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
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.device_type
        return objectchange


class ModularComponentTemplateModel(ComponentTemplateModel):
    """
    A ComponentTemplateModel which supports optional assignment to a ModuleType.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )
    module_type = models.ForeignKey(
        to='dcim.ModuleType',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True
        ordering = ('device_type', 'module_type', '_name')
        constraints = (
            models.UniqueConstraint(
                fields=('device_type', 'name'),
                name='%(app_label)s_%(class)s_unique_device_type_name'
            ),
            models.UniqueConstraint(
                fields=('module_type', 'name'),
                name='%(app_label)s_%(class)s_unique_module_type_name'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original DeviceType ID for reference under clean()
        self._original_device_type = self.device_type_id

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        if self.device_type is not None:
            objectchange.related_object = self.device_type
        elif self.module_type is not None:
            objectchange.related_object = self.module_type
        return objectchange

    def clean(self):
        super().clean()

        if self.pk is not None and self._original_device_type != self.device_type_id:
            raise ValidationError({
                "device_type": "Component templates cannot be moved to a different device type."
            })

        # A component template must belong to a DeviceType *or* to a ModuleType
        if self.device_type and self.module_type:
            raise ValidationError(
                "A component template cannot be associated with both a device type and a module type."
            )
        if not self.device_type and not self.module_type:
            raise ValidationError(
                "A component template must be associated with either a device type or a module type."
            )

    def resolve_name(self, module):
        if module:
            return self.name.replace(MODULE_TOKEN, module.module_bay.position)
        return self.name

    def resolve_label(self, module):
        if module:
            return self.label.replace(MODULE_TOKEN, module.module_bay.position)
        return self.label


class ConsolePortTemplate(ModularComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    component_model = ConsolePort

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'label': self.label,
            'description': self.description,
        }


class ConsoleServerPortTemplate(ModularComponentTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    component_model = ConsoleServerPort

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'label': self.label,
            'description': self.description,
        }


class PowerPortTemplate(ModularComponentTemplateModel):
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
        help_text=_("Maximum power draw (watts)")
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_("Allocated power draw (watts)")
    )

    component_model = PowerPort

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            maximum_draw=self.maximum_draw,
            allocated_draw=self.allocated_draw,
            **kwargs
        )

    def clean(self):
        super().clean()

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': f"Allocated draw cannot exceed the maximum draw ({self.maximum_draw}W)."
                })

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'maximum_draw': self.maximum_draw,
            'allocated_draw': self.allocated_draw,
            'label': self.label,
            'description': self.description,
        }


class PowerOutletTemplate(ModularComponentTemplateModel):
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
        help_text=_("Phase (for three-phase feeds)")
    )

    component_model = PowerOutlet

    def clean(self):
        super().clean()

        # Validate power port assignment
        if self.power_port:
            if self.device_type and self.power_port.device_type != self.device_type:
                raise ValidationError(
                    f"Parent power port ({self.power_port}) must belong to the same device type"
                )
            if self.module_type and self.power_port.module_type != self.module_type:
                raise ValidationError(
                    f"Parent power port ({self.power_port}) must belong to the same module type"
                )

    def instantiate(self, **kwargs):
        if self.power_port:
            power_port_name = self.power_port.resolve_name(kwargs.get('module'))
            power_port = PowerPort.objects.get(name=power_port_name, **kwargs)
        else:
            power_port = None
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            power_port=power_port,
            feed_leg=self.feed_leg,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'power_port': self.power_port.name if self.power_port else None,
            'feed_leg': self.feed_leg,
            'label': self.label,
            'description': self.description,
        }


class InterfaceTemplate(ModularComponentTemplateModel):
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
    poe_mode = models.CharField(
        max_length=50,
        choices=InterfacePoEModeChoices,
        blank=True,
        verbose_name='PoE mode'
    )
    poe_type = models.CharField(
        max_length=50,
        choices=InterfacePoETypeChoices,
        blank=True,
        verbose_name='PoE type'
    )

    component_model = Interface

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            mgmt_only=self.mgmt_only,
            poe_mode=self.poe_mode,
            poe_type=self.poe_type,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'mgmt_only': self.mgmt_only,
            'label': self.label,
            'description': self.description,
            'poe_mode': self.poe_mode,
            'poe_type': self.poe_type,
        }


class FrontPortTemplate(ModularComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
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

    component_model = FrontPort

    class Meta(ModularComponentTemplateModel.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('device_type', 'name'),
                name='%(app_label)s_%(class)s_unique_device_type_name'
            ),
            models.UniqueConstraint(
                fields=('module_type', 'name'),
                name='%(app_label)s_%(class)s_unique_module_type_name'
            ),
            models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'),
                name='%(app_label)s_%(class)s_unique_rear_port_position'
            ),
        )

    def clean(self):
        super().clean()

        try:

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

        except RearPortTemplate.DoesNotExist:
            pass

    def instantiate(self, **kwargs):
        if self.rear_port:
            rear_port_name = self.rear_port.resolve_name(kwargs.get('module'))
            rear_port = RearPort.objects.get(name=rear_port_name, **kwargs)
        else:
            rear_port = None
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            color=self.color,
            rear_port=rear_port,
            rear_port_position=self.rear_port_position,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'rear_port': self.rear_port.name,
            'rear_port_position': self.rear_port_position,
            'label': self.label,
            'description': self.description,
        }


class RearPortTemplate(ModularComponentTemplateModel):
    """
    Template for a pass-through port on the rear of a new Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    component_model = RearPort

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            color=self.color,
            positions=self.positions,
            **kwargs
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'positions': self.positions,
            'label': self.label,
            'description': self.description,
        }


class ModuleBayTemplate(ComponentTemplateModel):
    """
    A template for a ModuleBay to be created for a new parent Device.
    """
    position = models.CharField(
        max_length=30,
        blank=True,
        help_text=_('Identifier to reference when renaming installed components')
    )

    component_model = ModuleBay

    def instantiate(self, device):
        return self.component_model(
            device=device,
            name=self.name,
            label=self.label,
            position=self.position
        )

    def to_yaml(self):
        return {
            'name': self.name,
            'label': self.label,
            'position': self.position,
            'description': self.description,
        }


class DeviceBayTemplate(ComponentTemplateModel):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    component_model = DeviceBay

    def instantiate(self, device):
        return self.component_model(
            device=device,
            name=self.name,
            label=self.label
        )

    def clean(self):
        if self.device_type and self.device_type.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
            raise ValidationError(
                f"Subdevice role of device type ({self.device_type}) must be set to \"parent\" to allow device bays."
            )

    def to_yaml(self):
        return {
            'name': self.name,
            'label': self.label,
            'description': self.description,
        }


class InventoryItemTemplate(MPTTModel, ComponentTemplateModel):
    """
    A template for an InventoryItem to be created for a new parent Device.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_items',
        blank=True,
        null=True,
        db_index=True
    )
    component_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=MODULAR_COMPONENT_TEMPLATE_MODELS,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    component_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    component = GenericForeignKey(
        ct_field='component_type',
        fk_field='component_id'
    )
    role = models.ForeignKey(
        to='dcim.InventoryItemRole',
        on_delete=models.PROTECT,
        related_name='inventory_item_templates',
        blank=True,
        null=True
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='inventory_item_templates',
        blank=True,
        null=True
    )
    part_id = models.CharField(
        max_length=50,
        verbose_name='Part ID',
        blank=True,
        help_text=_('Manufacturer-assigned part identifier')
    )

    objects = TreeManager()
    component_model = InventoryItem

    class Meta:
        ordering = ('device_type__id', 'parent__id', '_name')
        constraints = (
            models.UniqueConstraint(
                fields=('device_type', 'parent', 'name'),
                name='%(app_label)s_%(class)s_unique_device_type_parent_name'
            ),
        )

    def instantiate(self, **kwargs):
        parent = InventoryItem.objects.get(name=self.parent.name, **kwargs) if self.parent else None
        if self.component:
            model = self.component.component_model
            component = model.objects.get(name=self.component.name, **kwargs)
        else:
            component = None
        return self.component_model(
            parent=parent,
            name=self.name,
            label=self.label,
            component=component,
            role=self.role,
            manufacturer=self.manufacturer,
            part_id=self.part_id,
            **kwargs
        )
