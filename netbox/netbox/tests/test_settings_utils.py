import os
import sys
import tempfile
from types import ModuleType
from unittest.mock import patch

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from netbox import settings_utils


class LoadConfigurationTest(SimpleTestCase):
    def test_explicit_module_wins(self):
        with patch('netbox.settings_utils.importlib.import_module') as import_module:
            settings_utils.load_configuration(
                install_mode='wheel', install_root='/opt/netbox',
                environ={'NETBOX_CONFIGURATION': 'my.config'},
            )
        import_module.assert_called_once_with('my.config')

    def test_checkout_uses_default_module(self):
        with patch('netbox.settings_utils.importlib.import_module') as import_module:
            settings_utils.load_configuration(
                install_mode='checkout', install_root='/repo', environ={},
            )
        import_module.assert_called_once_with('netbox.configuration')

    def test_checkout_missing_module_raises_improperly_configured(self):
        with patch(
            'netbox.settings_utils.importlib.import_module',
            side_effect=ModuleNotFoundError("No module named 'netbox.configuration'", name='netbox.configuration'),
        ):
            with self.assertRaises(ImproperlyConfigured):
                settings_utils.load_configuration(
                    install_mode='checkout', install_root='/repo', environ={},
                )

    def test_wheel_prefers_conf_dir(self):
        with tempfile.TemporaryDirectory() as root:
            conf = os.path.join(root, 'conf')
            os.mkdir(conf)
            preferred = os.path.join(conf, 'configuration.py')
            open(preferred, 'w').close()
            saved = list(sys.path)
            try:
                with patch('netbox.settings_utils._import_from_path') as import_from_path:
                    settings_utils.load_configuration(
                        install_mode='wheel', install_root=root, environ={},
                    )
                import_from_path.assert_called_once_with('netbox_local_configuration', preferred)
                self.assertEqual(sys.path, saved)
            finally:
                sys.path[:] = saved

    def test_wheel_falls_back_to_legacy_with_warning(self):
        with tempfile.TemporaryDirectory() as root:
            legacy_dir = os.path.join(root, 'netbox', 'netbox')
            os.makedirs(legacy_dir)
            legacy = os.path.join(legacy_dir, 'configuration.py')
            open(legacy, 'w').close()
            with (
                patch('netbox.settings_utils._import_from_path') as importer,
                self.assertWarns(RuntimeWarning),
            ):
                settings_utils.load_configuration(
                    install_mode='wheel', install_root=root, environ={},
                )
            self.assertEqual(importer.call_args.args[1], legacy)

    def test_wheel_missing_configuration_raises(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesMessage(ImproperlyConfigured, 'conf/configuration.py'):
                settings_utils.load_configuration(
                    install_mode='wheel', install_root=root, environ={},
                )

    def test_explicit_module_reraises_other_import_error(self):
        # A missing dependency of the config module must propagate, not become a friendly error.
        with patch(
            'netbox.settings_utils.importlib.import_module',
            side_effect=ModuleNotFoundError("No module named 'missing_dep'", name='missing_dep'),
        ):
            with self.assertRaises(ModuleNotFoundError):
                settings_utils.load_configuration(
                    install_mode='checkout', install_root='/repo',
                    environ={'NETBOX_CONFIGURATION': 'my.config'},
                )

    def test_import_from_path_loads_module_and_restores_sys_path(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, 'legacy_cfg.py')
            with open(path, 'w') as handle:
                handle.write('ALLOWED_HOSTS = ["example"]\n')
            self.addCleanup(sys.modules.pop, 'netbox_test_legacy_cfg', None)
            saved = list(sys.path)
            module = settings_utils._import_from_path('netbox_test_legacy_cfg', path)
            self.assertEqual(module.ALLOWED_HOSTS, ['example'])
            self.assertEqual(sys.path, saved)
            self.assertIs(sys.modules['netbox_test_legacy_cfg'], module)

    def test_import_from_path_removes_module_on_failure(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, 'broken_cfg.py')
            with open(path, 'w') as handle:
                handle.write('raise RuntimeError("Simulated configuration error")\n')
            with self.assertRaisesMessage(RuntimeError, 'Simulated configuration error'):
                settings_utils._import_from_path('netbox_test_broken_cfg', path)
            self.assertNotIn('netbox_test_broken_cfg', sys.modules)

    def test_import_from_path_rejects_unloadable_path(self):
        # A suffix-less file yields no loader; the helper must fail cleanly.
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, 'noext')
            open(path, 'w').close()
            with self.assertRaisesMessage(ImproperlyConfigured, 'Unable to load'):
                settings_utils._import_from_path('netbox_test_noext_cfg', path)

    def test_import_from_path_preserves_preexisting_sys_path_entry(self):
        # Only the index-0 entry this helper inserted is popped; a pre-existing entry survives.
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, 'preexisting_cfg.py')
            with open(path, 'w') as handle:
                handle.write('ALLOWED_HOSTS = ["example"]\n')
            self.addCleanup(sys.modules.pop, 'netbox_test_preexisting_cfg', None)
            saved = list(sys.path)
            sys.path.append(root)
            try:
                settings_utils._import_from_path('netbox_test_preexisting_cfg', path)
                self.assertEqual(sys.path, saved + [root])
            finally:
                sys.path[:] = saved

    def test_wheel_both_configs_present_warns_and_prefers_conf(self):
        with tempfile.TemporaryDirectory() as root:
            conf = os.path.join(root, 'conf')
            os.mkdir(conf)
            preferred = os.path.join(conf, 'configuration.py')
            open(preferred, 'w').close()
            legacy_dir = os.path.join(root, 'netbox', 'netbox')
            os.makedirs(legacy_dir)
            open(os.path.join(legacy_dir, 'configuration.py'), 'w').close()
            saved = list(sys.path)
            try:
                with (
                    patch('netbox.settings_utils._import_from_path') as import_from_path,
                    self.assertWarns(RuntimeWarning),
                ):
                    settings_utils.load_configuration(install_mode='wheel', install_root=root, environ={})
                import_from_path.assert_called_once_with('netbox_local_configuration', preferred)
            finally:
                sys.path[:] = saved


