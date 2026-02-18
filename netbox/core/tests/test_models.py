from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from core.choices import ObjectChangeActionChoices
from core.models import DataSource, Job, ObjectType
from dcim.models import Device, Location, Site
from netbox.constants import CENSOR_TOKEN, CENSOR_TOKEN_CHANGED


class DataSourceChangeLoggingTestCase(TestCase):

    def test_password_added_on_create(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'foobar123',
            }
        )

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_CREATE)
        self.assertIsNone(objectchange.prechange_data)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_added_on_update(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/'
        )
        datasource.snapshot()

        # Add a blank password
        datasource.parameters = {
            'username': 'jeff',
            'password': '',
        }

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertIsNone(objectchange.prechange_data['parameters'])
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], '')

        # Add a password
        datasource.parameters = {
            'username': 'jeff',
            'password': 'foobar123',
        }

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_changed(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'password1',
            }
        )
        datasource.snapshot()

        # Change the password
        datasource.parameters['password'] = 'password2'

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_removed_on_update(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'foobar123',
            }
        )
        datasource.snapshot()

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN)

        # Remove the password
        datasource.parameters['password'] = ''

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], '')

    def test_password_not_modified(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'username1',
                'password': 'foobar123',
            }
        )
        datasource.snapshot()

        # Remove the password
        datasource.parameters['username'] = 'username2'

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'username1')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'username2')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN)


class ObjectTypeTest(TestCase):

    def test_create(self):
        """
        Test that an ObjectType created for a given app_label & model name will be automatically assigned to
        the appropriate ContentType.
        """
        kwargs = {
            'app_label': 'foo',
            'model': 'bar',
        }
        ct = ContentType.objects.create(**kwargs)
        ot = ObjectType.objects.create(**kwargs)
        self.assertEqual(ot.contenttype_ptr, ct)

    def test_get_by_natural_key(self):
        """
        Test that get_by_natural_key() returns the appropriate ObjectType.
        """
        self.assertEqual(
            ObjectType.objects.get_by_natural_key('dcim', 'site'),
            ObjectType.objects.get(app_label='dcim', model='site')
        )
        with self.assertRaises(ObjectDoesNotExist):
            ObjectType.objects.get_by_natural_key('foo', 'bar')

    def test_get_for_id(self):
        """
        Test that get_by_id() returns the appropriate ObjectType.
        """
        ot = ObjectType.objects.get_by_natural_key('dcim', 'site')
        self.assertEqual(
            ObjectType.objects.get_for_id(ot.pk),
            ObjectType.objects.get(pk=ot.pk)
        )
        with self.assertRaises(ObjectDoesNotExist):
            ObjectType.objects.get_for_id(0)

    def test_get_for_model(self):
        """
        Test that get_by_model() returns the appropriate ObjectType.
        """
        self.assertEqual(
            ObjectType.objects.get_for_model(Site),
            ObjectType.objects.get_by_natural_key('dcim', 'site')
        )

    def test_get_for_models(self):
        """
        Test that get_by_models() returns the appropriate ObjectType mapping.
        """
        self.assertEqual(
            ObjectType.objects.get_for_models(Site, Location, Device),
            {
                Site: ObjectType.objects.get_by_natural_key('dcim', 'site'),
                Location: ObjectType.objects.get_by_natural_key('dcim', 'location'),
                Device: ObjectType.objects.get_by_natural_key('dcim', 'device'),
            }
        )

    def test_public(self):
        """
        Test that public() returns only ObjectTypes for public models.
        """
        public_ots = ObjectType.objects.public()
        self.assertIn(ObjectType.objects.get_by_natural_key('dcim', 'site'), public_ots)
        self.assertNotIn(ObjectType.objects.get_by_natural_key('extras', 'taggeditem'), public_ots)

    def test_with_feature(self):
        """
        Test that with_feature() returns only ObjectTypes for models which support the specified feature.
        """
        bookmarks_ots = ObjectType.objects.with_feature('bookmarks')
        self.assertIn(ObjectType.objects.get_by_natural_key('dcim', 'site'), bookmarks_ots)
        self.assertNotIn(ObjectType.objects.get_by_natural_key('dcim', 'cabletermination'), bookmarks_ots)


class JobTest(TestCase):

    @patch('core.models.jobs.django_rq.get_queue')
    def test_delete_cancels_job_from_correct_queue(self, mock_get_queue):
        """
        Test that when a job is deleted, it's canceled from the correct queue.
        """
        mock_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_queue.fetch_job.return_value = mock_rq_job
        mock_get_queue.return_value = mock_queue

        def dummy_func(**kwargs):
            pass

        # Enqueue a job with a custom queue name
        custom_queue = 'my_custom_queue'
        job = Job.enqueue(
            func=dummy_func,
            name='Test Job',
            queue_name=custom_queue
        )

        # Reset mock to clear enqueue call
        mock_get_queue.reset_mock()

        # Delete the job
        job.delete()

        # Verify the correct queue was used for cancellation
        mock_get_queue.assert_called_with(custom_queue)
        mock_queue.fetch_job.assert_called_with(str(job.job_id))
        mock_rq_job.cancel.assert_called_once()
