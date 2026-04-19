import jsonschema
import yaml
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonschema.exceptions import ValidationError as JSONValidationError

from dcim.choices import *
from extras.models import ConfigContextModel
from netbox.models import PrimaryModel
from netbox.models.features import ImageAttachmentsMixin
from netbox.models.mixins import WeightMixin
from utilities.fields import CounterCacheField
from utilities.jsonschema import validate_schema
from utilities.string import title
from utilities.tracking import TrackingModelMixin

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
    module_count = CounterCacheField(
        to_model='dcim.Module',
        to_field='module_type'
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
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def to_yaml(self):
        data = {
            'profile': self.profile.name if self.profile else None,
            'manufacturer': self.manufacturer.name,
            'model': self.model,
            'part_number': self.part_number,
            'description': self.description,
            'weight': float(self.weight) if self.weight is not None else None,
            'weight_unit': self.weight_unit,
            'airflow': self.airflow,
            'attribute_data': self.attribute_data,
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


class Module(TrackingModelMixin, PrimaryModel, ConfigContextModel):
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
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            from netbox.instantiation import instantiation_registry
            instantiation_registry.execute(
                self,
                adopt_components=getattr(self, '_adopt_components', False),
                disable_replication=getattr(self, '_disable_replication', False),
            )
