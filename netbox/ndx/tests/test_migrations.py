import uuid
from datetime import date
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.test import TestCase

from core.models import Job
from dcim.models import DeviceType, Manufacturer, RackType, Site
from ndx.checks import check_plugin_version
from ndx.models import Enrichment, ImportRecord, Provenance
from users.models import ObjectPermission

migration = import_module('ndx.migrations.0002_import_plugin_data')
cleanup_migration = import_module('ndx.migrations.0003_plugin_cleanup')

# Plugin tables as of netbox_ndx v0.11.0
PLUGIN_SCHEMA = """
CREATE TABLE netbox_ndx_ndximportrecord (
    id bigint PRIMARY KEY, created timestamptz NULL, last_updated timestamptz NULL, custom_field_data jsonb,
    ndx_id varchar(255) UNIQUE, ndx_manufacturer varchar(255), ndx_model varchar(255),
    ndx_vendor_slug varchar(100), ndx_version varchar(64), ndx_source varchar(20), content_type_id integer,
    object_id bigint, first_imported timestamptz, last_synced timestamptz, update_available boolean
);
CREATE TABLE netbox_ndx_ndxenrichment (
    id bigint PRIMARY KEY, created timestamptz NULL, last_updated timestamptz NULL, custom_field_data jsonb,
    import_record_id bigint, tdp_watts integer, airflow_cfm double precision, cooling_type varchar(50),
    ga_date varchar(20), eol_announced varchar(20), eos_date varchar(20), eosw_date varchar(20),
    eosec_date varchar(20), last_support_date varchar(20), max_operating_temp_c double precision,
    min_operating_temp_c double precision, max_operating_humidity integer, min_operating_humidity integer,
    max_operating_altitude_m integer, ingress_protection varchar(10), mtbf_hours integer,
    typical_power_draw_watts integer, max_power_draw_watts integer, noise_level_dba double precision,
    power_capacity_watts integer, nos varchar(100), nos_family varchar(100), api_types jsonb,
    snmp_sys_object_id varchar(255), snmp_vendor_oid_prefix varchar(255), has_lifecycle boolean,
    has_thermal boolean, has_environmental boolean, has_operational boolean, has_platform boolean,
    has_snmp boolean, extensions_data jsonb
);
CREATE TABLE netbox_ndx_ndxprovenance (
    id bigint PRIMARY KEY, created timestamptz NULL, last_updated timestamptz NULL, enrichment_id bigint,
    field varchar(100), source varchar(500), provenance_type varchar(50), confidence varchar(20), retrieved date,
    note text, UNIQUE (enrichment_id, field)
);
"""


def create_plugin_tables(migration_name=migration.PLUGIN_MIN_MIGRATION[1]):
    """
    Create the plugin's tables and record its migrations as applied up to the given migration.
    """
    with connection.cursor() as cursor:
        cursor.execute(PLUGIN_SCHEMA)
    MigrationRecorder(connection).record_applied('netbox_ndx', migration_name)


ENRICHMENT_VALUES = {
    'tdp_watts': 350, 'airflow_cfm': 65.0, 'cooling_type': 'fans', 'ga_date': '2018-11-01', 'eol_announced': '',
    'eos_date': '2025-10', 'eosw_date': '', 'eosec_date': '', 'last_support_date': '2028-10-31',
    'max_operating_temp_c': 45.0, 'min_operating_temp_c': 0.0, 'max_operating_humidity': 95,
    'min_operating_humidity': 5, 'max_operating_altitude_m': 3000, 'ingress_protection': 'IP20',
    'mtbf_hours': 250000, 'typical_power_draw_watts': 250, 'max_power_draw_watts': 350, 'noise_level_dba': 42.5,
    'nos': 'IOS-XE', 'nos_family': 'IOS', 'api_types': '["netconf"]', 'snmp_sys_object_id': '1.3.6.1.4.1.9.1.2745',
    'snmp_vendor_oid_prefix': '1.3.6.1.4.1.9', 'power_capacity_watts': 7200, 'has_lifecycle': True, 'has_thermal': True,
    'has_environmental': True, 'has_operational': True, 'has_platform': True, 'has_snmp': False,
    'extensions_data': '{"gnmi": {}}',
}


