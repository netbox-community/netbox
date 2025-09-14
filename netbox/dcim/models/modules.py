import jsonschema
import yaml
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from jsonschema.exceptions import ValidationError as JSONValidationError

from dcim.choices import *
from dcim.constants import MODULE_TOKEN
from dcim.utils import update_interface_bridges
from extras.models import ConfigContextModel, CustomField
from netbox.models import PrimaryModel
from netbox.models.features import ImageAttachmentsMixin
from netbox.models.mixins import WeightMixin
from utilities.jsonschema import validate_schema
from utilities.string import title
from .device_components import *

__all__ = (
    'Module',
    'ModuleType',
    'ModuleTypeProfile',
)


class ModuleTypeProfile(PrimaryModel):
    """
    A profile which defines the attributes which can be set on one or more ModuleTypes.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    schema = models.JSONField(
        blank=True,
        null=True,
        validators=[validate_schema],
        verbose_name=_('schema'),
    )

    clone_fields = ('schema',)

    class Meta:
        ordering = ('name',)
        verbose_name = _('module type profile')
        verbose_name_plural = _('module type profiles')

    def __str__(self):
        return self.name


class ModuleType(ImageAttachmentsMixin, PrimaryModel, WeightMixin):
    """
    A ModuleType represents a hardware element that can be installed within a device and which houses additional
    components; for example, a line card within a chassis-based switch such as the Cisco Catalyst 6500. Like a
    DeviceType, each ModuleType can have console, power, interface, and pass-through port templates assigned to it. It
    cannot, however house device bays or module bays.
    """
    profile = models.ForeignKey(
        to='dcim.ModuleTypeProfile',
        on_delete=models.PROTECT,
        related_name='module_types',
        blank=True,
        null=True
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='module_types'
    )
    model = models.CharField(
        verbose_name=_('model'),
        max_length=100
    )
    part_number = models.CharField(
        verbose_name=_('part number'),
        max_length=50,
        blank=True,
        help_text=_('Discrete part number (optional)')
    )
    airflow = models.CharField(
        verbose_name=_('airflow'),
        max_length=50,
        choices=ModuleAirflowChoices,
        blank=True,
        null=True
    )
    attribute_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('attributes')
    )

    clone_fields = ('profile', 'manufacturer', 'weight', 'weight_unit', 'airflow')
    prerequisite_models = (
        'dcim.Manufacturer',
    )

    class Meta:
        ordering = ('profile', 'manufacturer', 'model')
        constraints = (
            models.UniqueConstraint(
                fields=('manufacturer', 'model'),
                name='%(app_label)s_%(class)s_unique_manufacturer_model'
            ),
        )
        verbose_name = _('module type')
        verbose_name_plural = _('module types')

    def __str__(self):
        return self.model

    @property
    def full_name(self):
        return f"{self.manufacturer} {self.model}"

    @property
    def attributes(self):
        """
        Returns a human-friendly representation of the attributes defined for a ModuleType according to its profile.
        """
        if not self.attribute_data or self.profile is None or not self.profile.schema:
            return {}
        attrs = {}
        for name, options in self.profile.schema.get('properties', {}).items():
            key = options.get('title', title(name))
            attrs[key] = self.attribute_data.get(name)
        return dict(sorted(attrs.items()))

    def clean(self):
        super().clean()

        # Validate any attributes against the assigned profile's schema
        if self.profile and self.profile.schema:
            try:
                jsonschema.validate(self.attribute_data, schema=self.profile.schema)
            except JSONValidationError as e:
                raise ValidationError(_("Invalid schema: {error}").format(error=e))
        else:
            self.attribute_data = None

    def to_yaml(self):
        data = {
            'profile': self.profile.name if self.profile else None,
            'manufacturer': self.manufacturer.name,
            'model': self.model,
            'part_number': self.part_number,
            'description': self.description,
            'weight': float(self.weight) if self.weight is not None else None,
            'weight_unit': self.weight_unit,
            'comments': self.comments,
        }

        # Component templates
        if self.consoleporttemplates.exists():
            data['console-ports'] = [
                c.to_yaml() for c in self.consoleporttemplates.all()
            ]
        if self.consoleserverporttemplates.exists():
            data['console-server-ports'] = [
                c.to_yaml() for c in self.consoleserverporttemplates.all()
            ]
        if self.powerporttemplates.exists():
            data['power-ports'] = [
                c.to_yaml() for c in self.powerporttemplates.all()
            ]
        if self.poweroutlettemplates.exists():
            data['power-outlets'] = [
                c.to_yaml() for c in self.poweroutlettemplates.all()
            ]
        if self.interfacetemplates.exists():
            data['interfaces'] = [
                c.to_yaml() for c in self.interfacetemplates.all()
            ]
        if self.frontporttemplates.exists():
            data['front-ports'] = [
                c.to_yaml() for c in self.frontporttemplates.all()
            ]
        if self.rearporttemplates.exists():
            data['rear-ports'] = [
                c.to_yaml() for c in self.rearporttemplates.all()
            ]

        return yaml.dump(dict(data), sort_keys=False)


class Module(PrimaryModel, ConfigContextModel):
    """
    A Module represents a field-installable component within a Device which may itself hold multiple device components
    (for example, a line card within a chassis switch). Modules are instantiated from ModuleTypes.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='modules'
    )
    module_bay = models.OneToOneField(
        to='dcim.ModuleBay',
        on_delete=models.CASCADE,
        related_name='installed_module'
    )
    module_type = models.ForeignKey(
        to='dcim.ModuleType',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=ModuleStatusChoices,
        default=ModuleStatusChoices.STATUS_ACTIVE
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('serial number')
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('asset tag'),
        help_text=_('A unique tag used to identify this device')
    )

    clone_fields = ('device', 'module_type', 'status')

    class Meta:
        ordering = ('module_bay',)
        verbose_name = _('module')
        verbose_name_plural = _('modules')

    def __str__(self):
        return f'{self.module_bay.name}: {self.module_type} ({self.pk})'

    def get_status_color(self):
        return ModuleStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        if hasattr(self, "module_bay") and (self.module_bay.device != self.device):
            raise ValidationError(
                _("Module must be installed within a module bay belonging to the assigned device ({device}).").format(
                    device=self.device
                )
            )

        # Check for recursion
        module = self
        module_bays = []
        modules = []
        while module:
            if module.pk in modules or module.module_bay.pk in module_bays:
                raise ValidationError(_("A module bay cannot belong to a module installed within it."))
            modules.append(module.pk)
            module_bays.append(module.module_bay.pk)
            module = module.module_bay.module if module.module_bay else None

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        adopt_components = getattr(self, '_adopt_components', False)
        disable_replication = getattr(self, '_disable_replication', False)

        # We skip adding components if the module is being edited or
        # both replication and component adoption is disabled
        if not is_new or (disable_replication and not adopt_components):
            return

        # Iterate all component types
        for templates, component_attribute, component_model in [
            ("consoleporttemplates", "consoleports", ConsolePort),
            ("consoleserverporttemplates", "consoleserverports", ConsoleServerPort),
            ("interfacetemplates", "interfaces", Interface),
            ("powerporttemplates", "powerports", PowerPort),
            ("poweroutlettemplates", "poweroutlets", PowerOutlet),
            ("rearporttemplates", "rearports", RearPort),
            ("frontporttemplates", "frontports", FrontPort),
            ("modulebaytemplates", "modulebays", ModuleBay),
        ]:
            create_instances = []
            update_instances = []

            # Prefetch installed components
            installed_components = {
                component.name: component
                for component in getattr(self.device, component_attribute).filter(module__isnull=True)
            }

            # Get the template for the module type.
            for template in getattr(self.module_type, templates).all():
                template_instance = template.instantiate(device=self.device, module=self)

                if adopt_components:
                    existing_item = installed_components.get(template_instance.name)

                    # Check if there's a component with the same name already
                    if existing_item:
                        # Assign it to the module
                        existing_item.module = self
                        update_instances.append(existing_item)
                        continue

                # Only create new components if replication is enabled
                if not disable_replication:
                    create_instances.append(template_instance)

            # Set default values for any applicable custom fields
            if cf_defaults := CustomField.objects.get_defaults_for_model(component_model):
                for component in create_instances:
                    component.custom_field_data = cf_defaults

            if component_model is not ModuleBay:
                component_model.objects.bulk_create(create_instances)
                # Emit the post_save signal for each newly created object
                for component in create_instances:
                    post_save.send(
                        sender=component_model,
                        instance=component,
                        created=True,
                        raw=False,
                        using='default',
                        update_fields=None
                    )
            else:
                # ModuleBays must be saved individually for MPTT
                for instance in create_instances:
                    instance.name = instance.name.replace(MODULE_TOKEN, str(self.module_bay.position))
                    instance.save()

            update_fields = ['module']
            component_model.objects.bulk_update(update_instances, update_fields)
            # Emit the post_save signal for each updated object
            for component in update_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=False,
                    raw=False,
                    using='default',
                    update_fields=update_fields
                )

        # Interface bridges have to be set after interface instantiation
        update_interface_bridges(self.device, self.module_type.interfacetemplates, self)
