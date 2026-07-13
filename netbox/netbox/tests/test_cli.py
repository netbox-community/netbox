from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

from django.test import SimpleTestCase

from netbox import cli


class CliDispatchTest(SimpleTestCase):
    """The console script resolves pre-configuration commands before importing Django."""

    def _main(self, args, argv0='netbox'):
        # prog derives from sys.argv[0] even when argv is passed explicitly, so pin both.
        stdout, stderr = StringIO(), StringIO()
        with (
            patch.object(cli.sys, 'argv', [argv0, *args]),
            patch('django.core.management.execute_from_command_line') as execute,
            redirect_stdout(stdout), redirect_stderr(stderr),
        ):
            rc = cli.main(args)
        return rc, execute, stdout.getvalue(), stderr.getvalue()

    def test_version_flag_prints_version_without_django(self):
        with patch('netbox.cli.version', return_value='4.7.0b1'):
            rc, execute, out, _ = self._main(['--version'])
        execute.assert_not_called()
        self.assertEqual(out, '4.7.0b1\n')
        self.assertEqual(rc, 0)

    def test_version_command_prints_version_without_django(self):
        with patch('netbox.cli.version', return_value='4.7.0b1'):
            rc, execute, out, _ = self._main(['version'])
        execute.assert_not_called()
        self.assertEqual(out, '4.7.0b1\n')
        self.assertEqual(rc, 0)

    def test_version_help(self):
        rc, execute, out, _ = self._main(['version', '--help'])
        execute.assert_not_called()
        self.assertEqual(rc, 0)
        self.assertIn('usage: netbox version', out)

    def test_version_rejects_unexpected_arguments(self):
        rc, execute, _, err = self._main(['version', 'bogus'])
        execute.assert_not_called()
        self.assertEqual(rc, 2)
        self.assertIn('unrecognized arguments: bogus', err)

    def test_no_arguments_prints_help_without_django(self):
        rc, execute, out, _ = self._main([])
        execute.assert_not_called()
        self.assertEqual(rc, 0)
        self.assertIn('usage: netbox', out)
        for command in ('version', 'setup', 'secret-key'):
            self.assertIn(command, out)

    def test_help_flags_print_help_without_django(self):
        for flag in ('-h', '--help'):
            with self.subTest(flag=flag):
                rc, execute, out, _ = self._main([flag])
                execute.assert_not_called()
                self.assertEqual(rc, 0)
                self.assertIn('usage: netbox', out)
                for command in ('version', 'setup', 'secret-key'):
                    self.assertIn(command, out)

    def test_secret_key_prints_50_char_key_without_django(self):
        rc, execute, out, _ = self._main(['secret-key'])
        execute.assert_not_called()
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.strip()), 50)

    def test_secret_key_help(self):
        rc, execute, out, _ = self._main(['secret-key', '--help'])
        execute.assert_not_called()
        self.assertEqual(rc, 0)
        self.assertIn('usage: netbox secret-key', out)

    def test_secret_key_rejects_unexpected_arguments(self):
        rc, execute, _, err = self._main(['secret-key', 'bogus'])
        execute.assert_not_called()
        self.assertEqual(rc, 2)
        self.assertIn('unrecognized arguments: bogus', err)

    def test_setup_dispatches_to_scaffold_with_prog(self):
        with patch('netbox.scaffold.main', return_value=0) as setup_main:
            rc, execute, _, _ = self._main(['setup', '--target', '/srv/netbox'])
        execute.assert_not_called()
        setup_main.assert_called_once_with(['--target', '/srv/netbox'], prog='netbox setup')
        self.assertEqual(rc, 0)

    def test_setup_return_code_propagates(self):
        with patch('netbox.scaffold.main', return_value=3):
            rc, execute, _, _ = self._main(['setup'])
        execute.assert_not_called()
        self.assertEqual(rc, 3)

    def test_other_commands_dispatch_to_django(self):
        with (
            patch.object(cli.sys, 'argv', ['/opt/netbox/venv/bin/netbox', 'check', '--deploy']),
            patch.dict(cli.os.environ),
            patch('django.core.management.execute_from_command_line') as execute,
        ):
            cli.os.environ.pop('DJANGO_SETTINGS_MODULE', None)
            rc = cli.main(['check', '--deploy'])
            self.assertEqual(cli.os.environ['DJANGO_SETTINGS_MODULE'], 'netbox.settings')
        execute.assert_called_once_with(['netbox', 'check', '--deploy'])
        self.assertEqual(rc, 0)

    def test_subcommand_help_falls_through_to_django(self):
        rc, execute, _, _ = self._main(['migrate', '--help'])
        execute.assert_called_once_with(['netbox', 'migrate', '--help'])
        self.assertEqual(rc, 0)

    def test_prog_falls_back_for_python_m_invocation(self):
        with patch('netbox.scaffold.main', return_value=0) as setup_main:
            self._main(['setup'], argv0='/x/netbox/__main__.py')
        setup_main.assert_called_once_with([], prog='netbox setup')

    def test_prog_falls_back_when_argv_is_empty(self):
        out = StringIO()
        with (
            patch.object(cli.sys, 'argv', []),
            patch('django.core.management.execute_from_command_line') as execute,
            redirect_stdout(out),
        ):
            rc = cli.main([])
        execute.assert_not_called()
        self.assertEqual(rc, 0)
        self.assertIn('usage: netbox', out.getvalue())
