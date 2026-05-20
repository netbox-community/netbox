from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import CablePath, Interface
from utilities.testing.utils import create_test_device
from wireless import signals
from wireless.choices import WirelessChannelChoices
from wireless.models import WirelessLink


class WirelessLinkSignalTestCase(TestCase):
    """
    Verify wireless.signals.update_connected_interfaces and nullify_connected_interfaces
    keep the connected interfaces and CablePaths consistent with the WirelessLink lifecycle.
    """

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')
        # Eight interfaces — one distinct pair per test method so no test sees stale
        # in-memory state mutated by a previous test.
        cls.interfaces = [
            Interface.objects.create(
                device=cls.device,
                name=f'radio{i}',
                type=InterfaceTypeChoices.TYPE_80211AC,
                rf_channel=WirelessChannelChoices.CHANNEL_5G_32,
                rf_channel_frequency=5160,
                rf_channel_width=20,
            )
            for i in range(8)
        ]

    def test_creating_link_assigns_wireless_link_to_both_interfaces(self):
        interface_a, interface_b = self.interfaces[0], self.interfaces[1]
        link = WirelessLink(interface_a=interface_a, interface_b=interface_b, ssid='LINK1')
        link.save()

        interface_a.refresh_from_db()
        interface_b.refresh_from_db()
        self.assertEqual(interface_a.wireless_link, link)
        self.assertEqual(interface_b.wireless_link, link)

    def test_creating_link_creates_cablepaths(self):
        interface_a, interface_b = self.interfaces[2], self.interfaces[3]
        link = WirelessLink(interface_a=interface_a, interface_b=interface_b, ssid='LINK1')
        link.save()

        self.assertEqual(CablePath.objects.filter(_nodes__contains=link).count(), 2)

    def test_saving_existing_link_does_not_create_extra_paths(self):
        interface_a, interface_b = self.interfaces[4], self.interfaces[5]
        link = WirelessLink(interface_a=interface_a, interface_b=interface_b, ssid='LINK1')
        link.save()
        path_count = CablePath.objects.count()

        link.description = 'updated'
        link.save()

        self.assertEqual(CablePath.objects.count(), path_count)

    def test_deleting_link_clears_interfaces_and_paths(self):
        interface_a, interface_b = self.interfaces[6], self.interfaces[7]
        link = WirelessLink(interface_a=interface_a, interface_b=interface_b, ssid='LINK1')
        link.save()
        self.assertEqual(CablePath.objects.filter(_nodes__contains=link).count(), 2)

        link.delete()

        interface_a.refresh_from_db()
        interface_b.refresh_from_db()
        self.assertIsNone(interface_a.wireless_link)
        self.assertIsNone(interface_b.wireless_link)
        # All wireless cable paths should be gone.
        self.assertEqual(CablePath.objects.count(), 0)


class UpdateConnectedInterfacesDirectHandlerTestCase(SimpleTestCase):
    """
    Direct-call tests for update_connected_interfaces branches not reachable through
    normal model operations (raw=True is only set during Django's loaddata pathway).
    """

    def test_raw_import_skips_interface_assignment_and_path_creation(self):
        interface_a = SimpleNamespace(wireless_link=None, save=MagicMock())
        interface_b = SimpleNamespace(wireless_link=None, cable=None, save=MagicMock())
        instance = SimpleNamespace(interface_a=interface_a, interface_b=interface_b)

        with patch.object(signals, 'create_cablepaths') as create_cablepaths:
            signals.update_connected_interfaces(instance=instance, created=True, raw=True)

        interface_a.save.assert_not_called()
        interface_b.save.assert_not_called()
        create_cablepaths.assert_not_called()
