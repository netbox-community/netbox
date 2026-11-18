import json
import logging
from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import router, transaction
from django.utils.translation import gettext_lazy as _

from dcim import forms
from dcim.models import DeviceType, InterfaceTemplate, ModuleType, ModuleTypeProfile, RackType
from utilities.exceptions import PermissionsViolation
from utilities.fields import CounterCacheField

from .base import Importer, ImportSkipped, register_importer
from .utils import (
    enforce_object_permission,
    find_manufacturer,
    get_error_message,
    get_or_create_manufacturer,
    parse_strict_date,
    save_form,
)

__all__ = (
    'DeviceTypeImporter',
    'ModuleTypeImporter',
    'RackTypeImporter',
)

logger = logging.getLogger('netbox.ndx.importers')

TRANSCEIVER_PROFILE_FILE = (
    Path(__file__).resolve().parents[2] / 'dcim' / 'migrations' / 'initial_data' / 'module_type_profiles' /
    'transceiver.json'
)

# Catalog `fiber` values mapped to the Transceiver profile's `media` attribute
FIBER_MEDIA = {
    'SMF': 'SMF',
    'MMF': 'MMF',
    'MMF-OM3': 'MMF',
    'MMF-OM4': 'MMF',
    'MMF-OM5': 'MMF',
    'copper': 'DAC',
    'active-copper': 'AOC',
    'integrated': 'integrated',
    'n/a': None,
}

# Parent form fields which are populated from the top level of the catalog entry, or never from the catalog
EXCLUDED_PARENT_FIELDS = (
    'id', 'manufacturer', 'model', 'slug', 'part_number', 'default_platform', 'owner', 'tags', 'profile',
    'attribute_data', 'end_of_life',
)


class ComponentTemplatesMixin:
    """
    Import the component templates of a device or module type using NetBox's YAML import forms.
    """
    parent_field = None
    component_forms = {}

    def get_required_permissions(self, entry, instance):
        perms = super().get_required_permissions(entry, instance)
        dtl = entry.get('dtl') or {}
        for key, form_class in self.component_forms.items():
            model = form_class._meta.model
            if dtl.get(key) and not getattr(model, '_netbox_private', False):
                perms.add(f'dcim.add_{model._meta.model_name}')
                if instance:
                    perms.add(f'dcim.change_{model._meta.model_name}')
        # Assigning bridges modifies interfaces once they have been created
        if any(isinstance(item, dict) and item.get('bridge') for item in dtl.get('interfaces') or []):
            perms.add('dcim.change_interfacetemplate')
        return perms

    def import_components(self, parent, dtl, user, result):
        """
        Create or update the component templates defined in the catalog entry. Existing templates are matched by
        name and are never deleted. A component which cannot be imported is recorded without failing the entry.
        """
        for key, form_class in self.component_forms.items():
            model = form_class._meta.model
            for item in dtl.get(key) or []:
                if not isinstance(item, dict):
                    continue
                if key == 'port-mappings':
                    label = f"{key} {item.get('front_port')}:{item.get('front_port_position', 1)}"
                    instance = model.objects.filter(**{
                        self.parent_field: parent,
                        'front_port__name': item.get('front_port'),
                        'front_port_position': item.get('front_port_position', 1),
                    }).first()
                else:
                    if not item.get('name'):
                        continue
                    label = f"{key} {item['name']}"
                    instance = model.objects.filter(**{self.parent_field: parent, 'name': item['name']}).first()
                if key == 'inventory-items' and item.get('manufacturer'):
                    item = {**item, 'manufacturer': get_or_create_manufacturer(item['manufacturer']).name}
                try:
                    with transaction.atomic(using=router.db_for_write(model)):
                        component = save_form(
                            form_class,
                            {**item, self.parent_field: parent},
                            instance or model(),
                            protected=('name', 'front_port', 'front_port_position', self.parent_field),
                            warnings=result.warnings,
                            label=label,
                        )
                        enforce_object_permission(component, user, 'change' if instance else 'add')
                except PermissionsViolation:
                    # Fail the entire import
                    raise
                except Exception as e:
                    result.component_errors.append(f'{label}: {get_error_message(e)}')
                    logger.warning(f"Failed to import {label}: {e}")

        self.link_bridges(parent, dtl, user, result)

    def link_bridges(self, parent, dtl, user, result):
        """
        Assign interface bridges, which reference other interfaces by name.
        """
        for item in dtl.get('interfaces') or []:
            if not isinstance(item, dict) or not item.get('name') or not item.get('bridge'):
                continue
            interfaces = InterfaceTemplate.objects.filter(**{self.parent_field: parent})
            interface = interfaces.filter(name=item['name']).first()
            bridge = interfaces.filter(name=item['bridge']).first()
            if interface is None or bridge is None:
                result.component_errors.append(_("interfaces {name}: bridge {bridge} not found").format(
                    name=item['name'], bridge=item['bridge']
                ))
                continue
            if interface.bridge_id == bridge.pk:
                continue
            try:
                with transaction.atomic(using=router.db_for_write(InterfaceTemplate)):
                    interface.snapshot()
                    interface.bridge = bridge
                    interface.full_clean()
                    interface.save()
                    enforce_object_permission(interface, user, 'change')
            except PermissionsViolation:
                raise
            except Exception as e:
                result.component_errors.append(f"interfaces {item['name']}: {get_error_message(e)}")
                logger.warning(f"Failed to assign bridge for interfaces {item['name']}: {e}")


