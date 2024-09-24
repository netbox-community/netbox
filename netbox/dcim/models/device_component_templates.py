from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from dcim.choices import *
from dcim.constants import *
from netbox.models import ChangeLoggedModel
from utilities.fields import ColorField, NaturalOrderingField
from utilities.mptt import TreeManager
from utilities.ordering import naturalize_interface
from utilities.tracking import TrackingModelMixin
from wireless.choices import WirelessRoleChoices
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


class ComponentTemplateModel(ChangeLoggedModel, TrackingModelMixin):
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
        help_text=_(
            "{module} is accepted as a substitution for the module bay position when attached to a module type."
        )
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=64,
        blank=True,
        help_text=_('Physical label')
    )
    description = models.CharField(
        verbose_name=_('description'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original DeviceType ID for reference under clean()
        self._original_device_type = self.__dict__.get('device_type_id')

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.device_type
        return objectchange

    def clean(self):
        super().clean()

        if not self._state.adding and self._original_device_type != self.device_type_id:
            raise ValidationError({
                "device_type": _("Component templates cannot be moved to a different device type.")
            })


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

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        if self.device_type is not None:
            objectchange.related_object = self.device_type
        elif self.module_type is not None:
            objectchange.related_object = self.module_type
        return objectchange

    def clean(self):
        super().clean()

        # A component template must belong to a DeviceType *or* to a ModuleType
        if self.device_type and self.module_type:
            raise ValidationError(
                _("A component template cannot be associated with both a device type and a module type.")
            )
        if not self.device_type and not self.module_type:
            raise ValidationError(
                _("A component template must be associated with either a device type or a module type.")
            )

    def _get_module_tree(self, module):
        modules = []
        all_module_bays = module.device.modulebays.all().select_related('module')
        while module:
            modules.append(module)
            if module.module_bay:
                module = module.module_bay.module
            else:
                module = None

        modules.reverse()
        return modules

    def resolve_name(self, module):
        if MODULE_TOKEN not in self.name:
            return self.name

        if module:
            modules = self._get_module_tree(module)
            name = self.name
            for module in modules:
                name = name.replace(MODULE_TOKEN, module.module_bay.position, 1)
            return name
        return self.name

    def resolve_label(self, module):
        if MODULE_TOKEN not in self.label:
            return self.label

        if module:
            modules = self._get_module_tree(module)
            label = self.label
            for module in modules:
                label = label.replace(MODULE_TOKEN, module.module_bay.position, 1)
            return label
        return self.label


class ConsolePortTemplate(ModularComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    component_model = ConsolePort

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('console port template')
        verbose_name_plural = _('console port templates')

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
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )

    component_model = ConsoleServerPort

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('console server port template')
        verbose_name_plural = _('console server port templates')

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            **kwargs
        )
    instantiate.do_not_call_in_templates = True

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
        verbose_name=_('type'),
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True
    )
    maximum_draw = models.PositiveIntegerField(
        verbose_name=_('maximum draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_('Maximum power draw (watts)')
    )
    allocated_draw = models.PositiveIntegerField(
        verbose_name=_('allocated draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_('Allocated power draw (watts)')
    )

    component_model = PowerPort

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('power port template')
        verbose_name_plural = _('power port templates')

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            maximum_draw=self.maximum_draw,
            allocated_draw=self.allocated_draw,
            **kwargs
        )
    instantiate.do_not_call_in_templates = True

    def clean(self):
        super().clean()

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': _("Allocated draw cannot exceed the maximum draw ({maximum_draw}W).").format(maximum_draw=self.maximum_draw)
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
        verbose_name=_('type'),
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
        verbose_name=_('feed leg'),
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        help_text=_('Phase (for three-phase feeds)')
    )

    component_model = PowerOutlet

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('power outlet template')
        verbose_name_plural = _('power outlet templates')

    def clean(self):
        super().clean()

        # Validate power port assignment
        if self.power_port:
            if self.device_type and self.power_port.device_type != self.device_type:
                raise ValidationError(
                    _("Parent power port ({power_port}) must belong to the same device type").format(power_port=self.power_port)
                )
            if self.module_type and self.power_port.module_type != self.module_type:
                raise ValidationError(
                    _("Parent power port ({power_port}) must belong to the same module type").format(power_port=self.power_port)
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
    instantiate.do_not_call_in_templates = True

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
        verbose_name=_('type'),
        max_length=50,
        choices=InterfaceTypeChoices
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name=_('management only')
    )
    bridge = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='bridge_interfaces',
        null=True,
        blank=True,
        verbose_name=_('bridge interface')
    )
    poe_mode = models.CharField(
        max_length=50,
        choices=InterfacePoEModeChoices,
        blank=True,
        verbose_name=_('PoE mode')
    )
    poe_type = models.CharField(
        max_length=50,
        choices=InterfacePoETypeChoices,
        blank=True,
        verbose_name=_('PoE type')
    )
    rf_role = models.CharField(
        max_length=30,
        choices=WirelessRoleChoices,
        blank=True,
        verbose_name=_('wireless role')
    )

    component_model = Interface

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('interface template')
        verbose_name_plural = _('interface templates')

    def clean(self):
        super().clean()

        if self.bridge:
            if self.pk and self.bridge_id == self.pk:
                raise ValidationError({'bridge': _("An interface cannot be bridged to itself.")})
            if self.device_type and self.device_type != self.bridge.device_type:
                raise ValidationError({
                    'bridge': _("Bridge interface ({bridge}) must belong to the same device type").format(bridge=self.bridge)
                })
            if self.module_type and self.module_type != self.bridge.module_type:
                raise ValidationError({
                    'bridge': _("Bridge interface ({bridge}) must belong to the same module type").format(bridge=self.bridge)
                })

        if self.rf_role and self.type not in WIRELESS_IFACE_TYPES:
            raise ValidationError({
                'rf_role': "Wireless role may be set only on wireless interfaces."
            })

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            enabled=self.enabled,
            mgmt_only=self.mgmt_only,
            poe_mode=self.poe_mode,
            poe_type=self.poe_type,
            rf_role=self.rf_role,
            **kwargs
        )
    instantiate.do_not_call_in_templates = True

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'enabled': self.enabled,
            'mgmt_only': self.mgmt_only,
            'label': self.label,
            'description': self.description,
            'bridge': self.bridge.name if self.bridge else None,
            'poe_mode': self.poe_mode,
            'poe_type': self.poe_type,
            'rf_role': self.rf_role,
        }


