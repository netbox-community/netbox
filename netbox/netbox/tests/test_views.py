import urllib.parse
from contextlib import contextmanager
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse

from dcim.choices import DeviceStatusChoices, InterfaceTypeChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site, VirtualChassis
from extras.events import enqueue_event
from extras.models import ImageAttachment
from extras.validators import CustomValidator
from ipam.choices import VLANStatusChoices
from ipam.models import VLAN, VLANGroup
from netbox.constants import EMPTY_TABLE_TEXT
from netbox.search.backends import search_backend
from users.models import User
from utilities.testing import TestCase
from utilities.views import get_action_url


class HomeViewTestCase(TestCase):

    def test_home(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)


class SearchViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site Alpha', slug='alpha', description='Red'),
            Site(name='Site Bravo', slug='bravo', description='Red'),
            Site(name='Site Charlie', slug='charlie', description='Green'),
            Site(name='Site Delta', slug='delta', description='Green'),
            Site(name='Site Echo', slug='echo', description='Blue'),
            Site(name='Site Foxtrot', slug='foxtrot', description='Blue'),
        )
        Site.objects.bulk_create(sites)
        search_backend.cache(sites)

    def test_search(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_search_query(self):
        url = reverse('search')
        params = {
            'q': 'red',
        }
        query = urllib.parse.urlencode(params)

        # Test without view permission
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)

        # Add view permissions & query again. Only matching objects should be listed
        self.add_permissions('dcim.view_site')
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn('Site Alpha', content)
        self.assertIn('Site Bravo', content)
        self.assertNotIn('Site Charlie', content)
        self.assertNotIn('Site Delta', content)
        self.assertNotIn('Site Echo', content)
        self.assertNotIn('Site Foxtrot', content)

    def test_search_no_results(self):
        self.add_permissions('dcim.view_site')
        url = reverse('search')
        params = {
            'q': 'xxxxxxxxx',  # Matches nothing
        }
        query = urllib.parse.urlencode(params)

        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)


class MediaViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        ct = ContentType.objects.get_for_model(Site)
        cls.image_attachment = ImageAttachment.objects.create(
            object_type=ct,
            object_id=site.pk,
            name='Test Image',
            image='image-attachments/site_1_test.jpg',
            image_height=100,
            image_width=100,
        )

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.device_type = DeviceType.objects.create(
            model='Device Type 1',
            slug='device-type-1',
            manufacturer=manufacturer,
            front_image='devicetype-images/front.jpg',
        )

    def test_media_login_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should redirect to login page
        self.assertHttpStatus(response, 302)

    @override_settings(LOGIN_REQUIRED=False)
    def test_media_login_not_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should return a 404 (not found)
        self.assertHttpStatus(response, 404)

    def test_image_attachment_with_permission(self):
        self.add_permissions('extras.view_imageattachment')
        url = reverse('media', kwargs={'path': self.image_attachment.image.name})
        with patch('netbox.views.misc.serve', return_value=HttpResponse(status=200)):
            response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        self.assertEqual(response['Content-Security-Policy'], "sandbox; default-src 'none'")
        self.assertEqual(response['X-Content-Type-Options'], "nosniff")

    def test_image_attachment_without_permission(self):
        url = reverse('media', kwargs={'path': self.image_attachment.image.name})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_image_attachment_traversal_without_permission(self):
        # A traversal path that normalizes to a protected directory must still be denied.
        traversal_path = 'foo/../' + self.image_attachment.image.name
        url = reverse('media', kwargs={'path': traversal_path})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_device_type_with_permission(self):
        self.add_permissions('dcim.view_devicetype')
        url = reverse('media', kwargs={'path': self.device_type.front_image.name})
        with patch('netbox.views.misc.serve', return_value=HttpResponse(status=200)):
            response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        self.assertEqual(response['Content-Security-Policy'], "sandbox; default-src 'none'")
        self.assertEqual(response['X-Content-Type-Options'], "nosniff")

    def test_device_type_without_permission(self):
        url = reverse('media', kwargs={'path': self.device_type.front_image.name})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_device_type_traversal_without_permission(self):
        # A traversal path that normalizes to a protected directory must still be denied.
        traversal_path = 'foo/../' + self.device_type.front_image.name
        url = reverse('media', kwargs={'path': traversal_path})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)


