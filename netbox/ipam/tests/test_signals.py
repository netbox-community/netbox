import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase, override_settings

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from dcim.models import Location, Region, Site, SiteGroup
from ipam import signals
from ipam.models import VRF, IPAddress, Prefix
from netbox.context_managers import event_tracking
from users.models import User
from utilities.testing import PinnedConnectionRouter
from utilities.testing.utils import create_test_device, create_test_virtualmachine


def _build_request(user):
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = user
    return request


class PrefixHierarchySignalTestCase(TestCase):
    """
    Verify ipam.signals.handle_prefix_saved / handle_prefix_deleted keep the cached
    `_children` and `_depth` counters up to date as prefixes are added, modified, and
    removed.
    """

    def _refresh_counters(self, *prefixes):
        for prefix in prefixes:
            prefix.refresh_from_db()
        return prefixes

    def test_creating_prefix_initializes_hierarchy_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent, child)
        self.assertEqual(parent._children, 1)
        self.assertEqual(child._depth, 1)
        self.assertEqual(child._children, 0)

    def test_modifying_prefix_recomputes_old_and_new_position(self):
        parent_a = Prefix.objects.create(prefix='10.0.0.0/16')
        parent_b = Prefix.objects.create(prefix='192.168.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent_a, parent_b, child)
        self.assertEqual(parent_a._children, 1)
        self.assertEqual(parent_b._children, 0)

        # Move the child under parent_b.
        child.prefix = '192.168.1.0/24'
        child.save()

        self._refresh_counters(parent_a, parent_b, child)
        self.assertEqual(parent_a._children, 0)
        self.assertEqual(parent_b._children, 1)
        self.assertEqual(child._depth, 1)

    def test_unchanged_save_does_not_disturb_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent, child)
        original_children = parent._children
        original_depth = child._depth

        # Save with no field changes.
        parent.description = ''
        parent.save()

        self._refresh_counters(parent, child)
        self.assertEqual(parent._children, original_children)
        self.assertEqual(child._depth, original_depth)

    def test_deleting_prefix_recomputes_neighbor_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent)
        self.assertEqual(parent._children, 1)

        child.delete()

        self._refresh_counters(parent)
        self.assertEqual(parent._children, 0)


class ClearPrimaryIPSignalTestCase(TestCase):
    """
    Verify ipam.signals.clear_primary_ip detaches deleted IPAddresses from the Device or
    VirtualMachine they were assigned as primary. The behavior under test is the
    signal-driven snapshot+save (and resulting change-log entry), not the FK's
    on_delete=SET_NULL fallback.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_device_primary_ip4_delete_records_device_update(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='192.0.2.1/24')
        device.primary_ip4 = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.primary_ip4)

        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip4'])

    def test_device_primary_ip6_delete_clears_field_and_saves(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='2001:db8::1/64')
        device.primary_ip6 = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.primary_ip6)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip6'])

    def test_vm_primary_ip4_delete_records_vm_update(self):
        vm = create_test_virtualmachine('VM 1')
        ip = IPAddress.objects.create(address='192.0.2.10/24')
        vm.primary_ip4 = ip
        vm.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        vm.refresh_from_db()
        self.assertIsNone(vm.primary_ip4)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(vm),
            changed_object_id=vm.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip4'])

    def test_unrelated_ip_delete_records_no_device_change(self):
        device = create_test_device('Device 1')
        device_type = ContentType.objects.get_for_model(device)
        assigned = IPAddress.objects.create(address='192.0.2.1/24')
        unrelated = IPAddress.objects.create(address='192.0.2.2/24')
        device.primary_ip4 = assigned
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            unrelated.delete()

        device.refresh_from_db()
        self.assertEqual(device.primary_ip4, assigned)
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=device_type,
                changed_object_id=device.pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
            ).exists()
        )


class ClearOOBIPSignalTestCase(TestCase):
    """
    Verify ipam.signals.clear_oob_ip detaches a deleted IPAddress from any Device on
    which it was set as the OOB IP, and records a Device update change-log entry.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_device_oob_ip_delete_records_device_update(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='192.0.2.1/24')
        device.oob_ip = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.oob_ip)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['oob_ip'])

    def test_unrelated_ip_delete_records_no_device_change(self):
        device = create_test_device('Device 1')
        device_type = ContentType.objects.get_for_model(device)
        oob = IPAddress.objects.create(address='192.0.2.1/24')
        unrelated = IPAddress.objects.create(address='192.0.2.2/24')
        device.oob_ip = oob
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            unrelated.delete()

        device.refresh_from_db()
        self.assertEqual(device.oob_ip, oob)
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=device_type,
                changed_object_id=device.pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
            ).exists()
        )