class ConfigurationDirTest(SimpleTestCase):
    def test_returns_directory_of_module_file(self):
        module = ModuleType('cfg')
        module.__file__ = '/srv/netbox/conf/configuration.py'
        self.assertEqual(settings_utils.get_configuration_dir(module), '/srv/netbox/conf')

    def test_returns_none_without_file(self):
        self.assertIsNone(settings_utils.get_configuration_dir(ModuleType('cfg')))


class ResolveInstallPathsTest(SimpleTestCase):
    """resolve_install_paths() centralizes wheel-vs-checkout filesystem layout decisions."""

    def test_checkout_roots(self):
        with tempfile.TemporaryDirectory() as root:
            settings_dir = os.path.join(root, 'netbox', 'netbox')
            os.makedirs(settings_dir)
            base_dir = os.path.join(root, 'netbox')
            paths = settings_utils.resolve_install_paths(settings_dir, {})
            self.assertEqual(paths.install_mode, 'checkout')
            self.assertEqual(paths.base_dir, base_dir)
            self.assertEqual(paths.netbox_root, base_dir)
            self.assertEqual(paths.docs_root, os.path.join(root, 'docs'))
            self.assertEqual(paths.static_docs_root, os.path.join(base_dir, 'project-static', 'docs'))

    def test_wheel_roots_default_netbox_root(self):
        with tempfile.TemporaryDirectory() as root:
            settings_dir = os.path.join(root, 'site-packages', 'netbox')
            base_dir = os.path.join(settings_dir, '_data')
            os.makedirs(base_dir)
            paths = settings_utils.resolve_install_paths(settings_dir, {})
            self.assertEqual(paths.install_mode, 'wheel')
            self.assertEqual(paths.base_dir, base_dir)
            self.assertEqual(paths.netbox_root, '/opt/netbox')
            self.assertEqual(paths.docs_root, os.path.join(base_dir, 'docs'))
            self.assertEqual(paths.static_docs_root, os.path.join(base_dir, 'docs'))

    def test_netbox_root_env_override_is_abspathed(self):
        with tempfile.TemporaryDirectory() as root:
            settings_dir = os.path.join(root, 'site-packages', 'netbox')
            os.makedirs(os.path.join(settings_dir, '_data'))
            paths = settings_utils.resolve_install_paths(settings_dir, {'NETBOX_ROOT': 'relative/root'})
            self.assertEqual(paths.netbox_root, os.path.abspath('relative/root'))


