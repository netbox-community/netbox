import os
import tempfile
from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from core.choices import DataSourceStatusChoices
from core.management.commands import nbshell, upgrade
from core.management.commands.rqworker import DEFAULT_QUEUES


class MakeMigrationsTestCase(TestCase):
    @override_settings(DEVELOPER=False)
    def test_blocked_in_non_developer_mode(self):
        with self.assertRaisesMessage(CommandError, 'development purposes only'):
            call_command('makemigrations', stdout=StringIO(), stderr=StringIO())

    @override_settings(DEVELOPER=False)
    def test_check_flag_allowed_in_non_developer_mode(self):
        with patch('core.management.commands.makemigrations._Command.handle') as super_handle:
            call_command(
                'makemigrations',
                check_changes=True,
                stdout=StringIO(),
                stderr=StringIO(),
            )

        super_handle.assert_called_once()
        self.assertTrue(super_handle.call_args.kwargs['check_changes'])


class NbShellTestCase(TestCase):
    def test_color_helpers_wrap_text(self):
        self.assertIn('message', nbshell.color('green', 'message'))
        self.assertIn('message', nbshell.bright('message'))

    def test_get_models_excludes_private_models(self):
        public_model = type('PublicModel', (), {})
        private_model = type('PrivateModel', (), {'_netbox_private': True})
        app_config = SimpleNamespace(get_models=lambda: [public_model, private_model])

        self.assertEqual(nbshell.get_models(app_config), [public_model])

    def test_get_constants_returns_module_attributes(self):
        constants = SimpleNamespace(FOO='bar', ANSWER=42)

        with patch('core.management.commands.nbshell.import_string', return_value=constants):
            self.assertEqual(
                nbshell.get_constants(SimpleNamespace(name='testapp')),
                {'FOO': 'bar', 'ANSWER': 42},
            )

    def test_get_constants_handles_missing_constants_module(self):
        with patch('core.management.commands.nbshell.import_string', side_effect=ImportError):
            self.assertEqual(nbshell.get_constants(SimpleNamespace(name='testapp')), {})

    def test_executes_inline_command(self):
        namespace = {}

        with patch(
            'core.management.commands.nbshell.Command.get_namespace',
            return_value=namespace,
        ):
            call_command('nbshell', command='answer = 42')

        self.assertEqual(namespace['answer'], 42)

    def test_starts_interactive_shell_without_inline_command(self):
        namespace = {'answer': 42}

        with (
            patch('core.management.commands.nbshell.Command.get_namespace', return_value=namespace),
            patch('core.management.commands.nbshell.Command.get_banner_text', return_value='banner'),
            patch('core.management.commands.nbshell.code.interact', return_value=None) as interact,
        ):
            call_command('nbshell', stdout=StringIO())

        interact.assert_called_once_with(banner='banner', local=namespace)

    def test_get_namespace_includes_models_constants_and_helpers(self):
        class DummyModel:
            pass

        app_config = SimpleNamespace(
            name='dummyapp',
            get_models=lambda: [DummyModel],
        )
        command = nbshell.Command()
        command.django_models = {}

        with (
            patch('core.management.commands.nbshell.CORE_APPS', ('dummyapp',)),
            patch('core.management.commands.nbshell.get_installed_plugins', return_value={}),
            patch('core.management.commands.nbshell.apps.get_app_config', return_value=app_config),
            patch('core.management.commands.nbshell.get_constants', return_value={'CONSTANT': 'value'}),
        ):
            namespace = command.get_namespace()

        self.assertIs(namespace['dummyapp'].DummyModel, DummyModel)
        self.assertEqual(namespace['dummyapp'].CONSTANT, 'value')
        self.assertEqual(command.django_models['dummyapp'], ['DummyModel'])
        self.assertEqual(namespace['lsapps'], command._lsapps)
        self.assertEqual(namespace['lsmodels'], command._lsmodels)

    def test_list_apps_and_models_helpers(self):
        command = nbshell.Command()
        command.django_models = {'dcim': ['Device', 'Site']}
        app_config = SimpleNamespace(verbose_name='DCIM')

        with (
            patch('core.management.commands.nbshell.apps.get_app_config', return_value=app_config),
            patch('builtins.print') as print_,
        ):
            command._lsapps()
            command._lsmodels('dcim')

        self.assertIn(('dcim - DCIM',), [call.args for call in print_.call_args_list])
        self.assertIn(('DCIM:',), [call.args for call in print_.call_args_list])
        self.assertIn(('  dcim.Device',), [call.args for call in print_.call_args_list])
        self.assertIn(('  dcim.Site',), [call.args for call in print_.call_args_list])

    def test_list_models_reports_unknown_app(self):
        command = nbshell.Command()
        command.django_models = {}

        with patch('builtins.print') as print_:
            command._lsmodels('unknown')

        print_.assert_called_once_with('No models listed for unknown')

    def test_list_models_lists_all_apps_when_no_app_label_given(self):
        command = nbshell.Command()
        command.django_models = {'dcim': ['Device'], 'ipam': ['IPAddress']}
        app_configs = {
            'dcim': SimpleNamespace(verbose_name='DCIM'),
            'ipam': SimpleNamespace(verbose_name='IPAM'),
        }

        with (
            patch(
                'core.management.commands.nbshell.apps.get_app_config',
                side_effect=lambda label: app_configs[label],
            ),
            patch('builtins.print') as print_,
        ):
            command._lsmodels()

        printed = [call.args for call in print_.call_args_list]
        self.assertIn(('DCIM:',), printed)
        self.assertIn(('IPAM:',), printed)
        self.assertIn(('  dcim.Device',), printed)
        self.assertIn(('  ipam.IPAddress',), printed)

    def test_banner_includes_installed_plugins(self):
        with (
            patch('core.management.commands.nbshell.platform.node', return_value='netbox'),
            patch('core.management.commands.nbshell.platform.python_version', return_value='3.12.0'),
            patch('core.management.commands.nbshell.get_version', return_value='5.2.0'),
            patch('core.management.commands.nbshell.get_installed_plugins', return_value={'plugin': '1.2.3'}),
        ):
            banner = nbshell.Command.get_banner_text()

        self.assertIn('NetBox interactive shell', banner)
        self.assertIn('Plugins:', banner)
        self.assertIn('plugin', banner)


