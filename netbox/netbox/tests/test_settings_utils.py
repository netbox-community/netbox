import os
import sys
import tempfile
from types import ModuleType
from unittest.mock import patch

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from rq.queue import Queue

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

    def test_import_from_path_reuses_module_loaded_from_same_path(self):
        """A repeated load of the same path returns the first module and runs the file only once."""
        with tempfile.TemporaryDirectory() as root:
            marker = os.path.join(root, 'executions')
            path = os.path.join(root, 'cached_cfg.py')
            with open(path, 'w') as handle:
                handle.write(f'with open({marker!r}, "a") as handle:\n    handle.write("x")\n')
            self.addCleanup(sys.modules.pop, 'netbox_test_cached_cfg', None)
            first = settings_utils._import_from_path('netbox_test_cached_cfg', path)
            second = settings_utils._import_from_path('netbox_test_cached_cfg', path)
            self.assertIs(second, first)
            with open(marker) as handle:
                self.assertEqual(handle.read(), 'x')

    def test_import_from_path_replaces_module_loaded_from_another_path(self):
        """The same module name at a different path is loaded fresh, not served from the cache."""
        with tempfile.TemporaryDirectory() as root:
            first_path = os.path.join(root, 'first_cfg.py')
            second_path = os.path.join(root, 'second_cfg.py')
            with open(first_path, 'w') as handle:
                handle.write('ALLOWED_HOSTS = ["first"]\n')
            with open(second_path, 'w') as handle:
                handle.write('ALLOWED_HOSTS = ["second"]\n')
            self.addCleanup(sys.modules.pop, 'netbox_test_switched_cfg', None)
            settings_utils._import_from_path('netbox_test_switched_cfg', first_path)
            module = settings_utils._import_from_path('netbox_test_switched_cfg', second_path)
            self.assertEqual(module.ALLOWED_HOSTS, ['second'])
            self.assertIs(sys.modules['netbox_test_switched_cfg'], module)

    def test_import_from_path_restores_previous_module_on_failure(self):
        """A failed replacement does not evict the previously loaded module."""
        with tempfile.TemporaryDirectory() as root:
            module_name = 'netbox_test_restore_cfg'
            first_path = os.path.join(root, 'first_cfg.py')
            broken_path = os.path.join(root, 'broken_cfg.py')
            with open(first_path, 'w') as handle:
                handle.write('ALLOWED_HOSTS = ["first"]\n')
            with open(broken_path, 'w') as handle:
                handle.write('raise RuntimeError("Simulated configuration error")\n')
            self.addCleanup(sys.modules.pop, module_name, None)
            first = settings_utils._import_from_path(module_name, first_path)
            with self.assertRaisesMessage(RuntimeError, 'Simulated configuration error'):
                settings_utils._import_from_path(module_name, broken_path)
            self.assertIs(sys.modules[module_name], first)
            self.assertIs(settings_utils._import_from_path(module_name, first_path), first)

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


class ParseJobTimeoutTest(SimpleTestCase):
    """parse_job_timeout() normalizes RQ_DEFAULT_TIMEOUT to a comparable number of seconds."""

    def test_integer_is_returned_unchanged(self):
        self.assertEqual(settings_utils.parse_job_timeout(300), 300)

    def test_numeric_string_is_coerced(self):
        self.assertEqual(settings_utils.parse_job_timeout('300'), 300)

    def test_duration_string_is_normalized(self):
        self.assertEqual(settings_utils.parse_job_timeout('1h'), 3600)
        self.assertEqual(settings_utils.parse_job_timeout('30m'), 1800)
        self.assertEqual(settings_utils.parse_job_timeout('45s'), 45)

    def test_absent_or_zero_timeout_falls_back_to_queue_default(self):
        # RQ does not treat a null or zero default timeout as unlimited: Queue substitutes its own
        # default, which remains a real ceiling on job execution.
        for value in (None, 0, '0'):
            with self.subTest(value=value):
                self.assertEqual(settings_utils.parse_job_timeout(value), Queue.DEFAULT_TIMEOUT)

    def test_negative_timeout_is_unbounded(self):
        # -1 is RQ's documented infinite timeout; it disables the death penalty, so there is no
        # ceiling to compare against.
        self.assertIsNone(settings_utils.parse_job_timeout(-1))
        self.assertIsNone(settings_utils.parse_job_timeout('-1'))

    def test_invalid_value_raises(self):
        for value in ('1x', 'abc', [300]):
            with self.subTest(value=value):
                with self.assertRaisesMessage(ImproperlyConfigured, 'RQ_DEFAULT_TIMEOUT'):
                    settings_utils.parse_job_timeout(value)