class DeleteAtomicityMixin:
    """
    Scenario shared by the transactional and autocommit variants of the ObjectDeleteView
    atomicity test (Ref: #22934).

    VirtualChassis.delete() clears vc_position/vc_priority on each member device and saves them
    before calling super().delete(), so an aborted deletion must roll those writes back. Otherwise
    they commit while their queued events are discarded, leaving a committed change which
    dispatches no events.
    """
    PROTECTION_RULES = {'dcim.virtualchassis': [CustomValidator({'name': {'eq': 'Nonexistent'}})]}

    def create_virtual_chassis(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        virtual_chassis = VirtualChassis.objects.create(name='Virtual Chassis 1')
        device = Device.objects.create(
            name='Device 1', site=site, role=role, device_type=device_type,
            virtual_chassis=virtual_chassis, vc_position=1, vc_priority=10
        )

        return virtual_chassis, device

    def delete_virtual_chassis(self, virtual_chassis):
        return self.client.post(
            get_action_url(VirtualChassis, action='delete', kwargs={'pk': virtual_chassis.pk}),
            data={'confirm': True}
        )

    def assertDeleteRolledBack(self, virtual_chassis, device):
        self.assertTrue(VirtualChassis.objects.filter(pk=virtual_chassis.pk).exists())
        device.refresh_from_db()
        self.assertEqual(device.vc_position, 1)
        self.assertEqual(device.vc_priority, 10)


class RolledBackWriteEventQueueTestCase(DeleteAtomicityMixin, TestCase):
    """
    Verify that UI views which roll back a write transaction and return a normal response
    discard any events queued during the aborted transaction. (Ref: #22934)
    """
    @contextmanager
    def assertNoEventsDispatched(self, expect_queued=True):
        """
        Assert that no queued events are flushed to the events pipeline while within this block.

        Unless expect_queued is disabled, also assert that at least one event *was* queued, so a
        test cannot pass merely because nothing ever reached the queue (e.g. if the order in which
        objects are processed changes, and the abort comes to precede the first event).
        """
        with patch('core.signals.enqueue_event', side_effect=enqueue_event) as enqueue:
            with patch('netbox.context_managers.flush_events') as flush_events:
                yield
        flush_events.assert_not_called()
        if expect_queued:
            self.assertGreater(enqueue.call_count, 0, "No events were queued; nothing was cleared")

    def test_bulk_create_view_rollback(self):
        # A bulk create which trips a uniqueness constraint partway through must not dispatch
        # created events for the objects written before the abort.
        group = VLANGroup.objects.create(name='Test Group', slug='test-group')
        VLAN.objects.create(group=group, vid=101, name='VLAN-101')
        self.add_permissions('ipam.add_vlan', 'ipam.view_vlan')

        with self.assertNoEventsDispatched():
            response = self.client.post(reverse('ipam:vlan_bulk_add'), data={
                'pattern': '100,101',
                'group': group.pk,
                'name': 'VLAN-{vid}',
                'status': VLANStatusChoices.STATUS_ACTIVE,
            })
        self.assertHttpStatus(response, 200)

        # The transaction was rolled back, so VID 100 must not exist
        self.assertFalse(VLAN.objects.filter(group=group, vid=100).exists())

    @override_settings(
        PROTECTION_RULES={'dcim.site': [CustomValidator({'status': {'eq': SiteStatusChoices.STATUS_DECOMMISSIONING}})]}
    )
    def test_bulk_delete_view_rollback_abortrequest(self):
        # A bulk delete aborted by a protection rule must not dispatch deleted events for the
        # objects deleted before the abort.
        site_a = Site.objects.create(
            name='Site A', slug='site-a', status=SiteStatusChoices.STATUS_DECOMMISSIONING
        )
        site_b = Site.objects.create(name='Site B', slug='site-b', status=SiteStatusChoices.STATUS_ACTIVE)
        self.add_permissions('dcim.delete_site', 'dcim.view_site')

        with self.assertNoEventsDispatched():
            self.client.post(reverse('dcim:site_bulk_delete'), data={
                'pk': [site_a.pk, site_b.pk],
                'confirm': True,
                '_confirm': True,
            })

        # Both sites must still exist
        self.assertEqual(Site.objects.filter(pk__in=[site_a.pk, site_b.pk]).count(), 2)

    def test_bulk_delete_view_rollback_protectederror(self):
        # A bulk delete aborted by a dependent object must not dispatch deleted events for the
        # objects deleted before the abort.
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(device_types)
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        Device.objects.create(name='Device 1', site=site, role=role, device_type=device_types[1])
        self.add_permissions('dcim.delete_devicetype', 'dcim.view_devicetype')

        with self.assertNoEventsDispatched():
            self.client.post(reverse('dcim:devicetype_bulk_delete'), data={
                'pk': [dt.pk for dt in device_types],
                'confirm': True,
                '_confirm': True,
            })

        # Both device types must still exist
        self.assertEqual(DeviceType.objects.count(), 2)

    @override_settings(
        PROTECTION_RULES={'dcim.device': [CustomValidator({'status': {'eq': DeviceStatusChoices.STATUS_OFFLINE}})]}
    )
    def test_object_delete_view_rollback_abortrequest(self):
        # A cascading delete aborted by a protection rule on the parent must not dispatch deleted
        # events for the children collected before the abort. Django's collector deletes dependent
        # objects first, so the interface's pre_delete handler queues an event before the device's
        # protection rule trips.
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        device = Device.objects.create(
            name='Device 1', site=site, role=role, device_type=device_type,
            status=DeviceStatusChoices.STATUS_ACTIVE
        )
        interface = Interface.objects.create(device=device, name='eth0', type=InterfaceTypeChoices.TYPE_VIRTUAL)
        self.add_permissions('dcim.delete_device', 'dcim.view_device')

        with self.assertNoEventsDispatched():
            self.client.post(get_action_url(Device, action='delete', kwargs={'pk': device.pk}), data={
                'confirm': True,
            })

        # Both the device and its interface must still exist
        self.assertTrue(Device.objects.filter(pk=device.pk).exists())
        self.assertTrue(Interface.objects.filter(pk=interface.pk).exists())

    @override_settings(PROTECTION_RULES=DeleteAtomicityMixin.PROTECTION_RULES)
    def test_object_delete_view_rollback_is_atomic(self):
        # An aborted delete must not leave behind writes performed by the model's delete() before
        # super().delete(). Note what this detects: every test here runs inside the harness'
        # transaction, so an escaped write is rolled back with the test regardless, and the
        # assertions below cannot see it. Without the view's atomic block, AbortRequest instead
        # escapes the collector's atomic(savepoint=False) and marks the harness' transaction as
        # needing rollback, so this test fails with TransactionManagementError. The committed
        # symptom itself is covered by DeleteAtomicityTestCase below.
        virtual_chassis, device = self.create_virtual_chassis()
        self.add_permissions('dcim.delete_virtualchassis', 'dcim.view_virtualchassis')

        with self.assertNoEventsDispatched():
            self.delete_virtual_chassis(virtual_chassis)

        self.assertDeleteRolledBack(virtual_chassis, device)

    def test_object_delete_view_rollback_protectederror(self):
        # A delete aborted by a dependent object must not dispatch any events. Nothing is queued
        # today, as the collector raises before any pre_delete signal fires; assert the queue is
        # clear regardless, so correctness does not rest on Django's collection order.
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        Device.objects.create(name='Device 1', site=site, role=role, device_type=device_type)
        self.add_permissions('dcim.delete_devicetype', 'dcim.view_devicetype')

        with self.assertNoEventsDispatched(expect_queued=False):
            self.client.post(get_action_url(DeviceType, action='delete', kwargs={'pk': device_type.pk}), data={
                'confirm': True,
            })

        self.assertTrue(DeviceType.objects.filter(pk=device_type.pk).exists())


class DeleteAtomicityTestCase(DeleteAtomicityMixin, TransactionTestCase):
    """
    Exercise the autocommit path, which TestCase cannot reach: it wraps every test in a
    transaction, so a write which escapes the view's rollback is rolled back with the test and
    stays invisible to the assertions. Outside a transaction, a write performed by delete() before
    super().delete() genuinely commits unless the view opens its own atomic block. (Ref: #22934)

    Note: TransactionTestCase teardown flushes all tables, which removes rows seeded by data
    migrations from a --keepdb database (e.g. the dcim.0206 ModuleTypeProfiles). A fresh test
    database restores them.
    """
    def setUp(self):
        # A superuser, rather than the object permissions granted by utilities.testing.TestCase:
        # this case covers transaction handling, not permission enforcement.
        self.user = User.objects.create_user(username='testuser', is_superuser=True)
        self.client = Client()
        self.client.force_login(self.user)

    @override_settings(PROTECTION_RULES=DeleteAtomicityMixin.PROTECTION_RULES)
    def test_object_delete_view_rollback_is_atomic(self):
        virtual_chassis, device = self.create_virtual_chassis()

        self.delete_virtual_chassis(virtual_chassis)

        # Without the view's atomic block, the member device's cleared position and priority commit
        # here, leaving a change which dispatches no events
        self.assertDeleteRolledBack(virtual_chassis, device)