def normalize_dtl(dtl):
    """
    Return a copy of the catalog's device type definition prepared for import, along with the rated capacity (in
    watts) of a power distribution unit (or None).
    """
    dtl = {key: (list(value) if isinstance(value, list) else value) for key, value in (dtl or {}).items()}

    # Convert legacy front port mappings (embedded on each front port) to port-mappings
    if 'port-mappings' not in dtl:
        mappings = [
            {
                'front_port': port['name'],
                'front_port_position': port.get('front_port_position', 1),
                'rear_port': port['rear_port'],
                'rear_port_position': port.get('rear_port_position', 1),
            }
            for port in dtl.get('front-ports') or []
            if isinstance(port, dict) and port.get('name') and port.get('rear_port')
        ]
        if mappings:
            dtl['port-mappings'] = mappings

    # A type whose outlets draw from its own power ports is a PDU. Its power ports carry the unit's rated capacity
    # as their maximum draw, which would prevent NetBox from summing the draw of the outlets' loads. Move the
    # capacity to the enrichment record instead.
    capacity = None
    outlets = dtl.get('power-outlets') or []
    power_ports = dtl.get('power-ports') or []
    if power_ports and any(isinstance(o, dict) and o.get('power_port') for o in outlets):
        draws = [p['maximum_draw'] for p in power_ports if isinstance(p, dict) and p.get('maximum_draw') is not None]
        capacity = max(draws, default=None)
        dtl['power-ports'] = [
            {**p, 'maximum_draw': '', 'allocated_draw': ''} if isinstance(p, dict) else p for p in power_ports
        ]

    return dtl, capacity


