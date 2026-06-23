from io import BytesIO, StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from extras.management.commands import renaturalize, webhook_receiver
from extras.management.commands.webhook_receiver import WebhookHandler
from extras.models import ImageAttachment
from extras.tests.test_models import OverwriteStyleMemoryStorage, UnreadableSizeMemoryStorage
from users.models import User
from utilities.fields import NaturalOrderingField


class ReindexTestCase(TestCase):
    def test_reindex_all_registered_indexers(self):
        class DummyObjects:
            @staticmethod
            def iterator():
                return iter(())

        class DummyModel:
            objects = DummyObjects()
            _meta = SimpleNamespace(app_label='extras', model_name='dummy')

        indexer = SimpleNamespace(model=DummyModel)
        out = StringIO()

        with (
            patch('extras.management.commands.reindex.registry', {'search': {'extras.dummy': indexer}}),
            patch('extras.management.commands.reindex.search_backend') as search_backend,
        ):
            search_backend.clear.return_value = 0
            search_backend.cache.return_value = 0
            search_backend.size = 0

            call_command('reindex', stdout=out)

        search_backend.clear.assert_called_once_with(object_types=None)
        search_backend.cache.assert_called_once()
        self.assertIn('Completed.', out.getvalue())

    def test_reindex_lazy_skips_models_with_existing_cache(self):
        class DummyObjects:
            @staticmethod
            def iterator():
                return iter(())

        class DummyModel:
            objects = DummyObjects()
            _meta = SimpleNamespace(app_label='extras', model_name='dummy')

        content_type = object()
        indexer = SimpleNamespace(model=DummyModel)
        out = StringIO()

        with (
            patch('extras.management.commands.reindex.registry', {'search': {'extras.dummy': indexer}}),
            patch('extras.management.commands.reindex.search_backend') as search_backend,
            patch.object(ContentType.objects, 'get_for_model', return_value=content_type),
        ):
            search_backend.count.return_value = 1
            search_backend.size = 1

            call_command('reindex', lazy=True, stdout=out)

        search_backend.clear.assert_not_called()
        search_backend.count.assert_called_once_with(object_types=[content_type])
        search_backend.cache.assert_not_called()
        self.assertIn('Skipping', out.getvalue())

    def test_reindex_specific_model_caches_objects_and_reports_total_count(self):
        iterator = iter([object()])

        class DummyObjects:
            @staticmethod
            def iterator():
                return iterator

        class DummyModel:
            objects = DummyObjects()
            _meta = SimpleNamespace(app_label='extras', model_name='dummy')

        content_type = object()
        indexer = SimpleNamespace(model=DummyModel)
        out = StringIO()

        with (
            patch('extras.management.commands.reindex.registry', {'search': {'extras.dummy': indexer}}),
            patch('extras.management.commands.reindex.search_backend') as search_backend,
            patch.object(ContentType.objects, 'get_for_model', return_value=content_type),
        ):
            search_backend.clear.return_value = 2
            search_backend.cache.return_value = 1
            search_backend.size = 1

            call_command('reindex', 'extras.dummy', stdout=out)

        search_backend.clear.assert_called_once_with(object_types=[content_type])
        search_backend.cache.assert_called_once_with(iterator, remove_existing=False)
        self.assertIn('1 entries cached.', out.getvalue())
        self.assertIn('Total entries: 1', out.getvalue())

    def test_reindex_app_label_uses_matching_indexers(self):
        class DummyObjects:
            @staticmethod
            def iterator():
                return iter(())

        class DummyModel:
            objects = DummyObjects()
            _meta = SimpleNamespace(app_label='extras', model_name='dummy')

        class OtherModel:
            objects = DummyObjects()
            _meta = SimpleNamespace(app_label='dcim', model_name='device')

        content_type = object()
        indexer = SimpleNamespace(model=DummyModel)
        other_indexer = SimpleNamespace(model=OtherModel)

        with (
            patch(
                'extras.management.commands.reindex.registry',
                {'search': {'extras.dummy': indexer, 'dcim.device': other_indexer}},
            ),
            patch('extras.management.commands.reindex.search_backend') as search_backend,
            patch.object(ContentType.objects, 'get_for_model', return_value=content_type),
        ):
            search_backend.clear.return_value = 0
            search_backend.cache.return_value = 0
            search_backend.size = 0

            call_command('reindex', 'extras', stdout=StringIO())

        search_backend.clear.assert_called_once_with(object_types=[content_type])
        search_backend.cache.assert_called_once()

    def test_reindex_unknown_registered_model(self):
        with (
            patch('extras.management.commands.reindex.registry', {'search': {}}),
            self.assertRaisesMessage(CommandError, 'No indexer registered for extras.dummy'),
        ):
            call_command('reindex', 'extras.dummy', stdout=StringIO())

    def test_reindex_app_with_no_registered_indexers(self):
        with (
            patch('extras.management.commands.reindex.registry', {'search': {}}),
            self.assertRaisesMessage(CommandError, 'No indexers found'),
        ):
            call_command('reindex', 'extras', stdout=StringIO())

    def test_invalid_model_label(self):
        with self.assertRaisesMessage(CommandError, 'Invalid model'):
            call_command('reindex', 'dcim.rack.extra', stdout=StringIO())


class RenaturalizeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Test Device Type',
            slug='test-device-type',
        )
        device_role = DeviceRole.objects.create(
            name='Test Device Role',
            slug='test-device-role',
            color='ff0000',
        )
        cls.device = Device.objects.create(
            device_type=device_type,
            role=device_role,
            name='Test Device',
            site=site,
        )

    def test_recalculates_natural_ordering_fields(self):
        interface = Interface.objects.create(
            device=self.device,
            name='Ethernet10',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        field = next(field for field in Interface._meta.concrete_fields if type(field) is NaturalOrderingField)
        Interface.objects.filter(pk=interface.pk).update(**{field.name: 'incorrect'})

        out = StringIO()
        call_command('renaturalize', 'dcim.Interface', verbosity=2, stdout=out)

        interface.refresh_from_db()
        expected = field.naturalize_function(interface.name, max_length=field.max_length)
        self.assertEqual(getattr(interface, field.name), expected)
        self.assertIn('Ethernet10 ->', out.getvalue())
        self.assertIn('updated', out.getvalue())

    def test_recalculates_with_default_verbosity(self):
        interface = Interface.objects.create(
            device=self.device,
            name='Ethernet11',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        field = next(field for field in Interface._meta.concrete_fields if type(field) is NaturalOrderingField)
        Interface.objects.filter(pk=interface.pk).update(**{field.name: 'incorrect'})

        out = StringIO()
        call_command('renaturalize', 'dcim.Interface', verbosity=1, stdout=out)

        interface.refresh_from_db()
        expected = field.naturalize_function(interface.name, max_length=field.max_length)
        self.assertEqual(getattr(interface, field.name), expected)
        self.assertIn('Renaturalizing 1 models.', out.getvalue())
        self.assertIn('Done.', out.getvalue())

    def test_invalid_format(self):
        with self.assertRaisesMessage(CommandError, 'Invalid format'):
            call_command('renaturalize', 'dcim', stdout=StringIO())

    def test_model_without_natural_ordering(self):
        with self.assertRaisesMessage(CommandError, 'does not employ natural ordering'):
            call_command('renaturalize', 'extras.Tag', stdout=StringIO())

    def test_unknown_app_label(self):
        with self.assertRaises(CommandError):
            call_command('renaturalize', 'invalid.Interface', stdout=StringIO())

    def test_unknown_model_name(self):
        with self.assertRaisesMessage(CommandError, 'Unknown model: dcim.UnknownModel'):
            call_command('renaturalize', 'dcim.UnknownModel', stdout=StringIO())

    def test_get_models_discovers_all_models_with_natural_ordering_fields(self):
        field = next(field for field in Interface._meta.concrete_fields if type(field) is NaturalOrderingField)
        model = SimpleNamespace(_meta=SimpleNamespace(concrete_fields=[field]))
        app_config = SimpleNamespace(models={'interface': model})

        with patch('extras.management.commands.renaturalize.apps.get_app_configs', return_value=[app_config]):
            models = renaturalize.Command()._get_models(())

        self.assertEqual(models, [(model, [field])])


class RunScriptTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password',
        )

    def test_enqueues_script_job(self):
        class TestScript:
            full_name = 'test.Script'

            def as_form(self, data, files):
                form = MagicMock()
                form.is_valid.return_value = True
                form.cleaned_data = {
                    '_schedule_at': None,
                    '_interval': None,
                    '_commit': None,
                    'name': data['name'],
                }
                form.errors.get_json_data.return_value = {}
                return form

        script_obj = SimpleNamespace(python_class=TestScript)
        job = SimpleNamespace(duration='0 seconds')

        with (
            patch(
                'extras.management.commands.runscript.get_module_and_script',
                return_value=(None, script_obj),
            ) as get_module_and_script,
            patch(
                'extras.management.commands.runscript.ScriptJob.enqueue',
                return_value=job,
            ) as enqueue,
            patch('extras.management.commands.runscript.logging.getLogger'),
        ):
            call_command(
                'runscript',
                'test.Script',
                user='admin',
                data='{"name": "test"}',
                stdout=StringIO(),
            )

        get_module_and_script.assert_called_once_with('test', 'Script')
        enqueue.assert_called_once()
        kwargs = enqueue.call_args.kwargs
        self.assertEqual(kwargs['instance'], script_obj)
        self.assertEqual(kwargs['user'], self.user)
        self.assertTrue(kwargs['immediate'])
        self.assertEqual(kwargs['data'], {'name': 'test'})
        self.assertFalse(kwargs['commit'])

    def test_invalid_script_data_raises_error_without_enqueueing_job(self):
        class TestScript:
            full_name = 'test.Script'

            def as_form(self, data, files):
                form = MagicMock()
                form.is_valid.return_value = False
                form.errors.get_json_data.return_value = {
                    'name': [
                        {'message': 'This field is required.'},
                    ],
                }
                return form

        script_obj = SimpleNamespace(python_class=TestScript)
        logger = MagicMock()

        with (
            patch(
                'extras.management.commands.runscript.get_module_and_script',
                return_value=(None, script_obj),
            ) as get_module_and_script,
            patch('extras.management.commands.runscript.ScriptJob.enqueue') as enqueue,
            patch('extras.management.commands.runscript.logging.getLogger', return_value=logger),
        ):
            with self.assertRaises(CommandError):
                call_command(
                    'runscript',
                    'test.Script',
                    user='admin',
                    data='{}',
                    stdout=StringIO(),
                )

        get_module_and_script.assert_called_once_with('test', 'Script')
        enqueue.assert_not_called()
        logger.error.assert_any_call('Data is not valid:')
        logger.error.assert_any_call('\tname: This field is required.')

    def test_missing_user_falls_back_to_superuser_and_empty_data(self):
        class TestScript:
            full_name = 'test.Script'

            def as_form(self, data, files):
                form = MagicMock()
                form.is_valid.return_value = True
                form.cleaned_data = {
                    '_schedule_at': None,
                    '_interval': None,
                    '_commit': None,
                }
                form.errors.get_json_data.return_value = {}
                return form

        script_obj = SimpleNamespace(python_class=TestScript)
        job = SimpleNamespace(duration='0 seconds')

        with (
            patch(
                'extras.management.commands.runscript.get_module_and_script',
                return_value=(None, script_obj),
            ),
            patch(
                'extras.management.commands.runscript.ScriptJob.enqueue',
                return_value=job,
            ) as enqueue,
            patch('extras.management.commands.runscript.logging.getLogger'),
        ):
            call_command(
                'runscript',
                'test.Script',
                user='missing-user',
                stdout=StringIO(),
            )

        kwargs = enqueue.call_args.kwargs
        self.assertEqual(kwargs['user'], self.user)
        self.assertEqual(kwargs['data'], {})

    def test_no_user_argument_falls_back_to_first_superuser(self):
        class TestScript:
            full_name = 'test.Script'

            def as_form(self, data, files):
                form = MagicMock()
                form.is_valid.return_value = True
                form.cleaned_data = {
                    '_schedule_at': None,
                    '_interval': None,
                    '_commit': None,
                }
                form.errors.get_json_data.return_value = {}
                return form

        script_obj = SimpleNamespace(python_class=TestScript)
        job = SimpleNamespace(duration='0 seconds')

        with (
            patch(
                'extras.management.commands.runscript.get_module_and_script',
                return_value=(None, script_obj),
            ),
            patch(
                'extras.management.commands.runscript.ScriptJob.enqueue',
                return_value=job,
            ) as enqueue,
            patch('extras.management.commands.runscript.logging.getLogger'),
        ):
            call_command('runscript', 'test.Script', stdout=StringIO())

        self.assertEqual(enqueue.call_args.kwargs['user'], self.user)


class WebhookReceiverTestCase(TestCase):
    def test_starts_http_server(self):
        out = StringIO()

        with (
            patch('extras.management.commands.webhook_receiver.HTTPServer') as http_server,
            patch.object(WebhookHandler, 'show_headers', True),
        ):
            server = http_server.return_value
            server.serve_forever.side_effect = KeyboardInterrupt

            call_command(
                'webhook_receiver',
                port=9999,
                no_headers=True,
                stdout=out,
            )

            self.assertFalse(WebhookHandler.show_headers)

        http_server.assert_called_once_with(('localhost', 9999), WebhookHandler)
        server.serve_forever.assert_called_once_with()
        self.assertIn('Listening on port http://localhost:9999', out.getvalue())
        self.assertIn('Exiting', out.getvalue())

    def test_handler_routes_arbitrary_http_methods(self):
        handler = object.__new__(WebhookHandler)

        self.assertEqual(handler.__getattr__('do_PATCH').__func__, WebhookHandler.do_ANY)
        with self.assertRaises(AttributeError):
            handler.__getattr__('missing')

    def test_handler_logs_request_message(self):
        handler = object.__new__(WebhookHandler)
        handler.date_time_string = MagicMock(return_value='now')
        handler.address_string = MagicMock(return_value='127.0.0.1')

        with (
            patch('extras.management.commands.webhook_receiver.request_counter', 7),
            patch('builtins.print') as print_,
        ):
            handler.log_message('%s', 'message')

        print_.assert_called_once_with('[7] now 127.0.0.1 message')

    def test_handler_accepts_json_request_body(self):
        handler = object.__new__(WebhookHandler)
        body = b'{"ok": true}'
        handler.headers = {
            'Content-Length': str(len(body)),
            'Content-Type': 'application/json',
            'X-Test': 'value',
        }
        handler.rfile = BytesIO(body)
        handler.wfile = BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()
        handler.show_headers = True

        with (
            patch('extras.management.commands.webhook_receiver.request_counter', 1),
            patch('builtins.print') as print_,
        ):
            handler.do_ANY()
            self.assertEqual(webhook_receiver.request_counter, 2)

        handler.send_response.assert_called_once_with(200)
        handler.end_headers.assert_called_once_with()
        self.assertEqual(handler.wfile.getvalue(), b'Webhook received!\n')
        print_.assert_any_call('X-Test: value')
        print_.assert_any_call('{\n    "ok": true\n}')
        print_.assert_any_call('Completed request #1')

    def test_handler_prints_no_body_when_content_length_is_missing(self):
        handler = object.__new__(WebhookHandler)
        handler.headers = {}
        handler.rfile = BytesIO()
        handler.wfile = BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()
        handler.show_headers = False

        with (
            patch('extras.management.commands.webhook_receiver.request_counter', 1),
            patch('builtins.print') as print_,
        ):
            handler.do_ANY()

        print_.assert_any_call('(No body)')
        print_.assert_any_call('Completed request #1')


class PopulateImageSizesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ct_site = ContentType.objects.get_by_natural_key('dcim', 'site')
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def _legacy_attachment(self, name, image_name):
        # bulk_create skips save(), so image_size starts NULL, mimicking a row created before the field existed.
        attachment = ImageAttachment(
            object_type=self.ct_site,
            object_id=self.site.pk,
            name=name,
            image=image_name,
            image_height=100,
            image_width=100,
        )
        ImageAttachment.objects.bulk_create([attachment])
        return ImageAttachment.objects.get(name=name)

    def test_populates_null_image_sizes(self):
        field = ImageAttachment._meta.get_field('image')
        storage = OverwriteStyleMemoryStorage()
        storage.files['image-attachments/site_1_a.png'] = b'\x00' * 321

        attachment = self._legacy_attachment('Legacy 1', 'image-attachments/site_1_a.png')
        self.assertIsNone(attachment.image_size)

        out = StringIO()
        with patch.object(field, 'storage', storage):
            call_command('populate_image_sizes', stdout=out)
            # Read the persisted value back under the patched storage (refreshing the image field re-reads
            # dimensions from storage, which must be the in-memory backend).
            persisted = ImageAttachment.objects.get(pk=attachment.pk)
            self.assertEqual(persisted.image_size, 321)

        self.assertIn('Updated 1', out.getvalue())

    def test_skips_unreadable_files_and_is_rerunnable(self):
        field = ImageAttachment._meta.get_field('image')
        attachment = self._legacy_attachment('Legacy 2', 'image-attachments/site_1_missing.png')

        # First run: storage can't report size, so the row is skipped and left NULL.
        out = StringIO()
        with patch.object(field, 'storage', UnreadableSizeMemoryStorage()):
            call_command('populate_image_sizes', stdout=out)
            self.assertIsNone(ImageAttachment.objects.get(pk=attachment.pk).image_size)
        self.assertIn('Skipped 1', out.getvalue())

        # Second run: storage now works, and the previously-skipped row is picked up.
        storage = OverwriteStyleMemoryStorage()
        storage.files['image-attachments/site_1_missing.png'] = b'\x00' * 654
        out = StringIO()
        with patch.object(field, 'storage', storage):
            call_command('populate_image_sizes', stdout=out)
            self.assertEqual(ImageAttachment.objects.get(pk=attachment.pk).image_size, 654)

    def test_noop_when_nothing_to_update(self):
        out = StringIO()
        call_command('populate_image_sizes', stdout=out)
        self.assertIn('No image attachments require updating.', out.getvalue())
