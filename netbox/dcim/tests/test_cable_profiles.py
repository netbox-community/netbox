from django.test import tag

from dcim.choices import CableProfileChoices
from dcim.models import Cable, Interface, RearPort
from dcim.tests.utils import CablePathTestCase


class CableProfileLinkPeerTests(CablePathTestCase):
    """
    Tests for link peer resolution with cable profiles.
    """

    @tag('regression')  # #21917
    def test_trunk_4c1p_link_peers(self):
        """
        Link peers for trunk profile cables should honor connector mappings.
        """
        interfaces = [Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 5)]
        rear_ports = [
            RearPort.objects.create(device=self.device, name=f'Rear Port {i}', positions=1) for i in range(1, 5)
        ]

        cable = Cable(
            profile=CableProfileChoices.TRUNK_4C1P,
            a_terminations=interfaces,
            b_terminations=rear_ports,
        )
        cable.clean()
        cable.save()

        for interface, rear_port in zip(interfaces, rear_ports):
            interface.refresh_from_db()
            rear_port.refresh_from_db()

            self.assertEqual(interface.link_peers, [rear_port])
            self.assertEqual(rear_port.link_peers, [interface])

    @tag('regression')  # #21917
    def test_breakout_shuffle_link_peers(self):
        """
        Link peers for asymmetric breakout profiles should honor mapped connectors.
        """
        rear_ports = [
            RearPort.objects.create(device=self.device, name=f'Rear Port {i}', positions=4) for i in range(1, 3)
        ]
        interfaces = [Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 9)]

        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_2C4P_8C1P_SHUFFLE,
            a_terminations=rear_ports,
            b_terminations=interfaces,
        )
        cable.clean()
        cable.save()

        for rear_port in rear_ports:
            rear_port.refresh_from_db()
        for interface in interfaces:
            interface.refresh_from_db()

        self.assertEqual(rear_ports[0].link_peers, [interfaces[0], interfaces[1], interfaces[4], interfaces[5]])
        self.assertEqual(rear_ports[1].link_peers, [interfaces[2], interfaces[3], interfaces[6], interfaces[7]])

        for interface in interfaces[0:2] + interfaces[4:6]:
            self.assertEqual(interface.link_peers, [rear_ports[0]])

        for interface in interfaces[2:4] + interfaces[6:8]:
            self.assertEqual(interface.link_peers, [rear_ports[1]])