class DCIMTypeImporter(Importer):
    """
    Common functionality for importing device, module, and rack types.
    """
    form_class = None
    check_slug_conflict = True

    def find_existing(self, entry):
        if manufacturer := find_manufacturer(entry.get('manufacturer')):
            return self.model.objects.filter(manufacturer=manufacturer, model=entry.get('model')).first()
        return None

    def get_required_permissions(self, entry, instance):
        perms = super().get_required_permissions(entry, instance)
        perms.add('dcim.view_manufacturer')
        # An existing object keeps its manufacturer
        names = {entry.get('manufacturer') if instance is None else None} | {
            item.get('manufacturer') for item in (entry.get('dtl') or {}).get('inventory-items') or []
            if isinstance(item, dict) and item.get('manufacturer')
        }
        if any(name and not find_manufacturer(name) for name in names):
            perms.add('dcim.add_manufacturer')
        return perms

    def get_record(self, entry, dtl, manufacturer, instance):
        """
        Return the data for the import form from the catalog entry. An existing object keeps its manufacturer, model,
        and slug, which may have been changed locally.
        """
        record = {
            name: dtl[name] for name in self.form_class.base_fields
            if name in dtl and name not in EXCLUDED_PARENT_FIELDS and not isinstance(dtl[name], (list, dict))
        }
        if instance is None:
            record.update({
                'manufacturer': manufacturer.name,
                'model': entry.get('model'),
            })
            if 'slug' in self.form_class.base_fields:
                record['slug'] = entry.get('slug')
        if 'part_number' in self.form_class.base_fields and entry.get('part_number') is not None:
            # A whitespace-only part number would be mistaken for a real one
            record['part_number'] = entry['part_number'].strip()
        return record

    def save_object(self, entry, dtl, instance, user, result):
        if not entry.get('manufacturer') or not entry.get('model'):
            raise ValidationError(_("The catalog entry does not specify a manufacturer and model."))
        manufacturer = get_or_create_manufacturer(entry['manufacturer']) if instance is None else None

        # Skip an entry whose slug is held by a different type from the same manufacturer
        if self.check_slug_conflict and instance is None:
            conflict = self.model.objects.filter(manufacturer=manufacturer, slug=entry.get('slug')).first()
            if conflict is not None:
                raise ImportSkipped(_(
                    "A {object_type} with slug {slug} already exists for {manufacturer} ({model})."
                ).format(
                    object_type=self.model._meta.verbose_name,
                    slug=entry.get('slug'),
                    manufacturer=manufacturer,
                    model=conflict.model,
                ))

        record = self.get_record(entry, dtl, manufacturer, instance)
        return save_form(
            self.form_class,
            record,
            instance or self.model(),
            user=user,
            protected=('manufacturer', 'model', 'slug'),
            warnings=result.warnings,
            label=self.model._meta.verbose_name,
        )


class EndOfLifeMixin:
    """
    Populate a type's end_of_life date from the catalog's last support date.
    """
    def get_end_of_life(self, entry, instance):
        """
        Return the end of life date to set, or None to leave the field unchanged. A value which no longer matches
        the date previously imported from the catalog is assumed to have been set locally and is preserved.
        """
        lifecycle = (entry.get('enrichment') or {}).get('lifecycle') or {}
        end_of_life = parse_strict_date(lifecycle.get('last_support_date'))
        if end_of_life is None:
            return None
        if instance is None or instance.end_of_life is None:
            return end_of_life

        from ndx.models import Enrichment
        previous = Enrichment.objects.filter(
            import_record__object_type=ContentType.objects.get_for_model(instance),
            import_record__object_id=instance.pk,
        ).values_list('last_support_date', flat=True).first()
        if instance.end_of_life == parse_strict_date(previous):
            return end_of_life
        return None


@register_importer
class DeviceTypeImporter(EndOfLifeMixin, ComponentTemplatesMixin, DCIMTypeImporter):
    entry_type = 'device-type'
    model = DeviceType
    label = _('Device type')
    form_class = forms.DeviceTypeImportForm
    parent_field = 'device_type'
    component_forms = forms.DEVICE_TYPE_COMPONENT_IMPORT_FORMS

    def get_record(self, entry, dtl, manufacturer, instance):
        record = super().get_record(entry, dtl, manufacturer, instance)
        # Device bays require a parent device type
        if not record.get('subdevice_role') and dtl.get('device-bays'):
            record['subdevice_role'] = 'parent'
        if end_of_life := self.get_end_of_life(entry, instance):
            record['end_of_life'] = end_of_life
        return record

    def import_entry(self, entry, instance, user, result):
        dtl, capacity = normalize_dtl(entry.get('dtl'))
        device_type = self.save_object(entry, dtl, instance, user, result)
        self.import_components(device_type, dtl, user, result)
        if capacity is not None:
            result.enrichment_fields['power_capacity_watts'] = capacity
        return device_type

    def post_import(self, obj, entry, client, result):
        from django.conf import settings

        if settings.NDX_IMPORT_IMAGES:
            import_images(obj, entry, client, result)


