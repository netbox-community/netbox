import json
import tempfile
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase, override_settings


class BuildSchemaTestCase(TestCase):
    def test_output_is_valid_json(self):
        out = StringIO()

        call_command('buildschema', stdout=out)

        self.assertIsInstance(json.loads(out.getvalue()), dict)

    def test_write_flag_writes_schema_to_configured_base_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / 'netbox'
            output_dir = Path(tmpdir) / 'contrib'
            output_dir.mkdir()

            out = StringIO()
            with override_settings(BASE_DIR=base_dir):
                call_command('buildschema', write=True, stdout=out)

            output_file = output_dir / 'generated_schema.json'
            self.assertTrue(output_file.exists())
            self.assertIsInstance(json.loads(output_file.read_text(encoding='utf-8')), dict)
            self.assertIn(str(output_file), out.getvalue())


class TracePathsTestCase(TestCase):
    def test_no_cables(self):
        out = StringIO()

        call_command('trace_paths', no_input=True, stdout=out)

        self.assertIn('Finished.', out.getvalue())

    def test_force_no_cable_paths(self):
        out = StringIO()

        call_command('trace_paths', force=True, no_input=True, stdout=out)

        self.assertIn('Finished.', out.getvalue())

    def test_retraces_missing_cabled_endpoint_path(self):
        endpoint = object()

        class FakeQuerySet(list):
            def filter(self, *args, **kwargs):
                return self

            def count(self):
                return len(self)

        class FakeObjects:
            def filter(self, *args, **kwargs):
                return FakeQuerySet([endpoint])

        model = SimpleNamespace(
            objects=FakeObjects(),
            wireless_link=object(),
            _meta=SimpleNamespace(verbose_name='interface', verbose_name_plural='interfaces'),
        )
        out = StringIO()

        with (
            patch('dcim.management.commands.trace_paths.ENDPOINT_MODELS', (model,)),
            patch('dcim.management.commands.trace_paths.create_cablepaths') as create_cablepaths,
        ):
            call_command('trace_paths', no_input=True, stdout=out)

        create_cablepaths.assert_called_once_with([endpoint])
        self.assertIn('Retracing 1 cabled interfaces', out.getvalue())
        self.assertIn('Retraced 1 interfaces', out.getvalue())
        self.assertIn('Finished.', out.getvalue())

    def test_progress_bar_drawn_every_100_endpoints(self):
        endpoints = [object() for _ in range(100)]

        class FakeQuerySet(list):
            def filter(self, *args, **kwargs):
                return self

            def count(self):
                return len(self)

        class FakeObjects:
            def filter(self, *args, **kwargs):
                return FakeQuerySet(endpoints)

        model = SimpleNamespace(
            objects=FakeObjects(),
            wireless_link=object(),
            _meta=SimpleNamespace(verbose_name='interface', verbose_name_plural='interfaces'),
        )
        out = StringIO()

        with (
            patch('dcim.management.commands.trace_paths.ENDPOINT_MODELS', (model,)),
            patch('dcim.management.commands.trace_paths.create_cablepaths'),
        ):
            call_command('trace_paths', no_input=True, stdout=out)

        self.assertIn('[####################] 100%', out.getvalue())
        self.assertIn('Retraced 100 interfaces', out.getvalue())

    def test_force_aborts_when_confirmation_is_not_yes(self):
        out = StringIO()
        cable_paths = MagicMock()
        cable_paths.count.return_value = 1

        with (
            patch('dcim.management.commands.trace_paths.CablePath') as cable_path_model,
            patch('builtins.input', return_value='no'),
        ):
            cable_path_model.objects.all.return_value = cable_paths
            call_command('trace_paths', force=True, stdout=out)

        cable_paths.delete.assert_not_called()
        self.assertIn('WARNING: Forcing recalculation', out.getvalue())
        self.assertIn('Aborting', out.getvalue())

    def test_force_deletes_existing_paths_and_resets_sequence(self):
        out = StringIO()
        cable_paths = MagicMock()
        cable_paths.count.return_value = 2
        cable_paths.delete.return_value = (2, {})

        with (
            patch('dcim.management.commands.trace_paths.CablePath') as cable_path_model,
            patch('dcim.management.commands.trace_paths.ENDPOINT_MODELS', ()),
            patch('dcim.management.commands.trace_paths.connection') as connection,
        ):
            cable_path_model.objects.all.return_value = cable_paths
            connection.ops.sequence_reset_sql.return_value = ['RESET SEQUENCE']
            cursor = connection.cursor.return_value.__enter__.return_value

            call_command('trace_paths', force=True, no_input=True, stdout=out)

        cable_paths.delete.assert_called_once_with()
        cursor.execute.assert_called_once_with('RESET SEQUENCE')
        self.assertIn('Deleting 2 existing cable paths', out.getvalue())
        self.assertIn('Deleted 2 paths', out.getvalue())
        self.assertIn('Finished.', out.getvalue())
