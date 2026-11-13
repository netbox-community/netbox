import shutil
import tempfile
import uuid
from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.db.models.signals import pre_delete
from django.test import override_settings

from core.models import ObjectChange
from dcim.models import (
    DeviceType,
    FrontPortTemplate,
    InterfaceTemplate,
    InventoryItemTemplate,
    Manufacturer,
    ModuleType,
    ModuleTypeProfile,
    PortTemplateMapping,
    PowerPortTemplate,
    RackType,
)
from ndx.client import NDXImage
from ndx.importers import ImportAborted, Importer, get_importer, import_entries, register_importer
from ndx.models import Enrichment, ImportRecord, Provenance
from netbox.registry import registry
from users.models import ObjectPermission, User
from utilities.request import NetBoxFakeRequest, apply_request_processors
from utilities.testing import TestCase

from .utils import (
    mock_enrichment,
    mock_enrichment_flags,
    mock_entry,
    mock_error_response,
    mock_manifest_response,
    mock_pdu_entry,
)

DEVICE_TYPE_PERMISSIONS = (
    'dcim.add_devicetype', 'dcim.change_devicetype', 'dcim.view_devicetype', 'dcim.add_manufacturer',
    'dcim.view_manufacturer', 'dcim.add_consoleporttemplate', 'dcim.change_consoleporttemplate',
    'dcim.add_consoleserverporttemplate', 'dcim.change_consoleserverporttemplate', 'dcim.add_powerporttemplate',
    'dcim.change_powerporttemplate', 'dcim.add_poweroutlettemplate', 'dcim.change_poweroutlettemplate',
    'dcim.add_interfacetemplate', 'dcim.change_interfacetemplate', 'dcim.add_frontporttemplate',
    'dcim.change_frontporttemplate', 'dcim.add_rearporttemplate', 'dcim.change_rearporttemplate',
    'dcim.add_modulebaytemplate', 'dcim.change_modulebaytemplate', 'dcim.add_devicebaytemplate',
    'dcim.change_devicebaytemplate', 'dcim.add_inventoryitemtemplate', 'dcim.change_inventoryitemtemplate',
)


def get_client(entry, checksums=None):
    client = MagicMock()
    client.get_manifest.return_value = mock_manifest_response(checksums or {entry['vendor_slug']: 'abc123'})
    client.get_entry.return_value = entry
    client.get_image.return_value = None
    return client


class ImporterTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()

    def run_import(self, entry, user=None, checksums=None):
        client = get_client(entry, checksums)
        result = import_entries([f"{entry['vendor_slug']}/{entry['slug']}"], user or self.user, client=client)[0]
        return result, client

    def test_import_device_type(self):
        result, _ = self.run_import(mock_entry())
        self.assertTrue(result.success, result.errors)
        self.assertTrue(result.created)
        self.assertEqual(result.component_errors, [])

        device_type = DeviceType.objects.get(model='Catalyst 9300')
        self.assertEqual(result.object, device_type)
        self.assertEqual(device_type.manufacturer.name, 'Cisco')
        self.assertEqual(device_type.slug, 'catalyst-9300')
        self.assertEqual(device_type.part_number, 'C9300-24T')
        self.assertEqual(device_type.airflow, 'front-to-rear')
        self.assertEqual(device_type.weight, 6.5)
        self.assertEqual(device_type.comments, 'Imported from NDX.')
        # Device bays imply a parent device type
        self.assertEqual(device_type.subdevice_role, 'parent')

        self.assertEqual(device_type.interfacetemplates.count(), 3)
        interface = device_type.interfacetemplates.get(name='GigabitEthernet0/0/0')
        self.assertTrue(interface.mgmt_only)
        self.assertFalse(interface.enabled)
        self.assertEqual(interface.poe_mode, 'pd')
        self.assertTrue(device_type.interfacetemplates.get(name='GigabitEthernet0/0/1').enabled)
        self.assertEqual(device_type.interfacetemplates.get(name='radio0').rf_role, 'ap')
        self.assertEqual(device_type.powerporttemplates.get().maximum_draw, 350)
        self.assertEqual(device_type.consoleporttemplates.count(), 1)
        self.assertEqual(device_type.consoleserverporttemplates.count(), 1)
        self.assertEqual(device_type.frontporttemplates.get().positions, 2)
        self.assertEqual(device_type.rearporttemplates.get().positions, 4)
        self.assertEqual(device_type.modulebaytemplates.get().position, '1')
        self.assertEqual(device_type.devicebaytemplates.count(), 1)
        self.assertEqual(InventoryItemTemplate.objects.get(device_type=device_type).manufacturer.name, 'Cisco')
        mapping = PortTemplateMapping.objects.get(device_type=device_type)
        self.assertEqual(mapping.front_port.name, 'Front1')
        self.assertEqual(mapping.rear_port.name, 'Rear1')
        self.assertEqual(mapping.rear_port_position, 2)

        record = ImportRecord.objects.get()
        self.assertEqual(record.object, device_type)
        self.assertEqual(record.ndx_id, 'cisco/catalyst-9300')
        self.assertEqual(record.entry_type, 'device-type')
        self.assertEqual(record.vendor_slug, 'cisco')
        self.assertEqual(record.source, 'community')
        self.assertEqual(record.checksum, 'abc123')
        self.assertFalse(record.update_available)
        self.assertFalse(Enrichment.objects.exists())

    def test_reimport_device_type(self):
        self.run_import(mock_entry())
        device_type = DeviceType.objects.get()
        device_type.description = 'Local description'
        device_type.save()
        ImportRecord.objects.update(update_available=True, checksum='old')

        entry = mock_entry()
        entry['dtl']['comments'] = 'Updated comments'
        entry['dtl']['interfaces'][1]['label'] = 'Gi0/0/1'
        entry['dtl']['interfaces'].append({'name': 'GigabitEthernet0/0/2', 'type': '1000base-t'})
        result, _ = self.run_import(entry, checksums={'cisco': 'def456'})

        self.assertTrue(result.success, result.errors)
        self.assertFalse(result.created)
        self.assertEqual(result.component_errors, [])
        device_type.refresh_from_db()
        self.assertEqual(DeviceType.objects.count(), 1)
        self.assertEqual(device_type.comments, 'Updated comments')
        self.assertEqual(device_type.description, 'Local description')
        self.assertEqual(device_type.interfacetemplates.count(), 4)
        self.assertEqual(device_type.interfacetemplates.get(name='GigabitEthernet0/0/1').label, 'Gi0/0/1')
        self.assertEqual(PortTemplateMapping.objects.count(), 1)
        self.assertEqual(Manufacturer.objects.count(), 1)

        record = ImportRecord.objects.get()
        self.assertFalse(record.update_available)
        self.assertEqual(record.checksum, 'def456')

    def test_reimport_unchanged(self):
        self.run_import(mock_entry())
        request = NetBoxFakeRequest({
            'META': {}, 'COOKIES': {}, 'POST': {}, 'GET': {}, 'FILES': {}, 'user': self.user, 'method': 'POST',
            'path': '/ndx/catalog/import/', 'id': uuid.uuid4(),
        })
        with apply_request_processors(request):
            result, _ = self.run_import(mock_entry())
        self.assertTrue(result.success, result.errors)

        # Only the import record (its last_imported time) is changed
        changes = ObjectChange.objects.filter(request_id=request.id)
        self.assertEqual(set(changes.values_list('changed_object_type__model', flat=True)), {'importrecord'})

    def test_reimport_preserves_unsupplied_fields(self):
        # A type created outside the importer, with empty values stored in their default representations
        manufacturer = Manufacturer.objects.create(name='Cisco', slug='cisco')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Catalyst 9300', slug='catalyst-9300', part_number='C9300-24T', u_height=1
        )
        interface = InterfaceTemplate.objects.create(device_type=device_type, name='Gi1', type='1000base-t')
        values = {
            'airflow': device_type.airflow,
            'subdevice_role': device_type.subdevice_role,
            'poe_mode': interface.poe_mode,
            'poe_type': interface.poe_type,
            'rf_role': interface.rf_role,
        }

        request = NetBoxFakeRequest({
            'META': {}, 'COOKIES': {}, 'POST': {}, 'GET': {}, 'FILES': {}, 'user': self.user, 'method': 'POST',
            'path': '/ndx/catalog/import/', 'id': uuid.uuid4(),
        })
        entry = mock_entry(dtl={'u_height': 1, 'interfaces': [{'name': 'Gi1', 'type': '1000base-t'}]})
        with apply_request_processors(request):
            result, _ = self.run_import(entry)
        self.assertTrue(result.success, result.errors)
        self.assertFalse(result.created)

        device_type.refresh_from_db()
        interface.refresh_from_db()
        self.assertEqual({
            'airflow': device_type.airflow,
            'subdevice_role': device_type.subdevice_role,
            'poe_mode': interface.poe_mode,
            'poe_type': interface.poe_type,
            'rf_role': interface.rf_role,
        }, values)
        changes = ObjectChange.objects.filter(request_id=request.id)
        self.assertEqual(set(changes.values_list('changed_object_type__model', flat=True)), {'importrecord'})

    def test_enrichment(self):
        result, _ = self.run_import(mock_entry(
            source='netbox_labs', enrichment=mock_enrichment(), enrichment_flags=mock_enrichment_flags()
        ))
        self.assertTrue(result.success, result.errors)

        enrichment = Enrichment.objects.get()
        self.assertEqual(enrichment.import_record.source, 'netbox_labs')
        self.assertEqual(enrichment.tdp_watts, 350)
        self.assertEqual(enrichment.ga_date, '2018-11-01')
        self.assertEqual(enrichment.ingress_protection, 'IP20')
        self.assertEqual(enrichment.noise_level_dba, 42.5)
        self.assertEqual(enrichment.nos, 'IOS-XE')
        self.assertEqual(enrichment.api_types, ['netconf', 'restconf'])
        self.assertEqual(enrichment.snmp_sys_object_id, '1.3.6.1.4.1.9.1.2745')
        self.assertTrue(enrichment.has_lifecycle)
        self.assertTrue(enrichment.has_snmp)
        self.assertIn('platform', enrichment.extensions)

        self.assertEqual(Provenance.objects.count(), 2)
        provenance = Provenance.objects.get(field='thermal.tdp_watts')
        self.assertEqual(provenance.type, 'vendor_datasheet')
        # A timestamp is truncated to its date
        self.assertEqual(provenance.retrieved, date(2024, 2, 20))

        # Re-importing reconciles provenance entries by field
        enrichment_data = mock_enrichment()
        enrichment_data['provenance'] = enrichment_data['provenance'][:1]
        self.run_import(mock_entry(enrichment=enrichment_data, enrichment_flags=mock_enrichment_flags()))
        self.assertEqual(list(Provenance.objects.values_list('field', flat=True)), ['lifecycle.ga_date'])

    def test_invalid_enrichment_values_replaced(self):
        enrichment = mock_enrichment()
        enrichment['environmental']['mtbf_hours'] = 2 ** 40
        enrichment['provenance'].append({'field': 'x' * 101, 'source': 'https://example.com/'})
        result, _ = self.run_import(mock_entry(enrichment=enrichment))

        self.assertTrue(result.success, result.errors)
        self.assertIsNone(Enrichment.objects.get().mtbf_hours)
        self.assertEqual(Provenance.objects.count(), 2)
        self.assertEqual(len(result.warnings), 2)

    def test_end_of_life(self):
        self.run_import(mock_entry(enrichment=mock_enrichment()))
        device_type = DeviceType.objects.get()
        self.assertEqual(device_type.end_of_life, date(2028, 10, 31))

        # A changed catalog date replaces one which was imported previously
        enrichment = mock_enrichment()
        enrichment['lifecycle']['last_support_date'] = '2029-01-31'
        self.run_import(mock_entry(enrichment=enrichment))
        device_type.refresh_from_db()
        self.assertEqual(device_type.end_of_life, date(2029, 1, 31))

        # A locally modified date is preserved
        device_type.end_of_life = date(2030, 6, 30)
        device_type.save()
        enrichment['lifecycle']['last_support_date'] = '2029-02-28'
        self.run_import(mock_entry(enrichment=enrichment))
        device_type.refresh_from_db()
        self.assertEqual(device_type.end_of_life, date(2030, 6, 30))

    def test_end_of_life_partial_date_ignored(self):
        enrichment = mock_enrichment()
        enrichment['lifecycle']['last_support_date'] = '2028-10'
        self.run_import(mock_entry(enrichment=enrichment))
        self.assertIsNone(DeviceType.objects.get().end_of_life)
        self.assertEqual(Enrichment.objects.get().last_support_date, '2028-10')

    def test_pdu_power_model(self):
        result, _ = self.run_import(mock_pdu_entry())
        self.assertTrue(result.success, result.errors)

        device_type = DeviceType.objects.get()
        for port in PowerPortTemplate.objects.filter(device_type=device_type):
            self.assertIsNone(port.maximum_draw)
            self.assertIsNone(port.allocated_draw)
        self.assertEqual(device_type.poweroutlettemplates.get(name='Outlet 1').power_port.name, 'Input A')
        # The rated capacity is retained on the enrichment record
        self.assertEqual(Enrichment.objects.get().power_capacity_watts, 1440)

    def test_legacy_port_mappings(self):
        dtl = {
            'front-ports': [{'name': 'Front1', 'type': 'lc', 'rear_port': 'Rear1', 'rear_port_position': 3}],
            'rear-ports': [{'name': 'Rear1', 'type': 'lc', 'positions': 4}],
        }
        result, _ = self.run_import(mock_entry(dtl=dtl))
        self.assertTrue(result.success, result.errors)
        mapping = PortTemplateMapping.objects.get()
        self.assertEqual(mapping.front_port, FrontPortTemplate.objects.get(name='Front1'))
        self.assertEqual(mapping.rear_port_position, 3)

    def test_interface_bridge(self):
        dtl = {
            'interfaces': [
                {'name': 'eth0', 'type': '1000base-t', 'bridge': 'br0'},
                {'name': 'br0', 'type': 'bridge'},
            ],
        }
        result, _ = self.run_import(mock_entry(dtl=dtl))
        self.assertTrue(result.success, result.errors)
        self.assertEqual(InterfaceTemplate.objects.get(name='eth0').bridge, InterfaceTemplate.objects.get(name='br0'))

    def test_invalid_values_replaced(self):
        dtl = {
            'airflow': 'sideways',
            'interfaces': [{'name': 'eth0', 'type': 'warp-drive'}],
        }
        result, _ = self.run_import(mock_entry(dtl=dtl))
        self.assertTrue(result.success, result.errors)
        self.assertIsNone(DeviceType.objects.get().airflow)
        # A required choice falls back to "other"
        self.assertEqual(InterfaceTemplate.objects.get(name='eth0').type, 'other')
        self.assertEqual(len(result.warnings), 2)

    def test_invalid_value_preserves_existing(self):
        self.run_import(mock_entry())
        entry = mock_entry()
        entry['dtl']['airflow'] = 'sideways'
        result, _ = self.run_import(entry)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(DeviceType.objects.get().airflow, 'front-to-rear')

    def test_slug_conflict_skipped(self):
        manufacturer = Manufacturer.objects.create(name='Cisco', slug='cisco')
        DeviceType.objects.create(manufacturer=manufacturer, model='C9300', slug='catalyst-9300')

        result, _ = self.run_import(mock_entry())
        self.assertFalse(result.success)
        self.assertTrue(result.skipped)
        self.assertEqual(DeviceType.objects.count(), 1)
        self.assertFalse(ImportRecord.objects.exists())

    def test_reimport_locally_renamed(self):
        self.run_import(mock_entry())
        device_type = DeviceType.objects.get()
        device_type.model = 'Local name'
        device_type.slug = 'local-name'
        device_type.save()

        entry = mock_entry()
        entry['dtl']['comments'] = 'Updated comments'
        result, _ = self.run_import(entry)

        self.assertTrue(result.success, result.errors)
        self.assertFalse(result.created)
        device_type = DeviceType.objects.get()
        self.assertEqual(device_type.model, 'Local name')
        self.assertEqual(device_type.slug, 'local-name')
        self.assertEqual(device_type.comments, 'Updated comments')
        self.assertEqual(ImportRecord.objects.get().object, device_type)

    def test_object_tracked_by_other_entry(self):
        self.run_import(mock_entry())
        result, _ = self.run_import(mock_entry(slug='catalyst-9300-vendor'))

        self.assertFalse(result.success)
        self.assertTrue(result.skipped)
        self.assertIn('cisco/catalyst-9300', result.message)
        self.assertEqual(DeviceType.objects.count(), 1)
        self.assertEqual(list(ImportRecord.objects.values_list('ndx_id', flat=True)), ['cisco/catalyst-9300'])

    def test_existing_manufacturer_matched_by_slug(self):
        Manufacturer.objects.create(name='Cisco Systems', slug='cisco')
        result, _ = self.run_import(mock_entry())
        self.assertTrue(result.success, result.errors)
        self.assertEqual(Manufacturer.objects.count(), 1)
        self.assertEqual(DeviceType.objects.get().manufacturer.name, 'Cisco Systems')

    def test_import_module_type(self):
        ModuleTypeProfile.objects.filter(name='Transceiver').delete()
        enrichment = mock_enrichment()
        enrichment['extensions']['pluggable'] = {
            'form_factor': 'QSFP28',
            'line_rate': '100G',
            'media': 'LR4',
            'fiber': 'SMF',
            'connector': 'LC',
            'reach_m': 10000,
        }
        entry = mock_entry(
            slug='qsfp-100g-lr4', model='QSFP-100G-LR4', entry_type='module-type', enrichment=enrichment,
            dtl={'interfaces': [{'name': 'Port 1', 'type': '100gbase-x-qsfp28'}]},
        )
        result, _ = self.run_import(entry)
        self.assertTrue(result.success, result.errors)

        module_type = ModuleType.objects.get()
        self.assertEqual(module_type.profile.name, 'Transceiver')
        self.assertEqual(module_type.attribute_data, {
            'form_factor': 'QSFP28',
            'data_rate': '100G',
            'connector_type': 'LC',
            'reach': 10000,
            'media': 'SMF',
            'phy': '100GBASE-LR4',
        })
        self.assertEqual(module_type.interfacetemplates.count(), 1)
        self.assertEqual(module_type.end_of_life, date(2028, 10, 31))
        self.assertEqual(ImportRecord.objects.get().entry_type, 'module-type')

    def test_import_rack_type(self):
        entry = mock_entry(
            vendor_slug='apc', slug='ar3100', manufacturer='APC', model='AR3100', entry_type='rack-type',
            dtl={'form_factor': '4-post-cabinet', 'width': 19, 'u_height': 42, 'outer_unit': 'mm'},
        )
        result, _ = self.run_import(entry)
        self.assertTrue(result.success, result.errors)
        rack_type = RackType.objects.get()
        self.assertEqual(rack_type.form_factor, '4-post-cabinet')
        self.assertEqual(rack_type.u_height, 42)
        self.assertEqual(ImportRecord.objects.get().object, rack_type)

    def test_images(self):
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root)
        entry = mock_entry(front_image='images/cisco/catalyst-9300.front.jpg')
        client = get_client(entry)
        client.get_image.return_value = NDXImage(content=b'image', extension='.jpg')

        with override_settings(MEDIA_ROOT=media_root, NDX_IMPORT_IMAGES=True):
            result = import_entries(['cisco/catalyst-9300'], self.user, client=client)[0]

        self.assertTrue(result.success, result.errors)
        client.get_image.assert_called_once_with('cisco', 'catalyst-9300', 'front')
        device_type = DeviceType.objects.get()
        self.assertTrue(device_type.front_image.name.endswith('.jpg'))
        self.assertFalse(device_type.rear_image)
        # Counters written during the import are not overwritten
        self.assertEqual(device_type.interface_template_count, 3)

    def test_existing_images_preserved(self):
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root)
        entry = mock_entry(front_image='images/cisco/front.jpg', rear_image='images/cisco/rear.jpg')
        client = get_client(entry)
        client.get_image.return_value = NDXImage(content=b'image', extension='.jpg')

        with override_settings(MEDIA_ROOT=media_root, NDX_IMPORT_IMAGES=True):
            import_entries(['cisco/catalyst-9300'], self.user, client=client)
            device_type = DeviceType.objects.get()
            device_type.front_image.save('local.png', ContentFile(b'local'))

            client.get_image.reset_mock()
            result = import_entries(['cisco/catalyst-9300'], self.user, client=client)[0]

        self.assertTrue(result.success, result.errors)
        client.get_image.assert_not_called()
        device_type.refresh_from_db()
        self.assertTrue(device_type.front_image.name.endswith('local.png'))

    def test_post_import_failure(self):
        entry = mock_entry(front_image='images/cisco/front.jpg')
        with (
            override_settings(NDX_IMPORT_IMAGES=True),
            patch('ndx.importers.dcim.import_images', side_effect=OSError('Disk full')),
        ):
            result, _ = self.run_import(entry)

        # The import stands, with the failure reported (but not its details)
        self.assertTrue(result.success, result.errors)
        self.assertTrue(any('Post-import processing failed' in str(msg) for msg in result.warnings))
        self.assertFalse(any('Disk full' in str(msg) for msg in result.warnings))
        self.assertTrue(DeviceType.objects.exists())
        self.assertTrue(ImportRecord.objects.exists())

    def test_images_disabled(self):
        entry = mock_entry(front_image='images/cisco/catalyst-9300.front.png')
        client = get_client(entry)
        with override_settings(NDX_IMPORT_IMAGES=False):
            import_entries(['cisco/catalyst-9300'], self.user, client=client)
        client.get_image.assert_not_called()

    def test_permission_denied(self):
        user = User.objects.create_user(username='unprivileged')
        result, _ = self.run_import(mock_entry(), user=user)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, ['Permission denied'])
        self.assertFalse(DeviceType.objects.exists())

    def test_component_permissions_required(self):
        user = User.objects.create_user(username='limited')
        self.assign_permissions(user, ('dcim.add_devicetype', 'dcim.view_devicetype', 'dcim.add_manufacturer'))
        result, _ = self.run_import(mock_entry(), user=User.objects.get(pk=user.pk))
        self.assertEqual(result.errors, ['Permission denied'])

    def test_object_permission_constraints(self):
        user = User.objects.create_user(username='constrained')
        self.assign_permissions(user, [p for p in DEVICE_TYPE_PERMISSIONS if p != 'dcim.add_devicetype'])
        self.assign_permissions(user, ['dcim.add_devicetype'], constraints={'model': 'Something else'})
        result, _ = self.run_import(mock_entry(), user=User.objects.get(pk=user.pk))
        self.assertEqual(result.errors, ['Permission denied'])
        # The import is rolled back
        self.assertFalse(DeviceType.objects.exists())
        self.assertFalse(ImportRecord.objects.exists())

    def test_component_object_permission_constraints(self):
        user = User.objects.create_user(username='constrained')
        self.assign_permissions(user, [p for p in DEVICE_TYPE_PERMISSIONS if p != 'dcim.add_interfacetemplate'])
        self.assign_permissions(user, ['dcim.add_interfacetemplate'], constraints={'name': 'Something else'})
        result, _ = self.run_import(mock_entry(), user=User.objects.get(pk=user.pk))
        self.assertEqual(result.errors, ['Permission denied'])
        # The import is rolled back
        self.assertFalse(DeviceType.objects.exists())

    def test_bridge_requires_change_permission(self):
        entry = mock_entry()
        entry['dtl']['interfaces'][1]['bridge'] = 'GigabitEthernet0/0/0'
        user = User.objects.create_user(username='limited')
        self.assign_permissions(user, [p for p in DEVICE_TYPE_PERMISSIONS if p != 'dcim.change_interfacetemplate'])
        result, _ = self.run_import(entry, user=User.objects.get(pk=user.pk))
        self.assertEqual(result.errors, ['Permission denied'])

        self.assign_permissions(user, ['dcim.change_interfacetemplate'], constraints={'name': 'Something else'})
        result, _ = self.run_import(entry, user=User.objects.get(pk=user.pk))
        self.assertEqual(result.errors, ['Permission denied'])
        self.assertFalse(DeviceType.objects.exists())

    def test_unexpected_error_not_reported(self):
        with patch('ndx.importers.dcim.DeviceTypeImporter.import_entry', side_effect=RuntimeError('secret detail')):
            result, _ = self.run_import(mock_entry())
        self.assertFalse(result.success)
        self.assertNotIn('secret detail', ' '.join(map(str, result.errors)))

    def test_ndx_id_from_request(self):
        # The entry is tracked by the requested NDX ID, whatever the catalog response contains
        entry = mock_entry(vendor_slug='cisco-systems')
        client = get_client(entry)
        result = import_entries(['cisco/catalyst-9300'], self.user, client=client)[0]
        self.assertTrue(result.success, result.errors)
        record = ImportRecord.objects.get()
        self.assertEqual(record.ndx_id, 'cisco/catalyst-9300')
        self.assertEqual(record.vendor_slug, 'cisco')

    def test_permitted_user(self):
        user = User.objects.create_user(username='permitted')
        self.assign_permissions(user, DEVICE_TYPE_PERMISSIONS)
        result, _ = self.run_import(mock_entry(), user=User.objects.get(pk=user.pk))
        self.assertTrue(result.success, result.errors)

    def test_unsupported_entry_type(self):
        result, _ = self.run_import(mock_entry(entry_type='custom-object-type'))
        self.assertFalse(result.success)
        self.assertIn('Unsupported entry type', str(result.errors[0]))

    def test_entry_not_found(self):
        client = get_client(mock_entry())
        client.get_entry.return_value = mock_error_response(404)
        result = import_entries(['cisco/missing'], self.user, client=client)[0]
        self.assertFalse(result.success)
        self.assertEqual(str(result.errors[0]), 'This entry is not present in the NDX catalog.')

    def test_invalid_ndx_id(self):
        client = get_client(mock_entry())
        result = import_entries(['not-an-id'], self.user, client=client)[0]
        self.assertFalse(result.success)
        client.get_entry.assert_not_called()

    def test_manifest_unavailable(self):
        client = get_client(mock_entry())
        client.get_manifest.return_value = mock_error_response(401)
        with self.assertRaises(ImportAborted):
            import_entries(['cisco/catalyst-9300'], self.user, client=client)

        # A rate-limited manifest is tolerated
        client.get_manifest.return_value = mock_error_response(429)
        result = import_entries(['cisco/catalyst-9300'], self.user, client=client)[0]
        self.assertTrue(result.success, result.errors)
        self.assertEqual(ImportRecord.objects.get().checksum, '')

    def assign_permissions(self, user, names, constraints=None):
        from utilities.permissions import resolve_permission_type

        for name in names:
            object_type, action = resolve_permission_type(name)
            permission = ObjectPermission.objects.create(name=name, actions=[action], constraints=constraints)
            permission.users.add(user)
            permission.object_types.add(object_type)


class ImporterRegistryTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.registered = dict(registry['ndx_importers'])
        self.addCleanup(self.restore_registry)

    def restore_registry(self):
        registry['ndx_importers'].clear()
        registry['ndx_importers'].update(self.registered)
        pre_delete.disconnect(sender=ContentType, dispatch_uid='ndx_delete_import_records_contenttypes.contenttype')

    def test_core_importers(self):
        self.assertEqual(get_importer('device-type').model, DeviceType)
        self.assertEqual(get_importer('module-type').model, ModuleType)
        self.assertEqual(get_importer('rack-type').model, RackType)

    def test_register_importer(self):
        class SiteImporter(Importer):
            entry_type = 'site'
            model = ContentType
            label = 'Site'

        register_importer(SiteImporter)
        self.assertIsInstance(get_importer('site'), SiteImporter)

        with self.assertRaises(ImproperlyConfigured):
            register_importer(SiteImporter)

    def test_register_invalid_importer(self):
        class InvalidImporter(Importer):
            entry_type = 'Invalid Type'
            model = ContentType
            label = 'Invalid'

        with self.assertRaises(ImproperlyConfigured):
            register_importer(InvalidImporter)
        with self.assertRaises(ImproperlyConfigured):
            register_importer(object)
