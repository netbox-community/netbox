import re
import subprocess
import sys
from unittest import mock, skipIf

import strawberry
import strawberry_django
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.choices import JobIntervalChoices
from core.models import ObjectType
from dcim.models import Site
from extras.dashboard.widgets import DashboardWidget
from netbox.graphql import utils as graphql_utils
from netbox.graphql.schema import Query
from netbox.graphql.utils import register_model_graphql_type
from netbox.plugins import DEFAULT_RESOURCE_PATHS, _load_plugin_graphql_schemas
from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem
from netbox.plugins.registration import register_graphql_type_extensions
from netbox.plugins.utils import get_plugin_config
from netbox.registry import registry
from netbox.tests.dummy_plugin import config as dummy_config
from netbox.tests.dummy_plugin.data_backends import DummyBackend
from netbox.tests.dummy_plugin.jobs import DummySystemJob
from netbox.tests.dummy_plugin.models import DummyModel
from netbox.tests.dummy_plugin.webhook_callbacks import set_context


@skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
class PluginTestCase(TestCase):

    def test_config(self):

        self.assertIn('netbox.tests.dummy_plugin.DummyPluginConfig', settings.INSTALLED_APPS)

    def test_model_registration(self):
        self.assertTrue(
            ObjectType.objects.filter(app_label='dummy_plugin', model='dummymodel').exists()
        )

    def test_models(self):
        from netbox.tests.dummy_plugin.models import DummyModel

        # Test saving an instance
        instance = DummyModel(name='Instance 1', number=100)
        instance.save()
        self.assertIsNotNone(instance.pk)

        # Test deleting an instance
        instance.delete()
        self.assertIsNone(instance.pk)

    @override_settings(LOGIN_REQUIRED=False)
    def test_views(self):

        # Test URL resolution
        url = reverse('plugins:dummy_plugin:dummy_model_list')
        self.assertEqual(url, '/plugins/dummy-plugin/models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
    def test_api_views(self):

        # Test URL resolution
        url = reverse('plugins-api:dummy_plugin-api:dummymodel-list')
        self.assertEqual(url, '/api/plugins/dummy-plugin/dummy-models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(LOGIN_REQUIRED=False)
    def test_registered_views(self):

        # Test URL resolution
        url = reverse('dcim:site_extra', kwargs={'pk': 1})
        self.assertEqual(url, '/dcim/sites/1/other-stuff/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_menu(self):
        """
        Check menu registration.
        """
        menu = registry['plugins']['menus'][0]
        self.assertIsInstance(menu, PluginMenu)
        self.assertEqual(menu.label, 'Dummy Plugin')

    def test_menu_items(self):
        """
        Check menu_items registration.
        """
        self.assertIn('Dummy plugin', registry['plugins']['menu_items'])
        menu_items = registry['plugins']['menu_items']['Dummy plugin']
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(len(menu_items[0].buttons), 2)

    def test_template_extensions(self):
        """
        Check that plugin TemplateExtensions are registered.
        """
        from netbox.tests.dummy_plugin.template_content import GlobalContent, SiteContent

        self.assertIn(GlobalContent, registry['plugins']['template_extensions'][None])
        self.assertIn(SiteContent, registry['plugins']['template_extensions']['dcim.site'])

    def test_dashboard_widget(self):
        """
        Check that plugin dashboard widgets are registered.
        """
        self.assertIn('netbox.DummyDashboardWidget', registry['widgets'])

        widget_class = registry['widgets']['netbox.DummyDashboardWidget']
        self.assertTrue(issubclass(widget_class, DashboardWidget))

    def test_registered_columns(self):
        """
        Check that a plugin can register a custom column on a core model table.
        """
        from dcim.tables import SiteTable

        table = SiteTable(Site.objects.all())
        self.assertIn('foo', table.columns.names())

    def test_user_preferences(self):
        """
        Check that plugin UserPreferences are registered.
        """
        self.assertIn('dummy_plugin', registry['plugins']['preferences'])
        user_preferences = registry['plugins']['preferences']['dummy_plugin']
        self.assertEqual(type(user_preferences), dict)
        self.assertEqual(list(user_preferences.keys()), ['pref1', 'pref2'])

    def test_middleware(self):
        """
        Check that plugin middleware is registered.
        """
        self.assertIn('netbox.tests.dummy_plugin.middleware.DummyMiddleware', settings.MIDDLEWARE)

    def test_data_backends(self):
        """
        Check registered data backends.
        """
        self.assertIn('dummy', registry['data_backends'])
        self.assertIs(registry['data_backends']['dummy'], DummyBackend)

    def test_system_jobs(self):
        """
        Check registered system jobs.
        """
        self.assertIn(DummySystemJob, registry['system_jobs'])
        self.assertEqual(registry['system_jobs'][DummySystemJob]['interval'], JobIntervalChoices.INTERVAL_HOURLY)

    def test_queues(self):
        """
        Check that plugin queues are registered with the accurate name.
        """
        self.assertIn('netbox.tests.dummy_plugin.testing-low', settings.RQ_QUEUES)
        self.assertIn('netbox.tests.dummy_plugin.testing-medium', settings.RQ_QUEUES)
        self.assertIn('netbox.tests.dummy_plugin.testing-high', settings.RQ_QUEUES)

    def test_min_version(self):
        """
        Check enforcement of minimum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({}, '0.9')

    def test_max_version(self):
        """
        Check enforcement of maximum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({}, '10.0')

    def test_required_settings(self):
        """
        Validate enforcement of required settings.
        """
        class DummyConfigWithRequiredSettings(dummy_config):
            required_settings = ['foo']

        # Validation should pass when all required settings are present
        DummyConfigWithRequiredSettings.validate({'foo': True}, settings.RELEASE.version)

        # Validation should fail when a required setting is missing
        with self.assertRaises(ImproperlyConfigured):
            DummyConfigWithRequiredSettings.validate({}, settings.RELEASE.version)

    def test_default_settings(self):
        """
        Validate population of default config settings.
        """
        class DummyConfigWithDefaultSettings(dummy_config):
            default_settings = {
                'bar': 123,
            }

        # Populate the default value if setting has not been specified
        user_config = {}
        DummyConfigWithDefaultSettings.validate(user_config, settings.RELEASE.version)
        self.assertEqual(user_config['bar'], 123)

        # Don't overwrite specified values
        user_config = {'bar': 456}
        DummyConfigWithDefaultSettings.validate(user_config, settings.RELEASE.version)
        self.assertEqual(user_config['bar'], 456)

    def test_graphql(self):
        """
        Validate the registration and operation of plugin-provided GraphQL schemas.
        """
        from netbox.tests.dummy_plugin.graphql import DummyQuery

        self.assertIn(DummyQuery, registry['plugins']['graphql_schemas'])
        self.assertTrue(issubclass(Query, DummyQuery))

    def test_graphql_type_extensions(self):
        """
        Validate that plugin GraphQL type & filter extensions are registered and spliced into the built schema.
        """
        from netbox.graphql.schema import schema
        from netbox.tests.dummy_plugin.graphql_extensions import SiteFilterExtension, SiteTypeExtension

        # Extensions are registered against the targeted core model
        self.assertIn(SiteTypeExtension, registry['plugins']['graphql_type_extensions']['dcim.site'])
        self.assertIn(SiteFilterExtension, registry['plugins']['graphql_filter_extensions']['dcim.site'])

        # The injected field and filter appear in the assembled schema
        schema_str = schema.as_str()
        site_type = re.search(r'\ntype SiteType \{.*?\n\}', schema_str, re.DOTALL)
        self.assertIsNotNone(site_type, "SiteType not found in GraphQL schema")
        self.assertIn('dummy_plugin_field', site_type.group(0))
        site_filter = re.search(r'\ninput SiteFilter \{.*?\n\}', schema_str, re.DOTALL)
        self.assertIsNotNone(site_filter, "SiteFilter not found in GraphQL schema")
        self.assertIn('dummy_plugin_filter', site_filter.group(0))

    def test_load_resource_returns_none_for_missing_default_module(self):
        config = apps.get_app_config('dummy_plugin')
        with mock.patch.dict(DEFAULT_RESOURCE_PATHS, {'graphql_type_extensions': 'no_such_module.type_extensions'}):
            self.assertIsNone(config._load_resource('graphql_type_extensions'))

    def test_load_resource_propagates_nested_import_error(self):
        config = apps.get_app_config('dummy_plugin')
        with mock.patch.dict(DEFAULT_RESOURCE_PATHS, {'graphql_type_extensions': 'broken_import.type_extensions'}):
            with self.assertRaises(ModuleNotFoundError):
                config._load_resource('graphql_type_extensions')

    def test_graphql_finalizer_app_installed_after_plugins(self):
        finalizer = settings.INSTALLED_APPS.index('netbox.graphql.apps.GraphQLConfig')
        plugin_positions = [i for i, app in enumerate(settings.INSTALLED_APPS) if 'dummy_plugin' in app]
        self.assertTrue(plugin_positions)
        self.assertGreater(finalizer, max(plugin_positions))
        self.assertEqual(apps.get_app_config('netbox_graphql').name, 'netbox.graphql')

    def test_graphql_finalizer_runs_during_django_setup(self):
        """The finalizer assembles the schema before auditing targets, and its errors fail django.setup()."""
        # Source for a child interpreter, so it carries no indentation of its own.
        script = """
import sys
import django
from netbox.graphql import utils


def audit():
    if 'netbox.graphql.schema' not in sys.modules:
        raise RuntimeError('SCHEMA_NOT_ASSEMBLED')
    raise RuntimeError('AUDIT_RAN_AFTER_SCHEMA')


utils.validate_extension_targets = audit
django.setup()
"""
        # The child inherits this process's settings, which is safe only because ready() touches no database.
        result = subprocess.run(
            [sys.executable, '-c', script], capture_output=True, text=True, cwd=settings.BASE_DIR, timeout=300
        )
        self.assertNotEqual(result.returncode, 0, f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}")
        self.assertIn('AUDIT_RAN_AFTER_SCHEMA', result.stderr)

    def test_missing_plugin_app_config_raises_clear_error(self):
        installed = [*registry['plugins']['installed'], 'not_a_real_plugin']
        with mock.patch.dict(registry['plugins'], {'installed': installed}):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                _load_plugin_graphql_schemas()
        self.assertIn('not_a_real_plugin', str(ctx.exception))

    def test_plugin_schema_loading_is_idempotent(self):
        before = list(registry['plugins']['graphql_schemas'])
        self.addCleanup(lambda: registry['plugins']['graphql_schemas'].__setitem__(slice(None), before))
        _load_plugin_graphql_schemas()
        _load_plugin_graphql_schemas()
        self.assertEqual(registry['plugins']['graphql_schemas'], before)

    @override_settings(PLUGINS_CONFIG={'netbox.tests.dummy_plugin': {'foo': 123}})
    def test_get_plugin_config(self):
        """
        Validate that get_plugin_config() returns config parameters correctly.
        """
        plugin = 'netbox.tests.dummy_plugin'
        self.assertEqual(get_plugin_config(plugin, 'foo'), 123)
        self.assertEqual(get_plugin_config(plugin, 'bar'), None)
        self.assertEqual(get_plugin_config(plugin, 'bar', default=456), 456)

    def test_events_pipeline(self):
        """
        Check that events pipeline is registered.
        """
        self.assertIn('netbox.tests.dummy_plugin.events.process_events_queue', settings.EVENTS_PIPELINE)

    def test_webhook_callbacks(self):
        """
        Test the registration of webhook callbacks.
        """
        self.assertIn(set_context, registry['webhook_callbacks'])

    def test_jinja_filters_registered(self):
        """
        Check that Jinja filters exported by the dummy plugin are registered in
        registry['plugins']['jinja_filters'] after ready().
        """
        from netbox.tests.dummy_plugin.jinja_env import dummy_upper
        self.assertIn('dummy_upper', registry['plugins']['jinja_filters'])
        self.assertIs(registry['plugins']['jinja_filters']['dummy_upper'], dummy_upper)

    def test_jinja_filter_available_in_render(self):
        """
        Filters registered by a plugin must be usable inside render_jinja2().
        """
        from utilities.jinja2 import render_jinja2
        result = render_jinja2("{{ 'hello' | dummy_upper }}", {})
        self.assertEqual(result, 'HELLO')

    def test_get_jinja_context_merged_into_render(self):
        """
        Variables returned by a plugin's get_jinja_context() must appear in the
        context produced by RenderTemplateMixin.get_context().
        """
        from extras.models import ConfigTemplate
        ct = ConfigTemplate(name='jinja-ctx-test', template_code='')
        ctx = ct.get_context()
        self.assertIn('dummy_plugin_var', ctx)
        self.assertEqual(ctx['dummy_plugin_var'], 'hello_from_dummy')

    def test_get_jinja_context_bad_return_is_silenced(self):
        """
        A non-dict return from get_jinja_context() must not crash the render.
        """
        from unittest.mock import patch

        from extras.models import ConfigTemplate
        from netbox.tests.dummy_plugin import DummyPluginConfig
        ct = ConfigTemplate(name='bad-ctx-test', template_code='')
        with patch.object(DummyPluginConfig, 'get_jinja_context', return_value='not_a_dict'):
            ctx = ct.get_context()
        self.assertNotIn('dummy_plugin_var', ctx)

    def test_instance_jinja_filters_override_plugin_filters(self):
        """
        Instance-level JINJA_FILTERS must take precedence over plugin-registered filters
        of the same name.
        """
        from utilities.jinja2 import render_jinja2
        override = {'dummy_upper': lambda v: 'overridden'}
        with self.settings(JINJA_FILTERS=override):
            result = render_jinja2("{{ 'hello' | dummy_upper }}", {})
        self.assertEqual(result, 'overridden')


@skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
class PluginJinjaRegistrationTest(TestCase):
    """
    Tests for the register_jinja_filters() registration helper independent of
    the dummy plugin's startup path.
    """

    def test_register_jinja_filters_rejects_non_dict(self):
        from netbox.plugins.registration import register_jinja_filters
        with self.assertRaises(TypeError):
            register_jinja_filters([('my_filter', lambda v: v)])

    def test_register_jinja_filters_rejects_non_callable_value(self):
        from netbox.plugins.registration import register_jinja_filters
        with self.assertRaises(TypeError):
            register_jinja_filters({'my_filter': 'not_a_function'})

    def test_register_jinja_filters_merges_into_registry(self):
        from netbox.plugins.registration import register_jinja_filters
        fn = lambda v: v  # noqa: E731
        register_jinja_filters({'_test_temp_filter': fn})
        try:
            self.assertIs(registry['plugins']['jinja_filters']['_test_temp_filter'], fn)
        finally:
            del registry['plugins']['jinja_filters']['_test_temp_filter']


class PluginNavigationTestCase(TestCase):

    def test_plugin_menu_item_independent_permissions(self):
        item1 = PluginMenuItem(link='test1', link_text='Test 1')
        item1.permissions.append('leaked_permission')

        item2 = PluginMenuItem(link='test2', link_text='Test 2')

        self.assertIsNot(item1.permissions, item2.permissions)
        self.assertEqual(item1.permissions, ['leaked_permission'])
        self.assertEqual(item2.permissions, [])

    def test_plugin_menu_item_independent_buttons(self):
        item1 = PluginMenuItem(link='test1', link_text='Test 1')
        button = PluginMenuButton(link='button1', title='Button 1', icon_class='mdi-test')
        item1.buttons.append(button)

        item2 = PluginMenuItem(link='test2', link_text='Test 2')

        self.assertIsNot(item1.buttons, item2.buttons)
        self.assertEqual(len(item1.buttons), 1)
        self.assertEqual(item1.buttons[0], button)
        self.assertEqual(item2.buttons, [])

    def test_plugin_menu_button_independent_permissions(self):
        button1 = PluginMenuButton(link='button1', title='Button 1', icon_class='mdi-test')
        button1.permissions.append('leaked_permission')

        button2 = PluginMenuButton(link='button2', title='Button 2', icon_class='mdi-test')

        self.assertIsNot(button1.permissions, button2.permissions)
        self.assertEqual(button1.permissions, ['leaked_permission'])
        self.assertEqual(button2.permissions, [])

    def test_explicit_permissions_remain_independent(self):
        item1 = PluginMenuItem(link='test1', link_text='Test 1', permissions=['explicit_permission'])
        item2 = PluginMenuItem(link='test2', link_text='Test 2', permissions=['different_permission'])

        self.assertIsNot(item1.permissions, item2.permissions)
        self.assertEqual(item1.permissions, ['explicit_permission'])
        self.assertEqual(item2.permissions, ['different_permission'])


class RegisterGraphQLExtensionsTestCase(TestCase):
    """Validate registration-time checks for GraphQL type/filter extensions."""

    def test_rejects_extension_without_models(self):
        import strawberry

        from netbox.plugins.registration import register_graphql_type_extensions

        @strawberry.type
        class NoModels:
            pass

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([NoModels])

    def test_rejects_undecorated_extension(self):
        # A plain class (no @strawberry.type) must be rejected...
        from netbox.plugins.registration import register_graphql_type_extensions

        class Undecorated:
            models = ['dcim.device']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Undecorated])

    def test_rejects_undecorated_subclass_of_strawberry_type(self):
        # ...as must a subclass that only inherits __strawberry_definition__ without its own decoration.
        import strawberry

        from netbox.plugins.registration import register_graphql_type_extensions

        @strawberry.type
        class Base:
            pass

        class Child(Base):
            models = ['dcim.device']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Child])

    def test_rejects_unknown_model_label(self):
        import strawberry

        from netbox.plugins.registration import register_graphql_type_extensions

        @strawberry.type
        class BadTarget:
            models = ['dcim.notamodel']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([BadTarget])

    def test_filter_extension_requires_strawberry_type(self):
        # The filter path enforces the same @strawberry.type requirement as the type path.
        from netbox.plugins.registration import register_graphql_filter_extensions

        class UndecoratedFilter:
            models = ['dcim.device']

        with self.assertRaises(TypeError):
            register_graphql_filter_extensions([UndecoratedFilter])

    def test_raises_when_registered_after_assembly(self):
        @strawberry.type
        class LateExt:
            models = ['dcim.cable']
            late_field: str

        with self.assertRaises(ImproperlyConfigured) as ctx:
            register_graphql_type_extensions([LateExt])
        self.assertIn('strawberry.lazy()', str(ctx.exception))
        self.assertNotIn(LateExt, registry['plugins']['graphql_type_extensions'].get('dcim.cable', []))

    def test_rejects_string_models(self):
        @strawberry.type
        class Ext:
            models = 'dcim.site'
            field_a: str

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_duplicate_labels(self):
        @strawberry.type
        class Ext:
            models = ['dcim.site', 'dcim.Site']
            field_a: str

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_subclass_of_strawberry_django_type(self):
        @strawberry_django.type(DummyModel, fields='__all__')
        class Base:
            pass

        @strawberry.type
        class Ext(Base):
            models = ['dcim.site']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_duplicate_registration(self):
        @strawberry.type
        class Ext:
            models = ['dcim.cable']
            field_a: str

        with mock.patch.dict(registry['plugins']['graphql_type_extensions'], {'dcim.cable': [Ext]}):
            with self.assertRaises(TypeError):
                register_graphql_type_extensions([Ext])

    def test_rejects_interface_implementing_extension(self):
        @strawberry.interface
        class PluginInterface:
            plugin_field: str

        @strawberry.type
        class Ext(PluginInterface):
            models = ['dcim.site']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_extension_instance(self):
        @strawberry.type
        class Ext:
            models = ['dcim.site']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext()])

    def test_rejects_non_string_model_label(self):
        @strawberry.type
        class Ext:
            models = [None]

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_input_type_extension(self):
        @strawberry.input
        class Ext:
            models = ['dcim.site']
            field_a: str

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_interface_extension(self):
        @strawberry.interface
        class Ext:
            models = ['dcim.site']
            field_a: str

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejects_strawberry_django_type_extension(self):
        @strawberry_django.type(DummyModel, fields='__all__')
        class Ext:
            models = ['dcim.site']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_core_assembly_allowed_during_app_initialization(self):
        """Core types still assemble while apps are initializing, since the old apps.ready gate was removed."""
        with (
            mock.patch.object(apps, 'ready', False),
            mock.patch.dict(registry['plugins']['graphql_type_extensions'], {}, clear=True),
        ):
            @register_model_graphql_type(Site, strawberry_django.type, 'graphql_type_extensions', fields='__all__')
            class TestSiteType:
                pass

        self.assertTrue(hasattr(TestSiteType, '__strawberry_definition__'))

    def test_rejects_extension_with_unassembled_target(self):
        @strawberry.type
        class Ext:
            models = ['dcim.cablepath']
            field_a: str

        with mock.patch.dict(registry['plugins']['graphql_type_extensions'], {'dcim.cablepath': [Ext]}):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                graphql_utils.validate_extension_targets()
        self.assertIn('dcim.cablepath', str(ctx.exception))

    def test_extension_targets_validate_on_real_state(self):
        graphql_utils.validate_extension_targets()

    def test_rejects_annotated_models_marker(self):
        @strawberry.type
        class Ext:
            models: tuple[str, ...] = ('dcim.site',)

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([Ext])

    def test_rejected_registration_creates_no_registry_bucket(self):
        @strawberry.type
        class Ext:
            models = ['dcim.cable']
            field_a: str

        with self.assertRaises(ImproperlyConfigured):
            register_graphql_type_extensions([Ext])
        self.assertNotIn('dcim.cable', registry['plugins']['graphql_type_extensions'])

    def test_rejects_non_iterable_models(self):
        @strawberry.type
        class Ext:
            models = 5

        with self.assertRaises(TypeError) as ctx:
            register_graphql_type_extensions([Ext])
        self.assertIn("must declare 'models'", str(ctx.exception))

    def test_invalid_batch_entry_registers_nothing(self):
        self.addCleanup(lambda: registry['plugins']['graphql_type_extensions'].pop('dcim.cablepath', None))

        @strawberry.type
        class GoodExt:
            models = ['dcim.cablepath']
            field_a: str

        class BadExt:
            models = ['dcim.cablepath']

        with self.assertRaises(TypeError):
            register_graphql_type_extensions([GoodExt, BadExt])
        self.assertNotIn(GoodExt, registry['plugins']['graphql_type_extensions'].get('dcim.cablepath', ()))