class ImportPluginDataTestCase(TestCase):

    def run_migration(self):
        migration.import_plugin_data(apps, SimpleNamespace(connection=connection))

    def test_no_plugin_tables(self):
        self.run_migration()
        self.assertFalse(ImportRecord.objects.exists())

    def test_import_plugin_data(self):
        manufacturer = Manufacturer.objects.create(name='Cisco', slug='cisco')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Catalyst 9300', slug='c9300')
        rack_type = RackType.objects.create(manufacturer=manufacturer, model='Rack', slug='rack', width=19)
        device_type_ct = ContentType.objects.get_for_model(DeviceType).pk
        rack_type_ct = ContentType.objects.get_for_model(RackType).pk

        create_plugin_tables()
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO netbox_ndx_ndximportrecord (
                    id, created, last_updated, ndx_id, ndx_manufacturer, ndx_model, ndx_vendor_slug, ndx_version,
                    ndx_source, content_type_id, object_id, first_imported, last_synced, update_available
                ) VALUES (%s, NOW(), NOW(), %s, 'Cisco', 'Model', %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                """,
                [
                    (101, 'cisco/c9300', 'cisco', 'abc123', 'netbox_labs', device_type_ct, device_type.pk, True),
                    (102, 'cisco/rack', 'cisco', 'abc123', 'unknown', rack_type_ct, rack_type.pk, False),
                    # Orphaned record (the device type was deleted)
                    (103, 'cisco/deleted', 'cisco', 'abc123', 'community', device_type_ct, 999999, False),
                ],
            )
            columns = ', '.join(ENRICHMENT_VALUES)
            placeholders = ', '.join(['%s'] * len(ENRICHMENT_VALUES))
            cursor.executemany(
                f"""
                INSERT INTO netbox_ndx_ndxenrichment (id, created, last_updated, import_record_id, {columns})
                VALUES (%s, NOW(), NOW(), %s, {placeholders})
                """,
                [(201, 101, *ENRICHMENT_VALUES.values()), (203, 103, *ENRICHMENT_VALUES.values())],
            )
            cursor.executemany(
                """
                INSERT INTO netbox_ndx_ndxprovenance (
                    id, enrichment_id, field, source, provenance_type, confidence, retrieved, note
                ) VALUES (%s, %s, %s, 'https://cisco.com/', 'vendor_datasheet', 'high', '2024-01-15', '')
                """,
                [
                    (301, 201, 'lifecycle.ga_date'),
                    (303, 201, 'thermal.tdp_watts'),
                    (304, 203, 'lifecycle.ga_date'),
                ],
            )

        self.run_migration()

        self.assertEqual(sorted(ImportRecord.objects.values_list('pk', flat=True)), [101, 102])
        record = ImportRecord.objects.get(pk=101)
        self.assertEqual(record.object, device_type)
        self.assertEqual(record.ndx_id, 'cisco/c9300')
        self.assertEqual(record.entry_type, 'device-type')
        self.assertEqual(record.vendor_slug, 'cisco')
        self.assertEqual(record.source, 'netbox_labs')
        self.assertEqual(record.checksum, 'abc123')
        self.assertTrue(record.update_available)
        self.assertIsNotNone(record.last_imported)
        rack_record = ImportRecord.objects.get(pk=102)
        self.assertEqual(rack_record.entry_type, 'rack-type')
        self.assertEqual(rack_record.source, '')

        enrichment = Enrichment.objects.get()
        self.assertEqual(enrichment.import_record, record)
        self.assertEqual(enrichment.eos_date, '2025-10')
        self.assertEqual(enrichment.api_types, ['netconf'])
        self.assertEqual(enrichment.extensions, {'gnmi': {}})
        self.assertEqual(enrichment.power_capacity_watts, 7200)

        self.assertEqual(
            list(Provenance.objects.order_by('field').values_list('pk', 'field')),
            [(301, 'lifecycle.ga_date'), (303, 'thermal.tdp_watts')],
        )
        self.assertEqual(Provenance.objects.get(pk=301).retrieved, date(2024, 1, 15))

        # Primary key sequences continue past the copied rows
        new_record = ImportRecord.objects.create(
            object_type_id=device_type_ct, object_id=device_type.pk, ndx_id='cisco/new', entry_type='device-type',
            vendor_slug='cisco', last_imported=record.last_imported,
        )
        self.assertGreater(new_record.pk, 102)

    def test_outdated_plugin(self):
        create_plugin_tables('0004_retire_ndx_transceiver_profile')
        with self.assertRaises(RuntimeError):
            self.run_migration()


class PluginVersionCheckTestCase(TestCase):

    def test_no_plugin_tables(self):
        self.assertEqual(check_plugin_version(None, databases=['default']), [])

    def test_supported_plugin(self):
        create_plugin_tables()
        self.assertEqual(check_plugin_version(None, databases=['default']), [])

    def test_outdated_plugin(self):
        create_plugin_tables('0004_retire_ndx_transceiver_profile')

        # Not checked once the plugin's data has been imported
        self.assertEqual(check_plugin_version(None, databases=['default']), [])

        MigrationRecorder(connection).record_unapplied('ndx', '0002_import_plugin_data')
        errors = check_plugin_version(None, databases=['default'])
        self.assertEqual([error.id for error in errors], ['ndx.E001'])

        # No database access is permitted unless requested
        self.assertEqual(check_plugin_version(None), [])


class PluginCleanupTestCase(TestCase):

    def run_migration(self):
        schema_editor = SimpleNamespace(connection=connection)
        cleanup_migration.migrate_permissions(apps, schema_editor)
        cleanup_migration.delete_plugin_jobs(apps, schema_editor)

    def test_migrate_permissions(self):
        plugin_ct = ContentType.objects.create(app_label='netbox_ndx', model='ndximportrecord')
        site_ct = ContentType.objects.get_for_model(Site)
        permission = ObjectPermission.objects.create(name='NDX', actions=['view'])
        permission.object_types.set([plugin_ct, site_ct])
        constrained = ObjectPermission.objects.create(name='Constrained', actions=['view'], constraints={'id': 1})
        constrained.object_types.set([plugin_ct])

        self.run_migration()

        record_ct = ContentType.objects.get_for_model(ImportRecord)
        self.assertEqual(set(permission.object_types.all()), {plugin_ct, site_ct, record_ct})
        self.assertEqual(set(constrained.object_types.all()), {plugin_ct})

    def test_delete_plugin_jobs(self):
        jobs = {
            name: Job.objects.create(name=name, status=status, job_id=uuid.uuid4())
            for name, status in (
                ('NDX Sync Check', 'scheduled'),
                ('NDX Bulk Import', 'pending'),
                ('NDX Catalog Sync', 'scheduled'),
            )
        }
        completed = Job.objects.create(name='NDX Sync Check', status='completed', job_id=uuid.uuid4())

        self.run_migration()

        self.assertEqual(
            set(Job.objects.values_list('pk', flat=True)),
            {jobs['NDX Catalog Sync'].pk, completed.pk},
        )