@register_importer
class ModuleTypeImporter(EndOfLifeMixin, ComponentTemplatesMixin, DCIMTypeImporter):
    entry_type = 'module-type'
    model = ModuleType
    label = _('Module type')
    form_class = forms.ModuleTypeImportForm
    parent_field = 'module_type'
    component_forms = forms.MODULE_TYPE_COMPONENT_IMPORT_FORMS
    check_slug_conflict = False

    def get_required_permissions(self, entry, instance):
        perms = super().get_required_permissions(entry, instance)
        if get_pluggable(entry):
            perms.add('dcim.view_moduletypeprofile')
            if not ModuleTypeProfile.objects.filter(name='Transceiver').exists():
                perms.add('dcim.add_moduletypeprofile')
        return perms

    def get_record(self, entry, dtl, manufacturer, instance):
        record = super().get_record(entry, dtl, manufacturer, instance)
        if end_of_life := self.get_end_of_life(entry, instance):
            record['end_of_life'] = end_of_life
        # Map pluggable optic attributes to the core Transceiver profile
        if pluggable := get_pluggable(entry):
            record['profile'] = get_transceiver_profile().name
            record['attribute_data'] = get_transceiver_attributes(pluggable)
        return record

    def import_entry(self, entry, instance, user, result):
        dtl = normalize_dtl(entry.get('dtl'))[0]
        module_type = self.save_object(entry, dtl, instance, user, result)
        self.import_components(module_type, dtl, user, result)
        return module_type


@register_importer
class RackTypeImporter(DCIMTypeImporter):
    entry_type = 'rack-type'
    model = RackType
    label = _('Rack type')
    form_class = forms.RackTypeImportForm

    def import_entry(self, entry, instance, user, result):
        return self.save_object(entry, entry.get('dtl') or {}, instance, user, result)


#
# Helpers
#

def import_images(device_type, entry, client, result):
    """
    Download and attach the front and rear images for a device type. An image which is already present (whether
    imported previously or uploaded locally) is left unchanged.
    """
    vendor_slug, slug = entry.get('vendor_slug'), entry.get('slug')
    updated = False
    for face in ('front', 'rear'):
        # Fetch only the images the catalog publishes
        if not entry.get(f'{face}_image') or getattr(device_type, f'{face}_image'):
            continue
        if not (image := client.get_image(vendor_slug, slug, face)):
            result.image_errors.append(_('Failed to retrieve {face} image').format(face=face))
            continue
        if not updated:
            device_type.snapshot()
        filename = f'{slug}.{face}{image.extension}'
        getattr(device_type, f'{face}_image').save(filename, ContentFile(image.content), save=False)
        updated = True

    if updated:
        # Refresh counters which were updated in the database during import, so the save doesn't overwrite them
        counters = [f.name for f in device_type._meta.concrete_fields if isinstance(f, CounterCacheField)]
        device_type.refresh_from_db(fields=counters)
        device_type.full_clean()
        device_type.save()


def get_pluggable(entry):
    return ((entry.get('enrichment') or {}).get('extensions') or {}).get('pluggable')


def get_transceiver_profile():
    """
    Return the core Transceiver module type profile, creating it if needed (it is absent on installations which
    predate its introduction).
    """
    with TRANSCEIVER_PROFILE_FILE.open() as f:
        data = json.load(f)
    profile = ModuleTypeProfile.objects.filter(name=data['name']).first()
    if profile is None:
        profile = ModuleTypeProfile(**data)
        profile.full_clean()
        profile.save()
    return profile


def get_transceiver_attributes(pluggable):
    """
    Map a catalog pluggable definition to the attributes of the Transceiver module type profile.
    """
    if not isinstance(pluggable, dict):
        return {}
    attrs = {}
    if form_factor := pluggable.get('form_factor'):
        attrs['form_factor'] = form_factor
    if line_rate := pluggable.get('line_rate'):
        attrs['data_rate'] = line_rate
    if connector := pluggable.get('connector'):
        attrs['connector_type'] = connector
    # A fixed-length assembly (e.g. DAC) reports its length as its reach
    reach = pluggable.get('reach_m')
    if reach is None:
        reach = pluggable.get('length_m')
    if reach is not None:
        attrs['reach'] = reach
    if media := FIBER_MEDIA.get(pluggable.get('fiber'), pluggable.get('fiber')):
        attrs['media'] = media
    # Compose an Ethernet PHY name (e.g. 100GBASE-LR4) from the line rate and PMD
    if pmd := pluggable.get('media'):
        if line_rate and pluggable.get('protocol') in (None, 'ethernet'):
            attrs['phy'] = f'{line_rate}BASE-{pmd}'
        else:
            attrs['phy'] = pmd
    return attrs