class FrontPortTemplate(ModularComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPortTemplate',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        verbose_name=_('rear port position'),
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
        verbose_name = _('front port template')
        verbose_name_plural = _('front port templates')

    def clean(self):
        super().clean()

        try:

            # Validate rear port assignment
            if self.rear_port.device_type != self.device_type:
                raise ValidationError(
                    _("Rear port ({name}) must belong to the same device type").format(name=self.rear_port)
                )

            # Validate rear port position assignment
            if self.rear_port_position > self.rear_port.positions:
                raise ValidationError(
                    _("Invalid rear port position ({position}); rear port {name} has only {count} positions").format(
                        position=self.rear_port_position,
                        name=self.rear_port.name,
                        count=self.rear_port.positions
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
    instantiate.do_not_call_in_templates = True

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
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        verbose_name=_('positions'),
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )

    component_model = RearPort

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('rear port template')
        verbose_name_plural = _('rear port templates')

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.resolve_name(kwargs.get('module')),
            label=self.resolve_label(kwargs.get('module')),
            type=self.type,
            color=self.color,
            positions=self.positions,
            **kwargs
        )
    instantiate.do_not_call_in_templates = True

    def to_yaml(self):
        return {
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'positions': self.positions,
            'label': self.label,
            'description': self.description,
        }


class ModuleBayTemplate(ModularComponentTemplateModel):
    """
    A template for a ModuleBay to be created for a new parent Device.
    """
    position = models.CharField(
        verbose_name=_('position'),
        max_length=30,
        blank=True,
        help_text=_('Identifier to reference when renaming installed components')
    )

    component_model = ModuleBay

    class Meta(ModularComponentTemplateModel.Meta):
        verbose_name = _('module bay template')
        verbose_name_plural = _('module bay templates')

    def instantiate(self, **kwargs):
        return self.component_model(
            name=self.name,
            label=self.label,
            position=self.position,
            **kwargs
        )
    instantiate.do_not_call_in_templates = True

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

    class Meta(ComponentTemplateModel.Meta):
        verbose_name = _('device bay template')
        verbose_name_plural = _('device bay templates')

    def instantiate(self, device):
        return self.component_model(
            device=device,
            name=self.name,
            label=self.label
        )
    instantiate.do_not_call_in_templates = True

    def clean(self):
        if self.device_type and self.device_type.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
            raise ValidationError(
                _("Subdevice role of device type ({device_type}) must be set to \"parent\" to allow device bays.").format(device_type=self.device_type)
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
        to='contenttypes.ContentType',
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
        verbose_name=_('part ID'),
        blank=True,
        help_text=_('Manufacturer-assigned part identifier')
    )

    objects = TreeManager()
    component_model = InventoryItem

    class Meta:
        ordering = ('device_type__id', 'parent__id', '_name')
        indexes = (
            models.Index(fields=('component_type', 'component_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('device_type', 'parent', 'name'),
                name='%(app_label)s_%(class)s_unique_device_type_parent_name'
            ),
        )
        verbose_name = _('inventory item template')
        verbose_name_plural = _('inventory item templates')

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
    instantiate.do_not_call_in_templates = True
