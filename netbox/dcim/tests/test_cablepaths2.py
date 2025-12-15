from unittest import skip

from circuits.models import CircuitTermination
from dcim.choices import CableProfileChoices
from dcim.models import *
from dcim.svg import CableTraceSVG
from dcim.tests.utils import CablePathTestCase


class CablePathTests(CablePathTestCase):
    """
    Test the creation of CablePaths for Cables with different profiles applied.

    Tests are numbered as follows:
        1XX: Test direct connections using each profile
        2XX: Topology tests replicated from the legacy test case and adapted to use profiles
    """

    def test_101_cable_profile_single_1c1p(self):
        """
        [IF1] --C1-- [IF2]

        Cable profile: Single connector, single position
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.SINGLE_1C1P,
            a_terminations=[interfaces[0]],
            b_terminations=[interfaces[1]],
        )
        cable1.clean()
        cable1.save()

        path1 = self.assertPathExists(
            (interfaces[0], cable1, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interfaces[0].refresh_from_db()
        interfaces[1].refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertEqual(interfaces[0].cable_connector, 1)
        self.assertEqual(interfaces[0].cable_positions, [1])
        self.assertEqual(interfaces[1].cable_connector, 1)
        self.assertEqual(interfaces[1].cable_positions, [1])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_102_cable_profile_single_1c2p(self):
        """
        [IF1] --C1-- [FP1][RP1] --C3-- [RP2][FP3] --C4-- [IF3]
        [IF2] --C2-- [FP2]                  [FP4] --C5-- [IF4]

        Cable profile: Single connector, multiple positions
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]
        rear_ports = [
            RearPort.objects.create(device=self.device, name='Rear Port 1', positions=2),
            RearPort.objects.create(device=self.device, name='Rear Port 2', positions=2),
        ]
        front_ports = [
            FrontPort.objects.create(device=self.device, name='Front Port 1'),
            FrontPort.objects.create(device=self.device, name='Front Port 2'),
            FrontPort.objects.create(device=self.device, name='Front Port 3'),
            FrontPort.objects.create(device=self.device, name='Front Port 4'),
        ]
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=front_ports[0],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[1],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[2],
                front_port_position=1,
                rear_port=rear_ports[1],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[3],
                front_port_position=1,
                rear_port=rear_ports[1],
                rear_port_position=2,
            ),
        ])

        # Create cables
        cable1 = Cable(
            a_terminations=[interfaces[0]],
            b_terminations=[front_ports[0]],
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            a_terminations=[interfaces[1]],
            b_terminations=[front_ports[1]],
        )
        cable2.clean()
        cable2.save()
        cable3 = Cable(
            profile=CableProfileChoices.SINGLE_1C2P,
            a_terminations=[rear_ports[0]],
            b_terminations=[rear_ports[1]],
        )
        cable3.clean()
        cable3.save()
        cable4 = Cable(
            a_terminations=[interfaces[2]],
            b_terminations=[front_ports[2]],
        )
        cable4.clean()
        cable4.save()
        cable5 = Cable(
            a_terminations=[interfaces[3]],
            b_terminations=[front_ports[3]],
        )
        cable5.clean()
        cable5.save()

        path1 = self.assertPathExists(
            (
                interfaces[0], cable1, front_ports[0], rear_ports[0], cable3, rear_ports[1], front_ports[2], cable4,
                interfaces[2],
            ),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (
                interfaces[1], cable2, front_ports[1], rear_ports[0], cable3, rear_ports[1], front_ports[3], cable5,
                interfaces[3],
            ),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (
                interfaces[2], cable4, front_ports[2], rear_ports[1], cable3, rear_ports[0], front_ports[0], cable1,
                interfaces[0],
            ),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (
                interfaces[3], cable5, front_ports[3], rear_ports[1], cable3, rear_ports[0], front_ports[1], cable2,
                interfaces[1],
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)
        for iface in interfaces:
            iface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        for rear_port in rear_ports:
            rear_port.refresh_from_db()
        self.assertEqual(rear_ports[0].cable_connector, 1)
        self.assertEqual(rear_ports[0].cable_positions, [1, 2])
        self.assertEqual(rear_ports[1].cable_connector, 1)
        self.assertEqual(rear_ports[1].cable_positions, [1, 2])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_103_cable_profile_trunk_2c1p(self):
        """
        [IF1] --C1-- [IF3]
        [IF2]        [IF4]

        Cable profile: Multiple connectors, single position
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[interfaces[2], interfaces[3]],
        )
        cable1.clean()
        cable1.save()

        path1 = self.assertPathExists(
            (interfaces[0], cable1, interfaces[2]),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable1, interfaces[3]),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interfaces[2], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (interfaces[3], cable1, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertEqual(interfaces[0].cable_connector, 1)
        self.assertEqual(interfaces[0].cable_positions, [1])
        self.assertEqual(interfaces[1].cable_connector, 2)
        self.assertEqual(interfaces[1].cable_positions, [1])
        self.assertEqual(interfaces[2].cable_connector, 1)
        self.assertEqual(interfaces[2].cable_positions, [1])
        self.assertEqual(interfaces[3].cable_connector, 2)
        self.assertEqual(interfaces[3].cable_positions, [1])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_104_cable_profile_trunk_2c2p(self):
        """
        [IF1] --C1-- [FP1][RP1] --C9-- [RP3][FP5] --C5-- [IF5]
        [IF2] --C2-- [FP2]                  [FP6] --C6-- [IF6]
        [IF3] --C3-- [FP3][RP2]        [RP4][FP7] --C7-- [IF7]
        [IF4] --C4-- [FP4]                  [FP8] --C8-- [IF8]

        Cable profile: Multiple connectors, multiple positions
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
            Interface.objects.create(device=self.device, name='Interface 5'),
            Interface.objects.create(device=self.device, name='Interface 6'),
            Interface.objects.create(device=self.device, name='Interface 7'),
            Interface.objects.create(device=self.device, name='Interface 8'),
        ]
        rear_ports = [
            RearPort.objects.create(device=self.device, name='Rear Port 1', positions=2),
            RearPort.objects.create(device=self.device, name='Rear Port 2', positions=2),
            RearPort.objects.create(device=self.device, name='Rear Port 3', positions=2),
            RearPort.objects.create(device=self.device, name='Rear Port 4', positions=2),
        ]
        front_ports = [
            FrontPort.objects.create(device=self.device, name='Front Port 1'),
            FrontPort.objects.create(device=self.device, name='Front Port 2'),
            FrontPort.objects.create(device=self.device, name='Front Port 3'),
            FrontPort.objects.create(device=self.device, name='Front Port 4'),
            FrontPort.objects.create(device=self.device, name='Front Port 5'),
            FrontPort.objects.create(device=self.device, name='Front Port 6'),
            FrontPort.objects.create(device=self.device, name='Front Port 7'),
            FrontPort.objects.create(device=self.device, name='Front Port 8'),
        ]
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=front_ports[0],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[1],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[2],
                front_port_position=1,
                rear_port=rear_ports[1],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[3],
                front_port_position=1,
                rear_port=rear_ports[1],
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[4],
                front_port_position=1,
                rear_port=rear_ports[2],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[5],
                front_port_position=1,
                rear_port=rear_ports[2],
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[6],
                front_port_position=1,
                rear_port=rear_ports[3],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[7],
                front_port_position=1,
                rear_port=rear_ports[3],
                rear_port_position=2,
            ),
        ])

        # Create cables
        cable1 = Cable(a_terminations=[interfaces[0]], b_terminations=[front_ports[0]])
        cable1.clean()
        cable1.save()
        cable2 = Cable(a_terminations=[interfaces[1]], b_terminations=[front_ports[1]])
        cable2.clean()
        cable2.save()
        cable3 = Cable(a_terminations=[interfaces[2]], b_terminations=[front_ports[2]])
        cable3.clean()
        cable3.save()
        cable4 = Cable(a_terminations=[interfaces[3]], b_terminations=[front_ports[3]])
        cable4.clean()
        cable4.save()
        cable5 = Cable(a_terminations=[interfaces[4]], b_terminations=[front_ports[4]])
        cable5.clean()
        cable5.save()
        cable6 = Cable(a_terminations=[interfaces[5]], b_terminations=[front_ports[5]])
        cable6.clean()
        cable6.save()
        cable7 = Cable(a_terminations=[interfaces[6]], b_terminations=[front_ports[6]])
        cable7.clean()
        cable7.save()
        cable8 = Cable(a_terminations=[interfaces[7]], b_terminations=[front_ports[7]])
        cable8.clean()
        cable8.save()
        cable9 = Cable(
            profile=CableProfileChoices.TRUNK_2C2P,
            a_terminations=[rear_ports[0], rear_ports[1]],
            b_terminations=[rear_ports[2], rear_ports[3]]
        )
        cable9.clean()
        cable9.save()

        path1 = self.assertPathExists(
            (
                interfaces[0], cable1, front_ports[0], rear_ports[0], cable9, rear_ports[2], front_ports[4], cable5,
                interfaces[4],
            ),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (
                interfaces[1], cable2, front_ports[1], rear_ports[0], cable9, rear_ports[2], front_ports[5], cable6,
                interfaces[5],
            ),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (
                interfaces[2], cable3, front_ports[2], rear_ports[1], cable9, rear_ports[3], front_ports[6], cable7,
                interfaces[6],
            ),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (
                interfaces[3], cable4, front_ports[3], rear_ports[1], cable9, rear_ports[3], front_ports[7], cable8,
                interfaces[7],
            ),
            is_complete=True,
            is_active=True
        )
        path5 = self.assertPathExists(
            (
                interfaces[4], cable5, front_ports[4], rear_ports[2], cable9, rear_ports[0], front_ports[0], cable1,
                interfaces[0],
            ),
            is_complete=True,
            is_active=True
        )
        path6 = self.assertPathExists(
            (
                interfaces[5], cable6, front_ports[5], rear_ports[2], cable9, rear_ports[0], front_ports[1], cable2,
                interfaces[1],
            ),
            is_complete=True,
            is_active=True
        )
        path7 = self.assertPathExists(
            (
                interfaces[6], cable7, front_ports[6], rear_ports[3], cable9, rear_ports[1], front_ports[2], cable3,
                interfaces[2],
            ),
            is_complete=True,
            is_active=True
        )
        path8 = self.assertPathExists(
            (
                interfaces[7], cable8, front_ports[7], rear_ports[3], cable9, rear_ports[1], front_ports[3], cable4,
                interfaces[3],
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 8)
        for iface in interfaces:
            iface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertPathIsSet(interfaces[4], path5)
        self.assertPathIsSet(interfaces[5], path6)
        self.assertPathIsSet(interfaces[6], path7)
        self.assertPathIsSet(interfaces[7], path8)
        for rear_port in rear_ports:
            rear_port.refresh_from_db()
        self.assertEqual(rear_ports[0].cable_connector, 1)
        self.assertEqual(rear_ports[0].cable_positions, [1, 2])
        self.assertEqual(rear_ports[1].cable_connector, 2)
        self.assertEqual(rear_ports[1].cable_positions, [1, 2])
        self.assertEqual(rear_ports[2].cable_connector, 1)
        self.assertEqual(rear_ports[2].cable_positions, [1, 2])
        self.assertEqual(rear_ports[3].cable_connector, 2)
        self.assertEqual(rear_ports[3].cable_positions, [1, 2])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_105_cable_profile_breakout(self):
        """
        [IF1] --C1-- [FP1][RP1] --C2-- [IF5]
        [IF2] --C3-- [FP2]             [IF6]
        [IF3] --C4-- [FP3]             [IF7]
        [IF4] --C5-- [FP4]             [IF8]

        Cable profile: 1:4 breakout
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
            Interface.objects.create(device=self.device, name='Interface 5'),
            Interface.objects.create(device=self.device, name='Interface 6'),
            Interface.objects.create(device=self.device, name='Interface 7'),
            Interface.objects.create(device=self.device, name='Interface 8'),
        ]
        rear_ports = [
            RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4),
        ]
        front_ports = [
            FrontPort.objects.create(device=self.device, name='Front Port 1'),
            FrontPort.objects.create(device=self.device, name='Front Port 2'),
            FrontPort.objects.create(device=self.device, name='Front Port 3'),
            FrontPort.objects.create(device=self.device, name='Front Port 4'),
        ]
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=front_ports[0],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[1],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[2],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=3,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[3],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=4,
            ),
        ])

        # Create cables
        cable1 = Cable(a_terminations=[interfaces[0]], b_terminations=[front_ports[0]])
        cable1.clean()
        cable1.save()
        cable2 = Cable(a_terminations=[interfaces[1]], b_terminations=[front_ports[1]])
        cable2.clean()
        cable2.save()
        cable3 = Cable(a_terminations=[interfaces[2]], b_terminations=[front_ports[2]])
        cable3.clean()
        cable3.save()
        cable4 = Cable(a_terminations=[interfaces[3]], b_terminations=[front_ports[3]])
        cable4.clean()
        cable4.save()
        cable5 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[rear_ports[0]],
            b_terminations=interfaces[4:8],
        )
        cable5.clean()
        cable5.save()

        path1 = self.assertPathExists(
            (interfaces[0], cable1, front_ports[0], rear_ports[0], cable5, interfaces[4]),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable2, front_ports[1], rear_ports[0], cable5, interfaces[5]),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interfaces[2], cable3, front_ports[2], rear_ports[0], cable5, interfaces[6]),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (interfaces[3], cable4, front_ports[3], rear_ports[0], cable5, interfaces[7]),
            is_complete=True,
            is_active=True
        )
        path5 = self.assertPathExists(
            (interfaces[4], cable5, rear_ports[0], front_ports[0], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        path6 = self.assertPathExists(
            (interfaces[5], cable5, rear_ports[0], front_ports[1], cable2, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        path7 = self.assertPathExists(
            (interfaces[6], cable5, rear_ports[0], front_ports[2], cable3, interfaces[2]),
            is_complete=True,
            is_active=True
        )
        path8 = self.assertPathExists(
            (interfaces[7], cable5, rear_ports[0], front_ports[3], cable4, interfaces[3]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 8)
        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertPathIsSet(interfaces[4], path5)
        self.assertPathIsSet(interfaces[5], path6)
        self.assertPathIsSet(interfaces[6], path7)
        self.assertPathIsSet(interfaces[7], path8)
        self.assertEqual(interfaces[4].cable_connector, 1)
        self.assertEqual(interfaces[4].cable_positions, [1])
        self.assertEqual(interfaces[5].cable_connector, 2)
        self.assertEqual(interfaces[5].cable_positions, [1])
        self.assertEqual(interfaces[6].cable_connector, 3)
        self.assertEqual(interfaces[6].cable_positions, [1])
        self.assertEqual(interfaces[7].cable_connector, 4)
        self.assertEqual(interfaces[7].cable_positions, [1])
        rear_ports[0].refresh_from_db()
        self.assertEqual(rear_ports[0].cable_connector, 1)
        self.assertEqual(rear_ports[0].cable_positions, [1, 2, 3, 4])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_106_cable_profile_shuffle(self):
        """
        [IF1] --C1-- [FP1][RP1] --C17-- [RP3][FP9]  --C9--  [IF9]
        [IF2] --C2-- [FP2]                   [FP10] --C10-- [IF10]
        [IF3] --C3-- [FP3]                   [FP11] --C11-- [IF11]
        [IF4] --C4-- [FP4]                   [FP12] --C12-- [IF12]
        [IF5] --C5-- [FP5][RP2]         [RP4][FP13] --C13-- [IF9]
        [IF6] --C6-- [FP6]                   [FP14] --C14-- [IF10]
        [IF7] --C7-- [FP7]                   [FP15] --C15-- [IF11]
        [IF8] --C8-- [FP8]                   [FP16] --C16-- [IF12]

        Cable profile: Shuffle (2x2 MPO8)
        """
        interfaces = [
            # A side
            Interface.objects.create(device=self.device, name='Interface 1:1'),
            Interface.objects.create(device=self.device, name='Interface 1:2'),
            Interface.objects.create(device=self.device, name='Interface 1:3'),
            Interface.objects.create(device=self.device, name='Interface 1:4'),
            Interface.objects.create(device=self.device, name='Interface 2:1'),
            Interface.objects.create(device=self.device, name='Interface 2:2'),
            Interface.objects.create(device=self.device, name='Interface 2:3'),
            Interface.objects.create(device=self.device, name='Interface 2:4'),
            # B side
            Interface.objects.create(device=self.device, name='Interface 3:1'),
            Interface.objects.create(device=self.device, name='Interface 3:2'),
            Interface.objects.create(device=self.device, name='Interface 3:3'),
            Interface.objects.create(device=self.device, name='Interface 3:4'),
            Interface.objects.create(device=self.device, name='Interface 4:1'),
            Interface.objects.create(device=self.device, name='Interface 4:2'),
            Interface.objects.create(device=self.device, name='Interface 4:3'),
            Interface.objects.create(device=self.device, name='Interface 4:4'),
        ]
        rear_ports = [
            RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4),
            RearPort.objects.create(device=self.device, name='Rear Port 2', positions=4),
            RearPort.objects.create(device=self.device, name='Rear Port 3', positions=4),
            RearPort.objects.create(device=self.device, name='Rear Port 4', positions=4),
        ]
        front_ports = [
            FrontPort.objects.create(device=self.device, name='Front Port 1'),
            FrontPort.objects.create(device=self.device, name='Front Port 2'),
            FrontPort.objects.create(device=self.device, name='Front Port 3'),
            FrontPort.objects.create(device=self.device, name='Front Port 4'),
            FrontPort.objects.create(device=self.device, name='Front Port 5'),
            FrontPort.objects.create(device=self.device, name='Front Port 6'),
            FrontPort.objects.create(device=self.device, name='Front Port 7'),
            FrontPort.objects.create(device=self.device, name='Front Port 8'),
            FrontPort.objects.create(device=self.device, name='Front Port 9'),
            FrontPort.objects.create(device=self.device, name='Front Port 10'),
            FrontPort.objects.create(device=self.device, name='Front Port 11'),
            FrontPort.objects.create(device=self.device, name='Front Port 12'),
            FrontPort.objects.create(device=self.device, name='Front Port 13'),
            FrontPort.objects.create(device=self.device, name='Front Port 14'),
            FrontPort.objects.create(device=self.device, name='Front Port 15'),
            FrontPort.objects.create(device=self.device, name='Front Port 16'),
        ]
        port_mappings = []
        for i, front_port in enumerate(front_ports):
            port_mappings.append(
                PortMapping(
                    device=self.device,
                    front_port=front_ports[i],
                    front_port_position=1,
                    rear_port=rear_ports[int(i / 4)],
                    rear_port_position=(i % 4) + 1,
                ),
            )
        PortMapping.objects.bulk_create(port_mappings)

        # Create cables
        cables = []
        for interface, front_port in zip(interfaces, front_ports):
            cable = Cable(a_terminations=[interface], b_terminations=[front_port])
            cable.clean()
            cable.save()
            cables.append(cable)
        shuffle_cable = Cable(
            profile=CableProfileChoices.TRUNK_2C4P_SHUFFLE,
            a_terminations=rear_ports[0:2],
            b_terminations=rear_ports[2:4],
        )
        shuffle_cable.clean()
        shuffle_cable.save()

        paths = [
            # A-to-B paths
            self.assertPathExists(
                (
                    interfaces[0], cables[0], front_ports[0], rear_ports[0], shuffle_cable, rear_ports[2],
                    front_ports[8], cables[8], interfaces[8],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[1], cables[1], front_ports[1], rear_ports[0], shuffle_cable, rear_ports[2],
                    front_ports[9], cables[9], interfaces[9],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[2], cables[2], front_ports[2], rear_ports[0], shuffle_cable, rear_ports[3],
                    front_ports[12], cables[12], interfaces[12],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[3], cables[3], front_ports[3], rear_ports[0], shuffle_cable, rear_ports[3],
                    front_ports[13], cables[13], interfaces[13],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[4], cables[4], front_ports[4], rear_ports[1], shuffle_cable, rear_ports[2],
                    front_ports[10], cables[10], interfaces[10],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[5], cables[5], front_ports[5], rear_ports[1], shuffle_cable, rear_ports[2],
                    front_ports[11], cables[11], interfaces[11],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[6], cables[6], front_ports[6], rear_ports[1], shuffle_cable, rear_ports[3],
                    front_ports[14], cables[14], interfaces[14],
                ),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (
                    interfaces[7], cables[7], front_ports[7], rear_ports[1], shuffle_cable, rear_ports[3],
                    front_ports[15], cables[15], interfaces[15],
                ),
                is_complete=True,
                is_active=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), len(paths) * 2)

        for i, (interface, path) in enumerate(zip(interfaces, paths)):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, path)
        for i, rear_port in enumerate(rear_ports):
            rear_port.refresh_from_db()
            self.assertEqual(rear_port.cable_connector, (i % 2) + 1)
            self.assertEqual(rear_port.cable_positions, [1, 2, 3, 4])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_202_single_path_via_pass_through_with_breakouts(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF3]
        [IF2]                           [IF4]
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1', positions=4)
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=2,
                rear_port=rearport1,
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=3,
                rear_port=rearport1,
                rear_port_position=3,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=4,
                rear_port=rearport1,
                rear_port_position=4,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[frontport1],
            b_terminations=[interfaces[0], interfaces[1]],
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[rearport1],
            b_terminations=[interfaces[2], interfaces[3]]
        )
        cable2.clean()
        cable2.save()

        paths = [
            self.assertPathExists(
                (interfaces[0], cable1, frontport1, rearport1, cable2, interfaces[2]),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (interfaces[1], cable1, frontport1, rearport1, cable2, interfaces[3]),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (interfaces[2], cable2, rearport1, frontport1, cable1, interfaces[0]),
                is_complete=True,
                is_active=True
            ),
            self.assertPathExists(
                (interfaces[3], cable2, rearport1, frontport1, cable1, interfaces[1]),
                is_complete=True,
                is_active=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), 4)
        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], paths[0])
        self.assertPathIsSet(interfaces[1], paths[1])
        self.assertPathIsSet(interfaces[2], paths[2])
        self.assertPathIsSet(interfaces[3], paths[3])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_204_multiple_paths_via_pass_through_with_breakouts(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C3-- [RP2] [FP3] --C4-- [IF5]
        [IF2]                                              [IF6]
        [IF3] --C2-- [FP2]                    [FP4] --C5-- [IF7]
        [IF4]                                              [IF8]
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
            Interface.objects.create(device=self.device, name='Interface 5'),
            Interface.objects.create(device=self.device, name='Interface 6'),
            Interface.objects.create(device=self.device, name='Interface 7'),
            Interface.objects.create(device=self.device, name='Interface 8'),
        ]
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=8)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=8)
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1', positions=4)
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2', positions=4)
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 2:1', positions=4)
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 2:2', positions=4)
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=2,
                rear_port=rearport1,
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=5,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2,
                front_port_position=2,
                rear_port=rearport1,
                rear_port_position=6,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=2,
                rear_port=rearport2,
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=5,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=2,
                rear_port=rearport2,
                rear_port_position=6,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[frontport1],
            b_terminations=[interfaces[0], interfaces[1]],
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[frontport2],
            b_terminations=[interfaces[2], interfaces[3]],
        )
        cable2.clean()
        cable2.save()
        cable3 = Cable(
            profile=CableProfileChoices.SINGLE_1C8P,
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.clean()
        cable3.save()
        cable4 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[frontport3],
            b_terminations=[interfaces[4], interfaces[5]],
        )
        cable4.clean()
        cable4.save()
        cable5 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[frontport4],
            b_terminations=[interfaces[6], interfaces[7]],
        )
        cable5.clean()
        cable5.save()

        paths = [
            self.assertPathExists(
                (
                    interfaces[0], cable1, frontport1, rearport1, cable3, rearport2, frontport3, cable4,
                    interfaces[4],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[1], cable1, frontport1, rearport1, cable3, rearport2, frontport3, cable4,
                    interfaces[5],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[2], cable2, frontport2, rearport1, cable3, rearport2, frontport4, cable5,
                    interfaces[6],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[3], cable2, frontport2, rearport1, cable3, rearport2, frontport4, cable5,
                    interfaces[7],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[4], cable4, frontport3, rearport2, cable3, rearport1, frontport1, cable1,
                    interfaces[0],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[5], cable4, frontport3, rearport2, cable3, rearport1, frontport1, cable1,
                    interfaces[1],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[6], cable5, frontport4, rearport2, cable3, rearport1, frontport2, cable2,
                    interfaces[2],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[7], cable5, frontport4, rearport2, cable3, rearport1, frontport2, cable2,
                    interfaces[3],
                ),
                is_complete=True,
                is_active=True,
            ),
        ]
        self.assertEqual(CablePath.objects.count(), 8)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], paths[0])
        self.assertPathIsSet(interfaces[1], paths[1])
        self.assertPathIsSet(interfaces[2], paths[2])
        self.assertPathIsSet(interfaces[3], paths[3])
        self.assertPathIsSet(interfaces[4], paths[4])
        self.assertPathIsSet(interfaces[5], paths[5])
        self.assertPathIsSet(interfaces[6], paths[6])
        self.assertPathIsSet(interfaces[7], paths[7])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_212_interface_to_interface_via_circuit_with_breakouts(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [IF3]
        [IF2]                           [IF4]
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='Z'
        )

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[circuittermination1],
            b_terminations=[interfaces[0], interfaces[1]],
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[circuittermination2],
            b_terminations=[interfaces[2], interfaces[3]]
        )
        cable2.clean()
        cable2.save()

        # Check for two complete paths in either direction
        paths = [
            self.assertPathExists(
                (interfaces[0], cable1, circuittermination1, circuittermination2, cable2, interfaces[2]),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (interfaces[1], cable1, circuittermination1, circuittermination2, cable2, interfaces[3]),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (interfaces[2], cable2, circuittermination2, circuittermination1, cable1, interfaces[0]),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (interfaces[3], cable2, circuittermination2, circuittermination1, cable1, interfaces[1]),
                is_complete=True,
                is_active=True,
            ),
        ]
        self.assertEqual(CablePath.objects.count(), 4)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], paths[0])
        self.assertPathIsSet(interfaces[1], paths[1])
        self.assertPathIsSet(interfaces[2], paths[2])
        self.assertPathIsSet(interfaces[3], paths[3])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    # TBD: Is this a topology we want to support?
    @skip("Test applicability TBD")
    def test_217_interface_to_interface_via_rear_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP3] [FP3] --C3-- [IF2]
                     [FP2] [RP2]        [RP4] [FP4]
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
        ]
        rear_ports = [
            RearPort.objects.create(device=self.device, name='Rear Port 1'),
            RearPort.objects.create(device=self.device, name='Rear Port 2'),
            RearPort.objects.create(device=self.device, name='Rear Port 3'),
            RearPort.objects.create(device=self.device, name='Rear Port 4'),
        ]
        front_ports = [
            FrontPort.objects.create(device=self.device, name='Front Port 1'),
            FrontPort.objects.create(device=self.device, name='Front Port 2'),
            FrontPort.objects.create(device=self.device, name='Front Port 3'),
            FrontPort.objects.create(device=self.device, name='Front Port 4'),
        ]
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=front_ports[0],
                front_port_position=1,
                rear_port=rear_ports[0],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[1],
                front_port_position=1,
                rear_port=rear_ports[1],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[2],
                front_port_position=1,
                rear_port=rear_ports[2],
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=front_ports[3],
                front_port_position=1,
                rear_port=rear_ports[3],
                rear_port_position=1,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.SINGLE_2C1P,
            a_terminations=[interfaces[0]],
            b_terminations=[front_ports[0], front_ports[1]]
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            a_terminations=[rear_ports[0], rear_ports[1]],
            b_terminations=[rear_ports[2], rear_ports[3]]
        )
        cable2.clean()
        cable2.save()
        cable3 = Cable(
            profile=CableProfileChoices.SINGLE_2C1P,
            a_terminations=[interfaces[1]],
            b_terminations=[front_ports[2], front_ports[3]]
        )
        cable3.clean()
        cable3.save()

        # Check for one complete path in either direction
        paths = [
            self.assertPathExists(
                (
                    interfaces[0], cable1, (front_ports[0], front_ports[1]), (rear_ports[0], rear_ports[1]), cable2,
                    (rear_ports[2], rear_ports[3]), (front_ports[2], front_ports[3]), cable3, interfaces[1]
                ),
                is_complete=True
            ),
            self.assertPathExists(
                (
                    interfaces[1], cable3, (front_ports[2], front_ports[3]), (rear_ports[2], rear_ports[3]), cable2,
                    (rear_ports[0], rear_ports[1]), (front_ports[0], front_ports[1]), cable1, interfaces[0]
                ),
                is_complete=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), 2)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], paths[0])
        self.assertPathIsSet(interfaces[1], paths[1])

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

    def test_223_single_path_via_multiple_pass_throughs_with_breakouts(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF3]
        [IF2]        [FP2] [RP2]        [IF4]
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=1,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.TRUNK_2C2P,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[frontport1, frontport2]
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.TRUNK_2C2P,
            a_terminations=[rearport1, rearport2],
            b_terminations=[interfaces[2], interfaces[3]]
        )
        cable2.clean()
        cable2.save()

        # Validate paths
        self.assertPathExists(
            (interfaces[0], cable1, frontport1, rearport1, cable2, interfaces[2]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[1], cable1, frontport2, rearport2, cable2, interfaces[3]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[2], cable2, rearport1, frontport1, cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[3], cable2, rearport2, frontport2, cable1, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

    def test_304_add_port_mapping_between_connected_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[rearport1]
        )
        cable2.save()

        # Check for incomplete paths
        self.assertPathExists(
            (interface1, cable1, frontport1),
            is_complete=False,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, rearport1),
            is_complete=False,
            is_active=True
        )

        # Create a PortMapping between frontport1 and rearport1
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1,
        )

        # Check that paths are now complete
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, rearport1, frontport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )

    def test_305_delete_port_mapping_between_connected_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[rearport1]
        )
        cable2.save()
        portmapping1 = PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1,
        )

        # Check for complete paths
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, rearport1, frontport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )

        # Delete the PortMapping between frontport1 and rearport1
        portmapping1.delete()

        # Check that paths are no longer complete
        self.assertPathExists(
            (interface1, cable1, frontport1),
            is_complete=False,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, rearport1),
            is_complete=False,
            is_active=True
        )

    def test_306_change_port_mapping_between_connected_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C3-- [IF3]
        [IF2] --C2-- [FP2] [RP3] --C4-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport2]
        )
        cable2.save()
        cable3 = Cable(
            a_terminations=[interface3],
            b_terminations=[rearport1]
        )
        cable3.save()
        cable4 = Cable(
            a_terminations=[interface4],
            b_terminations=[rearport2]
        )
        cable4.save()
        portmapping1 = PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1,
        )

        # Verify expected initial paths
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable3, interface3),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface3, cable3, rearport1, frontport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )

        # Delete and replace the PortMapping to connect interface1 to interface4
        portmapping1.delete()
        portmapping2 = PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport2,
            rear_port_position=1,
        )

        # Verify expected new paths
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport2, cable4, interface4),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface4, cable4, rearport2, frontport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )

        # Delete and replace the PortMapping to connect interface2 to interface4
        portmapping2.delete()
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport2,
            front_port_position=1,
            rear_port=rearport2,
            rear_port_position=1,
        )

        # Verify expected new paths
        self.assertPathExists(
            (interface2, cable2, frontport2, rearport2, cable4, interface4),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface4, cable4, rearport2, frontport2, cable2, interface2),
            is_complete=True,
            is_active=True
        )
