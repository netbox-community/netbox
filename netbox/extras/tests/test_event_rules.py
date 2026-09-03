import json
import logging
import uuid
from io import BytesIO
from unittest import skipIf
from unittest.mock import Mock, PropertyMock, patch

import django_rq
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings, tag
from django.urls import reverse
from PIL import Image
from requests import Session
from rest_framework import status

from core.choices import JobNotificationChoices, ManagedFileRootPathChoices
from core.events import *
from core.models import Job, ObjectType
from dcim.choices import DeviceStatusChoices, InterfaceTypeChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from extras.choices import EventRuleActionChoices
from extras.events import enqueue_event, flush_events, process_event_rules, serialize_for_event
from extras.models import EventRule, Notification, Script, ScriptModule, Tag, Webhook
from extras.scripts import Script as ScriptBase
from extras.signals import process_job_end_event_rules
from extras.webhooks import generate_signature, send_webhook
from ipam.choices import IPAddressStatusChoices
from ipam.models import IPAddress, Prefix
from netbox.context_managers import event_tracking
from netbox.event_rules import (
    EventRuleAction,
    get_event_rule_action,
    get_event_rule_action_choices,
    register_event_rule_action,
)
from netbox.registry import registry
from netbox.tests.dummy_plugin.event_rules import DummyRaisingAction
from users.models import ObjectPermission
from utilities.testing import APITestCase, create_test_device, disable_warnings
from utilities.testing.mixins import RQQueueTestMixin