class RQWorkerTestCase(TestCase):
    def test_defaults_to_all_queues_and_enables_scheduler(self):
        with (
            patch('core.management.commands.rqworker.registry', {'system_jobs': {}}),
            patch('core.management.commands.rqworker._Command.handle') as super_handle,
            self.assertLogs('netbox.rqworker', level='WARNING') as logs,
        ):
            call_command('rqworker', stdout=StringIO(), stderr=StringIO())

        super_handle.assert_called_once()
        args, kwargs = super_handle.call_args
        self.assertEqual(args, DEFAULT_QUEUES)
        self.assertTrue(kwargs['with_scheduler'])
        self.assertEqual(len(logs.output), 1)
        self.assertIn('No queues have been specified', logs.output[0])

    def test_schedules_registered_system_jobs(self):
        job = MagicMock()
        job.name = 'TestJob'

        with (
            patch('core.management.commands.rqworker.registry', {'system_jobs': {job: {'interval': 5}}}),
            patch('core.management.commands.rqworker._Command.handle') as super_handle,
        ):
            call_command('rqworker', 'high', stdout=StringIO(), stderr=StringIO())

        job.enqueue_once.assert_called_once_with(interval=5)
        super_handle.assert_called_once()
        args, kwargs = super_handle.call_args
        self.assertEqual(args, ('high',))
        self.assertTrue(kwargs['with_scheduler'])

    def test_system_jobs_must_specify_interval(self):
        job = MagicMock()
        job.name = 'TestJob'

        with patch('core.management.commands.rqworker.registry', {'system_jobs': {job: {}}}):
            with self.assertRaisesMessage(TypeError, 'System job must specify an interval'):
                call_command('rqworker', stdout=StringIO(), stderr=StringIO())


