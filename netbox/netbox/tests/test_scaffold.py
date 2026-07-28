import contextlib
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from netbox import scaffold

_CONFIG_TEMPLATE_TEXT = (
    "# example configuration\n"
    "STORAGE_ROOT = '/opt/netbox/netbox/media'\n"
    "NETBOX_ROOT = '/opt/netbox'\n"
)
_CONTRIB_FILENAMES = (
    'apache.conf', 'gunicorn.py', 'netbox-rq.service', 'netbox.env', 'netbox.service', 'nginx.conf', 'uwsgi.ini',
)


class ScaffoldInstanceTest(SimpleTestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)

        bundled = root / '_data'
        contrib_src = bundled / 'contrib'
        contrib_src.mkdir(parents=True)
        for name in _CONTRIB_FILENAMES:
            (contrib_src / name).write_text(f'# {name} contents\n')
        # A real install leaves __pycache__ here too: pip's post-install bytecode compilation
        # runs on gunicorn.py, the only .py file among the examples.
        (contrib_src / '__pycache__').mkdir()
        self.contrib_src = contrib_src

        template = root / 'configuration_example.py'
        template.write_text(_CONFIG_TEMPLATE_TEXT)

        self.target = root / 'opt'
        self.target.mkdir()

        self.enterContext(patch('netbox.scaffold._bundled_data_dir', return_value=bundled))
        self.enterContext(patch('netbox.scaffold._config_template', return_value=template))
        self.enterContext(patch('netbox.scaffold._contrib_dir', return_value=contrib_src))

        # scaffold_instance()/main() print per-file progress to stdout (legitimate `netbox setup`
        # CLI feedback); swallow it here so it doesn't clutter the test runner's output. Tests that
        # assert on captured output redirect stdout themselves within the individual test method.
        self.enterContext(contextlib.redirect_stdout(StringIO()))

    def test_scaffolds_configuration_and_contrib_examples(self):
        """A fresh target gets conf/__init__.py, conf/configuration.py, local_requirements.txt, and contrib/."""
        written = scaffold.scaffold_instance(self.target)
        self.assertEqual((self.target / 'conf' / '__init__.py').read_bytes(), b'')
        self.assertEqual(
            (self.target / 'conf' / 'configuration.py').read_bytes(),
            _CONFIG_TEMPLATE_TEXT.encode('utf-8'),
        )
        self.assertEqual((self.target / 'local_requirements.txt').read_bytes(), b'')
        for name in _CONTRIB_FILENAMES:
            self.assertEqual(
                (self.target / 'contrib' / name).read_bytes(),
                (self.contrib_src / name).read_bytes(),
            )
        expected = [
            str(self.target / 'conf' / '__init__.py'),
            str(self.target / 'conf' / 'configuration.py'),
            str(self.target / 'local_requirements.txt'),
            *(str(self.target / 'contrib' / name) for name in _CONTRIB_FILENAMES),
        ]
        self.assertEqual(written, expected)
        self.assertFalse((self.target / 'contrib' / '__pycache__').exists())

    def test_never_clobbers_existing_configuration(self):
        """An existing conf/configuration.py is left untouched."""
        (self.target / 'conf').mkdir(parents=True)
        (self.target / 'conf' / 'configuration.py').write_text('SECRET = 1')
        written = scaffold.scaffold_instance(self.target)
        self.assertEqual((self.target / 'conf' / 'configuration.py').read_text(), 'SECRET = 1')
        self.assertNotIn(str(self.target / 'conf' / 'configuration.py'), written)

    def test_never_clobbers_existing_conf_init(self):
        """An existing conf/__init__.py is left untouched."""
        (self.target / 'conf').mkdir(parents=True)
        (self.target / 'conf' / '__init__.py').write_text('# user-owned\n')
        written = scaffold.scaffold_instance(self.target)
        self.assertEqual((self.target / 'conf' / '__init__.py').read_text(), '# user-owned\n')
        self.assertNotIn(str(self.target / 'conf' / '__init__.py'), written)

    def test_never_clobbers_existing_local_requirements(self):
        """An existing local_requirements.txt is left untouched."""
        (self.target / 'local_requirements.txt').write_text('django-auth-ldap\n')
        written = scaffold.scaffold_instance(self.target)
        self.assertEqual((self.target / 'local_requirements.txt').read_text(), 'django-auth-ldap\n')
        self.assertNotIn(str(self.target / 'local_requirements.txt'), written)

    def test_never_clobbers_existing_contrib_file(self):
        """An existing <target>/contrib/<name> file is left untouched; siblings are still written."""
        (self.target / 'contrib').mkdir(parents=True)
        (self.target / 'contrib' / 'gunicorn.py').write_text('# edited\n')
        written = scaffold.scaffold_instance(self.target)
        self.assertEqual((self.target / 'contrib' / 'gunicorn.py').read_text(), '# edited\n')
        self.assertNotIn(str(self.target / 'contrib' / 'gunicorn.py'), written)
        self.assertIn(str(self.target / 'contrib' / 'nginx.conf'), written)

    def test_main_uses_arguments(self):
        """main() dispatches --target through to scaffold_instance."""
        result = scaffold.main(['--target', str(self.target)])
        self.assertEqual(result, 0)
        self.assertEqual(
            (self.target / 'conf' / 'configuration.py').read_bytes(),
            _CONFIG_TEMPLATE_TEXT.encode('utf-8'),
        )

    def test_main_rejects_relative_target(self):
        """A relative --target is rejected with rc 2."""
        with (
            contextlib.redirect_stderr(StringIO()),
            self.assertRaises(SystemExit) as cm,
        ):
            scaffold.main(['--target', 'relative/path'])
        self.assertEqual(cm.exception.code, 2)

    def test_main_help_uses_netbox_setup_prog(self):
        """--help shows the netbox setup prog name."""
        out = StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            scaffold.main(['--help'])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn('usage: netbox setup', out.getvalue())

    def test_main_fails_friendly_without_bundled_data(self):
        """Without bundled package data, main() reports rc 1 and a friendly stderr message."""
        err = StringIO()
        with (
            patch('netbox.scaffold._bundled_data_dir', return_value=self.target / 'missing'),
            contextlib.redirect_stderr(err),
        ):
            rc = scaffold.main(['--target', '/tmp/x'])
        self.assertEqual(rc, 1)
        self.assertIn('installed netbox package', err.getvalue())


class ScaffoldResourceHelpersTest(SimpleTestCase):
    """The unpatched resource helpers resolve real paths under the installed netbox package."""

    def test_bundled_data_dir_resolves_under_package(self):
        self.assertTrue(str(scaffold._bundled_data_dir()).endswith('_data'))

    def test_config_template_resolves_under_package(self):
        self.assertTrue(str(scaffold._config_template()).endswith('configuration_example.py'))

    def test_contrib_dir_resolves_under_bundled_data(self):
        self.assertTrue(str(scaffold._contrib_dir()).endswith('_data/contrib'))
