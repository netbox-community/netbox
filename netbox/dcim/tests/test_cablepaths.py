from io import StringIO

from django.core.management import call_command

from circuits.models import *
from dcim.choices import CableEndChoices, LinkStatusChoices
from dcim.models import *
from dcim.svg import CableTraceSVG
from dcim.tests.utils import BaseCablePathTestCase
from dcim.utils import create_cablepaths, object_to_path_node
from utilities.exceptions import AbortRequest


class LegacyCablePathTestCase(BaseCablePathTestCase):
    """
    Test NetBox's ability to trace and retrace CablePaths in response to data model changes, without cable profiles.

    Tests are numbered as follows:
        1XX: Test direct connections between different endpoint types
        2XX: Test different cable topologies
        3XX: Test responses to changes in existing objects
        4XX: Test to exclude specific cable topologies
    """
    def _create_cable_raw(self, termination_a, termination_b, status=LinkStatusChoices.STATUS_CONNECTED):
        """
        Write a Cable and its terminations directly to the database, bypassing Cable.save(). Unprofiled
        cables only: the connector & positions a profile assigns are not replicated here.
        """
        cable = Cable(status=status)
        cable.save_base(raw=True)

        for termination, cable_end in (
            (termination_a, CableEndChoices.SIDE_A),
            (termination_b, CableEndChoices.SIDE_B),
        ):
            ct = CableTermination(cable=cable, cable_end=cable_end, termination=termination)
            ct.cache_related_objects()
            ct.save_base(raw=True)
            termination.cable = cable
            termination.cable_end = cable_end
            termination.save()

        return cable

    def test_101_interface_to_interface(self):
        """
        [IF1] --C1-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[interface2]
        )
        cable1.save()

        path1 = self.assertPathExists(
            (interface1, cable1, interface2),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interface2, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

        # Check that connected interfaces are fully cleaned up
        interface1.refresh_from_db()
        interface2.refresh_from_db()

        self.assertIsNone(interface1.cable_id)
        self.assertIsNone(interface1.cable_end)
        self.assertPathIsNotSet(interface1)

        self.assertIsNone(interface2.cable_id)
        self.assertIsNone(interface2.cable_end)
        self.assertPathIsNotSet(interface2)

    def test_102_consoleport_to_consoleserverport(self):
        """
        [CP1] --C1-- [CSP1]
        """
        consoleport1 = ConsolePort.objects.create(device=self.device, name='Console Port 1')
        consoleserverport1 = ConsoleServerPort.objects.create(device=self.device, name='Console Server Port 1')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[consoleport1],
            b_terminations=[consoleserverport1]
        )
        cable1.save()

        path1 = self.assertPathExists(
            (consoleport1, cable1, consoleserverport1),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (consoleserverport1, cable1, consoleport1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        consoleport1.refresh_from_db()
        consoleserverport1.refresh_from_db()
        self.assertPathIsSet(consoleport1, path1)
        self.assertPathIsSet(consoleserverport1, path2)

        # Test SVG generation
        CableTraceSVG(consoleport1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_103_powerport_to_poweroutlet(self):
        """
        [PP1] --C1-- [PO1]
        """
        powerport1 = PowerPort.objects.create(device=self.device, name='Power Port 1')
        poweroutlet1 = PowerOutlet.objects.create(device=self.device, name='Power Outlet 1')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[powerport1],
            b_terminations=[poweroutlet1]
        )
        cable1.save()

        path1 = self.assertPathExists(
            (powerport1, cable1, poweroutlet1),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (poweroutlet1, cable1, powerport1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        powerport1.refresh_from_db()
        poweroutlet1.refresh_from_db()
        self.assertPathIsSet(powerport1, path1)
        self.assertPathIsSet(poweroutlet1, path2)

        # Test SVG generation
        CableTraceSVG(powerport1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_104_powerport_to_powerfeed(self):
        """
        [PP1] --C1-- [PF1]
        """
        powerport1 = PowerPort.objects.create(device=self.device, name='Power Port 1')
        powerfeed1 = PowerFeed.objects.create(power_panel=self.powerpanel, name='Power Feed 1')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[powerport1],
            b_terminations=[powerfeed1]
        )
        cable1.save()

        path1 = self.assertPathExists(
            (powerport1, cable1, powerfeed1),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (powerfeed1, cable1, powerport1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        powerport1.refresh_from_db()
        powerfeed1.refresh_from_db()
        self.assertPathIsSet(powerport1, path1)
        self.assertPathIsSet(powerfeed1, path2)

        # Test SVG generation
        CableTraceSVG(powerport1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_120_single_interface_to_multi_interface(self):
        """
        [IF1] --C1-- [IF2]
                     [IF3]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[interface2, interface3]
        )
        cable1.save()

        path1 = self.assertPathExists(
            (interface1, cable1, (interface2, interface3)),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            ((interface2, interface3), cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)
        self.assertPathIsSet(interface3, path2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        self.assertPathIsNotSet(interface1)
        self.assertPathIsNotSet(interface2)
        self.assertPathIsNotSet(interface3)

    def test_121_multi_interface_to_multi_interface(self):
        """
        [IF1] --C1-- [IF3]
        [IF2]        [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1, interface2],
            b_terminations=[interface3, interface4]
        )
        cable1.save()

        path1 = self.assertPathExists(
            ((interface1, interface2), cable1, (interface3, interface4)),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            ((interface3, interface4), cable1, (interface1, interface2)),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path1)
        self.assertPathIsSet(interface3, path2)
        self.assertPathIsSet(interface4, path2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsNotSet(interface1)
        self.assertPathIsNotSet(interface2)
        self.assertPathIsNotSet(interface3)
        self.assertPathIsNotSet(interface4)

    def test_201_single_path_via_pass_through(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[interface2]
        )
        cable2.save()
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
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            (interface1, cable1, frontport1, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsNotSet(interface2)

    def test_202_single_path_via_pass_through_with_breakouts(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF3]
        [IF2]                           [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1, interface2],
            b_terminations=[frontport1]
        )
        cable1.save()
        self.assertPathExists(
            ([interface1, interface2], cable1, frontport1, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[interface3, interface4]
        )
        cable2.save()
        self.assertPathExists(
            ([interface1, interface2], cable1, frontport1, rearport1, cable2, [interface3, interface4]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            ([interface3, interface4], cable2, rearport1, frontport1, cable1, [interface1, interface2]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            ([interface1, interface2], cable1, frontport1, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path1)
        self.assertPathIsNotSet(interface3)
        self.assertPathIsNotSet(interface4)

    def test_203_multiple_paths_via_pass_through(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:2] --C5-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
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

        # Create cables 1-2
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        self.assertPathExists(
            (interface1, cable1, frontport1_1, rearport1),
            is_complete=False
        )
        self.assertPathExists(
            (interface2, cable2, frontport1_2, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.save()
        self.assertPathExists(
            (interface1, cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1),
            is_complete=False
        )
        self.assertPathExists(
            (interface2, cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cables 4-5
        cable4 = Cable(
            a_terminations=[frontport2_1],
            b_terminations=[interface3]
        )
        cable4.save()
        cable5 = Cable(
            a_terminations=[frontport2_2],
            b_terminations=[interface4]
        )
        cable5.save()
        path1 = self.assertPathExists(
            (interface1, cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1, cable4, interface3),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interface2, cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2, cable5, interface4),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interface3, cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (interface4, cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2, cable2, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)
        self.assertPathIsSet(interface3, path3)
        self.assertPathIsSet(interface4, path4)

    def test_204_multiple_paths_via_pass_through_with_breakouts(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF4]
        [IF2]                                                  [IF5]
        [IF3] --C2-- [FP1:2]                    [FP2:2] --C5-- [IF6]
        [IF4]                                                  [IF7]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        interface5 = Interface.objects.create(device=self.device, name='Interface 5')
        interface6 = Interface.objects.create(device=self.device, name='Interface 6')
        interface7 = Interface.objects.create(device=self.device, name='Interface 7')
        interface8 = Interface.objects.create(device=self.device, name='Interface 8')
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

        # Create cables 1-2
        cable1 = Cable(
            a_terminations=[interface1, interface2],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface3, interface4],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        self.assertPathExists(
            ([interface1, interface2], cable1, frontport1_1, rearport1),
            is_complete=False
        )
        self.assertPathExists(
            ([interface3, interface4], cable2, frontport1_2, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.save()
        self.assertPathExists(
            ([interface1, interface2], cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1),
            is_complete=False
        )
        self.assertPathExists(
            ([interface3, interface4], cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cables 4-5
        cable4 = Cable(
            a_terminations=[frontport2_1],
            b_terminations=[interface5, interface6]
        )
        cable4.save()
        cable5 = Cable(
            a_terminations=[frontport2_2],
            b_terminations=[interface7, interface8]
        )
        cable5.save()
        path1 = self.assertPathExists(
            (
                [interface1, interface2],
                cable1,
                frontport1_1,
                rearport1,
                cable3,
                rearport2,
                frontport2_1,
                cable4,
                [interface5, interface6],
            ),
            is_complete=True,
            is_active=True,
        )
        path2 = self.assertPathExists(
            (
                [interface3, interface4],
                cable2,
                frontport1_2,
                rearport1,
                cable3,
                rearport2,
                frontport2_2,
                cable5,
                [interface7, interface8],
            ),
            is_complete=True,
            is_active=True,
        )
        path3 = self.assertPathExists(
            (
                [interface5, interface6],
                cable4,
                frontport2_1,
                rearport2,
                cable3,
                rearport1,
                frontport1_1,
                cable1,
                [interface1, interface2],
            ),
            is_complete=True,
            is_active=True,
        )
        path4 = self.assertPathExists(
            (
                [interface7, interface8],
                cable5,
                frontport2_2,
                rearport2,
                cable3,
                rearport1,
                frontport1_2,
                cable2,
                [interface3, interface4],
            ),
            is_complete=True,
            is_active=True,
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        interface5.refresh_from_db()
        interface6.refresh_from_db()
        interface7.refresh_from_db()
        interface8.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path1)
        self.assertPathIsSet(interface3, path2)
        self.assertPathIsSet(interface4, path2)
        self.assertPathIsSet(interface5, path3)
        self.assertPathIsSet(interface6, path3)
        self.assertPathIsSet(interface7, path4)
        self.assertPathIsSet(interface8, path4)

    def test_205_multiple_paths_via_nested_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP2] [RP2] --C4-- [RP3] [FP3] --C5-- [RP4] [FP4:1] --C6-- [IF3]
        [IF2] --C2-- [FP1:2]                                                          [FP4:2] --C7-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=4)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4_1 = FrontPort.objects.create(device=self.device, name='Front Port 4:1')
        frontport4_2 = FrontPort.objects.create(device=self.device, name='Front Port 4:2')
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
                front_port=frontport2,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4_1,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4_2,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=2,
            ),
        ])

        # Create cables 1-2, 6-7
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        cable6 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport4_1]
        )
        cable6.save()
        cable7 = Cable(
            a_terminations=[interface4],
            b_terminations=[frontport4_2]
        )
        cable7.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3 and 5
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[frontport2]
        )
        cable3.save()
        cable5 = Cable(
            a_terminations=[rearport4],
            b_terminations=[frontport3]
        )
        cable5.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four (longer) partial paths; one from each interface

        # Create cable 4
        cable4 = Cable(
            a_terminations=[rearport2],
            b_terminations=[rearport3]
        )
        cable4.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1_1, rearport1, cable3, frontport2, rearport2, cable4, rearport3,
                frontport3, cable5, rearport4, frontport4_1, cable6, interface3,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable2, frontport1_2, rearport1, cable3, frontport2, rearport2, cable4, rearport3,
                frontport3, cable5, rearport4, frontport4_2, cable7, interface4,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable6, frontport4_1, rearport4, cable5, frontport3, rearport3, cable4, rearport2,
                frontport2, cable3, rearport1, frontport1_1, cable1, interface1,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface4, cable7, frontport4_2, rearport4, cable5, frontport3, rearport3, cable4, rearport2,
                frontport2, cable3, rearport1, frontport1_2, cable2, interface2,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)

    def test_206_multiple_paths_via_multiple_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [FP3:1] [RP3] --C6-- [RP4] [FP4:1] --C7-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:1] --C5-- [FP3:1]                    [FP4:2] --C8-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=4)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=4)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=4)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
        frontport2_1 = FrontPort.objects.create(device=self.device, name='Front Port 2:1')
        frontport2_2 = FrontPort.objects.create(device=self.device, name='Front Port 2:2')
        frontport3_1 = FrontPort.objects.create(device=self.device, name='Front Port 3:1')
        frontport3_2 = FrontPort.objects.create(device=self.device, name='Front Port 3:2')
        frontport4_1 = FrontPort.objects.create(device=self.device, name='Front Port 4:1')
        frontport4_2 = FrontPort.objects.create(device=self.device, name='Front Port 4:2')
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
            PortMapping(
                device=self.device,
                front_port=frontport3_1,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3_2,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=2,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4_1,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4_2,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=2,
            ),
        ])

        # Create cables 1-3, 6-8
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.save()
        cable6 = Cable(
            a_terminations=[rearport3],
            b_terminations=[rearport4]
        )
        cable6.save()
        cable7 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport4_1]
        )
        cable7.save()
        cable8 = Cable(
            a_terminations=[interface4],
            b_terminations=[frontport4_2]
        )
        cable8.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 4 and 5
        cable4 = Cable(
            a_terminations=[frontport2_1],
            b_terminations=[frontport3_1]
        )
        cable4.save()
        cable5 = Cable(
            a_terminations=[frontport2_2],
            b_terminations=[frontport3_2]
        )
        cable5.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1,
                cable4, frontport3_1, rearport3, cable6, rearport4, frontport4_1,
                cable7, interface3,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2,
                cable5, frontport3_2, rearport3, cable6, rearport4, frontport4_2,
                cable8, interface4,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable7, frontport4_1, rearport4, cable6, rearport3, frontport3_1,
                cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1,
                cable1, interface1,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface4, cable8, frontport4_2, rearport4, cable6, rearport3, frontport3_2,
                cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2,
                cable2, interface2,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 5
        cable5.delete()

        # Check for two complete paths (IF1 <--> IF2) and two partial (IF3 <--> IF4)
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 2)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 2)

    def test_207_multiple_paths_via_patched_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP2] [RP2] --C4-- [RP3] [FP3:1] --C5-- [IF3]
        [IF2] --C2-- [FP1:2]                                       [FP3:2] --C6-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=4)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3_1 = FrontPort.objects.create(device=self.device, name='Front Port 3:1')
        frontport3_2 = FrontPort.objects.create(device=self.device, name='Front Port 3:2')
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
                front_port=frontport2,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3_1,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport3_2,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=2,
            ),
        ])

        # Create cables 1-2, 5-6
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        cable5 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport3_1]
        )
        cable5.save()
        cable6 = Cable(
            a_terminations=[interface4],
            b_terminations=[frontport3_2]
        )
        cable6.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3-4
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[frontport2]
        )
        cable3.save()
        cable4 = Cable(
            a_terminations=[rearport2],
            b_terminations=[rearport3]
        )
        cable4.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1_1, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3_1, cable5, interface3,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable2, frontport1_2, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3_2, cable6, interface4,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable5, frontport3_1, rearport3, cable4, rearport2, frontport2,
                cable3, rearport1, frontport1_1, cable1, interface1,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface4, cable6, frontport3_2, rearport3, cable4, rearport2, frontport2,
                cable3, rearport1, frontport1_2, cable2, interface2,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)

    def test_208_unidirectional_split_paths(self):
        """
        [IF1] --C1-- [RP1] [FP1:1] --C2-- [IF2]
                           [FP1:2] --C3-- [IF3]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=2)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
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
        ])

        # Create cables 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[rearport1]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, rearport1),
            is_complete=False,
            is_split=True
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cables 2-3
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_1]
        )
        cable2.save()
        cable3 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport1_2]
        )
        cable3.save()
        self.assertPathExists(
            (interface2, cable2, frontport1_1, rearport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface3, cable3, frontport1_2, rearport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 3)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()

        # Check that the partial path was deleted and the two complete paths are now partial
        self.assertPathExists(
            (interface2, cable2, frontport1_1, rearport1),
            is_complete=False
        )
        self.assertPathExists(
            (interface3, cable3, frontport1_2, rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_209_rearport_without_frontport(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            front_port=frontport1, front_port_position=1, rear_port=rearport1, rear_port_position=1,
        )

        # Create cables
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable2.save()
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, rearport2),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Test SVG generation
        CableTraceSVG(interface1).render()

    def test_210_interface_to_circuittermination(self):
        """
        [IF1] --C1-- [CT1]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1]
        )
        cable1.save()

        # Check for incomplete path
        self.assertPathExists(
            (interface1, cable1, circuittermination1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_211_interface_to_interface_via_circuit(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1]
        )
        cable1.save()

        # Check for partial path from interface1
        self.assertPathExists(
            (interface1, cable1, circuittermination1),
            is_complete=False
        )

        # Create CT2
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='Z'
        )

        # Check for partial path to site
        self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, self.site),
            is_active=True
        )

        # Create cable 2
        cable2 = Cable(
            a_terminations=[circuittermination2],
            b_terminations=[interface2]
        )
        cable2.save()

        # Check for complete path in each direction
        self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, cable2, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, circuittermination2, circuittermination1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, self.site),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsNotSet(interface2)

    def test_212_interface_to_interface_via_circuit_with_breakouts(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [IF3]
        [IF2]                           [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1, interface2],
            b_terminations=[circuittermination1]
        )
        cable1.save()

        # Check for partial path from interface1
        self.assertPathExists(
            ([interface1, interface2], cable1, circuittermination1),
            is_complete=False
        )

        # Create CT2
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='Z'
        )

        # Check for partial path to site
        self.assertPathExists(
            ([interface1, interface2], cable1, circuittermination1, circuittermination2, self.site),
            is_active=True
        )

        # Create cable 2
        cable2 = Cable(
            a_terminations=[circuittermination2],
            b_terminations=[interface3, interface4]
        )
        cable2.save()

        # Check for complete path in each direction
        self.assertPathExists(
            (
                [interface1, interface2],
                cable1,
                circuittermination1,
                circuittermination2,
                cable2,
                [interface3, interface4],
            ),
            is_complete=True,
            is_active=True,
        )
        self.assertPathExists(
            (
                [interface3, interface4],
                cable2,
                circuittermination2,
                circuittermination1,
                cable1,
                [interface1, interface2],
            ),
            is_complete=True,
            is_active=True,
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            ([interface1, interface2], cable1, circuittermination1, circuittermination2, self.site),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path1)
        self.assertPathIsNotSet(interface3)
        self.assertPathIsNotSet(interface4)

    def test_213_interface_to_site_via_circuit(self):
        """
        [IF1] --C1-- [CT1] [CT2] --> [Site2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        site2 = Site.objects.create(name='Site 2', slug='site-2')
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=site2,
            term_side='Z'
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, site2),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_214_interface_to_providernetwork_via_circuit(self):
        """
        [IF1] --C1-- [CT1] [CT2] --> [PN1]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        providernetwork = ProviderNetwork.objects.create(name='Provider Network 1', provider=self.circuit.provider)
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=providernetwork,
            term_side='Z'
        )

        # Create cable 1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, providernetwork),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)
        self.assertTrue(CablePath.objects.first().is_complete)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_215_multiple_paths_via_circuit(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [CT1] [CT2] --C4-- [RP2] [FP2:1] --C5-- [IF3]
        [IF2] --C2-- [FP1:2]                                       [FP2:2] --C6-- [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
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
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site, term_side='Z'
        )

        # Create cables
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_2]
        )
        cable2.save()
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[circuittermination1]
        )
        cable3.save()
        cable4 = Cable(
            a_terminations=[rearport2],
            b_terminations=[circuittermination2]
        )
        cable4.save()
        cable5 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport2_1]
        )
        cable5.save()
        cable6 = Cable(
            a_terminations=[interface4],
            b_terminations=[frontport2_2]
        )
        cable6.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1_1, rearport1, cable3, circuittermination1, circuittermination2,
                cable4, rearport2, frontport2_1, cable5, interface3,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable2, frontport1_2, rearport1, cable3, circuittermination1, circuittermination2,
                cable4, rearport2, frontport2_2, cable6, interface4,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable5, frontport2_1, rearport2, cable4, circuittermination2, circuittermination1,
                cable3, rearport1, frontport1_1, cable1, interface1,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface4, cable6, frontport2_2, rearport2, cable4, circuittermination2, circuittermination1,
                cable3, rearport1, frontport1_2, cable2, interface2,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cables 3-4
        cable3.delete()
        cable4.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)

    def test_216_interface_to_interface_via_multiple_circuits(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [CT3] [CT4] --C3-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuit2 = Circuit.objects.create(provider=self.circuit.provider, type=self.circuit.type, cid='Circuit 2')
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
        circuittermination3 = CircuitTermination.objects.create(
            circuit=circuit2,
            termination=self.site,
            term_side='A'
        )
        circuittermination4 = CircuitTermination.objects.create(
            circuit=circuit2,
            termination=self.site,
            term_side='Z'
        )

        # Create cables
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[circuittermination2],
            b_terminations=[circuittermination3]
        )
        cable2.save()
        cable3 = Cable(
            a_terminations=[circuittermination4],
            b_terminations=[interface2]
        )
        cable3.save()

        # Check for paths
        self.assertPathExists(
            (
                interface1, cable1, circuittermination1, circuittermination2, cable2, circuittermination3,
                circuittermination4, cable3, interface2,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable3, circuittermination4, circuittermination3, cable2, circuittermination2,
                circuittermination1, cable1, interface1,
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, self.site),
            is_active=True
        )
        path2 = self.assertPathExists(
            (interface2, cable3, circuittermination4, circuittermination3, self.site),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

    def test_217_interface_to_interface_via_rear_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP3] [FP3] --C3-- [IF2]
                     [FP2] [RP2]        [RP4] [FP4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 4')
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
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
        ])

        # Create cables 1-2
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1, frontport2]
        )
        cable1.save()
        cable3 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport3, frontport4]
        )
        cable3.save()
        self.assertPathExists(
            (interface1, cable1, (frontport1, frontport2), (rearport1, rearport2)),
            is_complete=False
        )
        self.assertPathExists(
            (interface2, cable3, (frontport3, frontport4), (rearport3, rearport4)),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 2
        cable2 = Cable(
            a_terminations=[rearport1, rearport2],
            b_terminations=[rearport3, rearport4]
        )
        cable2.save()
        path1 = self.assertPathExists(
            (
                interface1, cable1, (frontport1, frontport2), (rearport1, rearport2), cable2,
                (rearport3, rearport4), (frontport3, frontport4), cable3, interface2
            ),
            is_complete=True
        )
        path2 = self.assertPathExists(
            (
                interface2, cable3, (frontport3, frontport4), (rearport3, rearport4), cable2,
                (rearport1, rearport2), (frontport1, frontport2), cable1, interface1
            ),
            is_complete=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 2
        cable2.delete()

        # Check for two partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 2)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

    def test_218_interfaces_to_interfaces_via_multiposition_rear_ports(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF3]
                     [FP1:2]                    [FP2:2]
        [IF2] --C2-- [FP1:3]                    [FP2:3] --C5-- [IF4]
                     [FP1:4]                    [FP2:4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=4)
        frontport1_1 = FrontPort.objects.create(device=self.device, name='Front Port 1:1')
        frontport1_2 = FrontPort.objects.create(device=self.device, name='Front Port 1:2')
        frontport1_3 = FrontPort.objects.create(device=self.device, name='Front Port 1:3')
        frontport1_4 = FrontPort.objects.create(device=self.device, name='Front Port 1:4')
        frontport2_1 = FrontPort.objects.create(device=self.device, name='Front Port 2:1')
        frontport2_2 = FrontPort.objects.create(device=self.device, name='Front Port 2:2')
        frontport2_3 = FrontPort.objects.create(device=self.device, name='Front Port 2:3')
        frontport2_4 = FrontPort.objects.create(device=self.device, name='Front Port 2:4')
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
                front_port=frontport1_3,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=3,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport1_4,
                front_port_position=1,
                rear_port=rearport1,
                rear_port_position=4,
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
            PortMapping(
                device=self.device,
                front_port=frontport2_3,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=3,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport2_4,
                front_port_position=1,
                rear_port=rearport2,
                rear_port_position=4,
            ),
        ])

        # Create cables 1-2
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1_1, frontport1_2]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[frontport1_3, frontport1_4]
        )
        cable2.save()
        self.assertPathExists(
            (interface1, cable1, (frontport1_1, frontport1_2), rearport1),
            is_complete=False
        )
        self.assertPathExists(
            (interface2, cable2, (frontport1_3, frontport1_4), rearport1),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable3.save()
        self.assertPathExists(
            (
                interface1,
                cable1,
                (frontport1_1, frontport1_2),
                rearport1,
                cable3,
                rearport2,
                (frontport2_1, frontport2_2),
            ),
            is_complete=False,
        )
        self.assertPathExists(
            (
                interface2,
                cable2,
                (frontport1_3, frontport1_4),
                rearport1,
                cable3,
                rearport2,
                (frontport2_3, frontport2_4),
            ),
            is_complete=False,
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cables 4-5
        cable4 = Cable(a_terminations=[frontport2_1, frontport2_2], b_terminations=[interface3])
        cable4.save()
        cable5 = Cable(a_terminations=[frontport2_3, frontport2_4], b_terminations=[interface4])
        cable5.save()
        path1 = self.assertPathExists(
            (
                interface1,
                cable1,
                (frontport1_1, frontport1_2),
                rearport1,
                cable3,
                rearport2,
                (frontport2_1, frontport2_2),
                cable4,
                interface3,
            ),
            is_complete=True,
            is_active=True,
        )
        path2 = self.assertPathExists(
            (
                interface2,
                cable2,
                (frontport1_3, frontport1_4),
                rearport1,
                cable3,
                rearport2,
                (frontport2_3, frontport2_4),
                cable5,
                interface4,
            ),
            is_complete=True,
            is_active=True,
        )
        path3 = self.assertPathExists(
            (
                interface3,
                cable4,
                (frontport2_1, frontport2_2),
                rearport2,
                cable3,
                rearport1,
                (frontport1_1, frontport1_2),
                cable1,
                interface1,
            ),
            is_complete=True,
            is_active=True,
        )
        path4 = self.assertPathExists(
            (
                interface4,
                cable5,
                (frontport2_3, frontport2_4),
                rearport2,
                cable3,
                rearport1,
                (frontport1_3, frontport1_4),
                cable2,
                interface2,
            ),
            is_complete=True,
            is_active=True,
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Test SVG generation
        CableTraceSVG(interface1).render()

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(is_complete=False).count(), 4)
        self.assertEqual(CablePath.objects.filter(is_complete=True).count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)
        self.assertPathIsSet(interface3, path3)
        self.assertPathIsSet(interface4, path4)

    def test_219_interface_to_interface_duplex_via_multiple_rearports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- [IF2]
                     [FP3] [RP3] --C4-- [RP4] [FP4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 4')
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
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
        ])

        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable2.save()
        cable4 = Cable(
            a_terminations=[rearport3],
            b_terminations=[rearport4]
        )
        cable4.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1, frontport3]
        )
        cable1.save()
        self.assertPathExists(
            (
                interface1, cable1, (frontport1, frontport3), (rearport1, rearport3), (cable2, cable4),
                (rearport2, rearport4), (frontport2, frontport4)
            ),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[frontport2, frontport4],
            b_terminations=[interface2]
        )
        cable3.save()
        self.assertPathExists(
            (
                interface1, cable1, (frontport1, frontport3), (rearport1, rearport3), (cable2, cable4),
                (rearport2, rearport4), (frontport2, frontport4), cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable3, (frontport2, frontport4), (rearport2, rearport4), (cable2, cable4),
                (rearport1, rearport3), (frontport1, frontport3), cable1, interface1
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Test SVG generation
        CableTraceSVG(interface1).render()

    def test_220_interface_to_interface_duplex_via_multiple_front_and_rear_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- [IF2]
        [IF2] --C5-- [FP3] [RP3] --C4-- [RP4] [FP4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 4')
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
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
        ])

        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable2.save()
        cable4 = Cable(
            a_terminations=[rearport3],
            b_terminations=[rearport4]
        )
        cable4.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2
            ),
            is_complete=False
        )
        # Create cable1
        cable5 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport3]
        )
        cable5.save()
        self.assertPathExists(
            (
                interface3, cable5, frontport3, rearport3, cable4, rearport4, frontport4
            ),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[frontport2, frontport4],
            b_terminations=[interface2]
        )
        cable3.save()
        self.assertPathExists(
            (
                interface2, cable3, (frontport2, frontport4), (rearport2, rearport4), (cable2, cable4),
                (rearport1, rearport3), (frontport1, frontport3), (cable1, cable5), (interface1, interface3)
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2, cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable5, frontport3, rearport3, cable4, rearport4, frontport4, cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 3)

        # Test SVG generation
        CableTraceSVG(interface1).render()

    def test_221_non_symmetric_paths(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- -------------------------------------- [IF2]
        [IF2] --C5-- [FP3] [RP3] --C4-- [RP4] [FP4] --C6-- [FP5] [RP5] --C7-- [RP6] [FP6] --C3---/
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4')
        rearport5 = RearPort.objects.create(device=self.device, name='Rear Port 5')
        rearport6 = RearPort.objects.create(device=self.device, name='Rear Port 6')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 4')
        frontport5 = FrontPort.objects.create(device=self.device, name='Front Port 5')
        frontport6 = FrontPort.objects.create(device=self.device, name='Front Port 6')
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
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport5,
                front_port_position=1,
                rear_port=rearport5,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport6,
                front_port_position=1,
                rear_port=rearport6,
                rear_port_position=1,
            ),
        ])

        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2],
            label='C2'
        )
        cable2.save()
        cable4 = Cable(
            a_terminations=[rearport3],
            b_terminations=[rearport4],
            label='C4'
        )
        cable4.save()
        cable6 = Cable(
            a_terminations=[frontport4],
            b_terminations=[frontport5],
            label='C6'
        )
        cable6.save()
        cable7 = Cable(
            a_terminations=[rearport5],
            b_terminations=[rearport6],
            label='C7'
        )
        cable7.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1],
            label='C1'
        )
        cable1.save()
        self.assertPathExists(
            (
                interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2
            ),
            is_complete=False
        )
        # Create cable1
        cable5 = Cable(
            a_terminations=[interface3],
            b_terminations=[frontport3],
            label='C5'
        )
        cable5.save()
        self.assertPathExists(
            (
                interface3, cable5, frontport3, rearport3, cable4, rearport4, frontport4, cable6, frontport5, rearport5,
                cable7, rearport6, frontport6
            ),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[frontport2, frontport6],
            b_terminations=[interface2],
            label='C3'
        )
        cable3.save()
        self.assertPathExists(
            (
                interface2, cable3, (frontport2, frontport6), (rearport2, rearport6), (cable2, cable7),
                (rearport1, rearport5), (frontport1, frontport5), (cable1, cable6)
            ),
            is_complete=False,
            is_split=True
        )
        self.assertPathExists(
            (
                interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2, cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface3, cable5, frontport3, rearport3, cable4, rearport4, frontport4, cable6, frontport5, rearport5,
                cable7, rearport6, frontport6, cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 3)

        # Test SVG generation
        CableTraceSVG(interface1).render()

    def test_222_single_path_via_multiple_singleposition_rear_ports(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]
                     [FP2] [RP2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
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

        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1, frontport2]
        )
        cable1.save()
        self.assertEqual(CablePath.objects.count(), 1)

        cable2 = Cable(
            a_terminations=[rearport1, rearport2],
            b_terminations=[interface2]
        )
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 2)

        self.assertPathExists(
            (interface1, cable1, (frontport1, frontport2), (rearport1, rearport2), cable2, interface2),
            is_complete=True
        )
        self.assertPathExists(
            (interface2, cable2, (rearport1, rearport2), (frontport1, frontport2), cable1, interface1),
            is_complete=True
        )

        # Test SVG generation both directions
        CableTraceSVG(interface1).render()
        CableTraceSVG(interface2).render()

    def test_223_interface_to_interface_via_multiple_circuit_terminations(self):
        provider = Provider.objects.first()
        circuit_type = CircuitType.objects.first()
        circuit1 = self.circuit
        circuit2 = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 2')
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuittermination1_A = CircuitTermination.objects.create(
            circuit=circuit1,
            termination=self.site,
            term_side='A'
        )
        circuittermination1_Z = CircuitTermination.objects.create(
            circuit=circuit1,
            termination=self.site,
            term_side='Z'
        )
        circuittermination2_A = CircuitTermination.objects.create(
            circuit=circuit2,
            termination=self.site,
            term_side='A'
        )
        circuittermination2_Z = CircuitTermination.objects.create(
            circuit=circuit2,
            termination=self.site,
            term_side='Z'
        )

        # Create cables
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[circuittermination1_A, circuittermination2_A]
        )
        cable2 = Cable(
            a_terminations=[interface2],
            b_terminations=[circuittermination1_Z, circuittermination2_Z]
        )
        cable1.save()
        cable2.save()

        self.assertEqual(CablePath.objects.count(), 2)

        path1 = self.assertPathExists(
            (
                interface1,
                cable1,
                (circuittermination1_A, circuittermination2_A),
                (circuittermination1_Z, circuittermination2_Z),
                cable2,
                interface2

            ),
            is_active=True,
            is_complete=True,
        )
        interface1.refresh_from_db()
        self.assertPathIsSet(interface1, path1)

        path2 = self.assertPathExists(
            (
                interface2,
                cable2,
                (circuittermination1_Z, circuittermination2_Z),
                (circuittermination1_A, circuittermination2_A),
                cable1,
                interface1

            ),
            is_active=True,
            is_complete=True,
        )
        interface2.refresh_from_db()
        self.assertPathIsSet(interface2, path2)

    def test_224_single_path_via_multiple_pass_throughs_with_breakouts(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF3]
        [IF2]        [FP2] [RP2]        [IF4]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        interface4 = Interface.objects.create(device=self.device, name='Interface 4')
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
            a_terminations=[interface1, interface2],
            b_terminations=[frontport1, frontport2]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[rearport1, rearport2],
            b_terminations=[interface3, interface4]
        )
        cable2.save()

        # Validate paths
        self.assertPathExists(
            (
                [interface1, interface2], cable1, [frontport1, frontport2],
                [rearport1, rearport2], cable2, [interface3, interface4],
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                [interface3, interface4], cable2, [rearport1, rearport2],
                [frontport1, frontport2], cable1, [interface1, interface2],
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_225_circuittermination_origin_passive_network(self):
        """
        [CT1] --C1-- [RP1] [FP1]

        A CircuitTermination cabled into a passive (FrontPort/RearPort-only) device can become a
        CablePath origin. Unlike PathEndpoint origins, CircuitTermination has no `_path` back-reference
        field, so saving and deleting such a path must not attempt to write it (see #22825).
        """
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device, front_port=frontport1, front_port_position=1,
            rear_port=rearport1, rear_port_position=1,
        )
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        cable1 = Cable(
            a_terminations=[circuittermination1],
            b_terminations=[rearport1]
        )
        cable1.save()

        # Re-fetch so the in-memory instance reflects the cable set above (from_origin reads .cable).
        circuittermination1.refresh_from_db()

        # A path traced from the CircuitTermination origin must save without raising FieldDoesNotExist
        # on the missing `_path` field.
        cablepath = CablePath.from_origin([circuittermination1])
        cablepath.save()
        self.assertEqual(cablepath.origin_type.model_class(), CircuitTermination)
        self.assertEqual(cablepath.origins, [circuittermination1])

        # Deleting the path must likewise not attempt to clear a nonexistent `_path` field.
        cablepath.delete()
        self.assertIsNone(CablePath.objects.filter(pk=cablepath.pk).first())

    def test_301_create_path_via_existing_cable(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
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

        # Create cable 2
        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2]
        )
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[frontport2],
            b_terminations=[interface2]
        )
        cable3.save()
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, rearport2, frontport2, cable3, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable3, frontport2, rearport2, cable2, rearport1, frontport1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_302_update_path_on_cable_status_change(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
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

        # Create cables 1 and 2
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1]
        )
        cable1.save()
        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[interface2]
        )
        cable2.save()
        self.assertEqual(CablePath.objects.filter(is_active=True).count(), 2)
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "planned"
        cable2 = Cable.objects.get(pk=cable2.pk)  # Rebuild object to ditch A/B terminations set earlier
        cable2.status = LinkStatusChoices.STATUS_PLANNED
        cable2.save()
        self.assertPathExists(
            (interface1, cable1, frontport1, rearport1, cable2, interface2),
            is_complete=True,
            is_active=False
        )
        self.assertPathExists(
            (interface2, cable2, rearport1, frontport1, cable1, interface1),
            is_complete=True,
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "connected"
        cable2 = Cable.objects.get(pk=cable2.pk)
        cable2.status = LinkStatusChoices.STATUS_CONNECTED
        cable2.save()
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
        self.assertEqual(CablePath.objects.count(), 2)

    def test_303_remove_termination_from_existing_cable(self):
        """
        [IF1] --C1-- [IF2]
                     [IF3]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[interface2, interface3]
        )
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, [interface2, interface3]),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            ([interface2, interface3], cable1, interface1),
            is_complete=True,
            is_active=True
        )

        # Remove the termination to interface 3
        cable1 = Cable.objects.first()
        cable1.b_terminations = [interface2]
        cable1.save()
        self.assertPathExists(
            (interface1, cable1, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable1, interface1),
            is_complete=True,
            is_active=True
        )

        # Verify _path is cleared on removed interface (#21127)
        interface3.refresh_from_db()
        self.assertPathIsNotSet(interface3)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_304_retrace_cable_created_without_save(self):
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')

        cable = self._create_cable_raw(interface1, interface2)
        self.assertEqual(CablePath.objects.count(), 0)

        cable.update_dependent_objects()

        self.assertPathExists((interface1, cable, interface2), is_complete=True, is_active=True)
        self.assertPathExists((interface2, cable, interface1), is_complete=True, is_active=True)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_305_retrace_cable_extends_incomplete_path(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2], with C2 written raw. Retracing from a termination which is not
        itself a path endpoint must extend the existing incomplete path.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1
        )

        cable1 = Cable(a_terminations=[interface1], b_terminations=[frontport1])
        cable1.save()
        self.assertPathExists((interface1, cable1, frontport1, rearport1), is_complete=False)

        cable2 = self._create_cable_raw(rearport1, interface2)
        self.assertEqual(CablePath.objects.count(), 1)

        cable2.update_dependent_objects()

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
        self.assertEqual(CablePath.objects.count(), 2)

    def test_306_retrace_cable_status_from_database(self):
        """
        A raw write leaves no in-memory record of the Cable's status, so path activity must come from the
        stored value.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')

        cable = self._create_cable_raw(interface1, interface2, status=LinkStatusChoices.STATUS_PLANNED)
        cable.update_dependent_objects()

        self.assertPathExists((interface1, cable, interface2), is_complete=True, is_active=False)
        self.assertPathExists((interface2, cable, interface1), is_complete=True, is_active=False)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_307_retrace_cable_preserves_path_via_pass_through(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [IF2]. Retracing C1, whose B side is not a path endpoint, must
        preserve the reverse path originating at IF2.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device,
            front_port=frontport1,
            front_port_position=1,
            rear_port=rearport1,
            rear_port_position=1
        )
        cable1 = Cable(a_terminations=[interface1], b_terminations=[frontport1])
        cable1.save()
        cable2 = Cable(a_terminations=[rearport1], b_terminations=[interface2])
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 2)

        Cable.objects.get(pk=cable1.pk).update_dependent_objects()

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
        self.assertEqual(CablePath.objects.count(), 2)

    def test_308_retrace_midspan_cable_preserves_paths(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- [IF2]. Retracing C2, which originates nothing
        itself (both sides are rear ports), must preserve both paths.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        ports = {}
        for i in (1, 2):
            ports[f'rear{i}'] = RearPort.objects.create(device=self.device, name=f'Rear Port {i}')
            ports[f'front{i}'] = FrontPort.objects.create(device=self.device, name=f'Front Port {i}')
            PortMapping.objects.create(
                device=self.device,
                front_port=ports[f'front{i}'],
                front_port_position=1,
                rear_port=ports[f'rear{i}'],
                rear_port_position=1
            )
        cable1 = Cable(a_terminations=[interface1], b_terminations=[ports['front1']])
        cable1.save()
        cable2 = Cable(a_terminations=[ports['rear1']], b_terminations=[ports['rear2']])
        cable2.save()
        cable3 = Cable(a_terminations=[ports['front2']], b_terminations=[interface2])
        cable3.save()
        self.assertEqual(CablePath.objects.count(), 2)

        # Twice: with no path endpoint of its own, every path this Cable carries is restored from the
        # origins of the paths it replaces, so a repeat call must neither duplicate nor drop them
        for _ in range(2):
            Cable.objects.get(pk=cable2.pk).update_dependent_objects()

        self.assertPathExists(
            (
                interface1, cable1, ports['front1'], ports['rear1'], cable2, ports['rear2'], ports['front2'],
                cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (
                interface2, cable3, ports['front2'], ports['rear2'], cable2, ports['rear1'], ports['front1'],
                cable1, interface1
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_309_retrace_cable_preserves_path_via_circuit(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [IF2]. Retracing C1, whose B side is a circuit termination, must
        preserve the reverse path originating at IF2.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit, termination=self.site, term_side='A'
        )
        circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit, termination=self.site, term_side='Z'
        )
        cable1 = Cable(a_terminations=[interface1], b_terminations=[circuittermination1])
        cable1.save()
        cable2 = Cable(a_terminations=[circuittermination2], b_terminations=[interface2])
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 2)

        Cable.objects.get(pk=cable1.pk).update_dependent_objects()

        self.assertPathExists(
            (interface1, cable1, circuittermination1, circuittermination2, cable2, interface2),
            is_complete=True,
            is_active=True
        )
        self.assertPathExists(
            (interface2, cable2, circuittermination2, circuittermination1, cable1, interface1),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_310_retrace_cable_is_idempotent(self):
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')

        cable = Cable(a_terminations=[interface1], b_terminations=[interface2])
        cable.save()
        self.assertEqual(CablePath.objects.count(), 2)

        cable.update_dependent_objects()

        path1 = self.assertPathExists((interface1, cable, interface2), is_complete=True, is_active=True)
        path2 = self.assertPathExists((interface2, cable, interface1), is_complete=True, is_active=True)
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

    def test_311_retrace_cable_preserves_circuittermination_origin(self):
        """
        [CT1] --C1-- [RP1] [FP1]

        A CircuitTermination origin is not a PathEndpoint, so the retrace cannot reproduce its path by
        tracing the Cable's terminations; it must be restored from the recorded origin instead.
        """
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        PortMapping.objects.create(
            device=self.device, front_port=frontport1, front_port_position=1,
            rear_port=rearport1, rear_port_position=1,
        )
        circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit,
            termination=self.site,
            term_side='A'
        )
        cable1 = Cable(a_terminations=[circuittermination1], b_terminations=[rearport1])
        cable1.save()

        circuittermination1.refresh_from_db()
        CablePath.from_origin([circuittermination1]).save()
        self.assertEqual(CablePath.objects.count(), 1)

        for _ in range(2):
            Cable.objects.get(pk=cable1.pk).update_dependent_objects()

            self.assertPathExists((circuittermination1, cable1, rearport1, frontport1), is_complete=False)
            self.assertEqual(CablePath.objects.count(), 1)

    def test_312_replacing_a_termination_retires_superseded_paths(self):
        """
        [IF1] --C1-- [IF2] becomes [IF1] --C1-- [IF3], and back again

        Each replacement must leave only the two paths the cable's current terminations trace.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        cable1 = Cable(a_terminations=[interface1], b_terminations=[interface2])
        cable1.save()
        self.assertEqual(CablePath.objects.count(), 2)

        for peer, detached in ((interface3, interface2), (interface2, interface3)):
            with self.subTest(peer=peer.name):
                cable1 = Cable.objects.get(pk=cable1.pk)
                cable1.b_terminations = [peer]
                cable1.full_clean()
                cable1.save()

                self.assertCurrentPathExists((interface1, cable1, peer), is_complete=True, is_active=True)
                self.assertCurrentPathExists((peer, cable1, interface1), is_complete=True, is_active=True)
                self.assertEqual(CablePath.objects.count(), 2)
                detached.refresh_from_db()
                self.assertIsNone(detached.cable)
                self.assertPathIsNotSet(detached)

    def test_313_adding_a_termination_retires_superseded_paths(self):
        """
        [IF1] --C1-- [IF2] gains a second B-side termination [IF3]

        Extending an end must retire the paths whose destinations the extension supersedes.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        cable1 = Cable(a_terminations=[interface1], b_terminations=[interface2])
        cable1.save()
        self.assertEqual(CablePath.objects.count(), 2)

        cable1 = Cable.objects.get(pk=cable1.pk)
        cable1.b_terminations = [interface2, interface3]
        cable1.full_clean()
        cable1.save()

        self.assertCurrentPathExists(
            (interface1, cable1, [interface2, interface3]), is_complete=True, is_active=True
        )
        path2 = self.assertPathExists(
            ([interface2, interface3], cable1, interface1), is_complete=True, is_active=True
        )
        for interface in (interface2, interface3):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, path2)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_314_retracing_one_joint_origin_restores_the_whole_hop(self):
        """
        [IF1] --C1-- [IF2]
                     [IF3]

        trace_paths retraces a cable end as a unit, so repairing one co-origin restores the joint hop.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        cable1 = Cable(a_terminations=[interface1], b_terminations=[interface2, interface3])
        cable1.save()
        self.assertEqual(CablePath.objects.count(), 2)

        # trace_paths selects on a null _path
        Interface.objects.filter(pk=interface2.pk).update(_path=None)

        call_command('trace_paths', no_input=True, stdout=StringIO())

        for interface in (interface1, interface2, interface3):
            interface.refresh_from_db()
            self.assertIsNotNone(interface._path_id, msg=f'{interface} left without a path')
        self.assertPathExists(([interface2, interface3], cable1, interface1))
        self.assertEqual(CablePath.objects.count(), 2)

    def test_315_retracing_a_cable_end_retires_a_superseded_co_origin_path(self):
        """
        [IF1] --C1-- [IF2]
                     [IF3]

        A path superseded at a co-origin of the retraced end is retired, not left beside its replacement.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')

        cable1 = Cable(a_terminations=[interface1], b_terminations=[interface2, interface3])
        cable1.save()
        self.assertEqual(CablePath.objects.count(), 2)

        # Seed the stale row a pre-fix install would hold, then restore both origins to the shared path
        interface3 = Interface.objects.get(pk=interface3.pk)
        joint_path = interface3._path
        superseded = CablePath.from_origin([interface3])
        superseded.save()
        joint_path.save()

        # trace_paths selects on a null _path
        Interface.objects.filter(pk=interface2.pk).update(_path=None)

        call_command('trace_paths', no_input=True, stdout=StringIO())

        self.assertFalse(
            CablePath.objects.filter(pk=superseded.pk).exists(), msg='the superseded path survived the retrace'
        )
        self.assertPathExists(([interface2, interface3], cable1, interface1))
        self.assertEqual(CablePath.objects.count(), 2)

    def test_316_retracing_a_partial_origin_group_retires_its_co_origins_paths(self):
        """
        Retracing one origin of a shared path must also replace its co-origin's stale paths.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        interface3 = Interface.objects.create(device=self.device, name='Interface 3')
        cable = Cable(a_terminations=[interface1], b_terminations=[interface2, interface3])
        cable.save()

        interface3.refresh_from_db()
        joint_path = interface3._path
        superseded = CablePath.from_origin([interface3])
        superseded.save()
        joint_path.save()

        interface2.refresh_from_db()
        create_cablepaths([interface2])

        self.assertFalse(CablePath.objects.filter(pk=superseded.pk).exists())
        self.assertFalse(CablePath.objects.filter(pk=joint_path.pk).exists())
        self.assertCurrentPathExists((interface2, cable, interface1), is_complete=True)
        self.assertCurrentPathExists((interface3, cable, interface1), is_complete=True)
        self.assertCurrentPathExists((interface1, cable, [interface2, interface3]), is_complete=True)
        self.assertEqual(CablePath.objects.count(), 3)

    def test_317_retracing_preserves_another_current_origin_group(self):
        """
        An origin group whose references the deletion does not clear is left intact, rows and all.
        """
        interfaces = [
            Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 5)
        ]
        interface1, interface2, interface3, interface4 = interfaces
        cable = Cable(a_terminations=[interface1], b_terminations=interfaces[1:])
        cable.save()
        for interface in interfaces:
            interface.refresh_from_db()

        # Overlapping groups from earlier partial retraces, with interface3 and interface4 on the second
        interface2._path.delete()
        first = CablePath.from_origin([interface2, interface3])
        first.save()
        second = CablePath.from_origin([interface3, interface4])
        second.save()

        create_cablepaths([interface2])

        self.assertFalse(CablePath.objects.filter(pk=first.pk).exists())
        self.assertCurrentPathExists((interface2, cable, interface1), is_complete=True)
        self.assertTrue(
            CablePath.objects.filter(pk=second.pk).exists(), msg='the untouched origin group was replaced'
        )
        second.refresh_from_db()
        self.assertEqual(second.path[0], [object_to_path_node(interface3), object_to_path_node(interface4)])
        for interface in (interface3, interface4):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, second)
        self.assertEqual(CablePath.objects.count(), 3)

    def test_318_recovery_preserves_the_requested_connector_groups(self):
        """
        A recovered group must not replace a connector group already rebuilt by this call.
        """
        interfaces = [
            Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 5)
        ]
        interface1, interface2, interface3, interface4 = interfaces
        cable = Cable(a_terminations=[interface1], b_terminations=interfaces[1:])
        cable.save()
        for interface in interfaces:
            interface.refresh_from_db()

        CablePath.from_origin([interface2, interface3]).save()
        # Use a connector grouping that cannot be persisted to isolate requested-group precedence.
        interface2.cable_connector = 1
        interface3.cable_connector = 2
        interface4.cable_connector = 2

        create_cablepaths([interface2, interface3, interface4])

        self.assertCurrentPathExists((interface2, cable, interface1), is_complete=True)
        shared_path = self.assertPathExists(([interface3, interface4], cable, interface1), is_complete=True)
        for interface in (interface3, interface4):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, shared_path)
        self.assertEqual(CablePath.objects.count(), 3)

    def test_319_recovery_separates_origins_on_different_links(self):
        """
        A stale origin hop holding origins since moved apart is recovered as one group per current cable end.
        """
        interfaces = [
            Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 7)
        ]
        interface1, interface2, interface3, interface4, interface5, interface6 = interfaces
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[interface2, interface3, interface4, interface5],
        )
        cable1.save()

        # The hop as stored while all four shared cable1
        interface2.refresh_from_db()
        stale_nodes = interface2._path.path

        # Move one origin through ordinary saves, so only the CablePath below is stale
        cable1.b_terminations = [interface2, interface3, interface4]
        cable1.save()
        interface5.refresh_from_db()
        cable2 = Cable(a_terminations=[interface6], b_terminations=[interface5])
        cable2.save()

        interface2.refresh_from_db()
        interface5.refresh_from_db()
        current_cable1 = interface2._path
        current_cable2 = interface5._path

        # Leave the obsolete row as their only originating path, so recovery gets the whole mixed hop
        current_cable1.delete()
        current_cable2.delete()
        superseded = CablePath(path=stale_nodes, is_complete=True, is_active=True)
        superseded.save()

        create_cablepaths([Interface.objects.get(pk=interface2.pk)])

        self.assertFalse(CablePath.objects.filter(pk=superseded.pk).exists())
        self.assertCurrentPathExists((interface2, cable1, interface1), is_complete=True)
        # The origins still sharing cable1 stay one group, and the moved one is recovered on its own cable
        shared = self.assertPathExists(([interface3, interface4], cable1, interface1), is_complete=True)
        for interface in (interface3, interface4):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, shared)
        self.assertCurrentPathExists((interface5, cable2, interface6), is_complete=True)
        self.assertEqual(CablePath.objects.count(), 5)

    def test_320_retracing_repairs_an_endpoint_whose_cable_end_drifted(self):
        """
        An endpoint whose denormalized cable_end no longer matches its CableTermination is still retraced.
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        cable1 = Cable(a_terminations=[interface1], b_terminations=[interface2])
        cable1.save()

        # The termination row still says B, which is the drift this command exists to repair
        Interface.objects.filter(pk=interface2.pk).update(
            _path=None, cable_end=CableEndChoices.SIDE_A
        )

        call_command('trace_paths', no_input=True, stdout=StringIO())

        self.assertCurrentPathExists((interface2, cable1, interface1), is_complete=True)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_321_recovery_follows_a_chain_of_cleared_references(self):
        """
        Recovering an origin can clear another group's references, whose origins are recovered in turn.
        """
        interfaces = [
            Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 5)
        ]
        interface1, interface2, interface3, interface4 = interfaces
        cable = Cable(a_terminations=[interface1], b_terminations=interfaces[1:])
        cable.save()
        for interface in interfaces:
            interface.refresh_from_db()

        # interface3 references the first group, so losing it starts the chain
        interface2._path.delete()
        first = CablePath.from_origin([interface2, interface3])
        first.save()
        second = CablePath.from_origin([interface3, interface4])
        second.save()
        first.save()

        create_cablepaths([interface2])

        self.assertFalse(CablePath.objects.filter(pk__in=[first.pk, second.pk]).exists())
        for interface in interfaces[1:]:
            self.assertCurrentPathExists((interface, cable, interface1), is_complete=True)
        self.assertEqual(CablePath.objects.count(), 4)

    def test_401_exclude_midspan_devices(self):
        """
        [IF1] --C1-- [FP1][Test Device][RP1] --C2-- [RP2][Test Device][FP2] --C3-- [IF2]
                     [FP3][Test mid-span Device][RP3] --C4-- [RP4][Test mid-span Device][FP4] /
        """
        device = Device.objects.create(
            site=self.site,
            device_type=self.device.device_type,
            role=self.device.role,
            name='Test mid-span Device'
        )
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1')
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2')
        rearport3 = RearPort.objects.create(device=device, name='Rear Port 3')
        rearport4 = RearPort.objects.create(device=device, name='Rear Port 4')
        frontport1 = FrontPort.objects.create(device=self.device, name='Front Port 1')
        frontport2 = FrontPort.objects.create(device=self.device, name='Front Port 2')
        frontport3 = FrontPort.objects.create(device=self.device, name='Front Port 3')
        frontport4 = FrontPort.objects.create(device=self.device, name='Front Port 4')
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
            PortMapping(
                device=self.device,
                front_port=frontport3,
                front_port_position=1,
                rear_port=rearport3,
                rear_port_position=1,
            ),
            PortMapping(
                device=self.device,
                front_port=frontport4,
                front_port_position=1,
                rear_port=rearport4,
                rear_port_position=1,
            ),
        ])

        cable2 = Cable(
            a_terminations=[rearport1],
            b_terminations=[rearport2],
            label='C2'
        )
        cable2.save()
        cable4 = Cable(
            a_terminations=[rearport3],
            b_terminations=[rearport4],
            label='C4'
        )
        cable4.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(
            a_terminations=[interface1],
            b_terminations=[frontport1, frontport3],
            label='C1'
        )
        with self.assertRaises(AbortRequest):
            cable1.save()

        self.assertPathDoesNotExist(
            (
                interface1, cable1, (frontport1, frontport3), (rearport1, rearport3), (cable2, cable4),
                (rearport2, rearport4), (frontport2, frontport4)
            ),
            is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable 3
        cable3 = Cable(
            a_terminations=[frontport2, frontport4],
            b_terminations=[interface2],
            label='C3'
        )

        with self.assertRaises(AbortRequest):
            cable3.save()

        self.assertPathDoesNotExist(
            (
                interface2, cable3, (frontport2, frontport4), (rearport2, rearport4), (cable2, cable4),
                (rearport1, rearport3), (frontport1, frontport2), cable1, interface1
            ),
            is_complete=True,
            is_active=True
        )
        self.assertPathDoesNotExist(
            (
                interface1, cable1, (frontport1, frontport3), (rearport1, rearport3), (cable2, cable4),
                (rearport2, rearport4), (frontport2, frontport4), cable3, interface2
            ),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 0)

    def test_402_exclude_circuit_loopback(self):
        interface = Interface.objects.create(device=self.device, name='Interface 1')
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
        cable = Cable(
            a_terminations=[interface],
            b_terminations=[circuittermination1, circuittermination2]
        )
        cable.save()

        path = self.assertPathExists(
            (interface, cable, (circuittermination1, circuittermination2)),
            is_active=True,
            is_complete=False,
            is_split=True
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface.refresh_from_db()
        self.assertPathIsSet(interface, path)
