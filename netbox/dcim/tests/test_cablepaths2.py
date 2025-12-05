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

    def test_101_cable_profile_straight_single(self):
        """
        [IF1] --C1-- [IF2]

        Cable profile: Straight single
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_SINGLE,
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
        self.assertEqual(interfaces[0].cable_position, 1)
        self.assertEqual(interfaces[1].cable_position, 1)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_102_cable_profile_straight_multi(self):
        """
        [IF1] --C1-- [IF3]
        [IF2]        [IF4]

        Cable profile: Straight multi
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
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
        self.assertEqual(interfaces[0].cable_position, 1)
        self.assertEqual(interfaces[1].cable_position, 2)
        self.assertEqual(interfaces[2].cable_position, 1)
        self.assertEqual(interfaces[3].cable_position, 2)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_103_cable_profile_2x2_mpo8(self):
        """
        [IF1:1] --C1-- [IF3:1]
        [IF1:2]        [IF3:2]
        [IF1:3]        [IF3:3]
        [IF1:4]        [IF3:4]
        [IF2:1]        [IF4:1]
        [IF2:2]        [IF4:2]
        [IF2:3]        [IF4:3]
        [IF2:4]        [IF4:4]

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

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.SHUFFLE_2X2_MPO8,
            a_terminations=interfaces[0:8],
            b_terminations=interfaces[8:16],
        )
        cable1.clean()
        cable1.save()

        paths = [
            # A-to-B paths
            self.assertPathExists(
                (interfaces[0], cable1, interfaces[8]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[1], cable1, interfaces[9]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[2], cable1, interfaces[12]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[3], cable1, interfaces[13]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[4], cable1, interfaces[10]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[5], cable1, interfaces[11]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[6], cable1, interfaces[14]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[7], cable1, interfaces[15]), is_complete=True, is_active=True
            ),
            # B-to-A paths
            self.assertPathExists(
                (interfaces[8], cable1, interfaces[0]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[9], cable1, interfaces[1]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[10], cable1, interfaces[4]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[11], cable1, interfaces[5]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[12], cable1, interfaces[2]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[13], cable1, interfaces[3]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[14], cable1, interfaces[6]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[15], cable1, interfaces[7]), is_complete=True, is_active=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), len(paths))

        for i, (interface, path) in enumerate(zip(interfaces, paths)):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, path)
            self.assertEqual(interface.cable_end, 'A' if i < 8 else 'B')
            self.assertEqual(interface.cable_position, (i % 8) + 1)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_104_cable_profile_4x4_mpo8(self):
        """
        [IF1:1] --C1-- [IF3:1]
        [IF1:2]        [IF3:2]
        [IF1:3]        [IF3:3]
        [IF1:4]        [IF3:4]
        [IF2:1]        [IF4:1]
        [IF2:2]        [IF4:2]
        [IF2:3]        [IF4:3]
        [IF2:4]        [IF4:4]

        Cable profile: Shuffle (4x4 MPO8)
        """
        interfaces = [
            # A side
            Interface.objects.create(device=self.device, name='Interface 1:1'),
            Interface.objects.create(device=self.device, name='Interface 1:2'),
            Interface.objects.create(device=self.device, name='Interface 2:1'),
            Interface.objects.create(device=self.device, name='Interface 2:2'),
            Interface.objects.create(device=self.device, name='Interface 3:1'),
            Interface.objects.create(device=self.device, name='Interface 3:2'),
            Interface.objects.create(device=self.device, name='Interface 4:1'),
            Interface.objects.create(device=self.device, name='Interface 4:2'),
            # B side
            Interface.objects.create(device=self.device, name='Interface 5:1'),
            Interface.objects.create(device=self.device, name='Interface 5:2'),
            Interface.objects.create(device=self.device, name='Interface 6:1'),
            Interface.objects.create(device=self.device, name='Interface 6:2'),
            Interface.objects.create(device=self.device, name='Interface 7:1'),
            Interface.objects.create(device=self.device, name='Interface 7:2'),
            Interface.objects.create(device=self.device, name='Interface 8:1'),
            Interface.objects.create(device=self.device, name='Interface 8:2'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.SHUFFLE_4X4_MPO8,
            a_terminations=interfaces[0:8],
            b_terminations=interfaces[8:16],
        )
        cable1.clean()
        cable1.save()

        paths = [
            # A-to-B paths
            self.assertPathExists(
                (interfaces[0], cable1, interfaces[8]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[1], cable1, interfaces[10]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[2], cable1, interfaces[12]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[3], cable1, interfaces[14]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[4], cable1, interfaces[9]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[5], cable1, interfaces[11]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[6], cable1, interfaces[13]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[7], cable1, interfaces[15]), is_complete=True, is_active=True
            ),
            # B-to-A paths
            self.assertPathExists(
                (interfaces[8], cable1, interfaces[0]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[9], cable1, interfaces[4]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[10], cable1, interfaces[1]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[11], cable1, interfaces[5]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[12], cable1, interfaces[2]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[13], cable1, interfaces[6]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[14], cable1, interfaces[3]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[15], cable1, interfaces[7]), is_complete=True, is_active=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), len(paths))

        for i, (interface, path) in enumerate(zip(interfaces, paths)):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, path)
            self.assertEqual(interface.cable_end, 'A' if i < 8 else 'B')
            self.assertEqual(interface.cable_position, (i % 8) + 1)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=frontport1,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=1,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[frontport1],
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
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
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF4]
        [IF2]                                                  [IF5]
        [IF3] --C2-- [FP1:2]                    [FP2:2] --C5-- [IF6]
        [IF4]                                                  [IF7]
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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=4)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
        frontport2_1 = FrontPort.objects.create(device=self.device, name='Front Port 2:1')
        frontport2_2 = FrontPort.objects.create(device=self.device, name='Front Port 2:2')
        PortMapping.objects.bulk_create([
            PortMapping(
                device=self.device,
                front_port=frontport1_1,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1_2,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2_1,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2_2,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=2,
            ),
        ])

        # Create cables
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[frontport1_1]
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[2], interfaces[3]],
            b_terminations=[frontport1_2]
        )
        cable2.clean()
        cable2.save()
        cable3 = Cable(
            profile=CableProfileChoices.STRAIGHT_SINGLE,
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.clean()
        cable3.save()
        cable4 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[frontport2_1],
            b_terminations=[interfaces[4], interfaces[5]]
        )
        cable4.clean()
        cable4.save()
        cable5 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[frontport2_2],
            b_terminations=[interfaces[6], interfaces[7]]
        )
        cable5.clean()
        cable5.save()

        paths = [
            self.assertPathExists(
                (
                    interfaces[0], cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1, cable4,
                    interfaces[4],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[1], cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1, cable4,
                    interfaces[5],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[2], cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2, cable5,
                    interfaces[6],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[3], cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2, cable5,
                    interfaces[7],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[4], cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1, cable1,
                    interfaces[0],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[5], cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1, cable1,
                    interfaces[1],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[6], cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2, cable2,
                    interfaces[2],
                ),
                is_complete=True,
                is_active=True,
            ),
            self.assertPathExists(
                (
                    interfaces[7], cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2, cable2,
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
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[circuittermination1]
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
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
            profile=CableProfileChoices.STRAIGHT_MULTI,
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
            profile=CableProfileChoices.STRAIGHT_MULTI,
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
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[frontport1, frontport2]
        )
        cable1.clean()
        cable1.save()
        cable2 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[rearport1, rearport2],
            b_terminations=[interfaces[2], interfaces[3]]
        )
        cable2.clean()
        cable2.save()

        # Validate paths
        self.assertPathExists(
            (interfaces[0], cable1, [frontport1, frontport2], [rearport1, rearport2], cable2, interfaces[2]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[1], cable1, [frontport1, frontport2], [rearport1, rearport2], cable2, interfaces[3]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[2], cable2, [rearport1, rearport2], [frontport1, frontport2], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interfaces[3], cable2, [rearport1, rearport2], [frontport1, frontport2], cable1, interfaces[1]),
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
