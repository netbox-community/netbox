from django.test import TestCase

from circuits.models import *
from dcim.choices import LinkStatusChoices
from dcim.models import *
from dcim.svg import CableTraceSVG
from dcim.utils import object_to_path_node
from utilities.exceptions import AbortRequest


class CablePathTestCase(TestCase):
    """
    Test NetBox's ability to trace and retrace CablePaths in response to data model changes. Tests are numbered
    as follows:

        1XX: Test direct connections between different endpoint types
        2XX: Test different cable topologies
        3XX: Test responses to changes in existing objects
        4XX: Test to exclude specific cable topologies
    """
    @classmethod
    def setUpTestData(cls):

        # Create a single device that will hold all components
        cls.site = Site.objects.create(name='Site', slug='site')

        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.device = Device.objects.create(site=cls.site, device_type=device_type, role=role, name='Test Device')

        cls.powerpanel = PowerPanel.objects.create(site=cls.site, name='Power Panel')

        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        cls.circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')

    def _get_cablepath(self, nodes, **kwargs):
        """
        Return a given cable path

        :param nodes: Iterable of steps, with each step being either a single node or a list of nodes

        :return: The matching CablePath (if any)
        """
        path = []
        for step in nodes:
            if type(step) in (list, tuple):
                path.append([object_to_path_node(node) for node in step])
            else:
                path.append([object_to_path_node(step)])
        return CablePath.objects.filter(path=path, **kwargs).first()

    def assertPathExists(self, nodes, **kwargs):
        """
        Assert that a CablePath from origin to destination with a specific intermediate path exists. Returns the
        first matching CablePath, if found.

        :param nodes: Iterable of steps, with each step being either a single node or a list of nodes
        """
        cablepath = self._get_cablepath(nodes, **kwargs)
        self.assertIsNotNone(cablepath, msg='CablePath not found')

        return cablepath

    def assertPathDoesNotExist(self, nodes, **kwargs):
        """
        Assert that a specific CablePath does *not* exist.

        :param nodes: Iterable of steps, with each step being either a single node or a list of nodes
        """
        cablepath = self._get_cablepath(nodes, **kwargs)
        self.assertIsNone(cablepath, msg='Unexpected CablePath found')

    def assertPathIsSet(self, origin, cablepath, msg=None):
        """
        Assert that a specific CablePath instance is set as the path on the origin.

        :param origin: The originating path endpoint
        :param cablepath: The CablePath instance originating from this endpoint
        :param msg: Custom failure message (optional)
        """
        if msg is None:
            msg = f"Path #{cablepath.pk} not set on originating endpoint {origin}"
        self.assertEqual(origin._path_id, cablepath.pk, msg=msg)

    def assertPathIsNotSet(self, origin, msg=None):
        """
        Assert that a specific CablePath instance is set as the path on the origin.

        :param origin: The originating path endpoint
        :param msg: Custom failure message (optional)
        """
        if msg is None:
            msg = f"Path #{origin._path_id} set as origin on {origin}; should be None!"
        self.assertIsNone(origin._path_id, msg=msg)

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
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
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport2, rear_port_position=1
        )
        frontport2_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport2, rear_port_position=2
        )

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
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport2, rear_port_position=1
        )
        frontport2_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport2, rear_port_position=2
        )

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
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=4)
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=self.device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 4:1', rear_port=rearport4, rear_port_position=1
        )
        frontport4_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 4:2', rear_port=rearport4, rear_port_position=2
        )

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
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport2, rear_port_position=1
        )
        frontport2_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport2, rear_port_position=2
        )
        frontport3_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 3:1', rear_port=rearport3, rear_port_position=1
        )
        frontport3_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 3:2', rear_port=rearport3, rear_port_position=2
        )
        frontport4_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 4:1', rear_port=rearport4, rear_port_position=1
        )
        frontport4_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 4:2', rear_port=rearport4, rear_port_position=2
        )

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
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 5', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=4)
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 5', rear_port=rearport2, rear_port_position=1
        )
        frontport3_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport3, rear_port_position=1
        )
        frontport3_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport3, rear_port_position=2
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=4)
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
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
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport2_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport2, rear_port_position=1
        )
        frontport2_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport2, rear_port_position=2
        )
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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=self.device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4 = FrontPort.objects.create(
            device=self.device, name='Front Port 4', rear_port=rearport4, rear_port_position=1
        )

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
        frontport1_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:1', rear_port=rearport1, rear_port_position=1
        )
        frontport1_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:2', rear_port=rearport1, rear_port_position=2
        )
        frontport1_3 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:3', rear_port=rearport1, rear_port_position=3
        )
        frontport1_4 = FrontPort.objects.create(
            device=self.device, name='Front Port 1:4', rear_port=rearport1, rear_port_position=4
        )
        frontport2_1 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:1', rear_port=rearport2, rear_port_position=1
        )
        frontport2_2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:2', rear_port=rearport2, rear_port_position=2
        )
        frontport2_3 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:3', rear_port=rearport2, rear_port_position=3
        )
        frontport2_4 = FrontPort.objects.create(
            device=self.device, name='Front Port 2:4', rear_port=rearport2, rear_port_position=4
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=self.device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4 = FrontPort.objects.create(
            device=self.device, name='Front Port 4', rear_port=rearport4, rear_port_position=1
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=self.device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4 = FrontPort.objects.create(
            device=self.device, name='Front Port 4', rear_port=rearport4, rear_port_position=1
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=self.device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=self.device, name='Rear Port 4', positions=1)
        rearport5 = RearPort.objects.create(device=self.device, name='Rear Port 5', positions=1)
        rearport6 = RearPort.objects.create(device=self.device, name='Rear Port 6', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=self.device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4 = FrontPort.objects.create(
            device=self.device, name='Front Port 4', rear_port=rearport4, rear_port_position=1
        )
        frontport5 = FrontPort.objects.create(
            device=self.device, name='Front Port 5', rear_port=rearport5, rear_port_position=1
        )
        frontport6 = FrontPort.objects.create(
            device=self.device, name='Front Port 6', rear_port=rearport6, rear_port_position=1
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )

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

    def test_301_create_path_via_existing_cable(self):
        """
        [IF1] --C1-- [FP1] [RP1] --C2-- [RP2] [FP2] --C3-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )

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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )

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

        # Create cables 1
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
        rearport1 = RearPort.objects.create(device=self.device, name='Rear Port 1', positions=1)
        rearport2 = RearPort.objects.create(device=self.device, name='Rear Port 2', positions=1)
        rearport3 = RearPort.objects.create(device=device, name='Rear Port 3', positions=1)
        rearport4 = RearPort.objects.create(device=device, name='Rear Port 4', positions=1)
        frontport1 = FrontPort.objects.create(
            device=self.device, name='Front Port 1', rear_port=rearport1, rear_port_position=1
        )
        frontport2 = FrontPort.objects.create(
            device=self.device, name='Front Port 2', rear_port=rearport2, rear_port_position=1
        )
        frontport3 = FrontPort.objects.create(
            device=device, name='Front Port 3', rear_port=rearport3, rear_port_position=1
        )
        frontport4 = FrontPort.objects.create(
            device=device, name='Front Port 4', rear_port=rearport4, rear_port_position=1
        )

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
