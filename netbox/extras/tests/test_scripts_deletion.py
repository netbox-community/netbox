import uuid
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.db import router
from django.db.models import QuerySet
from django.test import TestCase, override_settings
from django.urls import reverse

from core.choices import JobStatusChoices, ManagedFileRootPathChoices
from core.models import DataSource, Job
from extras.models import Script, ScriptModule
from extras.validators import CustomValidator
from netbox.models.deletion import ConfirmCollector, CountOnly
from utilities.exceptions import AbortRequest
from utilities.testing import TestCase as ViewTestCase


class ScriptDeletionTestCase(TestCase):
    """
    Regression tests for #22812: deleting a JobsMixin object (Script, ScriptModule, DataSource)
    with many associated Jobs must not load every Job into memory at once.
    """
    @classmethod
    def setUpTestData(cls):
        cls.script_ct = ContentType.objects.get_for_model(Script, for_concrete_model=False)

    def _create_module(self):
        return ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path=f'test_{uuid.uuid4().hex[:8]}.py',
        )

    def _create_script(self, module=None):
        module = module or self._create_module()
        script = Script.objects.create(module=module, name=f'S{uuid.uuid4().hex[:8]}')
        return module, script

    def _add_jobs(self, obj, count, object_type=None):
        object_type = object_type or ContentType.objects.get_for_model(type(obj), for_concrete_model=False)
        Job.objects.bulk_create([
            Job(
                object_type=object_type,
                object_id=obj.pk,
                name='testjob',
                status=JobStatusChoices.STATUS_COMPLETED,
                job_id=uuid.uuid4(),
                data={'output': 'x' * 50},
            )
            for _ in range(count)
        ])

    def test_delete_script_deletes_all_jobs(self):
        _, script = self._create_script()
        self._add_jobs(script, 2500)
        self.assertEqual(script.jobs.count(), 2500)

        script.delete()

        self.assertFalse(Script.objects.filter(pk=script.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 0)

    def test_delete_script_batches_jobs(self):
        _, script = self._create_script()
        self._add_jobs(script, 5)

        job_delete_calls = []
        original_delete = QuerySet.delete

        def counting_delete(qs, *args, **kwargs):
            if qs.model is Job:
                job_delete_calls.append(len(qs))
            return original_delete(qs, *args, **kwargs)

        with mock.patch('netbox.models.features.JOB_DELETE_BATCH_SIZE', 2):
            with mock.patch.object(QuerySet, 'delete', counting_delete):
                script.delete()

        # 5 jobs at a batch size of 2 => three batched deletes (2, 2, 1)
        self.assertEqual(job_delete_calls, [2, 2, 1])
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 0)

    def test_delete_scriptmodule_cascades_to_scripts_and_jobs(self):
        module, script = self._create_script()
        self._add_jobs(script, 100)

        module.delete()

        self.assertFalse(ScriptModule.objects.filter(pk=module.pk).exists())
        self.assertFalse(Script.objects.filter(pk=script.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 0)

    def test_delete_scriptmodule_batches_child_script_jobs(self):
        # The reporter's actual path: a script is only removable via the UI by deleting its
        # ScriptModule. The module's delete must batch the child Script's jobs.
        module, script = self._create_script()
        self._add_jobs(script, 5)

        job_delete_calls = []
        original_delete = QuerySet.delete

        def counting_delete(qs, *args, **kwargs):
            if qs.model is Job:
                job_delete_calls.append(len(qs))
            return original_delete(qs, *args, **kwargs)

        with mock.patch('netbox.models.features.JOB_DELETE_BATCH_SIZE', 2):
            with mock.patch.object(QuerySet, 'delete', counting_delete):
                module.delete()

        # 5 child-script jobs at a batch size of 2 => three batched deletes (2, 2, 1). The module
        # has no jobs of its own, so JobsMixin.delete adds no further Job deletes.
        self.assertEqual(job_delete_calls, [2, 2, 1])
        self.assertFalse(Script.objects.filter(pk=script.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 0)

    def test_delete_datasource_deletes_jobs(self):
        datasource = DataSource.objects.create(name='DS', type='local', source_url='/tmp/test')
        self._add_jobs(datasource, 100)
        ds_ct = ContentType.objects.get_for_model(DataSource, for_concrete_model=False)
        self.assertEqual(Job.objects.filter(object_type=ds_ct, object_id=datasource.pk).count(), 100)

        datasource.delete()

        self.assertFalse(DataSource.objects.filter(pk=datasource.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=ds_ct, object_id=datasource.pk).count(), 0)

    def test_soft_delete_preserves_jobs(self):
        _, script = self._create_script()
        self._add_jobs(script, 10)

        script.delete(soft_delete=True)

        script.refresh_from_db()
        self.assertFalse(script.is_executable)
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 10)

    @override_settings(PROTECTION_RULES={'extras.script': [CustomValidator({'name': {'eq': ''}})]})
    def test_delete_rolls_back_jobs_on_parent_failure(self):
        # A protection rule that no real script can satisfy (name must be empty) makes the
        # cascade's pre_delete handler raise AbortRequest *after* JobsMixin.delete has already
        # batch-deleted the jobs. JobsMixin.delete wraps the batch loop and super().delete() in a
        # transaction, so the job deletions must roll back, leaving no orphaned partial state.
        # This exercises the real deletion-abort path rather than mocking Django internals.
        _, script = self._create_script()
        self._add_jobs(script, 10)

        with self.assertRaises(AbortRequest):
            script.delete()

        self.assertTrue(Script.objects.filter(pk=script.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 10)

    @override_settings(PROTECTION_RULES={'extras.script': [CustomValidator({'name': {'eq': ''}})]})
    def test_delete_scriptmodule_rolls_back_child_jobs_on_failure(self):
        # Same abort path via the module: the protection rule fires when the cascade pre_deletes
        # the child Script, after ScriptModule.delete has already batch-deleted that script's jobs.
        # The transaction must roll those job deletions back, leaving no orphaned partial state.
        module, script = self._create_script()
        self._add_jobs(script, 10)

        with self.assertRaises(AbortRequest):
            module.delete()

        self.assertTrue(ScriptModule.objects.filter(pk=module.pk).exists())
        self.assertTrue(Script.objects.filter(pk=script.pk).exists())
        self.assertEqual(Job.objects.filter(object_type=self.script_ct, object_id=script.pk).count(), 10)


class ConfirmCollectorTestCase(TestCase):
    """
    #22812: the delete-confirmation page must not materialize every dependent Job.
    """
    def _create_script_with_jobs(self, count):
        module = ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path=f'test_{uuid.uuid4().hex[:8]}.py',
        )
        script = Script.objects.create(module=module, name=f'S{uuid.uuid4().hex[:8]}')
        ct = ContentType.objects.get_for_model(Script, for_concrete_model=False)
        Job.objects.bulk_create([
            Job(object_type=ct, object_id=script.pk, name='j', status=JobStatusChoices.STATUS_COMPLETED,
                job_id=uuid.uuid4(), data={'output': 'x' * 50})
            for _ in range(count)
        ])
        return script

    def test_confirm_collector_counts_jobs_without_instantiating(self):
        script = self._create_script_with_jobs(500)

        init_calls = []
        original_init = Job.__init__

        def counting_init(self, *args, **kwargs):
            init_calls.append(1)
            original_init(self, *args, **kwargs)

        with mock.patch.object(Job, '__init__', counting_init):
            collector = ConfirmCollector(using=router.db_for_write(Script))
            collector.collect([script])

        # No Job rows were instantiated; the relation was counted instead.
        self.assertEqual(len(init_calls), 0)
        self.assertNotIn(Job, collector.data)
        self.assertEqual(collector.generic_relation_counts.get(Job), 500)
        # The non-job cascade (the Script itself) is still collected.
        self.assertIn(Script, collector.data)

    def test_count_only_wrapper(self):
        # CountOnly reports its count via len() but iterates empty, so it slots into the
        # dependent-objects mapping as a non-expandable, non-materializing row.
        wrapper = CountOnly(3000)
        self.assertEqual(len(wrapper), 3000)
        self.assertEqual(list(wrapper), [])
        self.assertTrue(wrapper.count_only)

    def test_confirm_collector_omits_jobs_when_none(self):
        # A jobless object must not record a zero count, or the confirmation page would show a
        # spurious "0 jobs" row (#22812 regression).
        datasource = DataSource.objects.create(name='DS', type='local', source_url='/tmp/test')

        collector = ConfirmCollector(using=router.db_for_write(DataSource))
        collector.collect([datasource])

        self.assertNotIn(Job, collector.generic_relation_counts)


class ObjectDeleteViewCountsTestCase(ViewTestCase):
    """
    #22812: the delete-confirmation view must report a JobsMixin object's jobs as a count
    (via CountOnly) without materializing them, and _get_dependent_objects must keep returning
    a single dict.
    """
    def test_get_dependent_objects_returns_count_only_for_jobs(self):
        from netbox.views.generic.object_views import ObjectDeleteView

        module = ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path=f'test_{uuid.uuid4().hex[:8]}.py',
        )
        script = Script.objects.create(module=module, name=f'S{uuid.uuid4().hex[:8]}')
        ct = ContentType.objects.get_for_model(Script, for_concrete_model=False)
        Job.objects.bulk_create([
            Job(
                object_type=ct, object_id=script.pk, name='j',
                status=JobStatusChoices.STATUS_COMPLETED, job_id=uuid.uuid4(),
            )
            for _ in range(50)
        ])

        view = ObjectDeleteView()
        view.queryset = ScriptModule.objects.all()
        dependent_objects = view._get_dependent_objects(module)

        # Single dict returned (not a tuple); jobs represented as a CountOnly.
        self.assertIsInstance(dependent_objects, dict)
        self.assertIn(Job, dependent_objects)
        self.assertIsInstance(dependent_objects[Job], CountOnly)
        self.assertEqual(len(dependent_objects[Job]), 50)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_confirm_page_renders_job_count(self):
        module = ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path=f'test_{uuid.uuid4().hex[:8]}.py',
        )
        script = Script.objects.create(module=module, name=f'S{uuid.uuid4().hex[:8]}')
        ct = ContentType.objects.get_for_model(Script, for_concrete_model=False)
        Job.objects.bulk_create([
            Job(
                object_type=ct, object_id=script.pk, name='j',
                status=JobStatusChoices.STATUS_COMPLETED, job_id=uuid.uuid4(),
            )
            for _ in range(50)
        ])

        # ScriptModule is a proxy over core.ManagedFile, so the delete view requires the
        # concrete model's permission (core.delete_managedfile), not extras.delete_scriptmodule.
        self.add_permissions('core.delete_managedfile')
        url = reverse('extras:scriptmodule_delete', kwargs={'pk': module.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Assert on the rendered context, not brittle HTML substrings: Job is present in
        # dependent_objects as a CountOnly reporting the true count, so the confirmation page
        # renders it as a summarized (non-expandable) row without materializing 50 Job rows.
        dependent_objects = response.context['dependent_objects']
        self.assertIn(Job, dependent_objects)
        self.assertIsInstance(dependent_objects[Job], CountOnly)
        self.assertEqual(len(dependent_objects[Job]), 50)
        self.assertTrue(dependent_objects[Job].count_only)

    def test_get_dependent_objects_omits_jobs_when_none(self):
        from netbox.views.generic.object_views import ObjectDeleteView

        # A module with no jobs must not produce a CountOnly(0) entry (#22812 regression).
        module = ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path=f'test_{uuid.uuid4().hex[:8]}.py',
        )

        view = ObjectDeleteView()
        view.queryset = ScriptModule.objects.all()
        dependent_objects = view._get_dependent_objects(module)

        self.assertNotIn(Job, dependent_objects)