class PrefixDenormalizationTriggerTestCase(TestCase):
    """
    Verify the PostgreSQL triggers (installed by ipam migration 0091) that keep a Prefix's
    denormalized scope columns in sync with its Site/Location.

    These replace the former Python `post_save` handler in netbox.denormalized. Unlike that
    handler, the triggers also fire for bulk QuerySet.update() writes (exercised below).
    """

    def test_site_region_group_change_propagates_to_prefix(self):
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a, group=group_a)
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Site),
            scope_id=site.pk,
        )
        self.assertEqual(prefix._region, region_a)
        self.assertEqual(prefix._site_group, group_a)

        site.region = region_b
        site.group = group_b
        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._region, region_b)
        self.assertEqual(prefix._site_group, group_b)

    def test_location_site_change_propagates_to_prefix(self):
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site_a = Site.objects.create(name='Site A', slug='site-a', region=region_a, group=group_a)
        site_b = Site.objects.create(name='Site B', slug='site-b', region=region_b, group=group_b)
        location = Location.objects.create(name='Loc', slug='loc', site=site_a)
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Location),
            scope_id=location.pk,
        )
        self.assertEqual(prefix._site, site_a)

        # Move the Location to a different Site; the trigger updates _site and pulls the new
        # site's region/group through in the same statement.
        location.site = site_b
        location.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_b)
        self.assertEqual(prefix._region, region_b)
        self.assertEqual(prefix._site_group, group_b)

    def test_bulk_update_of_site_propagates_to_prefix(self):
        """
        A bulk QuerySet.update() bypasses post_save (the old handler never fired for it);
        the DB trigger fires regardless.
        """
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a)
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Site),
            scope_id=site.pk,
        )
        self.assertEqual(prefix._region, region_a)

        Site.objects.filter(pk=site.pk).update(region=region_b)

        prefix.refresh_from_db()
        self.assertEqual(prefix._region, region_b)


class PrefixHierarchySignalConnectionTestCase(TestCase):
    """
    Verify the prefix hierarchy handlers issue every query against the connection the saved
    Prefix was written to, rather than letting DATABASE_ROUTERS select one. On an
    installation with routers configured (e.g. netbox_branching), a routed query would
    recount the hierarchy against one database and write the result to another.

    These handlers are invoked directly rather than through save()/delete(): every query
    they make is against Prefix, which is also the model being written, so a router which
    fails routed Prefix queries would trip on the save itself.
    """

    @classmethod
    def setUpTestData(cls):
        cls.vrf = VRF.objects.create(name='VRF 1')

    def test_prefix_saved_handler_pins_queries_to_given_connection(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16', vrf=self.vrf)
        child = Prefix.objects.create(prefix='10.0.1.0/24', vrf=self.vrf)

        # Re-fetch and move the child, leaving the vrf relation uncached: a lookup which
        # filters on self.vrf rather than self.vrf_id fetches it over a routed connection,
        # which the VRF entry below catches. The same applies to the throwaway Prefix the
        # handler builds to clean up the child's previous position. The instance is not
        # re-fetched after the save, as that would reset the _prefix snapshot the handler
        # compares against and it would decline to do any work at all.
        child = Prefix.objects.get(pk=child.pk)
        child.prefix = '10.0.2.0/24'
        child.save()
        self.assertNotEqual(child.prefix, child._prefix)

        router = PinnedConnectionRouter(Prefix, VRF)
        with override_settings(DATABASE_ROUTERS=[router]):
            signals.handle_prefix_saved(instance=child, created=False, using='default')

        parent.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(parent._children, 1)
        self.assertEqual(child._depth, 1)

    def test_prefix_deleted_handler_pins_queries_to_given_connection(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16', vrf=self.vrf)
        child = Prefix.objects.create(prefix='10.0.1.0/24', vrf=self.vrf)

        child = Prefix.objects.get(pk=child.pk)
        router = PinnedConnectionRouter(Prefix, VRF)
        with override_settings(DATABASE_ROUTERS=[router]):
            signals.handle_prefix_deleted(instance=child, using='default')

        parent.refresh_from_db()
        self.assertEqual(parent._children, 1)