class ValidateWebhookDefaultTimeoutTest(SimpleTestCase):
    """validate_webhook_default_timeout() is the startup check applied to WEBHOOK_DEFAULT_TIMEOUT."""

    def test_valid_timeout_below_job_timeout(self):
        settings_utils.validate_webhook_default_timeout(60, 300)

    def test_timeout_at_or_above_job_timeout_raises(self):
        for timeout in (300, 301):
            with self.subTest(timeout=timeout):
                with self.assertRaisesMessage(ImproperlyConfigured, 'must be less than RQ_DEFAULT_TIMEOUT'):
                    settings_utils.validate_webhook_default_timeout(timeout, 300)

    def test_normalized_job_timeout_is_enforced(self):
        # A duration string such as "1h" must be normalized by the caller and enforced like any other value.
        job_timeout = settings_utils.parse_job_timeout('1h')
        with self.assertRaises(ImproperlyConfigured):
            settings_utils.validate_webhook_default_timeout(3600, job_timeout)
        settings_utils.validate_webhook_default_timeout(3599, job_timeout)

    def test_unbounded_job_timeout_skips_comparison(self):
        settings_utils.validate_webhook_default_timeout(3600, None)

    def test_out_of_range_timeout_raises(self):
        for timeout in (0, 3601):
            with self.subTest(timeout=timeout):
                with self.assertRaisesMessage(ImproperlyConfigured, 'between 1 and 3600'):
                    settings_utils.validate_webhook_default_timeout(timeout, None)

    def test_non_integer_timeout_raises(self):
        for timeout in ('60', 60.5, None):
            with self.subTest(timeout=timeout):
                with self.assertRaisesMessage(ImproperlyConfigured, 'must be an integer'):
                    settings_utils.validate_webhook_default_timeout(timeout, 300)


class LoadLdapConfigTest(SimpleTestCase):
    def test_loads_sibling_ldap_config(self):
        with tempfile.TemporaryDirectory() as conf_dir:
            with open(os.path.join(conf_dir, 'ldap_config.py'), 'w') as handle:
                handle.write('AUTH_LDAP_SERVER_URI = "ldaps://example"\n')
            self.addCleanup(sys.modules.pop, 'netbox.ldap_config', None)
            module = settings_utils.load_ldap_config(conf_dir)
            self.assertEqual(module.AUTH_LDAP_SERVER_URI, 'ldaps://example')
            self.assertIs(sys.modules['netbox.ldap_config'], module)

    def test_repeated_calls_reuse_the_sibling_module(self):
        """Two calls with an unchanged sibling ldap_config.py return the same module object."""
        with tempfile.TemporaryDirectory() as conf_dir:
            with open(os.path.join(conf_dir, 'ldap_config.py'), 'w') as handle:
                handle.write('AUTH_LDAP_SERVER_URI = "ldaps://example"\n')
            self.addCleanup(sys.modules.pop, 'netbox.ldap_config', None)
            first = settings_utils.load_ldap_config(conf_dir)
            second = settings_utils.load_ldap_config(conf_dir)
            self.assertIs(second, first)

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