class SecretKeyHintTest(SimpleTestCase):
    """secret_key_hint() picks the SECRET_KEY-too-short hint by install mode."""

    def test_wheel_mode_suggests_console_command(self):
        self.assertEqual(settings_utils.secret_key_hint('wheel', '/opt/netbox/lib/netbox'), 'netbox secret-key')

    def test_checkout_mode_suggests_generate_secret_key_script(self):
        self.assertEqual(
            settings_utils.secret_key_hint('checkout', '/repo/netbox'),
            'python /repo/netbox/generate_secret_key.py',
        )


class LoadLdapConfigTest(SimpleTestCase):
    def test_loads_sibling_ldap_config(self):
        with tempfile.TemporaryDirectory() as conf_dir:
            with open(os.path.join(conf_dir, 'ldap_config.py'), 'w') as handle:
                handle.write('AUTH_LDAP_SERVER_URI = "ldaps://example"\n')
            self.addCleanup(sys.modules.pop, 'netbox.ldap_config', None)
            module = settings_utils.load_ldap_config(conf_dir)
            self.assertEqual(module.AUTH_LDAP_SERVER_URI, 'ldaps://example')
            self.assertIs(sys.modules['netbox.ldap_config'], module)

    def test_legacy_fallback_loads_historical_module_with_warning(self):
        legacy = ModuleType('netbox.ldap_config')
        legacy.AUTH_LDAP_SERVER_URI = 'ldaps://legacy'
        with tempfile.TemporaryDirectory() as conf_dir:
            with patch.dict(sys.modules, {'netbox.ldap_config': legacy}), self.assertWarns(RuntimeWarning):
                module = settings_utils.load_ldap_config(conf_dir, allow_legacy_fallback=True)
        self.assertIs(module, legacy)

    def test_legacy_fallback_prefers_sibling_file(self):
        legacy = ModuleType('netbox.ldap_config')
        legacy.AUTH_LDAP_SERVER_URI = 'ldaps://legacy'
        with tempfile.TemporaryDirectory() as conf_dir:
            with open(os.path.join(conf_dir, 'ldap_config.py'), 'w') as handle:
                handle.write('AUTH_LDAP_SERVER_URI = "ldaps://sibling"\n')
            with patch.dict(sys.modules, {'netbox.ldap_config': legacy}):
                module = settings_utils.load_ldap_config(conf_dir, allow_legacy_fallback=True)
            self.assertEqual(module.AUTH_LDAP_SERVER_URI, 'ldaps://sibling')

    def test_legacy_fallback_disabled_raises(self):
        legacy = ModuleType('netbox.ldap_config')
        with tempfile.TemporaryDirectory() as conf_dir:
            with patch.dict(sys.modules, {'netbox.ldap_config': legacy}):
                with self.assertRaisesMessage(ImproperlyConfigured, 'alongside configuration.py'):
                    settings_utils.load_ldap_config(conf_dir)

    def test_legacy_fallback_missing_module_raises(self):
        with tempfile.TemporaryDirectory() as conf_dir:
            with patch(
                'netbox.settings_utils.importlib.import_module',
                side_effect=ModuleNotFoundError("No module named 'netbox.ldap_config'", name='netbox.ldap_config'),
            ):
                with self.assertRaisesMessage(ImproperlyConfigured, 'alongside configuration.py'):
                    settings_utils.load_ldap_config(conf_dir, allow_legacy_fallback=True)

    def test_legacy_fallback_reraises_broken_dependency(self):
        with tempfile.TemporaryDirectory() as conf_dir:
            with patch(
                'netbox.settings_utils.importlib.import_module',
                side_effect=ModuleNotFoundError("No module named 'missing_dep'", name='missing_dep'),
            ):
                with self.assertRaises(ModuleNotFoundError):
                    settings_utils.load_ldap_config(conf_dir, allow_legacy_fallback=True)

    def test_none_config_dir_raises(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'unable to determine'):
            settings_utils.load_ldap_config(None)

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as conf_dir:
            with self.assertRaisesMessage(ImproperlyConfigured, 'ldap_config.py'):
                settings_utils.load_ldap_config(conf_dir)

    def test_configuration_dir_setting_matches_active_configuration(self):
        from netbox import configuration_testing
        self.assertEqual(
            django_settings.CONFIGURATION_DIR,
            os.path.dirname(os.path.abspath(configuration_testing.__file__)),
        )
