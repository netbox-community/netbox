from collections.abc import Iterable, Mapping

import jsonschema
import yaml
from django.core.exceptions import ValidationError
from django.db import OperationalError, models, router, transaction
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from jsonschema.exceptions import ValidationError as JSONValidationError

from dcim.choices import *
from dcim.utils import create_port_mappings, update_interface_bridges, update_interface_parents
from extras.models import CustomField
from netbox.models import PrimaryModel
from netbox.models.features import ImageAttachmentsMixin
from netbox.models.mixins import WeightMixin
from utilities.exceptions import AbortRequest
from utilities.fields import ColorField, CounterCacheField
from utilities.jsonschema import validate_schema
from utilities.string import title
from utilities.tracking import TrackingModelMixin

from .device_components import *
from .module_moves import ModuleMovePlan

__all__ = (
    'Module',
    'ModuleBayType',
    'ModuleType',
    'ModuleTypeProfile',
)


class ModuleBayType(PrimaryModel):
    """
    A type classification for module bays. When bay types are assigned to both a ModuleBay and a
    ModuleType, module installation is permitted only if the two sets share at least one common
    member (i.e. an empty set on either side means unconstrained).
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='module_bay_types',
        blank=True,
        null=True,
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True,
    )

    clone_fields = ('manufacturer', 'color')

    class Meta:
        ordering = ('manufacturer', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('manufacturer', 'name'),
                name='%(app_label)s_%(class)s_unique_manufacturer_name',
                nulls_distinct=False,
            ),
            models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='%(app_label)s_%(class)s_unique_manufacturer_slug',
                nulls_distinct=False,
            ),
        )
        verbose_name = _('module bay type')
        verbose_name_plural = _('module bay types')

    def __str__(self):
        if self.manufacturer:
            return f'{self.manufacturer} {self.name}'
        return self.name


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
    DeviceType, each ModuleType can have console, power, interface, pass-through port, and module bay templates assigned
    to it. It cannot, however, house device bays.
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
    cooling_method = models.CharField(
        verbose_name=_('cooling method'),
        max_length=50,
        choices=CoolingMethodChoices,
        blank=True,
        null=True
    )
    end_of_life = models.DateField(
        verbose_name=_('end of life'),
        blank=True,
        null=True,
        help_text=_('The date after which this module type is no longer supported by the manufacturer')
    )
    attribute_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('attributes')
    )
    module_bay_types = models.ManyToManyField(
        to='dcim.ModuleBayType',
        related_name='module_types',
        blank=True,
        verbose_name=_('module bay types'),
        help_text=_('Types of module bays this module type can be installed in (empty = unconstrained)'),
    )
    module_count = CounterCacheField(
        to_model='dcim.Module',
        to_field='module_type'
    )

    # Counter fields
    console_port_template_count = CounterCacheField(
        to_model='dcim.ConsolePortTemplate',
        to_field='module_type'
    )
    console_server_port_template_count = CounterCacheField(
        to_model='dcim.ConsoleServerPortTemplate',
        to_field='module_type'
    )
    power_port_template_count = CounterCacheField(
        to_model='dcim.PowerPortTemplate',
        to_field='module_type'
    )
    power_outlet_template_count = CounterCacheField(
        to_model='dcim.PowerOutletTemplate',
        to_field='module_type'
    )
    cooling_intake_template_count = CounterCacheField(
        to_model='dcim.CoolingIntakeTemplate',
        to_field='module_type'
    )
    cooling_outflow_template_count = CounterCacheField(
        to_model='dcim.CoolingOutflowTemplate',
        to_field='module_type'
    )
    interface_template_count = CounterCacheField(
        to_model='dcim.InterfaceTemplate',
        to_field='module_type'
    )
    front_port_template_count = CounterCacheField(
        to_model='dcim.FrontPortTemplate',
        to_field='module_type'
    )
    rear_port_template_count = CounterCacheField(
        to_model='dcim.RearPortTemplate',
        to_field='module_type'
    )
    module_bay_template_count = CounterCacheField(
        to_model='dcim.ModuleBayTemplate',
        to_field='module_type'
    )

    clone_fields = ('profile', 'manufacturer', 'weight', 'weight_unit', 'airflow', 'cooling_method')
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
        indexes = (
            models.Index(fields=('profile', 'manufacturer', 'model')),  # Default ordering
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
            value = self.attribute_data.get(name)
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
                value = ', '.join(str(v) for v in value)
            attrs[key] = value
        return dict(sorted(attrs.items()))

    def get_incompatible_modules(self):
        """
        Return a queryset of Module instances of this type that are installed in bays whose
        bay type sets are non-empty and share no members with this type's bay type set.
        If this type has no bay type constraints, no installation can be incompatible.
        """
        type_type_pks = list(self.module_bay_types.values_list('pk', flat=True))
        if not type_type_pks:
            return Module.objects.none()
        # Bays that have any compatible type (the intersection is non-empty)
        compatible_bay_pks = ModuleBay.objects.filter(
            module_bay_types__pk__in=type_type_pks
        ).values_list('pk', flat=True)
        # Bays with at least one type set (constrained bays); distinct() prevents M2M join duplicates
        constrained_bay_pks = ModuleBay.objects.filter(
            module_bay_types__isnull=False
        ).distinct().values_list('pk', flat=True)
        return Module.objects.filter(
            module_type=self,
            module_bay__pk__in=constrained_bay_pks,
        ).exclude(
            module_bay__pk__in=compatible_bay_pks,
        )

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
            'airflow': self.airflow,
            'cooling_method': self.cooling_method,
            'end_of_life': self.end_of_life.isoformat() if self.end_of_life else None,
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
        if self.coolingintaketemplates.exists():
            data['cooling-ports'] = [
                c.to_yaml() for c in self.coolingintaketemplates.all()
            ]
        if self.coolingoutflowtemplates.exists():
            data['cooling-outlets'] = [
                c.to_yaml() for c in self.coolingoutflowtemplates.all()
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

        # Port mappings
        port_mapping_data = [
            c.to_yaml() for c in self.port_mappings.all()
        ]

        if port_mapping_data:
            data['port-mappings'] = port_mapping_data

        return yaml.dump(dict(data), sort_keys=False)


class Module(TrackingModelMixin, PrimaryModel):
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

    @property
    def is_bay_compatible(self):
        """
        Return True if this module's type is compatible with its installed bay, or if either has no type constraints.
        Returns False when both the bay and module type have non-empty, disjoint bay type sets.
        """
        if not (self.module_bay_id and self.module_type_id):
            return True
        # Use .all() so a prefetch cache (populated by the API list queryset) is honoured; .values_list()
        # creates a fresh queryset that bypasses the cache and causes N+1 hits in list views.
        bay_types = {t.pk for t in self.module_bay.module_bay_types.all()}
        type_types = {t.pk for t in self.module_type.module_bay_types.all()}
        if bay_types and type_types and not (bay_types & type_types):
            return False
        return True

    def clean(self):
        super().clean()

        if hasattr(self, "module_bay") and (self.module_bay.device != self.device):
            raise ValidationError(
                _("Module must be installed within a module bay belonging to the assigned device ({device}).").format(
                    device=self.device
                )
            )

        if not self.is_bay_compatible:
            raise ValidationError(
                _('Module type {module_type} is not compatible with module bay {module_bay}: '
                  'their bay type sets have no common members.').format(
                    module_type=self.module_type,
                    module_bay=self.module_bay,
                )
            )

        # Prevent module from being installed in a disabled bay
        if hasattr(self, 'module_bay') and self.module_bay and not self.module_bay.enabled:
            current_module_bay_id = Module.objects.filter(pk=self.pk).values_list('module_bay_id', flat=True).first()
            if self.pk is None or current_module_bay_id != self.module_bay_id:
                raise ValidationError({
                    'module_bay': _("Cannot install a module in a disabled module bay.")
                })

        # Prevent installation into an occupied module bay
        if hasattr(self, 'module_bay') and self.module_bay_id and (
            occupant := Module.objects.filter(module_bay_id=self.module_bay_id).exclude(pk=self.pk).first()
        ):
            raise ValidationError({
                'module_bay': _(
                    "Module bay {module_bay} is already occupied by module {module}."
                ).format(module_bay=self.module_bay, module=occupant)
            })

        # Validate a requested move (device and/or module bay change) of an existing module
        if not self._state.adding and hasattr(self, 'module_bay') and self.module_bay_id and self.device_id:
            old = Module.objects.filter(pk=self.pk).first()
            if old and (old.device_id != self.device_id or old.module_bay_id != self.module_bay_id):
                if old.module_type_id != self.module_type_id:
                    raise ValidationError({
                        'module_type': _(
                            "Changing a module's type while moving it is not supported. Change the module "
                            "type and move the module as separate operations."
                        )
                    })
                try:
                    ModuleMovePlan.from_module(old_module=old, new_module=self).validate()
                except ValueError as e:
                    raise ValidationError({'module_bay': str(e)}) from e

        # Check for recursion
        module = self
        module_bays = []
        modules = []
        while module:
            module_module_bay = getattr(module, "module_bay", None)
            if module.pk in modules or (module_module_bay and module_module_bay.pk in module_bays):
                raise ValidationError(_("A module bay cannot belong to a module installed within it."))
            modules.append(module.pk)
            if module_module_bay:
                module_bays.append(module_module_bay.pk)
            module = module_module_bay.module if module_module_bay else None

    def save(self, *args, **kwargs):
        if self.pk is None:
            self._save_new(*args, **kwargs)
            return

        update_fields = kwargs.get('update_fields')
        placement_fields = {'device', 'device_id', 'module_bay', 'module_bay_id'}
        if update_fields is not None and placement_fields.isdisjoint(update_fields):
            # Placement columns cannot be written by this save, so no move can occur.
            super().save(*args, **kwargs)
            return

        self._save_existing(*args, **kwargs)

    def _save_new(self, *args, **kwargs):
        super().save(*args, **kwargs)

        adopt_components = getattr(self, '_adopt_components', False)
        disable_replication = getattr(self, '_disable_replication', False)

        # We skip adding components if both replication and component adoption is disabled
        if disable_replication and not adopt_components:
            return

        # Iterate all component types
        for templates, component_attribute, component_model in [
            ("consoleporttemplates", "consoleports", ConsolePort),
            ("consoleserverporttemplates", "consoleserverports", ConsoleServerPort),
            ("interfacetemplates", "interfaces", Interface),
            ("powerporttemplates", "powerports", PowerPort),
            ("poweroutlettemplates", "poweroutlets", PowerOutlet),
            ("coolingintaketemplates", "coolingintakes", CoolingIntake),
            ("coolingoutflowtemplates", "coolingoutflows", CoolingOutflow),
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
                template_instance._source_template = template

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

            # Set denormalized references
            for component in create_instances:
                component._site = self.device.site
                component._location = self.device.location
                component._rack = self.device.rack

            # Bulk-create new instances. ModuleBay is ltree-backed: its parent is set
            # in ModuleBayTemplate.instantiate() (bulk_create bypasses ModuleBay.save()),
            # and the BEFORE INSERT trigger derives path/sort_path from parent_id per row.
            component_model.objects.bulk_create(create_instances)

            # Copy M2M module_bay_types from template to new ModuleBay instances.
            if component_model is ModuleBay:
                for component in create_instances:
                    if src := getattr(component, '_source_template', None):
                        component.module_bay_types.set(src.module_bay_types.all())

            for component in create_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=True,
                    raw=False,
                    using='default',
                    update_fields=None
                )

            update_fields = ['module']
            # ModuleBay.parent is derived from .module in ModuleBay.save(), and the
            # path/sort_path trigger only fires on parent_id/name changes. A bare
            # bulk_update(['module']) bypasses both, leaving the adopted bay rooted
            # at its pre-adoption location. Set parent in lockstep so the BEFORE
            # trigger recomputes path/sort_path.
            if component_model is ModuleBay:
                for instance in update_instances:
                    instance.parent = self.module_bay
                update_fields = ['module', 'parent']

            component_model.objects.bulk_update(update_instances, update_fields)
            for component in update_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=False,
                    raw=False,
                    using='default',
                    update_fields=update_fields
                )

        # Replicate any front/rear port mappings from the ModuleType
        create_port_mappings(self.device, self.module_type, self)

        # Interface parents & bridges have to be set after interface instantiation. Parents are applied first so that
        # channel subinterfaces validate against a populated parent.
        update_interface_parents(self.device, self.module_type.interfacetemplates, self)
        update_interface_bridges(self.device, self.module_type.interfacetemplates, self)

    def _save_existing(self, *args, **kwargs):
        try:
            with transaction.atomic(using=router.db_for_write(Module)):
                # Root row locks first (matches API ETag path); all routing below decides from this locked read
                locked_old = Module.objects.select_for_update().only(
                    'device', 'module_bay', 'module_type'
                ).filter(pk=self.pk).first()
                if locked_old is None:
                    # A new pk, or a row concurrently deleted; create instead.
                    self._save_new(*args, **kwargs)
                    return

                delta_fields = []
                if locked_old.device_id != self.device_id:
                    delta_fields.append('device')
                if locked_old.module_bay_id != self.module_bay_id:
                    delta_fields.append('module_bay')

                if not delta_fields:
                    super().save(*args, **kwargs)
                    return

                update_fields = kwargs.get('update_fields')
                if update_fields is not None:
                    field_attnames = {'device': 'device_id', 'module_bay': 'module_bay_id'}
                    listed = {
                        field for field in delta_fields
                        if field in update_fields or field_attnames[field] in update_fields
                    }
                    if not listed:
                        # None of the changed placement fields are part of this write, so no move happens.
                        super().save(*args, **kwargs)
                        return
                    if listed != set(delta_fields):
                        raise AbortRequest(_(
                            "A module move must include every changed placement field in update_fields: "
                            "'device' (or 'device_id') and/or 'module_bay' (or 'module_bay_id')."
                        ))

                if locked_old.module_type_id != self.module_type_id:
                    raise AbortRequest(_(
                        "Changing a module's type while moving it is not supported. Change the module type and "
                        "move the module as separate operations."
                    ))

                try:
                    plan = ModuleMovePlan.from_module(old_module=locked_old, new_module=self)
                    plan.lock()
                except ValueError as e:
                    raise AbortRequest(str(e)) from e
                try:
                    plan.validate()
                except ValidationError as e:
                    raise AbortRequest(' '.join(e.messages)) from e

                super().save(*args, **kwargs)
                plan.apply_after_root_save()
        except OperationalError as e:
            if getattr(e.__cause__, 'sqlstate', None) == '40P01':
                raise AbortRequest(_(
                    "This module or its components are being modified by another request. Please try again."
                )) from e
            raise
