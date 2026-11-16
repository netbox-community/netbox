from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from core.models import ObjectChange
from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface, Region, Site, SiteGroup
from netbox.context_managers import event_tracking
from users.models import User
from utilities.testing import create_test_device
from wireless.models import WirelessLAN, WirelessLink


class WirelessLANTestCase(TestCase):

    # Regression test for #22682
    def test_deleting_site_group_does_not_delete_wirelesslan_scoped_to_member_site(self):
        sitegroup = SiteGroup.objects.create(name='Site Group 1', slug='site-group-1')
        site = Site.objects.create(name='Site 1', slug='site-1', group=sitegroup)
        wlan = WirelessLAN.objects.create(ssid='WLAN 1', scope=site)

        sitegroup.delete()

        site.refresh_from_db()
        wlan.refresh_from_db()
        self.assertIsNone(site.group)
        self.assertEqual(wlan.scope, site)
        self.assertIsNone(wlan._site_group_id)

    # Regression test for #22682
    def test_deleting_region_does_not_delete_wirelesslan_scoped_to_member_site(self):
        region = Region.objects.create(name='Region 1', slug='region-1')
        site = Site.objects.create(name='Site 2', slug='site-2', region=region)
        wlan = WirelessLAN.objects.create(ssid='WLAN 2', scope=site)

        region.delete()

        site.refresh_from_db()
        wlan.refresh_from_db()
        self.assertIsNone(site.region)
        self.assertEqual(wlan.scope, site)
        self.assertIsNone(wlan._region_id)

    def test_deleting_site_group_scoped_to_it_directly_still_deletes_wirelesslan(self):
        sitegroup = SiteGroup.objects.create(name='Site Group 2', slug='site-group-2')
        wlan = WirelessLAN.objects.create(ssid='WLAN 3', scope=sitegroup)

        sitegroup.delete()

        self.assertFalse(WirelessLAN.objects.filter(pk=wlan.pk).exists())

    def test_deleting_region_scoped_to_it_directly_still_deletes_wirelesslan(self):
        region = Region.objects.create(name='Region 2', slug='region-2')
        wlan = WirelessLAN.objects.create(ssid='WLAN 4', scope=region)

        region.delete()

        self.assertFalse(WirelessLAN.objects.filter(pk=wlan.pk).exists())


class WirelessLinkTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')
        cls.user = User.objects.create_user(username='testuser')

    # Regression test for #23617
    def test_creating_wireless_link_records_interface_prechange(self):
        interfaces = [
            Interface.objects.create(device=self.device, name=name, type=InterfaceTypeChoices.TYPE_80211AC)
            for name in ('radio0', 'radio1')
        ]
        request = RequestFactory().post('/')
        request.id = uuid4()
        request.user = self.user

        with event_tracking(request):
            wireless_link = WirelessLink.objects.create(
                interface_a=interfaces[0],
                interface_b=interfaces[1],
                ssid='LINK1',
            )

        for interface in interfaces:
            change = ObjectChange.objects.get(
                changed_object_type=ContentType.objects.get_for_model(Interface),
                changed_object_id=interface.pk,
            )
            self.assertIsNone(change.prechange_data['wireless_link'])
            self.assertEqual(change.postchange_data['wireless_link'], wireless_link.pk)
            self.assertFalse(hasattr(interface, '_prechange_snapshot'))

    # Regression test for #23617
    def test_creating_wireless_link_keeps_existing_interface_snapshot(self):
        interfaces = [
            Interface.objects.create(device=self.device, name=name, type=InterfaceTypeChoices.TYPE_80211AC)
            for name in ('radio0', 'radio1')
        ]
        request = RequestFactory().post('/')
        request.id = uuid4()
        request.user = self.user

        with event_tracking(request):
            interfaces[0].snapshot()
            interfaces[0].description = 'updated'
            WirelessLink.objects.create(interface_a=interfaces[0], interface_b=interfaces[1], ssid='LINK1')

        change = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Interface),
            changed_object_id=interfaces[0].pk,
        )
        self.assertEqual(change.prechange_data['description'], '')
        self.assertEqual(change.postchange_data['description'], 'updated')

    def test_resaving_wireless_link_does_not_log_connected_interfaces(self):
        interface_a = Interface.objects.create(
            device=self.device,
            name='radio0',
            type=InterfaceTypeChoices.TYPE_80211AC,
        )
        interface_b = Interface.objects.create(
            device=self.device,
            name='radio1',
            type=InterfaceTypeChoices.TYPE_80211AC,
        )
        wireless_link = WirelessLink.objects.create(
            interface_a=interface_a,
            interface_b=interface_b,
            ssid='LINK1',
        )

        interface_a.refresh_from_db()
        interface_b.refresh_from_db()
        self.assertEqual(interface_a.wireless_link, wireless_link)
        self.assertEqual(interface_b.wireless_link, wireless_link)

        # Reload the WirelessLink to avoid relying on FK objects cached during creation.
        wireless_link = WirelessLink.objects.get(pk=wireless_link.pk)

        request = RequestFactory().post('/')
        request.id = uuid4()
        request.user = self.user

        with event_tracking(request):
            wireless_link.snapshot()
            wireless_link.save()

        interface_type = ContentType.objects.get_for_model(Interface)
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=interface_type,
                changed_object_id__in=(interface_a.pk, interface_b.pk),
            ).exists()
        )