class SyncDataSourceTestCase(TestCase):
    class FakeDataSource:
        def __init__(self, name):
            self.name = name
            self.pk = name
            self.sync = MagicMock()

        def __str__(self):
            return self.name

        def get_status_display(self):
            return 'completed'

    class FakeQuerySet(list):
        def values(self, *fields):
            return [{field: getattr(item, field) for field in fields} for item in self]

    def test_requires_name_or_all(self):
        with self.assertRaisesMessage(CommandError, 'Must specify at least one data source'):
            call_command('syncdatasource', stdout=StringIO())

    def test_invalid_name(self):
        with patch('core.management.commands.syncdatasource.DataSource') as data_source_model:
            data_source_model.objects.filter.return_value = self.FakeQuerySet()
            with self.assertRaisesMessage(CommandError, 'Invalid data source names: nonexistent-source'):
                call_command('syncdatasource', 'nonexistent-source', stdout=StringIO())

        data_source_model.objects.filter.assert_called_once()
        self.assertEqual(
            set(data_source_model.objects.filter.call_args.kwargs['name__in']),
            {'nonexistent-source'},
        )

    def test_all_syncs_datasource(self):
        datasource = MagicMock()
        datasource.__str__.return_value = 'Test Data Source'
        datasource.get_status_display.return_value = 'completed'

        out = StringIO()

        with patch('core.management.commands.syncdatasource.DataSource') as data_source_model:
            data_source_model.objects.all.return_value = [datasource]
            call_command('syncdatasource', sync_all=True, stdout=out)

        data_source_model.objects.all.assert_called_once_with()
        datasource.sync.assert_called_once_with()
        self.assertIn('Syncing Test Data Source', out.getvalue())
        self.assertIn('completed', out.getvalue())

    def test_named_datasource_syncs_matching_datasource(self):
        datasource = self.FakeDataSource('source-a')
        datasources = self.FakeQuerySet([datasource])
        out = StringIO()

        with patch('core.management.commands.syncdatasource.DataSource') as data_source_model:
            data_source_model.objects.filter.return_value = datasources
            call_command('syncdatasource', 'source-a', stdout=out)

        data_source_model.objects.filter.assert_called_once()
        self.assertEqual(
            set(data_source_model.objects.filter.call_args.kwargs['name__in']),
            {'source-a'},
        )
        datasource.sync.assert_called_once_with()
        self.assertIn('[1] Syncing source-a', out.getvalue())
        self.assertIn('completed', out.getvalue())
        self.assertNotIn('Syncing 1 data sources.', out.getvalue())
        self.assertNotIn('Finished.', out.getvalue())

    def test_sync_failure_marks_datasource_failed_and_reraises(self):
        datasource = MagicMock()
        datasource.__str__.return_value = 'source-a'
        datasource.pk = 1
        datasource.sync.side_effect = RuntimeError('boom')

        with patch('core.management.commands.syncdatasource.DataSource') as data_source_model:
            data_source_model.objects.all.return_value = [datasource]

            with self.assertRaisesMessage(RuntimeError, 'boom'):
                call_command('syncdatasource', sync_all=True, stdout=StringIO())

        data_source_model.objects.filter.assert_called_once_with(pk=1)
        data_source_model.objects.filter.return_value.update.assert_called_once_with(
            status=DataSourceStatusChoices.FAILED,
        )

    def test_multiple_names_prints_summary_and_syncs_datasources(self):
        datasource_a = self.FakeDataSource('source-a')
        datasource_b = self.FakeDataSource('source-b')
        datasources = self.FakeQuerySet([datasource_a, datasource_b])
        out = StringIO()

        with patch('core.management.commands.syncdatasource.DataSource') as data_source_model:
            data_source_model.objects.filter.return_value = datasources
            call_command('syncdatasource', 'source-a', 'source-b', stdout=out)

        data_source_model.objects.filter.assert_called_once()
        self.assertEqual(
            set(data_source_model.objects.filter.call_args.kwargs['name__in']),
            {'source-a', 'source-b'},
        )
        datasource_a.sync.assert_called_once_with()
        datasource_b.sync.assert_called_once_with()
        self.assertIn('Syncing 2 data sources.', out.getvalue())
        self.assertIn('[1] Syncing source-a', out.getvalue())
        self.assertIn('[2] Syncing source-b', out.getvalue())
        self.assertIn('Finished.', out.getvalue())


