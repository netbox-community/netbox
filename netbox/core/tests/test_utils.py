from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import reverse

from core.models import DataSource, Job, ObjectType
from core.utils import register_job_result_url
from dcim.models import Site
from netbox.registry import registry


class JobResultURLTestCase(TestCase):

    def setUp(self):
        patcher = patch.dict(registry, {'job_result_urls': {}})
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def get_job(model=None, name='Test Job'):
        object_type = ObjectType.objects.get_for_model(model) if model else None
        return Job(pk=123, name=name, object_type=object_type, object_id=1 if model else None)

    def test_register_job_result_url(self):
        def func(job):
            return None

        self.assertIs(register_job_result_url(DataSource)(func), func)
        self.assertIs(register_job_result_url(DataSource, job_name='Sync')(func), func)
        self.assertEqual(registry['job_result_urls'], {
            ('core.datasource', None): func,
            ('core.datasource', 'Sync'): func,
        })

    def test_register_duplicate(self):
        register_job_result_url(DataSource, job_name='Sync')(lambda job: None)
        with self.assertRaises(ImproperlyConfigured):
            register_job_result_url(DataSource, job_name='Sync')(lambda job: None)

    def test_no_object(self):
        register_job_result_url(DataSource)(lambda job: '/foo/')

        self.assertEqual(self.get_job().get_absolute_url(), reverse('core:job', args=[123]))

    def test_no_registration_for_model(self):
        register_job_result_url(DataSource)(lambda job: '/foo/')

        self.assertEqual(self.get_job(Site).get_absolute_url(), reverse('core:job', args=[123]))

    def test_model(self):
        register_job_result_url(DataSource)(lambda job: f'/foo/{job.object_id}/')

        self.assertEqual(self.get_job(DataSource).get_absolute_url(), '/foo/1/')

    def test_job_name_takes_precedence(self):
        register_job_result_url(DataSource)(lambda job: '/foo/')
        register_job_result_url(DataSource, job_name='Sync')(lambda job: '/bar/')

        self.assertEqual(self.get_job(DataSource, name='Sync').get_absolute_url(), '/bar/')
        self.assertEqual(self.get_job(DataSource, name='Other').get_absolute_url(), '/foo/')

    def test_declined(self):
        register_job_result_url(DataSource, job_name='Sync')(lambda job: None)

        self.assertEqual(self.get_job(DataSource, name='Sync').get_absolute_url(), reverse('core:job', args=[123]))

        # Declining defers to the function registered for the model alone
        register_job_result_url(DataSource)(lambda job: '/foo/')
        self.assertEqual(self.get_job(DataSource, name='Sync').get_absolute_url(), '/foo/')

    def test_exception(self):
        @register_job_result_url(DataSource)
        def func(job):
            return reverse('plugins:invalid')

        with self.assertLogs('netbox.jobs', level='ERROR'):
            self.assertEqual(self.get_job(DataSource).get_absolute_url(), reverse('core:job', args=[123]))

    def test_unresolvable_model(self):
        register_job_result_url(DataSource)(lambda job: '/foo/')

        # e.g. a model belonging to a plugin which has been uninstalled
        object_type = ContentType.objects.create(app_label='uninstalled_plugin', model='foo')
        job = Job(pk=123, name='Test Job', object_type=object_type, object_id=1)

        self.assertEqual(job.get_absolute_url(), reverse('core:job', args=[123]))
