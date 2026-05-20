from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from core.models import ObjectChange
from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from netbox.context_managers import event_tracking
from users.models import User
from utilities.testing import create_test_device
from wireless.models import WirelessLink


class WirelessLinkTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')
        cls.user = User.objects.create_user(username='testuser')

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