class UpgradeCommandTest(TestCase):
    """The upgrade command orchestrates the application task sequence for installs and upgrades."""

    def _run(self, **kwargs):
        out = StringIO()
        with (
            patch('core.management.commands.upgrade.call_command') as cc,
            patch('core.management.commands.upgrade.subprocess.run') as sub,
        ):
            call_command('upgrade', stdout=out, **kwargs)
        return [c.args[0] for c in cc.call_args_list], cc, sub, out.getvalue()

    def test_full_sequence_order(self):
        seq, _, sub, _ = self._run()
        self.assertEqual(seq, [
            'migrate', 'trace_paths',
            'collectstatic', 'remove_stale_contenttypes', 'reindex', 'clearsessions',
        ])
        sub.assert_not_called()  # docs not built by default

    def test_readonly_skips_all_tasks_including_static(self):
        """--readonly prints a skip message for every task, including the three without dedicated flags."""
        seq, _, sub, out = self._run(readonly=True)
        self.assertEqual(seq, [])
        sub.assert_not_called()
        self.assertIn('Skipping database migrations.', out)
        self.assertIn('Skipping cable path check.', out)
        self.assertIn('Skipping static file collection.', out)
        self.assertIn('Skipping stale content type removal.', out)
        self.assertIn('Skipping search index rebuild.', out)
        self.assertIn('Skipping expired session cleanup.', out)

    def test_skip_flags(self):
        seq, _, _, _ = self._run(skip_migrations=True, skip_static=True, skip_reindex=True)
        self.assertEqual(
            seq,
            ['trace_paths', 'remove_stale_contenttypes', 'clearsessions'],
        )

    def test_build_docs_invokes_zensical_when_sources_present(self):
        with patch('core.management.commands.upgrade._docs_source_root', return_value='/repo'):
            _, _, sub, _ = self._run(build_docs=True)
        sub.assert_called_once()
        self.assertEqual(sub.call_args.args[0], ['zensical', 'build', '-c'])

    def test_build_docs_skipped_when_sources_absent(self):
        with patch('core.management.commands.upgrade._docs_source_root', return_value=None):
            _, _, sub, _ = self._run(build_docs=True)
        sub.assert_not_called()

    def test_readonly_with_build_docs_skips_docs(self):
        with patch('core.management.commands.upgrade._docs_source_root', return_value='/repo'):
            _, _, sub, _ = self._run(readonly=True, build_docs=True)
        sub.assert_not_called()

    def test_docs_source_root_checkout_shaped(self):
        """mkdocs.yml beside the application root (checkout layout) is found."""
        with tempfile.TemporaryDirectory() as root:
            base_dir = os.path.join(root, 'netbox')
            os.mkdir(base_dir)
            open(os.path.join(root, 'mkdocs.yml'), 'w').close()
            with override_settings(BASE_DIR=base_dir):
                self.assertEqual(upgrade._docs_source_root(), root)

    def test_docs_source_root_none_when_absent(self):
        """No mkdocs.yml beside the application root returns None."""
        with tempfile.TemporaryDirectory() as root:
            base_dir = os.path.join(root, 'netbox')
            os.mkdir(base_dir)
            with override_settings(BASE_DIR=base_dir):
                self.assertIsNone(upgrade._docs_source_root())