class EventRuleTestCase(RQQueueTestMixin, APITestCase):

    def setUp(self):
        super().setUp()

        # Ensure the queue has been cleared for each test
        self.queue = django_rq.get_queue('default')
        self.queue.empty()

    def tearDown(self):
        super().tearDown()

        # Clear the queue so leftover jobs do not leak to the next test suite
        self.queue.empty()

    def test_enqueue_event_requires_saved_instance(self):
        """enqueue_event raises ValueError for an unsaved instance."""
        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        site = Site(name='Site 1', slug='site-1')
        with patch('extras.events.has_feature', return_value=True):
            with self.assertRaises(ValueError):
                enqueue_event({}, site, request, OBJECT_CREATED)

    @classmethod
    def setUpTestData(cls):

        site_type = ObjectType.objects.get_for_model(Site)
        DUMMY_URL = 'http://localhost:9000/'
        DUMMY_SECRET = 'LOOKATMEIMASECRETSTRING'

        webhooks = Webhook.objects.bulk_create((
            Webhook(name='Webhook 1', payload_url=DUMMY_URL, secret=DUMMY_SECRET, additional_headers='X-Foo: Bar'),
            Webhook(name='Webhook 2', payload_url=DUMMY_URL, secret=DUMMY_SECRET),
            Webhook(name='Webhook 3', payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        ))

        webhook_type = ObjectType.objects.get(app_label='extras', model='webhook')
        event_rules = EventRule.objects.bulk_create((
            EventRule(
                name='Event Rule 1',
                event_types=[OBJECT_CREATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 1},
            ),
            EventRule(
                name='Event Rule 2',
                event_types=[OBJECT_UPDATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 2},
            ),
            EventRule(
                name='Event Rule 3',
                event_types=[OBJECT_DELETED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 3},
            ),
        ))
        for event_rule in event_rules:
            event_rule.object_types.set([site_type])

        Tag.objects.bulk_create((
            Tag(name='Foo', slug='foo'),
            Tag(name='Bar', slug='bar'),
            Tag(name='Baz', slug='baz'),
        ))

    def test_eventrule_snapshot_changed_condition(self):
        """
        An event rule using the 'changed' operator fires only when the attribute
        transitions to the target value, not on subsequent updates that leave it
        unchanged.  Exercises the full process_event_rules() path.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        site_type = ObjectType.objects.get_for_model(Site)
        event_rule = EventRule.objects.create(
            name='Status Change Rule',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
            conditions={
                'and': [
                    {'attr': 'status.value', 'value': SiteStatusChoices.STATUS_ACTIVE},
                    {'attr': 'status', 'op': 'changed'},
                ]
            }
        )
        event_rule.object_types.set([site_type])

        site = Site.objects.create(name='Site Snapshot', slug='site-snapshot', status=SiteStatusChoices.STATUS_PLANNED)
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site')

        # planned → active: the 'changed' condition is satisfied; rule must fire
        response = self.client.patch(url, {'status': SiteStatusChoices.STATUS_ACTIVE}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == event_rule]
        self.assertEqual(len(rule_jobs), 1, 'Expected rule to fire on status transition to active')
        self.queue.empty()

        # description update while status stays active: 'changed' condition fails; rule must not fire
        response = self.client.patch(url, {'description': 'Updated'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == event_rule]
        self.assertEqual(len(rule_jobs), 0, 'Expected rule not to fire when status is unchanged')

    def test_eventrule_conditions(self):
        """
        Test evaluation of EventRule conditions.
        """
        event_rule = EventRule(
            name='Event Rule 1',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                'and': [
                    {
                        'attr': 'status.value',
                        'value': 'active',
                    }
                ]
            }
        )

        # Create a Site to evaluate
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_STAGING)
        data = serialize_for_event(site)

        # Evaluate the conditions (status='staging')
        self.assertFalse(event_rule.eval_conditions(data))

        # Change the site's status
        site.status = SiteStatusChoices.STATUS_ACTIVE
        data = serialize_for_event(site)

        # Evaluate the conditions (status='active')
        self.assertTrue(event_rule.eval_conditions(data))

    def test_single_create_process_eventrule(self):
        """
        Check that creating an object with an applicable EventRule queues a background task for the rule's action.
        """
        # Create an object via the REST API
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'tags': [
                {'name': 'Foo'},
                {'name': 'Bar'},
            ]
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site', 'extras.view_tag')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for the new object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
        self.assertEqual(job.kwargs['data']['id'], response.data['id'])
        self.assertEqual(job.kwargs['data']['foo'], 1)
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['snapshots']['postchange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Bar', 'Foo'])

    def test_single_create_rollback_discards_events(self):
        """
        Check that creating an object which is then rolled back by the object-level permission check
        in perform_create() queues no background task.
        """
        # Permit the creation of active sites only. The new object is saved (queueing its event)
        # before _validate_objects() rejects it and the transaction is rolled back.
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add'],
            constraints={'status': SiteStatusChoices.STATUS_ACTIVE},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Site))

        data = {'name': 'Site 1', 'slug': 'site-1', 'status': SiteStatusChoices.STATUS_PLANNED}
        url = reverse('dcim-api:site-list')
        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Site.objects.count(), 0)

        # No task may be queued for a creation that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_bulk_create_process_eventrule(self):
        """
        Check that bulk creating multiple objects with an applicable EventRule queues a background task for each
        new object.
        """
        # Create multiple objects via the REST API
        data = [
            {
                'name': 'Site 1',
                'slug': 'site-1',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
            {
                'name': 'Site 2',
                'slug': 'site-2',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
            {
                'name': 'Site 3',
                'slug': 'site-3',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site', 'extras.view_tag')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 3)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for each new object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
            self.assertEqual(job.kwargs['data']['id'], response.data[i]['id'])
            self.assertEqual(job.kwargs['data']['foo'], 1)
            self.assertEqual(len(job.kwargs['data']['tags']), len(response.data[i]['tags']))
            self.assertEqual(job.kwargs['snapshots']['postchange']['name'], response.data[i]['name'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Bar', 'Foo'])

    def test_bulk_create_rollback_discards_events(self):
        """
        Check that a sequential bulk create which is rolled back queues no background tasks for the
        objects that were provisionally created before the failure.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        site = Site.objects.create(name='Site 1', slug='site-1')

        # Bulk creates are performed one object at a time, so each valid object is provisionally
        # created (and its event queued) before a later object fails validation.
        event_rule = EventRule.objects.get(name='Event Rule 1')
        event_rule.object_types.set([ObjectType.objects.get_for_model(Device)])

        data = [
            {
                'name': 'Device 1',
                'device_type': device_type.pk,
                'role': role.pk,
                'site': site.pk,
                'status': DeviceStatusChoices.STATUS_ACTIVE,
            },
            {},  # Missing all required fields
        ]
        url = reverse('dcim-api:device-list')
        self.add_permissions('dcim.add_device', 'dcim.view_site', 'dcim.view_devicetype', 'dcim.view_devicerole')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Device.objects.count(), 0)

        # No task may be queued for a creation that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_available_objects_create_rollback_discards_events(self):
        """
        Check that creating an object via an available-objects endpoint (e.g. available-ips) queues
        no background task when the object-level permission check rolls the transaction back.
        """
        prefix = Prefix.objects.create(prefix='192.0.2.0/24')

        event_rule = EventRule.objects.get(name='Event Rule 1')
        event_rule.object_types.set([ObjectType.objects.get_for_model(IPAddress)])

        # Permit the creation of active IP addresses only. The new object is saved (queueing its
        # event) before _validate_objects() rejects it and the transaction is rolled back.
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add'],
            constraints={'status': IPAddressStatusChoices.STATUS_ACTIVE},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))
        self.add_permissions('ipam.view_prefix')

        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})
        data = {'status': IPAddressStatusChoices.STATUS_RESERVED}
        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(IPAddress.objects.count(), 0)

        # No task may be queued for a creation that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_single_update_process_eventrule(self):
        """
        Check that updating an object with an applicable EventRule queues a background task for the rule's action.
        """
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Update an object via the REST API
        data = {
            'name': 'Site X',
            'comments': 'Updated the site',
            'tags': [
                {'name': 'Baz'}
            ]
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site', 'extras.view_tag')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for the updated object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(job.kwargs['data']['foo'], 2)
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['snapshots']['prechange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])
        self.assertEqual(job.kwargs['snapshots']['postchange']['name'], 'Site X')
        self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Baz'])

    def test_single_update_rollback_discards_events(self):
        """
        Check that updating an object which is then rolled back by the object-level permission check
        in perform_update() queues no background task.
        """
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE)

        # Permit the modification of active sites only. Setting the status to "planned" takes the
        # object outside the permission's scope, so it is saved (queueing its event) and then
        # rejected by _validate_objects(), rolling the transaction back.
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['change'],
            constraints={'status': SiteStatusChoices.STATUS_ACTIVE},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Site))

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        with disable_warnings('django.request'):
            response = self.client.patch(
                url, {'status': SiteStatusChoices.STATUS_PLANNED}, format='json', **self.header
            )
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)
        site.refresh_from_db()
        self.assertEqual(site.status, SiteStatusChoices.STATUS_ACTIVE)

        # No task may be queued for an update that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_bulk_update_process_eventrule(self):
        """
        Check that bulk updating multiple objects with an applicable EventRule queues a background task for each
        updated object.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Update three objects via the REST API
        data = [
            {
                'id': sites[0].pk,
                'name': 'Site X',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
            {
                'id': sites[1].pk,
                'name': 'Site Y',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
            {
                'id': sites[2].pk,
                'name': 'Site Z',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.change_site', 'extras.view_tag')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for each updated object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
            self.assertEqual(job.kwargs['data']['id'], data[i]['id'])
            self.assertEqual(job.kwargs['data']['foo'], 2)
            self.assertEqual(len(job.kwargs['data']['tags']), len(response.data[i]['tags']))
            self.assertEqual(job.kwargs['snapshots']['prechange']['name'], sites[i].name)
            self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['name'], response.data[i]['name'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Baz'])

    def test_bulk_update_rollback_discards_events(self):
        """
        Check that a bulk update which is rolled back because one object failed validation queues no
        background tasks for the objects that were provisionally updated.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        # The first two objects are valid and will be provisionally updated; the third fails
        # validation, rolling the entire batch back.
        data = [
            {'id': sites[0].pk, 'name': 'Site X'},
            {'id': sites[1].pk, 'name': 'Site Y'},
            {'id': sites[2].pk, 'status': 'not-a-valid-status'},
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.change_site')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # No object may have been modified
        for site in sites:
            site.refresh_from_db()
        self.assertListEqual([site.name for site in sites], ['Site 1', 'Site 2', 'Site 3'])

        # No task may be queued for an update that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_single_delete_process_eventrule(self):
        """
        Check that deleting an object with an applicable EventRule queues a background task for the rule's action.
        """
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Delete an object via the REST API
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a task was queued for the deleted object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 3'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(job.kwargs['data']['foo'], 3)
        self.assertEqual(job.kwargs['snapshots']['prechange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])

    def test_single_delete_rollback_discards_events(self):
        """
        Check that deleting an object whose cascading deletion is aborted queues no background task
        for the dependent objects that were already processed.
        """
        device = create_test_device('Device 1')
        Interface.objects.create(
            device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED, description='Has one'
        )
        Interface.objects.create(device=device, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED)

        event_rule = EventRule.objects.get(name='Event Rule 3')
        event_rule.object_types.set([ObjectType.objects.get_for_model(Interface)])

        url = reverse('dcim-api:device-detail', kwargs={'pk': device.pk})
        self.add_permissions('dcim.delete_device')

        # Deleting the Device cascades to both Interfaces. The first satisfies the protection rule
        # and so is processed (queueing its event); the second does not, aborting the request.
        protection_rules = {'dcim.interface': [{'description': {'required': True}}]}
        with override_settings(PROTECTION_RULES=protection_rules):
            response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Device.objects.filter(pk=device.pk).exists())
        self.assertEqual(Interface.objects.filter(device=device).count(), 2)

        # No task may be queued for a deletion that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_bulk_delete_process_eventrule(self):
        """
        Check that bulk deleting multiple objects with an applicable EventRule queues a background task for each
        deleted object.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Delete three objects via the REST API
        data = [
            {'id': site.pk} for site in sites
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a background task was queued for each deleted object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 3'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
            self.assertEqual(job.kwargs['data']['id'], sites[i].pk)
            self.assertEqual(job.kwargs['data']['foo'], 3)
            self.assertEqual(job.kwargs['snapshots']['prechange']['name'], sites[i].name)
            self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])

    def test_bulk_delete_rollback_discards_events(self):
        """
        Check that a bulk delete which is rolled back because one object is protected queues no
        background tasks for the objects that were provisionally deleted.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        # A Device references the third Site, whose deletion will therefore raise a ProtectedError
        # and roll the entire batch back.
        create_test_device('Device 1', site=sites[2])

        data = [{'id': site.pk} for site in sites]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_409_CONFLICT)
        self.assertEqual(Site.objects.count(), 3)

        # No task may be queued for a deletion that was rolled back
        self.assertEqual(self.queue.count, 0)

    def test_bulk_delete_abort_discards_events(self):
        """
        Check that a bulk delete blocked by a signal receiver raising AbortRequest (rather than by a
        database constraint) also queues no background tasks for the objects that were provisionally
        deleted before the failure.
        """
        sites = (
            Site(name='Site 1', slug='site-1', description='Has a description'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        data = [{'id': site.pk} for site in sites]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.delete_site')

        # Site 2 has no description, so its deletion is blocked once Site 1 has already been deleted
        protection_rules = {'dcim.site': [{'description': {'required': True}}]}
        with override_settings(PROTECTION_RULES=protection_rules):
            response = self.client.delete(url, data, format='json', **self.header)
        # 400 rather than 409: a protection rule rejects the request, it is not a conflict with a
        # dependent object (see BulkDestroyModelMixin.bulk_destroy)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Site.objects.count(), 2)

        # The failure is correlated to the blocked object only
        self.assertEqual([e['id'] for e in response.data['errors']], [sites[1].pk])

        # No task may be queued for a deletion that was rolled back
        self.assertEqual(self.queue.count, 0)

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_send_webhook(self):
        request_id = uuid.uuid4()
        url_path = reverse('dcim:site_add')

        def dummy_send(_, request, **kwargs):
            """
            A dummy implementation of Session.send() to be used for testing.
            Always returns a 200 HTTP response.
            """
            event = EventRule.objects.get(name='Event Rule 1')
            webhook = event.action_object
            signature = generate_signature(request.body, webhook.secret)

            # Validate the outgoing request headers
            self.assertEqual(request.headers['Content-Type'], webhook.http_content_type)
            self.assertEqual(request.headers['X-Hook-Signature'], signature)
            self.assertEqual(request.headers['X-Foo'], 'Bar')

            # The webhook does not define its own timeout, so the global default should be used
            self.assertEqual(kwargs['timeout'], settings.WEBHOOK_DEFAULT_TIMEOUT)

            # Validate the outgoing request body
            body = json.loads(request.body)
            self.assertEqual(body['event'], 'created')
            self.assertEqual(body['timestamp'], job.kwargs['timestamp'])
            self.assertEqual(body['object_type'], 'dcim.site')
            self.assertEqual(body['data']['name'], 'Site 1')
            self.assertEqual(body['data']['foo'], 1)
            self.assertEqual(body['context']['foo'], 123)  # From netbox.tests.dummy_plugin
            self.assertEqual(body['request']['id'], str(request_id))
            self.assertEqual(body['request']['method'], 'GET')
            self.assertEqual(body['request']['path'], url_path)
            self.assertEqual(body['request']['user'], 'testuser')

            return HttpResponse()

        # Create a dummy request
        request = RequestFactory().get(url_path)
        request.id = request_id
        request.user = self.user

        # Enqueue a webhook for processing
        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        # Retrieve the job from queue
        job = self.queue.jobs[0]

        # Patch the Session object with our dummy_send() method, then process the webhook for sending
        with patch.object(Session, 'send', dummy_send):
            send_webhook(**job.kwargs)

    def test_send_webhook_per_webhook_timeout(self):
        """
        A webhook which defines its own timeout should use that value in preference to the
        global WEBHOOK_DEFAULT_TIMEOUT.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook.timeout = 5
        webhook.save()

        def dummy_send(_, request, **kwargs):
            self.assertEqual(kwargs['timeout'], 5)
            return HttpResponse()

        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        job = self.queue.jobs[0]
        with patch.object(Session, 'send', dummy_send):
            send_webhook(**job.kwargs)

    @override_settings(RQ_DEFAULT_TIMEOUT=10)
    def test_send_webhook_timeout_exceeding_job_timeout_is_logged(self):
        """
        A timeout which meets or exceeds the background job timeout should be logged as a warning. This can
        occur when RQ_DEFAULT_TIMEOUT has been lowered after the webhook was saved, which Webhook.clean()
        cannot catch.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook.timeout = 30
        webhook.save()

        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        job = self.queue.jobs[0]
        with patch.object(Session, 'send', lambda _, request, **kwargs: HttpResponse()):
            with self.assertLogs('netbox.webhooks', level='WARNING') as cm:
                send_webhook(**job.kwargs)

        self.assertIn(
            'Webhook timeout (30 seconds) is not less than the background job timeout (10 seconds)',
            '\n'.join(cm.output)
        )

    def test_send_webhook_timeout_is_logged(self):
        """
        A request which times out should be logged as an error before the exception is re-raised, so that the
        failure is discoverable without resorting to the RQ worker's traceback.
        """
        def timing_out_send(_, request, **kwargs):
            raise requests.exceptions.ConnectTimeout('Connection timed out')

        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        job = self.queue.jobs[0]
        with patch.object(Session, 'send', timing_out_send):
            with self.assertLogs('netbox.webhooks', level='ERROR') as cm:
                with self.assertRaises(requests.exceptions.Timeout):
                    send_webhook(**job.kwargs)

        self.assertIn(f'timed out after {settings.WEBHOOK_DEFAULT_TIMEOUT} seconds', cm.output[0])

    def test_job_completed_webhook_without_request(self):
        """
        Ensure job_end event processing can enqueue a webhook even when the EventContext
        lacks a request context.

        The job_start/job_end signal receivers only populate `user` and `data`, so webhook
        processing must tolerate the absence of a request.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        webhook = Webhook.objects.get(name='Webhook 1')
        event_rule = EventRule.objects.create(
            name='Event Rule Job Completed',
            event_types=[JOB_COMPLETED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        event_rule.object_types.set([script_type])
        # Mimic the `core.job_end` signal sender expected by extras.signals.process_job_end_event_rules
        # (notably: no request, and thus no legacy `username`)
        sender = Mock(object_type=script_type, data={}, user=self.user)
        process_job_end_event_rules(sender)
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], event_rule)
        self.assertEqual(job.kwargs['event_type'], JOB_COMPLETED)
        self.assertEqual(job.kwargs['object_type'], script_type)
        self.assertNotIn('request', job.kwargs)

    def _job_event_rule(self, conditions=None):
        webhook = Webhook.objects.get(name='Webhook 1')
        event_rule = EventRule.objects.create(
            name='Event Rule Job Completed',
            event_types=[JOB_COMPLETED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=ObjectType.objects.get_for_model(Webhook),
            action_object_id=webhook.pk,
            conditions=conditions,
        )
        event_rule.object_types.set([ObjectType.objects.get_for_model(Script)])
        return event_rule

    def test_job_event_with_null_data(self):
        """
        Job.data is nullable, and a job which recorded no data is entirely routine. Event
        processing must handle it rather than raising while merging the payload.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        self._job_event_rule()
        process_job_end_event_rules(Mock(object_type=script_type, data=None, user=self.user))
        self.assertEqual(self.queue.count, 1)
        self.assertEqual(self.queue.jobs[0].kwargs['data'], {})

    def test_job_event_with_null_data_and_conditions(self):
        """
        A condition referencing an attribute of a null payload is a non-match rather than an
        error: the rule is skipped without logging, since a job which recorded no data is
        routine rather than a misconfigured rule.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        self._job_event_rule(conditions={'attr': 'status', 'value': 'completed'})
        with self.assertNoLogs('netbox.event_rules', level='ERROR'):
            process_job_end_event_rules(Mock(object_type=script_type, data=None, user=self.user))
        self.assertEqual(self.queue.count, 0)

    def test_job_event_with_null_data_does_not_satisfy_conditions(self):
        """
        A null payload must not satisfy a conditioned rule, however the condition is phrased:
        there is no data to evaluate, so nothing may enqueue the rule's action. A test for null
        and a negated test are the two phrasings which would otherwise match.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        for conditions in (
            {'attr': 'status', 'value': None},
            {'attr': 'status', 'value': 'completed', 'negate': True},
        ):
            with self.subTest(conditions=conditions):
                event_rule = self._job_event_rule(conditions=conditions)
                with self.assertNoLogs('netbox.event_rules', level='ERROR'):
                    process_job_end_event_rules(Mock(object_type=script_type, data=None, user=self.user))
                self.assertEqual(self.queue.count, 0)
                event_rule.delete()

    def test_job_event_with_non_dict_data(self):
        """
        A payload which is neither null nor a dict is unexpected: log it, but continue
        processing rather than aborting the batch.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        self._job_event_rule()
        for payload in ([1, 2], 'a string', 42):
            self.queue.empty()
            with self.assertLogs('netbox.events_processor', level='WARNING') as cm:
                process_job_end_event_rules(Mock(object_type=script_type, data=payload, user=self.user))
            self.assertIn(type(payload).__name__, cm.output[0])
            self.assertEqual(self.queue.count, 1)
            self.assertEqual(self.queue.jobs[0].kwargs['data'], {})

    def test_job_event_with_non_dict_data_and_conditions(self):
        """
        An invalid payload is no more evaluable than an absent one, so a conditioned rule must
        fail closed for it — including for the phrasings which a payload normalized to an empty
        dict would otherwise satisfy. The invalid payload is still reported once for the event,
        as the anomaly it is.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        for conditions in (
            {'attr': 'status', 'value': None},
            {'attr': 'status', 'value': 'completed', 'negate': True},
            {'attr': 'status', 'value': 'completed'},
        ):
            event_rule = self._job_event_rule(conditions=conditions)
            for payload in ([1, 2], 'a string', 42):
                with self.subTest(conditions=conditions, payload=payload):
                    self.queue.empty()
                    with self.assertLogs('netbox.events_processor', level='WARNING') as cm:
                        process_job_end_event_rules(
                            Mock(object_type=script_type, data=payload, user=self.user)
                        )
                    self.assertIn(type(payload).__name__, cm.output[0])
                    self.assertEqual(self.queue.count, 0)
            event_rule.delete()

    def test_no_matching_rules_leaves_payload_unserialized(self):
        """
        Normalizing the payload must not defeat EventContext's lazy serialization: an
        event with no applicable rules should never have its payload materialized.
        """
        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        site = Site.objects.create(name='Site Lazy', slug='site-lazy')

        queue = {}
        enqueue_event(queue, site, request, OBJECT_UPDATED)
        event = queue[f'dcim.site:{site.pk}']
        self.assertNotIn('data', event.data)

        process_event_rules(
            event_rules=EventRule.objects.none(),
            object_type=ObjectType.objects.get_for_model(Site),
            event=event,
        )
        self.assertNotIn('data', event.data)

    def test_duplicate_enqueue_refreshes_lazy_payload(self):
        """
        When the same object is enqueued more than once in a single request,
        lazy serialization should use the most recently enqueued instance while
        preserving the original event['object'] reference.
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')
        stale_site = Site.objects.get(pk=site.pk)

        queue = {}
        enqueue_event(queue, stale_site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        # Data should not be materialized yet (lazy serialization)
        self.assertNotIn('data', event.data)

        fresh_site = Site.objects.get(pk=site.pk)
        fresh_site.description = 'foo'
        fresh_site.save()

        enqueue_event(queue, fresh_site, request, OBJECT_UPDATED)

        # The original object reference should be preserved
        self.assertIs(event['object'], stale_site)

        # But serialized data should reflect the fresher instance
        self.assertEqual(event['data']['description'], 'foo')
        self.assertEqual(event['snapshots']['postchange']['description'], 'foo')

    def test_duplicate_enqueue_invalidates_materialized_data(self):
        """
        If event['data'] has already been materialized before a second enqueue
        for the same object, the stale payload should be discarded and rebuilt
        from the fresher instance on next access.
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')

        queue = {}
        enqueue_event(queue, site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        # Force early materialization
        self.assertEqual(event['data']['description'], '')

        # Now update and re-enqueue
        fresh_site = Site.objects.get(pk=site.pk)
        fresh_site.description = 'updated'
        fresh_site.save()

        enqueue_event(queue, fresh_site, request, OBJECT_UPDATED)

        # Stale data should have been invalidated; new access should reflect update
        self.assertEqual(event['data']['description'], 'updated')

    def test_update_then_delete_enqueue_freezes_payload(self):
        """
        When an update event is coalesced with a subsequent delete, the event
        type should be promoted to OBJECT_DELETED and the payload should be
        eagerly frozen (since the object will be inaccessible after deletion).
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')

        queue = {}
        enqueue_event(queue, site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        enqueue_event(queue, site, request, OBJECT_DELETED)

        # Event type should have been promoted
        self.assertEqual(event['event_type'], OBJECT_DELETED)

        # Data should already be materialized (frozen), not lazy
        self.assertIn('data', event.data)
        self.assertEqual(event['data']['name'], 'Site 1')
        self.assertIsNone(event['snapshots']['postchange'])

    @tag('regression')  # #21338
    def test_cable_creation_event_payload_includes_connected_endpoints(self):
        """
        Interface update events queued during cable creation must include the
        peer interface in connected_endpoints and link_peers.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        event_rule = EventRule.objects.create(
            name='Interface Update Rule',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=ObjectType.objects.get_for_model(Webhook),
            action_object_id=webhook.id,
        )
        event_rule.object_types.set([ObjectType.objects.get_for_model(Interface)])

        device = create_test_device('Device 1')
        interface_a = Interface.objects.create(device=device, name='eth0')
        interface_b = Interface.objects.create(device=device, name='eth1')

        # Create a cable between the two interfaces via the REST API
        data = {
            'a_terminations': [{'object_type': 'dcim.interface', 'object_id': interface_a.pk}],
            'b_terminations': [{'object_type': 'dcim.interface', 'object_id': interface_b.pk}],
        }
        url = reverse('dcim-api:cable-list')
        self.add_permissions('dcim.add_cable')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # One update event was queued for each interface
        self.assertEqual(self.queue.count, 2)
        payloads = {job.kwargs['data']['id']: job.kwargs['data'] for job in self.queue.jobs}
        peers = {interface_a.pk: interface_b.pk, interface_b.pk: interface_a.pk}
        self.assertEqual(set(payloads), set(peers))
        for interface_id, payload in payloads.items():
            peer_id = peers[interface_id]
            self.assertIsNotNone(payload['connected_endpoints'])
            self.assertEqual([endpoint['id'] for endpoint in payload['connected_endpoints']], [peer_id])
            self.assertEqual([peer['id'] for peer in payload['link_peers']], [peer_id])
            self.assertTrue(payload['connected_endpoints_reachable'])

    def test_duplicate_triggers(self):
        """
        Test for erroneous duplicate event triggers resulting from saving an object multiple times
        within the span of a single request.
        """
        url = reverse('dcim:site_add')
        request = RequestFactory().get(url)
        request.id = uuid.uuid4()
        request.user = self.user

        # Test create & update
        with event_tracking(request):
            site = Site(name='Site 1', slug='site-1')
            site.save()
            site.description = 'foo'
            site.save()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
        self.queue.empty()

        # Test multiple updates
        site = Site.objects.create(name='Site 2', slug='site-2')
        with event_tracking(request):
            site.description = 'foo'
            site.save()
            site.description = 'bar'
            site.save()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
        self.queue.empty()

        # Test update & delete
        site = Site.objects.create(name='Site 3', slug='site-3')
        with event_tracking(request):
            site.description = 'foo'
            site.save()
            site.delete()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
        self.queue.empty()

    def test_non_dict_action_data_does_not_crash_flush(self):
        """
        Pre-existing non-dict action_data must not cause flush_events() to
        raise.
        """
        # flush_events() logs a warning about the invalid action_data; mute it so the expected
        # message doesn't clutter the test runner's output.
        events_logger = logging.getLogger('netbox.events_processor')
        original_level = events_logger.level
        events_logger.setLevel(logging.CRITICAL)
        self.addCleanup(events_logger.setLevel, original_level)

        site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        bad_rule = EventRule.objects.create(
            name='Bad action_data rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
            action_data={},
        )
        bad_rule.object_types.set([site_type])

        # Simulate a legacy row that predates model validation.
        EventRule.objects.filter(pk=bad_rule.pk).update(action_data='not a dict')

        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        response = self.client.post(url, {'name': 'Site X', 'slug': 'site-x'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

    @tag('regression')
    def test_eventrule_script_action_with_object_image_files(self):
        """
        Verify that a Script event-rule action can be enqueued and executed cleanly when the
        triggering object carries uploaded files (e.g. DeviceType images).
        This is a regression test for issue #22376.

        """
        # Create a dummy script class and an instance of it
        class DummyScript(ScriptBase):
            class Meta:
                name = "Dummy Script"

            def run(self, data, commit=True):
                return "finished successfully"

        dummy_script = DummyScript()

        # Create ScriptModule and Script
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='dummy_script.py',
            )
        script = Script.objects.create(
            module=module,
            name='Dummy Script',
            is_executable=True,
        )
        script_type = ObjectType.objects.get_for_model(Script)

        # Create an event rule that triggers on DeviceType update with Script action
        devicetype_type = ObjectType.objects.get_for_model(DeviceType)
        event_rule = EventRule.objects.create(
            name='Test Script Event Rule with Files',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.SCRIPT,
            action_object_type=script_type,
            action_object_id=script.pk,
        )
        event_rule.object_types.set([devicetype_type])

        # Create a manufacturer and DeviceType
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            slug='test-manufacturer',
        )
        devicetype = DeviceType.objects.create(
            model='Test DeviceType',
            slug="test-devicetype",
            manufacturer=manufacturer,
        )

        # Create an image file
        image = BytesIO()
        Image.new('RGB', (1, 1)).save(image, format='PNG')
        image.name = 'test_image.png'
        image.seek(0)

        # PATCH the DeviceType via REST API to add the image
        data = {
            'front_image': image,
        }
        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': devicetype.pk})
        self.add_permissions('dcim.change_devicetype')

        # Mock the script's python_class to prevent the test from trying to load from disk
        with patch.object(Script, 'python_class') as mock:
            mock.return_value = dummy_script
            # Since in core/models/jobs.py Jobs are enqueued with a transaction.on_commit-handler
            # we simulate commit by using captureOnCommitCallbacks context manager
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.patch(url, data, format='multipart', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

            # Assert that the script job was enqueued cleanly and is waiting for execution
            self.assertEqual(self.queue.count, 1)
            script_job = Job.objects.filter(name=dummy_script.name).last()
            self.assertEqual(script_job.status, "pending")

            # silence rqworker (cleaner output) and trigger job execution
            logging.getLogger('rq.worker').setLevel(logging.ERROR)
            self.run_rq_jobs('default')

        # Assert that our script was executed without any errors
        script_job.refresh_from_db()
        self.assertEqual(script_job.status, "completed")
        self.assertEqual(script_job.data.get('output', ''), "finished successfully")

    @tag('regression')  # Issue #22872
    def test_eventrule_script_action_invalid_meta_does_not_abort_change(self):
        """
        A Script event-rule action whose Meta configuration is invalid must be logged and skipped without aborting
        the triggering object change or raising an HTTP 500 (#22872). Because event rules are processed in-request,
        an unhandled ValidationError here would fail the originating request.
        """
        class BadMetaScript(ScriptBase):
            class Meta:
                name = "Bad Meta Script"
                job_timeout = 'not-a-timeout'

            def run(self, data, commit=True):
                return "never reached"

        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='bad_meta_script.py',
            )
        script = Script.objects.create(module=module, name='Bad Meta Script', is_executable=True)
        script_type = ObjectType.objects.get_for_model(Script)

        # Trigger on Manufacturer rather than Site: the class-level event rules all target Site, so a Site-based rule
        # here would collide with them and perturb other tests' queue expectations.
        manufacturer_type = ObjectType.objects.get_for_model(Manufacturer)
        event_rule = EventRule.objects.create(
            name='Bad Meta Script Rule',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.SCRIPT,
            action_object_type=script_type,
            action_object_id=script.pk,
        )
        event_rule.object_types.set([manufacturer_type])

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        self.add_permissions('dcim.change_manufacturer')
        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': manufacturer.pk})

        # python_class is a property returning the script class; patch it to return our bad-Meta class so validate_meta
        # (a classmethod on it) is exercised the way production reads it.
        with patch.object(Script, 'python_class', new_callable=PropertyMock) as mock:
            mock.return_value = BadMetaScript
            with self.captureOnCommitCallbacks(execute=True):
                with self.assertLogs('netbox.events_processor', 'ERROR') as captured:
                    response = self.client.patch(url, {'description': 'updated'}, format='json', **self.header)

        # The triggering object change succeeds despite the misconfigured script
        self.assertHttpStatus(response, status.HTTP_200_OK)
        manufacturer.refresh_from_db()
        self.assertEqual(manufacturer.description, 'updated')

        # No script job was enqueued (nothing queued, no Job record), and the misconfiguration was logged
        self.assertEqual(self.queue.count, 0)
        self.assertEqual(Job.objects.filter(name=BadMetaScript.Meta.name).count(), 0)
        self.assertTrue(any('Bad Meta Script Rule' in line for line in captured.output))

    @tag('regression')  # Issue #22852
    def test_eventrule_script_action_honors_script_defaults(self):
        """A script run from an event rule uses the notification policy and job timeout from its Meta class."""
        class DummyScript(ScriptBase):
            class Meta:
                name = 'Dummy Defaults Script'
                notifications_default = JobNotificationChoices.NOTIFICATION_ON_FAILURE
                job_timeout = 600

            def run(self, data, commit=True):
                return 'finished successfully'

        dummy_script = DummyScript()

        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='dummy_defaults_script.py',
            )
        script = Script.objects.create(
            module=module,
            name=dummy_script.name,
            is_executable=True,
        )

        event_rule = EventRule.objects.create(
            name='Test Script Defaults Event Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.SCRIPT,
            action_object_type=ObjectType.objects.get_for_model(Script),
            action_object_id=script.pk,
        )
        event_rule.object_types.set([ObjectType.objects.get_for_model(DeviceType)])

        manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        self.add_permissions('dcim.add_devicetype')

        with patch.object(Script, 'python_class') as mock:
            mock.return_value = dummy_script
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    reverse('dcim-api:devicetype-list'),
                    {
                        'manufacturer': manufacturer.pk,
                        'model': 'Test DeviceType',
                        'slug': 'test-devicetype',
                    },
                    format='json',
                    **self.header,
                )
            self.assertHttpStatus(response, status.HTTP_201_CREATED)

            self.assertEqual(self.queue.count, 1)
            self.assertEqual(self.queue.jobs[0].timeout, 600)
            script_job = Job.objects.get(name=dummy_script.name)
            self.assertEqual(script_job.notifications, JobNotificationChoices.NOTIFICATION_ON_FAILURE)

            # silence rqworker (cleaner output) and trigger job execution
            rq_logger = logging.getLogger('rq.worker')
            self.addCleanup(rq_logger.setLevel, rq_logger.level)
            rq_logger.setLevel(logging.ERROR)
            self.run_rq_jobs('default')

        script_job.refresh_from_db()
        self.assertEqual(script_job.status, "completed")
        self.assertFalse(
            Notification.objects.filter(
                user=self.user,
                object_type=ObjectType.objects.get_for_model(Job),
                object_id=script_job.pk,
            ).exists()
        )

    @tag('regression')
    def test_eventrule_webhook_action_with_object_image_files(self):
        """
        Verify that a Webhook event-rule action can be enqueued and executed cleanly when
        the triggering object carries uploaded files (e.g. DeviceType images).
        This is a regression test for issue #20873.
        """
        # Create an event rule that triggers on DeviceType update with Script action
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        devicetype_type = ObjectType.objects.get_for_model(DeviceType)
        event_rule = EventRule.objects.create(
            name='Test Webhook Event Rule with Files',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        event_rule.object_types.set([devicetype_type])

        # Create a manufacturer and DeviceType
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            slug='test-manufacturer',
        )
        devicetype = DeviceType.objects.create(
            model='Test DeviceType',
            slug="test-devicetype",
            manufacturer=manufacturer,
        )

        # Create an image file
        image = BytesIO()
        Image.new('RGB', (1, 1)).save(image, format='PNG')
        image.name = 'test_image.png'
        image.seek(0)

        # PATCH the DeviceType via REST API to add the image
        data = {
            'front_image': image,
        }
        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': devicetype.pk})
        self.add_permissions('dcim.change_devicetype')

        response = self.client.patch(url, data, format='multipart', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Assert that the webhook job was enqueued cleanly
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], event_rule)
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)

    def test_unregistered_action_type_does_not_block_other_rules(self):
        """
        An unregistered action_type must not block other EventRules for the same event. Kept on
        this class, not a separate RQQueueTestMixin one, since two such classes in different
        `--parallel` subsuites cross-flush each other's Redis queue.
        """
        site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.create(name='Dispatch Test Webhook', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        good_rule = EventRule.objects.create(
            name='Good Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        good_rule.object_types.set([site_type])

        bad_rule = EventRule.objects.create(
            name='Bad Rule',
            event_types=[OBJECT_CREATED],
            action_type='someplugin.not_installed',
        )
        bad_rule.object_types.set([site_type])

        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        with self.assertLogs('netbox.events_processor', level='WARNING') as cm:
            response = self.client.post(
                url, {'name': 'Dispatch Site', 'slug': 'dispatch-site'}, format='json', **self.header
            )
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertTrue(any('someplugin.not_installed' in message for message in cm.output))

        # The good rule's webhook must still have been enqueued despite the bad rule.
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == good_rule]
        self.assertEqual(len(rule_jobs), 1)

    def test_raising_enqueue_does_not_block_other_rules(self):
        """A raising action registered as plugin-provided (the default) must not block other rules."""
        register_event_rule_action(DummyRaisingAction)
        self.addCleanup(registry['event_rule_actions'].pop, DummyRaisingAction.slug, None)

        site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.create(name='Dispatch Test Webhook 2', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        good_rule = EventRule.objects.create(
            name='Good Rule 2',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        good_rule.object_types.set([site_type])

        raising_rule = EventRule.objects.create(
            name='Raising Rule',
            event_types=[OBJECT_CREATED],
            action_type=DummyRaisingAction.slug,
        )
        raising_rule.object_types.set([site_type])

        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        with self.assertLogs('netbox.events_processor', level='ERROR') as cm:
            response = self.client.post(
                url, {'name': 'Dispatch Site 2', 'slug': 'dispatch-site-2'}, format='json', **self.header
            )
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertTrue(any('Raising Rule' in message for message in cm.output))

        # The good rule's webhook must still have been enqueued despite the raising rule.
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == good_rule]
        self.assertEqual(len(rule_jobs), 1)

    def test_raising_action_registered_as_non_plugin_propagates(self):
        """A raising action registered with is_plugin_provided=False (as core actions are) must propagate."""
        class RaisingCoreLikeAction(EventRuleAction):
            slug = 'test.raising_core_like_action'
            label = 'Raising Core-Like Action'
            object_required = False

            def enqueue(self, **kwargs):
                raise RuntimeError("intentional failure for test")

        register_event_rule_action(RaisingCoreLikeAction, is_plugin_provided=False)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.raising_core_like_action', None)

        site_type = ObjectType.objects.get_for_model(Site)
        rule = EventRule.objects.create(
            name='Raising Core-Like Rule',
            event_types=[OBJECT_CREATED],
            action_type='test.raising_core_like_action',
        )
        rule.object_types.set([site_type])

        with self.assertRaises(RuntimeError):
            process_event_rules([rule], object_type=site_type, event={'data': {}, 'event_type': OBJECT_CREATED})


class EventRuleActionRegistrationTestCase(TestCase):
    """
    Unit tests for the EventRuleAction registry (netbox.event_rules).
    """

    def tearDown(self):
        super().tearDown()
        # The registry is a global dict; test-registered actions must not leak into other tests.
        for slug in ('test.dummy_action', 'test.duplicate_action'):
            registry['event_rule_actions'].pop(slug, None)

    def test_register_event_rule_action(self):
        class DummyAction(EventRuleAction):
            slug = 'test.dummy_action'
            label = 'Dummy Action'
            description = 'A dummy action for testing'

        register_event_rule_action(DummyAction)

        action = get_event_rule_action('test.dummy_action')
        self.assertIsInstance(action, DummyAction)

        choices = {choice.value: choice.label for choice in get_event_rule_action_choices()}
        self.assertEqual(choices.get('test.dummy_action'), 'Dummy Action')

    def test_register_event_rule_action_as_decorator(self):
        @register_event_rule_action
        class DummyAction(EventRuleAction):
            slug = 'test.dummy_action'
            label = 'Dummy Action'

        self.assertIsInstance(get_event_rule_action('test.dummy_action'), DummyAction)

    def test_duplicate_slug_raises(self):
        class FirstAction(EventRuleAction):
            slug = 'test.duplicate_action'
            label = 'First'

        class SecondAction(EventRuleAction):
            slug = 'test.duplicate_action'
            label = 'Second'

        register_event_rule_action(FirstAction)
        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(SecondAction)

    def test_slug_starting_with_digit_rejected(self):
        """A slug starting with a digit would sanitize into a GraphQL-invalid enum member name."""
        class DigitSlugAction(EventRuleAction):
            slug = '2fa.notify'
            label = 'Digit Slug Action'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(DigitSlugAction)
        self.assertIsNone(get_event_rule_action('2fa.notify'))

    def test_slug_with_hyphen_rejected(self):
        """Hyphens are not permitted, though plugin distribution names conventionally use them."""
        class HyphenSlugAction(EventRuleAction):
            slug = 'my-plugin.open_ticket'
            label = 'Hyphen Slug Action'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(HyphenSlugAction)
        self.assertIsNone(get_event_rule_action('my-plugin.open_ticket'))

    def test_slug_with_leading_underscore_rejected(self):
        """A leading underscore sanitizes into a "__"-prefixed name, which GraphQL reserves for introspection."""
        class LeadingUnderscoreAction(EventRuleAction):
            slug = '_internal.foo'
            label = 'Leading Underscore Action'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(LeadingUnderscoreAction)
        self.assertIsNone(get_event_rule_action('_internal.foo'))

    def test_slug_with_uppercase_rejected(self):
        """Slugs must be lowercase, though plugin/class names conventionally are not."""
        class UppercaseSlugAction(EventRuleAction):
            slug = 'MyPlugin.action'
            label = 'Uppercase Slug Action'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(UppercaseSlugAction)
        self.assertIsNone(get_event_rule_action('MyPlugin.action'))

    def test_slug_enum_key_collision_rejected(self):
        """Two distinct slugs that sanitize to the same GraphQL enum member name must not both register."""
        class DotAction(EventRuleAction):
            slug = 'test.collision_action'
            label = 'Dot Action'

        class UnderscoreAction(EventRuleAction):
            slug = 'test_collision_action'
            label = 'Underscore Action'

        register_event_rule_action(DotAction)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.collision_action', None)
        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(UnderscoreAction)
        self.assertIsNone(get_event_rule_action('test_collision_action'))

    def test_missing_slug_raises_at_registration(self):
        # Class definition itself must succeed; only registration checks slug/label.
        class NoSlugAction(EventRuleAction):
            label = 'No Slug'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(NoSlugAction)

    def test_missing_label_raises_at_registration(self):
        class NoLabelAction(EventRuleAction):
            slug = 'test.no_label'

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(NoLabelAction)

    def test_intermediate_base_class_without_slug_or_label_is_definable(self):
        """
        slug/label are checked at registration, not class definition, so several concrete actions
        can share an intermediate base class which sets neither.
        """
        class PluginActionBase(EventRuleAction):
            object_required = False

            def enqueue(self, **kwargs):
                pass

        class ConcreteAction(PluginActionBase):
            slug = 'test.intermediate_base_concrete_action'
            label = 'Concrete Action'

        register_event_rule_action(ConcreteAction)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.intermediate_base_concrete_action', None)

        self.assertIsInstance(get_event_rule_action('test.intermediate_base_concrete_action'), ConcreteAction)

    def test_unregistered_slug_returns_none(self):
        self.assertIsNone(get_event_rule_action('this.does.not.exist'))

    def test_core_actions_are_registered(self):
        """WebhookAction/ScriptAction/NotificationAction are registered at app startup."""
        core_slugs = (
            EventRuleActionChoices.WEBHOOK, EventRuleActionChoices.SCRIPT, EventRuleActionChoices.NOTIFICATION,
        )
        for slug in core_slugs:
            self.assertIsNotNone(get_event_rule_action(slug))

    def test_get_object_queryset_returns_none_without_object_model(self):
        action = EventRuleAction()
        self.assertIsNone(action.get_object_queryset())

    def test_internal_validate_requires_object_when_object_required(self):
        action = EventRuleAction()
        action.object_required = True
        with self.assertRaises(ValidationError):
            action._validate(action_object=None, action_data={})

    def test_internal_validate_passes_when_object_not_required(self):
        action = EventRuleAction()
        action.object_required = False
        # Must not raise
        action._validate(action_object=None, action_data={})

    def test_internal_validate_rejects_wrong_object_type(self):
        action = EventRuleAction()
        action.object_model = Webhook
        action.object_required = True
        site = Site(name='Not A Webhook')
        with self.assertRaises(ValidationError):
            action._validate(action_object=site, action_data={})

    def test_internal_validate_rejects_object_for_action_without_object_model(self):
        """An action which declares no object_model must reject a target object outright."""
        action = EventRuleAction()
        with self.assertRaises(ValidationError):
            action._validate(action_object=Webhook(), action_data={})

    def test_object_required_without_object_model_rejected_at_registration(self):
        """object_required with no object_model could never be satisfied, so it's caught early."""
        class ImpossibleAction(EventRuleAction):
            slug = 'test.impossible_action'
            label = 'Impossible Action'
            object_required = True

        with self.assertRaises(ImproperlyConfigured):
            register_event_rule_action(ImpossibleAction)
        self.assertIsNone(get_event_rule_action('test.impossible_action'))

    def test_get_object_label_defaults_to_object_model_verbose_name(self):
        """The object picker's label defaults to the model's verbose name, capitalized."""
        self.assertEqual(get_event_rule_action(EventRuleActionChoices.NOTIFICATION).get_object_label(),
                         'Notification group')
        self.assertEqual(get_event_rule_action(EventRuleActionChoices.WEBHOOK).get_object_label(), 'Webhook')

    def test_get_object_label_honors_explicit_override(self):
        class LabeledAction(EventRuleAction):
            object_model = Webhook
            object_label = 'Destination'

        self.assertEqual(LabeledAction().get_object_label(), 'Destination')

    def test_get_object_label_is_none_without_object_model(self):
        self.assertIsNone(EventRuleAction().get_object_label())

    def test_validate_is_noop_by_default(self):
        action = EventRuleAction()
        # Must not raise
        action.validate(action_object=None, action_data={})

    def test_validate_override_does_not_need_super(self):
        """A subclass overriding validate() gets the base object_required check for free, no super() needed."""
        class CustomValidatingAction(EventRuleAction):
            slug = 'test.custom_validating_action'
            label = 'Custom Validating Action'
            object_model = Webhook
            object_required = True

            def validate(self, *, action_object, action_data):
                if action_data.get('bad'):
                    raise ValidationError({'action_data': 'bad action_data for test'})

        action = CustomValidatingAction()

        # The subclass's own check fires
        with self.assertRaises(ValidationError):
            action._validate(action_object=Webhook(), action_data={'bad': True})

        # ...as does the base object_required check
        with self.assertRaises(ValidationError):
            action._validate(action_object=None, action_data={})

        action._validate(action_object=Webhook(), action_data={})  # must not raise

    def test_enqueue_not_implemented_by_default(self):
        action = EventRuleAction()
        with self.assertRaises(NotImplementedError):
            action.enqueue(event_rule=None, event_context={}, action_object=None, action_data={})

    def test_is_plugin_provided_defaults_true_before_registration(self):
        """is_plugin_provided is True on an instance that never goes through registration."""
        self.assertTrue(EventRuleAction().is_plugin_provided)


class EventRuleActionAvailabilityTestCase(TestCase):
    """
    An EventRule with an unregistered action_type must remain loadable, skip gracefully during
    processing, and display as "unavailable" -- but reject full_clean() until action_type changes.
    """

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.create(name='Availability Test Webhook', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        cls.healthy_rule = EventRule.objects.create(
            name='Healthy Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        cls.healthy_rule.object_types.set([site_type])

        # .objects.create() calls save(), not full_clean(), so an unregistered action_type can be
        # persisted directly, matching the state of a row whose providing plugin was uninstalled.
        cls.unavailable_rule = EventRule.objects.create(
            name='Unavailable Rule',
            event_types=[OBJECT_CREATED],
            action_type='someplugin.not_installed',
        )
        cls.unavailable_rule.object_types.set([site_type])

    def test_action_is_available_true_for_registered_action(self):
        self.assertTrue(self.healthy_rule.action_is_available)
        self.assertIsNotNone(self.healthy_rule.action_provider)

    def test_action_is_available_false_for_unregistered_action(self):
        self.assertFalse(self.unavailable_rule.action_is_available)
        self.assertIsNone(self.unavailable_rule.action_provider)

    def test_get_action_type_display_for_registered_action(self):
        self.assertEqual(self.healthy_rule.get_action_type_display(), 'Webhook')

    def test_get_action_type_display_for_unregistered_action(self):
        self.assertEqual(
            self.unavailable_rule.get_action_type_display(),
            'someplugin.not_installed (unavailable)',
        )

    def test_get_action_type_color_for_registered_action(self):
        self.assertIsNone(self.healthy_rule.get_action_type_color())

    def test_get_action_type_color_for_unregistered_action(self):
        self.assertEqual(self.unavailable_rule.get_action_type_color(), 'red')

    def test_clean_rejects_unchanged_unavailable_action_type(self):
        """A persisted-but-unavailable action_type is rejected by full_clean() even when left unchanged."""
        rule = EventRule.objects.get(pk=self.unavailable_rule.pk)
        rule.enabled = False
        with self.assertRaises(ValidationError):
            rule.full_clean()

    def test_clean_rejects_new_row_with_unregistered_action_type(self):
        rule = EventRule(
            name='New Unregistered Rule',
            event_types=[OBJECT_CREATED],
            action_type='someplugin.also_not_installed',
        )
        with self.assertRaises(ValidationError):
            rule.full_clean()

    def test_clean_rejects_changing_to_unregistered_action_type(self):
        rule = EventRule.objects.get(pk=self.healthy_rule.pk)
        rule.action_type = 'someplugin.newly_unregistered'
        with self.assertRaises(ValidationError):
            rule.full_clean()

    def test_clean_accepts_registered_action_with_valid_object(self):
        rule = EventRule.objects.get(pk=self.healthy_rule.pk)
        rule.full_clean()  # must not raise


class EventRuleNoObjectActionTestCase(TestCase):
    """
    Model-layer tests for an EventRuleAction which declares object_model=None (no target object).
    """

    def tearDown(self):
        super().tearDown()
        registry['event_rule_actions'].pop('test.model_no_object_action', None)

    def test_full_clean_and_save_with_no_object_action(self):
        class NoObjectAction(EventRuleAction):
            slug = 'test.model_no_object_action'
            label = 'Model No-Object Action'
            object_required = False

        register_event_rule_action(NoObjectAction)

        site_type = ObjectType.objects.get_for_model(Site)
        rule = EventRule(
            name='Model No-Object Rule',
            event_types=[OBJECT_CREATED],
            action_type='test.model_no_object_action',
        )
        rule.full_clean()  # must not raise: no action_object required or supplied
        rule.save()
        rule.object_types.set([site_type])

        rule.refresh_from_db()
        self.assertIsNone(rule.action_object_type)
        self.assertIsNone(rule.action_object_id)
        self.assertIsNone(rule.action_object)


class WebhookRenderHeadersTest(TestCase):

    def test_render_headers(self):
        """Basic header rendering with Jinja2 interpolation."""
        webhook = Webhook(
            name='Webhook 1',
            payload_url='http://localhost:9000/',
            additional_headers='X-Foo: Bar\nX-Object: {{ data.name }}',
        )
        headers = webhook.render_headers({'data': {'name': 'Site 1'}})
        self.assertEqual(headers, {'X-Foo': 'Bar', 'X-Object': 'Site 1'})

    def test_render_headers_multiline_block(self):
        """A multi-line Jinja2 block (e.g. a loop generating headers) must render against the full template."""
        webhook = Webhook(
            name='Webhook 1',
            payload_url='http://localhost:9000/',
            additional_headers=(
                '{% for k, v in data.headers.items() %}X-{{ k }}: {{ v }}\n'
                '{% endfor %}'
            ),
        )
        headers = webhook.render_headers({'data': {'headers': {'Foo': '1', 'Bar': '2'}}})
        self.assertEqual(headers, {'X-Foo': '1', 'X-Bar': '2'})

    def test_render_headers_skips_blank_lines(self):
        """Blank lines in the rendered output (e.g. from Jinja2 block tags) must be skipped, not raise."""
        webhook = Webhook(
            name='Webhook 1',
            payload_url='http://localhost:9000/',
            # Block tags on their own lines leave behind blank lines once rendered
            additional_headers=(
                '{% for k, v in data.headers.items() %}\n'
                'X-{{ k }}: {{ v }}\n'
                '{% endfor %}'
            ),
        )
        headers = webhook.render_headers({'data': {'headers': {'Foo': '1', 'Bar': '2'}}})
        self.assertEqual(headers, {'X-Foo': '1', 'X-Bar': '2'})

    def test_render_headers_skips_lines_without_separator(self):
        """A non-blank line lacking a 'Name: Value' separator must be skipped, not raise."""
        webhook = Webhook(
            name='Webhook 1',
            payload_url='http://localhost:9000/',
            additional_headers='X-Foo: Bar\nthis line has no colon\nX-Baz: Qux',
        )
        headers = webhook.render_headers({})
        self.assertEqual(headers, {'X-Foo': 'Bar', 'X-Baz': 'Qux'})

    def test_render_headers_header_safe_filter_available(self):
        """
        The `header_safe` filter must be available when rendering headers, and must strip control characters
        (including CR/LF) so that untrusted data cannot smuggle additional headers via CR/LF injection.
        """
        webhook = Webhook(
            name='Webhook 1',
            payload_url='http://localhost:9000/',
            additional_headers='X-Object: {{ data.name | header_safe }}',
        )
        headers = webhook.render_headers({'data': {'name': 'legit\r\nX-Injected: evil\x00'}})

        # The injected newline is stripped, so only a single (sanitized) header is produced
        self.assertEqual(list(headers.keys()), ['X-Object'])
        self.assertNotIn('X-Injected', headers)
        self.assertEqual(headers['X-Object'], 'legitX-Injected: evil')
