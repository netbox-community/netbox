import contextlib
import tempfile
from io import StringIO
from pathlib import Path
from unittest import skipUnless
from unittest.mock import patch

from django.test import SimpleTestCase

from netbox import scaffold

_CONTRIB_DIR = Path(__file__).resolve().parents[3] / 'contrib'


class ScaffoldInstanceTest(SimpleTestCase):
    def _fake_examples(self, tmp):
        src = Path(tmp) / 'examples'
        src.mkdir()
        for name in ('gunicorn.py', 'nginx.conf', 'apache.conf', 'netbox.env'):
            (src / name).write_text(f'# {name}')
        (src / 'netbox.service').write_text(
            'PIDFile=/var/tmp/netbox.pid\n'
            'ExecStart=/opt/netbox/venv/bin/gunicorn --pythonpath /opt/netbox/netbox netbox.wsgi\n'
        )
        (src / 'netbox-rq.service').write_text(
            'Group=netbox\n'
            'ExecStart=/opt/netbox/venv/bin/python3 /opt/netbox/netbox/manage.py rqworker high default low\n'
        )
        return src

    def test_scaffolds_instance_root_and_conf(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                written = scaffold.scaffold_instance(target, systemd)
            self.assertTrue((target / 'gunicorn.py').exists())
            self.assertTrue((target / 'nginx.conf').exists())
            self.assertTrue((target / 'netbox.env').exists())
            self.assertTrue((systemd / 'netbox.service').exists())
            self.assertTrue((systemd / 'netbox-rq.service').exists())
            self.assertTrue((target / 'conf' / '__init__.py').exists())
            self.assertTrue((target / 'conf' / 'configuration.py').exists())
            self.assertTrue(written)

    def test_never_clobbers_existing_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            (target / 'conf').mkdir(parents=True)
            (target / 'conf' / 'configuration.py').write_text('SECRET = 1')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd)
            self.assertEqual((target / 'conf' / 'configuration.py').read_text(), 'SECRET = 1')

    def test_existing_file_is_skipped_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            (target / 'gunicorn.py').write_text('# keep me')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                written = scaffold.scaffold_instance(target, systemd)
            self.assertEqual((target / 'gunicorn.py').read_text(), '# keep me')
            self.assertNotIn(str(target / 'gunicorn.py'), written)

    def test_main_uses_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                result = scaffold.main(['--target', str(target), '--systemd-dir', str(systemd)])
            self.assertEqual(result, 0)
            self.assertTrue((target / 'gunicorn.py').exists())
            self.assertTrue((target / 'conf' / 'configuration.py').exists())

    def test_main_rejects_relative_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('netbox.scaffold._examples_dir', return_value=Path(tmp)):
                with self.assertRaises(SystemExit):
                    scaffold.main(['--target', 'relative/path'])

    def test_resource_helpers_resolve_under_package(self):
        self.assertTrue(str(scaffold._examples_dir()).endswith('_data/examples'))
        self.assertTrue(str(scaffold._config_template()).endswith('configuration_example.py'))

    def test_render_rewrites_both_layouts(self):
        text = 'WorkingDirectory=/opt/netbox\nMEDIA=/opt/netbox/netbox/media\nvenv=/opt/netbox/venv/bin'
        out = scaffold._render(text, '/srv/netbox')
        self.assertIn('WorkingDirectory=/srv/netbox', out)
        self.assertIn('MEDIA=/srv/netbox/media', out)
        self.assertIn('venv=/srv/netbox/venv/bin', out)
        self.assertNotIn('/opt/netbox', out)

    def test_render_does_not_double_rewrite_target_containing_opt_netbox(self):
        out = scaffold._render('cfg=/opt/netbox/netbox/media\nvenv=/opt/netbox/venv', '/opt/netbox-prod')
        self.assertIn('cfg=/opt/netbox-prod/media', out)
        self.assertIn('venv=/opt/netbox-prod/venv', out)
        self.assertNotIn('/opt/netbox-prod-prod', out)

    def test_scaffold_renders_target_into_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'srv'
            target.mkdir()
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd)
            svc = (systemd / 'netbox.service').read_text()
            self.assertIn(str(target), svc)
            self.assertNotIn('/opt/netbox', svc)

    def test_scaffold_adapts_service_units_for_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'srv'
            target.mkdir()
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd)
            wsgi = (systemd / 'netbox.service').read_text()
            rq = (systemd / 'netbox-rq.service').read_text()
            self.assertIn(f'EnvironmentFile=-{target}/netbox.env', wsgi)
            self.assertNotIn('--pythonpath', wsgi)
            self.assertIn(f'EnvironmentFile=-{target}/netbox.env', rq)
            self.assertIn(f'ExecStart={target}/venv/bin/netbox rqworker high default low', rq)
            self.assertNotIn('manage.py', rq)

    def test_apply_pip_transforms_raises_on_missing_anchor(self):
        with self.assertRaisesRegex(RuntimeError, 'anchor not found'):
            scaffold._apply_pip_transforms('netbox.service', '# no anchors here')

    def test_apply_pip_transforms_ignores_files_without_rules(self):
        self.assertEqual(scaffold._apply_pip_transforms('nginx.conf', '# unchanged'), '# unchanged')

    @skipUnless(_CONTRIB_DIR.is_dir(), 'contrib sources not present')
    def test_pip_transforms_match_canonical_contrib_files(self):
        for name, substitutions in scaffold._PIP_TRANSFORMS.items():
            text = (_CONTRIB_DIR / name).read_text()
            for old, _new in substitutions:
                self.assertIn(old, text, f'{name}: stale transform anchor {old!r}')

    @skipUnless(_CONTRIB_DIR.is_dir(), 'contrib sources not present')
    def test_canonical_contrib_files_render_for_pip(self):
        rendered = {
            name: scaffold._render(
                scaffold._apply_pip_transforms(name, (_CONTRIB_DIR / name).read_text()), '/srv/netbox'
            )
            for name in ('netbox.service', 'netbox-rq.service', 'nginx.conf', 'apache.conf')
        }
        self.assertNotIn('--pythonpath', rendered['netbox.service'])
        self.assertIn('EnvironmentFile=-/srv/netbox/netbox.env', rendered['netbox.service'])
        self.assertIn('PIDFile=/var/tmp/netbox.pid', rendered['netbox.service'])
        self.assertIn('RestartSec=30', rendered['netbox.service'])
        self.assertIn(
            'ExecStart=/srv/netbox/venv/bin/netbox rqworker high default low\n', rendered['netbox-rq.service']
        )
        self.assertNotIn('manage.py', rendered['netbox-rq.service'])
        self.assertIn('EnvironmentFile=-/srv/netbox/netbox.env', rendered['netbox-rq.service'])
        self.assertIn('alias /srv/netbox/static/;', rendered['nginx.conf'])
        self.assertIn('/srv/netbox/static', rendered['apache.conf'])
        for name, text in rendered.items():
            self.assertNotIn('/opt/netbox', text, name)
            self.assertNotIn('/srv/netbox/netbox/', text, name)

    def test_creates_empty_local_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd)
            self.assertTrue((target / 'local_requirements.txt').exists())
            self.assertEqual((target / 'local_requirements.txt').read_text(), '')

    def test_does_not_clobber_existing_local_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            (target / 'local_requirements.txt').write_text('django-auth-ldap\n')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd)
            self.assertEqual((target / 'local_requirements.txt').read_text(), 'django-auth-ldap\n')

    def test_force_does_not_clobber_existing_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            (target / 'conf').mkdir(parents=True)
            (target / 'conf' / 'configuration.py').write_text('SECRET = 1')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd, force=True)
            self.assertEqual((target / 'conf' / 'configuration.py').read_text(), 'SECRET = 1')

    def test_force_does_not_clobber_existing_local_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            (target / 'local_requirements.txt').write_text('django-auth-ldap\n')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd, force=True)
            self.assertEqual((target / 'local_requirements.txt').read_text(), 'django-auth-ldap\n')

    def test_force_does_not_clobber_existing_conf_init(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            (target / 'conf').mkdir(parents=True)
            (target / 'conf' / '__init__.py').write_text('# user-owned\n')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                scaffold.scaffold_instance(target, systemd, force=True)
            self.assertEqual((target / 'conf' / '__init__.py').read_text(), '# user-owned\n')

    def test_force_does_not_clobber_existing_netbox_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fake_examples(tmp)
            target = Path(tmp) / 'opt'
            target.mkdir()
            (target / 'netbox.env').write_text('NETBOX_ROOT=/srv/custom\n')
            systemd = Path(tmp) / 'systemd'
            systemd.mkdir()
            with (
                patch('netbox.scaffold._examples_dir', return_value=src),
                patch('netbox.scaffold._config_template', return_value=src / 'gunicorn.py'),
            ):
                written = scaffold.scaffold_instance(target, systemd, force=True)
            self.assertEqual((target / 'netbox.env').read_text(), 'NETBOX_ROOT=/srv/custom\n')
            self.assertNotIn(str(target / 'netbox.env'), written)

    def test_main_help_uses_netbox_setup_prog(self):
        out = StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            scaffold.main(['--help'])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn('usage: netbox setup', out.getvalue())

    def test_main_rejects_stale_secret_key_subcommand(self):
        err = StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            scaffold.main(['secret-key'])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn('unrecognized arguments', err.getvalue())

    def test_main_fails_friendly_without_bundled_examples(self):
        err = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch('netbox.scaffold._examples_dir', return_value=Path(tmp) / 'missing'),
                contextlib.redirect_stderr(err),
            ):
                rc = scaffold.main(['--target', '/tmp/x'])
        self.assertEqual(rc, 1)
        self.assertIn('installed netbox package', err.getvalue())
