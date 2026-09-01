import io
import sys
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import PropertyMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from netaddr import IPAddress, IPNetwork

from core.choices import JobNotificationChoices, JobStatusChoices, ManagedFileRootPathChoices
from core.models import Job
from dcim.models import DeviceRole
from extras.constants import SCRIPT_MODULE_NAME_PREFIX
from extras.jobs import ScriptJob
from extras.models import Script as ScriptModel
from extras.models import ScriptModule
from extras.scripts import *

CHOICES = (
    ('ff0000', 'Red'),
    ('00ff00', 'Green'),
    ('0000ff', 'Blue')
)

YAML_DATA = """
Foo: 123
Bar: 456
Baz:
 - A
 - B
 - C
"""

JSON_DATA = """
{
  "Foo": 123,
  "Bar": 456,
  "Baz": ["A", "B", "C"]
}
"""


class ScriptVariablesTestCase(TestCase):

    def test_stringvar(self):

        class TestScript(Script):

            var1 = StringVar(
                min_length=3,
                max_length=3,
                regex=r'[a-z]+'
            )

        # Validate min_length enforcement
        data = {'var1': 'xx'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_length enforcement
        data = {'var1': 'xxxx'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate regex enforcement
        data = {'var1': 'ABC'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': 'abc'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_textvar(self):

        class TestScript(Script):

            var1 = TextVar()

        # Validate valid data
        data = {'var1': 'This is a test string'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_integervar(self):

        class TestScript(Script):

            var1 = IntegerVar(
                min_value=5,
                max_value=10
            )

        # Validate min_value enforcement
        data = {'var1': 4}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_value enforcement
        data = {'var1': 11}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': 7}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_decimalvar(self):

        class TestScript(Script):

            var1 = DecimalVar(
                min_value=-100.500,
                max_value=100.500,
                max_digits=6,
                decimal_places=3,
                required=False
            )

            var2 = DecimalVar(
                max_digits=3,
                decimal_places=1,
                required=False
            )

        # Validate min_value enforcement
        data = {'var1': -100.501}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_value enforcement
        data = {'var1': 100.501}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_digits enforcement
        data = {'var2': 123.4}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var2', form.errors)

        # Validate decimal_places
        data = {'var2': 1.23}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var2', form.errors)

        # Validate valid data
        data = {'var1': '50.123'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], Decimal(data['var1']))

    def test_booleanvar(self):

        class TestScript(Script):

            var1 = BooleanVar()

        # Validate True
        data = {'var1': True}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], True)

        # Validate False
        data = {'var1': False}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], False)

    def test_choicevar(self):

        class TestScript(Script):

            var1 = ChoiceVar(
                choices=CHOICES
            )

        # Validate valid choice
        data = {'var1': 'ff0000'}
        form = TestScript().as_form(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], 'ff0000')

        # Validate invalid choice
        data = {'var1': 'taupe'}
        form = TestScript().as_form(data)
        self.assertFalse(form.is_valid())

    def test_multichoicevar(self):

        class TestScript(Script):

            var1 = MultiChoiceVar(
                choices=CHOICES
            )

        # Validate single choice
        data = {'var1': ['ff0000']}
        form = TestScript().as_form(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], ['ff0000'])

        # Validate multiple choices
        data = {'var1': ('ff0000', '00ff00')}
        form = TestScript().as_form(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], ['ff0000', '00ff00'])

        # Validate invalid choice
        data = {'var1': 'taupe'}
        form = TestScript().as_form(data)
        self.assertFalse(form.is_valid())

    def test_objectvar(self):

        class TestScript(Script):
            var1 = ObjectVar(model=DeviceRole)

        # Populate some objects
        for i in range(1, 6):
            DeviceRole(
                name='Device Role {}'.format(i),
                slug='device-role-{}'.format(i)
            ).save()

        # Validate valid data
        data = {'var1': DeviceRole.objects.first().pk}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'].pk, data['var1'])

    def test_multiobjectvar(self):

        class TestScript(Script):
            var1 = MultiObjectVar(model=DeviceRole)

        # Populate some objects
        for i in range(1, 6):
            DeviceRole(
                name='Device Role {}'.format(i),
                slug='device-role-{}'.format(i)
            ).save()

        # Validate valid data
        data = {'var1': [role.pk for role in DeviceRole.objects.all()[:3]]}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'][0].pk, data['var1'][0])
        self.assertEqual(form.cleaned_data['var1'][1].pk, data['var1'][1])
        self.assertEqual(form.cleaned_data['var1'][2].pk, data['var1'][2])

    def test_filevar(self):

        class TestScript(Script):

            var1 = FileVar()

        # Dummy file
        testfile = SimpleUploadedFile(
            name='test_file.txt',
            content=b'This is a dummy file for testing'
        )

        # Validate valid data
        file_data = {'var1': testfile}
        form = TestScript().as_form(None, file_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], testfile)

    def test_ipaddressvar(self):

        class TestScript(Script):

            var1 = IPAddressVar()

        # Validate IP network enforcement
        data = {'var1': '1.2.3'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate IP mask exclusion
        data = {'var1': '192.0.2.0/24'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': '192.0.2.1'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], IPAddress(data['var1']))

    def test_ipaddresswithmaskvar(self):

        class TestScript(Script):

            var1 = IPAddressWithMaskVar()

        # Validate IP network enforcement
        data = {'var1': '1.2.3'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate IP mask requirement
        data = {'var1': '192.0.2.0'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': '192.0.2.0/24'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], IPNetwork(data['var1']))

    def test_ipnetworkvar(self):

        class TestScript(Script):

            var1 = IPNetworkVar()

        # Validate IP network enforcement
        data = {'var1': '1.2.3'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate host IP check
        data = {'var1': '192.0.2.1/24'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': '192.0.2.0/24'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], IPNetwork(data['var1']))

    def test_datevar(self):

        class TestScript(Script):

            var1 = DateVar()
            var2 = DateVar(required=False)

        # Test date validation
        data = {'var1': 'not a date'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        input_date = date(2024, 4, 1)
        data = {'var1': input_date}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], input_date)
        # Validate required=False works for this Var type
        self.assertEqual(form.cleaned_data['var2'], None)

    def test_datetimevar(self):

        class TestScript(Script):

            var1 = DateTimeVar()
            var2 = DateTimeVar(required=False)

        # Test datetime validation
        data = {'var1': 'not a datetime'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        input_datetime = datetime(2024, 4, 1, 8, 0, 0, 0, UTC)
        data = {'var1': input_datetime}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], input_datetime)
        # Validate required=False works for this Var type
        self.assertEqual(form.cleaned_data['var2'], None)


class ScriptModuleLoadingTestCase(TestCase):

    def test_module_does_not_shadow_core_app(self):
        """
        Loading a custom script whose filename matches a core app label must not replace that
        app's package in sys.modules. Regression test for issue #22566.
        """
        import circuits  # The real core app package

        script_content = (
            b"from extras.scripts import Script\n\n\n"
            b"class TestScript(Script):\n    pass\n"
        )

        class _Storage:
            def open(self, name, mode='rb'):
                return io.BytesIO(script_content)

        module = ScriptModule(file_root='scripts', file_path='circuits.py')
        namespaced_key = f'{SCRIPT_MODULE_NAME_PREFIX}circuits'
        self.addCleanup(lambda: sys.modules.pop(namespaced_key, None))

        with patch('extras.models.mixins.storages') as mock_storages:
            mock_storages.__getitem__.return_value = _Storage()
            loaded = module.get_module()

            # The script module is registered under the private, namespaced key, and its own
            # __name__ matches that key (i.e. sys.modules[module.__name__] resolves to the module)
            self.assertIs(sys.modules[namespaced_key], loaded)
            self.assertEqual(loaded.__name__, namespaced_key)

            # The namespacing must not leak into the derived script name stored in the database
            self.assertEqual(next(iter(module.module_scripts)), 'TestScript')

            # Nor into the user-facing names exposed on the Script class (used for logger
            # namespaces, page headers, etc.): these must reflect the original filename.
            script_class = loaded.TestScript
            self.assertEqual(script_class.module, 'circuits')
            self.assertEqual(script_class.full_name, 'circuits.TestScript')
            self.assertEqual(script_class.root_module(), 'circuits')

        # The real circuits app must be untouched and remain an importable package
        self.assertIs(sys.modules['circuits'], circuits)
        self.assertTrue(hasattr(circuits, '__path__'))

    def test_script_logger_uses_public_module_name(self):
        """
        A dynamically loaded script logs to the public netbox.scripts.<module>.<class> namespace.
        """
        script_content = (
            b"from extras.scripts import Script\n\n\n"
            b"class TestScript(Script):\n    pass\n"
        )

        class _Storage:
            def open(self, name, mode='rb'):
                return io.BytesIO(script_content)

        module = ScriptModule(file_root='scripts', file_path='example.py')
        namespaced_key = f'{SCRIPT_MODULE_NAME_PREFIX}example'
        self.addCleanup(lambda: sys.modules.pop(namespaced_key, None))

        with patch('extras.models.mixins.storages') as mock_storages:
            mock_storages.__getitem__.return_value = _Storage()
            script_class = module.get_module().TestScript

        # This is the name runscript and ScriptJob attach their handlers to
        logger_name = f'netbox.scripts.{script_class.full_name}'
        script = script_class()
        self.assertEqual(script.logger.name, logger_name)

        with self.assertLogs(logger_name, 'INFO') as captured:
            script.log_success('Start')
        self.assertIn('Start', captured.output[0])


class ScriptMetaValidationTestCase(TestCase):
    """
    Tests for BaseScript.validate_meta() (#22872): invalid execution-related Meta values must raise an actionable
    ValidationError, while unset/valid values must not.
    """

    def test_valid_meta_passes(self):
        class TestScript(Script):
            class Meta:
                job_timeout = 600
                notifications_default = JobNotificationChoices.NOTIFICATION_ON_FAILURE

            def run(self, data, commit):
                pass

        TestScript.validate_meta()  # should not raise

    def test_job_timeout_duration_string_passes(self):
        class TestScript(Script):
            class Meta:
                job_timeout = '1h'

            def run(self, data, commit):
                pass

        TestScript.validate_meta()  # should not raise

    def test_unset_meta_passes(self):
        class TestScript(Script):
            def run(self, data, commit):
                pass

        # job_timeout defaults to None and notifications_default to ALWAYS; neither should be rejected
        TestScript.validate_meta()

    def test_all_notification_choices_pass(self):
        for choice in JobNotificationChoices.values():
            class TestScript(Script):
                class Meta:
                    notifications_default = choice

                def run(self, data, commit):
                    pass

            TestScript.validate_meta()  # should not raise

    def test_invalid_job_timeout_raises(self):
        class TestScript(Script):
            class Meta:
                job_timeout = 'not-a-timeout'

            def run(self, data, commit):
                pass

        with self.assertRaises(ValidationError) as cm:
            TestScript.validate_meta()
        self.assertIn('job_timeout', cm.exception.message_dict)

    def test_invalid_notifications_default_raises(self):
        class TestScript(Script):
            class Meta:
                notifications_default = 'on_error'

            def run(self, data, commit):
                pass

        with self.assertRaises(ValidationError) as cm:
            TestScript.validate_meta()
        self.assertIn('notifications_default', cm.exception.message_dict)

    def test_non_string_job_timeout_raises(self):
        # A job_timeout of an unexpected type must surface as a ValidationError, not an unhandled TypeError.
        class TestScript(Script):
            class Meta:
                job_timeout = [60]

            def run(self, data, commit):
                pass

        with self.assertRaises(ValidationError) as cm:
            TestScript.validate_meta()
        self.assertIn('job_timeout', cm.exception.message_dict)

    def test_non_positive_job_timeout_raises(self):
        # parse_timeout() accepts 0 and negatives, but a non-positive timeout is nonsensical and must be rejected.
        for value in (0, -30):
            class TestScript(Script):
                class Meta:
                    job_timeout = value

                def run(self, data, commit):
                    pass

            with self.assertRaises(ValidationError) as cm:
                TestScript.validate_meta()
            self.assertIn('job_timeout', cm.exception.message_dict)


class ScriptJobEnqueueValidationTestCase(TestCase):
    """
    Tests that ScriptJob.enqueue() validates Meta before creating a Job (#22872). This is the choke point exercised by
    event-rule actions and recurring reschedules, which have no request layer to catch the error.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('scriptrunner')

    def _make_script(self, python_class):
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path=f'meta_validation_{id(python_class)}.py',
            )
        script = ScriptModel.objects.create(module=module, name=python_class.Meta.name, is_executable=True)
        # Return the raw python_class regardless of on-disk module state
        patcher = patch.object(ScriptModel, 'python_class', property(lambda self, pc=python_class: pc))
        patcher.start()
        self.addCleanup(patcher.stop)
        return script

    def test_enqueue_rejects_invalid_job_timeout(self):
        class BadTimeout(Script):
            class Meta:
                name = 'Bad Timeout'
                job_timeout = 'not-a-timeout'

            def run(self, data, commit):
                pass

        script = self._make_script(BadTimeout)
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(ValidationError):
                ScriptJob.enqueue(
                    instance=script, user=self.user, job_timeout=BadTimeout.job_timeout,
                    notifications=BadTimeout.notifications_default, data={}, commit=True,
                )
        self.assertEqual(Job.objects.count(), 0)

    def test_enqueue_rejects_invalid_notifications_default(self):
        class BadNotifications(Script):
            class Meta:
                name = 'Bad Notifications'
                notifications_default = 'on_error'

            def run(self, data, commit):
                pass

        script = self._make_script(BadNotifications)
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(ValidationError):
                ScriptJob.enqueue(
                    instance=script, user=self.user, job_timeout=BadNotifications.job_timeout,
                    notifications=BadNotifications.notifications_default, data={}, commit=True,
                )
        self.assertEqual(Job.objects.count(), 0)

    def test_enqueue_accepts_valid_meta(self):
        class GoodScript(Script):
            class Meta:
                name = 'Good Script'
                job_timeout = '1h'
                notifications_default = JobNotificationChoices.NOTIFICATION_ALWAYS

            def run(self, data, commit):
                pass

        script = self._make_script(GoodScript)
        # Do not execute the on_commit callback: the Job row is created by Job.enqueue() before the RQ push is
        # registered, so asserting the row exists needs no real enqueue. Executing it would leave a job in the shared
        # Redis queue that races other tests under the parallel runner (see #22872).
        with self.captureOnCommitCallbacks():
            job = ScriptJob.enqueue(
                instance=script, user=self.user, job_timeout=GoodScript.job_timeout,
                notifications=GoodScript.notifications_default, data={}, commit=True,
            )
        self.assertIsNotNone(job)
        self.assertEqual(Job.objects.count(), 1)

    def test_enqueue_positional_instance_is_validated_and_forwarded(self):
        """
        The instance may be passed positionally (JobRunner.enqueue() forwards it to Job.enqueue()'s first argument).
        The override must validate it without breaking that inherited calling contract (#22872).
        """
        class BadTimeout(Script):
            class Meta:
                name = 'Bad Timeout Positional'
                job_timeout = 'not-a-timeout'

            def run(self, data, commit):
                pass

        script = self._make_script(BadTimeout)
        # Passed positionally, not instance=... — must still be validated and rejected.
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(ValidationError):
                ScriptJob.enqueue(script, user=self.user, data={}, commit=True)
        self.assertEqual(Job.objects.count(), 0)

    def test_enqueue_positional_instance_valid_meta_creates_job(self):
        """A valid script passed positionally must enqueue cleanly, i.e. the override forwards args unchanged."""
        class GoodScript(Script):
            class Meta:
                name = 'Good Positional'

            def run(self, data, commit):
                pass

        script = self._make_script(GoodScript)
        # Do not execute the on_commit callback (see the note in test_enqueue_accepts_valid_meta): asserting the Job
        # row exists needs no real RQ push, and executing it would leak a job into the shared queue (see #22872).
        with self.captureOnCommitCallbacks():
            job = ScriptJob.enqueue(script, user=self.user, data={}, commit=True)
        self.assertIsNotNone(job)
        self.assertEqual(Job.objects.count(), 1)

    def test_reschedule_with_invalid_meta_preserves_completed_run(self):
        """
        If a recurring script's Meta.job_timeout becomes invalid between runs, the occurrence that just ran to
        completion must keep its COMPLETED status and not be re-terminated as ERRORED, no successor may be scheduled,
        and the reschedule failure must be recorded on the job (#22872).
        """
        class RecurringScript(Script):
            class Meta:
                name = 'Recurring'
                # No custom job_timeout at schedule time: valid.

            def run(self, data, commit):
                pass

        script = self._make_script(RecurringScript)

        # Create a completed, recurring job as if a scheduled occurrence had just finished successfully.
        job = Job.objects.create(
            object=script,
            name='Recurring',
            status=JobStatusChoices.STATUS_COMPLETED,
            user=self.user,
            interval=60,
            job_id=uuid.uuid4(),
        )

        # The script's Meta is edited to an invalid job_timeout before the reschedule fires.
        class RecurringScriptBadTimeout(RecurringScript):
            class Meta(RecurringScript.Meta):
                job_timeout = 'not-a-timeout'

        with patch.object(ScriptModel, 'python_class', new_callable=PropertyMock) as mock_pc:
            mock_pc.return_value = RecurringScriptBadTimeout
            with self.captureOnCommitCallbacks(execute=True):
                # handle() runs the script (which succeeds) and then reschedules in its finally block; the reschedule
                # enqueue is what fails validation here.
                ScriptJob.handle(job, data={}, commit=False)

        job.refresh_from_db()
        # The completed run's status is preserved (not flipped to ERRORED)
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        # No successor was scheduled
        self.assertEqual(
            Job.objects.filter(name='Recurring').exclude(pk=job.pk).count(), 0
        )
        # The reschedule failure was recorded on the job
        self.assertTrue(any('not rescheduled' in entry.get('message', '') for entry in job.log_entries))
