"""
Tests for optional background processing of REST API bulk write operations (#21992).

These exercise the ?background=true path: a bulk create/update/delete returns 202 with a
job reference, the AsyncAPIJob performs the work, and the result is recorded on the job.

To run without a live RQ worker, setUp() (a) patches AsyncAPIJob.enqueue to run the job
inline (immediate=True) and (b) reports a worker as available for the worker-liveness guard.
Individual tests that exercise those guards override this locally.
"""
import uuid
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from core.models import Job, ObjectChange
from dcim.models import DeviceType, Manufacturer, Region
from users.models import ObjectPermission
from utilities.testing.api import APITestCase
from utilities.testing.mixins import RQQueueTestMixin


class BackgroundBulkWriteTests(RQQueueTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regions = [
            Region.objects.create(name=f'Region {i}', slug=f'region-{i}')
            for i in range(1, 4)
        ]

    def setUp(self):
        super().setUp()

        # Run enqueued jobs inline (immediate=True) so they execute within the test.
        import netbox.jobs as jobs_module
        self._orig_enqueue = jobs_module.AsyncAPIJob.enqueue.__func__

        def _immediate_enqueue(cls, *args, **kwargs):
            kwargs.setdefault('immediate', True)
            return self._orig_enqueue(cls, *args, **kwargs)

        jobs_module.AsyncAPIJob.enqueue = classmethod(_immediate_enqueue)
        self.addCleanup(
            setattr, jobs_module.AsyncAPIJob, 'enqueue', classmethod(self._orig_enqueue)
        )

        # Report a worker as available so _enqueue_bulk_job's liveness guard passes.
        worker_patcher = patch(
            'netbox.api.viewsets.mixins.any_workers_for_queue', return_value=True
        )
        worker_patcher.start()
        self.addCleanup(worker_patcher.stop)

    def grant(self, *actions, constraints=None):
        perm = ObjectPermission.objects.create(
            name='Test permission', actions=list(actions), constraints=constraints
        )
        perm.users.add(self.user)
        perm.object_types.add(ContentType.objects.get_for_model(Region))

    def _ct(self):
        return ContentType.objects.get_for_model(Region)

    def _assert_job_link(self, response):
        """Assert the 202 body + Location header reference the same job detail URL."""
        job_block = response.data['job']
        self.assertEqual(response['Location'], job_block['url'])
        self.assertTrue(
            job_block['url'].endswith(f"/api/core/jobs/{job_block['id']}/"),
            job_block['url'],
        )

    # ------------------------------------------------------------------ create

    def test_background_bulk_create(self):
        self.grant('add', 'view')
        payload = [
            {'name': 'Region A', 'slug': 'region-a'},
            {'name': 'Region B', 'slug': 'region-b'},
        ]
        response = self.client.post(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self._assert_job_link(response)

        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertTrue(Region.objects.filter(slug='region-a').exists())
        self.assertTrue(Region.objects.filter(slug='region-b').exists())
        # Result captured on the job.
        self.assertEqual(job.data['status_code'], status.HTTP_201_CREATED)
        self.assertEqual(len(job.data['data']), 2)
        # URLs in the captured result are absolute and derived from the request host
        # (the worker carries the request's scheme/host forward), not hardcoded localhost.
        for obj in job.data['data']:
            self.assertTrue(obj['url'].startswith('http://testserver/'), obj['url'])

    # ------------------------------------------------------------------ update

    def test_background_bulk_update_patch(self):
        self.grant('change', 'view')
        payload = [{'id': r.pk, 'description': 'bg'} for r in self.regions]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self._assert_job_link(response)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(job.data['status_code'], status.HTTP_200_OK)
        for r in Region.objects.filter(pk__in=[x.pk for x in self.regions]):
            self.assertEqual(r.description, 'bg')

    def test_background_bulk_update_put(self):
        # PUT (full, partial=False) bulk update must enqueue and persist like PATCH. Region
        # only requires name + slug, so a full representation is straightforward.
        self.grant('change', 'view')
        payload = [
            {'id': r.pk, 'name': r.name, 'slug': r.slug, 'description': 'put-bg'}
            for r in self.regions
        ]
        response = self.client.put(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        for r in Region.objects.filter(pk__in=[x.pk for x in self.regions]):
            self.assertEqual(r.description, 'put-bg')

    def test_background_bulk_update_object_permission_subset(self):
        # Constrained to Region 1 only; bulk update of all three should update only the
        # permitted subset and SUCCEED (matching synchronous behavior; no rollback).
        self.grant('change', 'view', constraints={'name': 'Region 1'})
        payload = [{'id': r.pk, 'description': 'subset'} for r in self.regions]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        # DB side effect AND captured result reflect the permitted subset only.
        self.assertEqual(Region.objects.filter(description='subset').count(), 1)
        self.assertEqual(job.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(len(job.data['data']), 1)

    def test_background_bulk_update_all_or_nothing(self):
        self.grant('change', 'view')
        payload = [
            {'id': self.regions[0].pk, 'description': 'ok'},
            {'id': self.regions[1].pk, 'slug': ''},  # invalid: blank slug
        ]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_FAILED)
        # The failure detail (a 400 validation error) is captured in job.data + job.error.
        self.assertEqual(job.data['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertTrue(job.error)
        # Neither item persisted (whole batch rolled back).
        self.regions[0].refresh_from_db()
        self.assertNotEqual(self.regions[0].description, 'ok')

    # ------------------------------------------------------------------ delete

    def test_background_bulk_delete(self):
        self.grant('delete', 'view')
        payload = [{'id': r.pk} for r in self.regions]
        response = self.client.delete(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(job.data['status_code'], status.HTTP_204_NO_CONTENT)
        self.assertFalse(Region.objects.filter(pk__in=[r.pk for r in self.regions]).exists())

    def test_background_bulk_delete_protected_dependent(self):
        # A protected dependency makes the delete fail. The worker must capture this as the
        # same 409 the synchronous API returns (via exception_to_response), terminating the
        # job as "failed" with the dependent listed, NOT as an unexpected "errored" job.
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')

        perm = ObjectPermission.objects.create(name='Delete manufacturers', actions=['delete'])
        perm.users.add(self.user)
        perm.object_types.add(ContentType.objects.get_for_model(Manufacturer))

        response = self.client.delete(
            '/api/dcim/manufacturers/?background=true',
            [{'id': manufacturer.pk}], format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_FAILED)
        self.assertEqual(job.data['status_code'], status.HTTP_409_CONFLICT)
        # The protected object was not deleted.
        self.assertTrue(Manufacturer.objects.filter(pk=manufacturer.pk).exists())

    # ------------------------------------------------------------------ contract guards

    def test_synchronous_rejection_no_job(self):
        # Malformed payload (missing required id) must 400 synchronously, with no Job created.
        self.grant('change', 'view')
        response = self.client.patch(
            '/api/dcim/regions/?background=true',
            [{'description': 'no id'}],
            format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Job.objects.count(), 0)

    def test_if_match_with_background_rejected(self):
        self.grant('change', 'view')
        payload = [{'id': self.regions[0].pk, 'description': 'x'}]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json',
            HTTP_IF_MATCH='W/"whatever"', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Job.objects.count(), 0)

    def test_no_worker_returns_503_no_job(self):
        # When no worker is servicing the queue, the request is refused (no silent 202).
        self.grant('change', 'view')
        payload = [{'id': self.regions[0].pk, 'description': 'x'}]
        with patch('netbox.api.viewsets.mixins.any_workers_for_queue', return_value=False):
            response = self.client.patch(
                '/api/dcim/regions/?background=true', payload, format='json', **self.header
            )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(Job.objects.count(), 0)

    def test_get_with_background_is_ignored(self):
        self.grant('view')
        response = self.client.get('/api/dcim/regions/?background=true', **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Job.objects.count(), 0)

    def test_single_object_create_not_backgrounded(self):
        # A single-object (non-list) create with ?background=true runs synchronously (201).
        self.grant('add', 'view')
        response = self.client.post(
            '/api/dcim/regions/?background=true',
            {'name': 'Solo', 'slug': 'solo'},
            format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 0)

    # ------------------------------------------------------------------ enqueue scheduling

    def test_non_immediate_enqueue_creates_pending_job(self):
        # Without the immediate=True shortcut, enqueue must schedule a pending job (and not
        # execute inline). This confirms the real transaction.on_commit scheduling path.
        self.grant('change', 'view')
        import netbox.jobs as jobs_module
        # Restore the un-patched enqueue for this test only.
        jobs_module.AsyncAPIJob.enqueue = classmethod(self._orig_enqueue)

        payload = [{'id': self.regions[0].pk, 'description': 'queued'}]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        job = Job.objects.get(pk=response.data['job']['id'])
        self.assertEqual(job.status, JobStatusChoices.STATUS_PENDING)
        # The write has NOT happened yet (job is only queued).
        self.regions[0].refresh_from_db()
        self.assertNotEqual(self.regions[0].description, 'queued')

    # ------------------------------------------------------------------ error terminal states

    def test_inactive_user_fails_job(self):
        # Models the real timing the worker guards against: the request was accepted (the
        # user was active at enqueue), but the user is deactivated before the worker runs.
        # We drive AsyncAPIJob directly because the HTTP layer would otherwise reject an
        # inactive user's token at authentication time, never reaching the worker.
        from netbox.jobs import AsyncAPIJob

        self.grant('change', 'view')
        self.user.is_active = False
        self.user.save()

        job = Job.objects.create(name='Bulk update regions', user=self.user, job_id=uuid.uuid4())
        with self.assertRaises(JobFailed):
            AsyncAPIJob(job).run(
                viewset_class='dcim.api.views.RegionViewSet',
                action='bulk_update',
                payload=[{'id': self.regions[0].pk, 'description': 'x'}],
                user_pk=self.user.pk,
                request_id='',
                method='PATCH',
                action_kwargs={'partial': True},
            )
        job.refresh_from_db()
        self.assertIn('active', job.error.lower())
        self.regions[0].refresh_from_db()
        self.assertNotEqual(self.regions[0].description, 'x')

    # ------------------------------------------------------------------ host parsing

    def test_ipv6_host_builds_correct_request(self):
        # A bracketed IPv6 host:port must not be split on its inner colons. Assert directly on
        # the request the worker reconstructs: get_host() must round-trip the bracketed host,
        # and SERVER_NAME/SERVER_PORT must be the IPv6 literal and port (a host.partition(':')
        # implementation would yield SERVER_NAME='[' here).
        from netbox.jobs import AsyncAPIJob

        request = AsyncAPIJob._build_request(
            payload=[], method='PATCH', request_id=str(uuid.uuid4()),
            scheme='https', host='[::1]:8443',
        )
        self.assertEqual(request.get_host(), '[::1]:8443')
        self.assertEqual(request.META['SERVER_NAME'], '::1')
        self.assertEqual(request.META['SERVER_PORT'], '8443')
        self.assertEqual(request.scheme, 'https')

    # ------------------------------------------------------------------ change logging

    def test_background_update_changelog_fidelity(self):
        self.grant('change', 'view')
        payload = [{'id': r.pk, 'description': 'logged'} for r in self.regions]
        response = self.client.patch(
            '/api/dcim/regions/?background=true', payload, format='json', **self.header
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        request_id = response['X-Request-ID']

        changes = ObjectChange.objects.filter(changed_object_type=self._ct())
        self.assertEqual(changes.count(), 3)
        self.assertTrue(all(c.user_id == self.user.pk for c in changes))
        # The original request UUID is propagated to the worker so change records group correctly.
        self.assertTrue(all(str(c.request_id) == request_id for c in changes))
