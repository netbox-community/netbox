from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.models import *
from dcim.choices import CableStatusChoices
from dcim.models import *
from dcim.utils import objects_to_path


class CablePathTestCase(TestCase):
    """
    Test NetBox's ability to trace and retrace CablePaths in response to data model changes. Tests are numbered
    as follows:

        1XX: Test direct connections between different endpoint types
        2XX: Test different cable topologies
        3XX: Test responses to changes in existing objects
    """
    @classmethod
    def setUpTestData(cls):

        # Create a single device that will hold all components
        site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        device = Device.objects.create(site=site, device_type=device_type, device_role=device_role, name='Test Device')

        # Create console/power components for testing
        cls.consoleport1 = ConsolePort.objects.create(device=device, name='Console Port 1')
        cls.consoleserverport1 = ConsoleServerPort.objects.create(device=device, name='Console Server Port 1')
        cls.powerport1 = PowerPort.objects.create(device=device, name='Power Port 1')
        cls.poweroutlet1 = PowerPort.objects.create(device=device, name='Power Outlet 1')

        # Create 4 interfaces for testing
        cls.interface1 = Interface(device=device, name=f'Interface 1')
        cls.interface2 = Interface(device=device, name=f'Interface 2')
        cls.interface3 = Interface(device=device, name=f'Interface 3')
        cls.interface4 = Interface(device=device, name=f'Interface 4')
        Interface.objects.bulk_create([
            cls.interface1,
            cls.interface2,
            cls.interface3,
            cls.interface4
        ])

        # Create four RearPorts with four positions each, and two with only one position
        cls.rear_port1 = RearPort(device=device, name=f'RP1', positions=4)
        cls.rear_port2 = RearPort(device=device, name=f'RP2', positions=4)
        cls.rear_port3 = RearPort(device=device, name=f'RP3', positions=4)
        cls.rear_port4 = RearPort(device=device, name=f'RP4', positions=4)
        cls.rear_port5 = RearPort(device=device, name=f'RP5', positions=1)
        cls.rear_port6 = RearPort(device=device, name=f'RP6', positions=1)
        RearPort.objects.bulk_create([
            cls.rear_port1,
            cls.rear_port2,
            cls.rear_port3,
            cls.rear_port4,
            cls.rear_port5,
            cls.rear_port6
        ])

        # Create FrontPorts to match RearPorts (4x4 + 2x1)
        cls.front_port1_1 = FrontPort(device=device, name=f'FP1:1', rear_port=cls.rear_port1, rear_port_position=1)
        cls.front_port1_2 = FrontPort(device=device, name=f'FP1:2', rear_port=cls.rear_port1, rear_port_position=2)
        cls.front_port1_3 = FrontPort(device=device, name=f'FP1:3', rear_port=cls.rear_port1, rear_port_position=3)
        cls.front_port1_4 = FrontPort(device=device, name=f'FP1:4', rear_port=cls.rear_port1, rear_port_position=4)
        cls.front_port2_1 = FrontPort(device=device, name=f'FP2:1', rear_port=cls.rear_port2, rear_port_position=1)
        cls.front_port2_2 = FrontPort(device=device, name=f'FP2:2', rear_port=cls.rear_port2, rear_port_position=2)
        cls.front_port2_3 = FrontPort(device=device, name=f'FP2:3', rear_port=cls.rear_port2, rear_port_position=3)
        cls.front_port2_4 = FrontPort(device=device, name=f'FP2:4', rear_port=cls.rear_port2, rear_port_position=4)
        cls.front_port3_1 = FrontPort(device=device, name=f'FP3:1', rear_port=cls.rear_port3, rear_port_position=1)
        cls.front_port3_2 = FrontPort(device=device, name=f'FP3:2', rear_port=cls.rear_port3, rear_port_position=2)
        cls.front_port3_3 = FrontPort(device=device, name=f'FP3:3', rear_port=cls.rear_port3, rear_port_position=3)
        cls.front_port3_4 = FrontPort(device=device, name=f'FP3:4', rear_port=cls.rear_port3, rear_port_position=4)
        cls.front_port4_1 = FrontPort(device=device, name=f'FP4:1', rear_port=cls.rear_port4, rear_port_position=1)
        cls.front_port4_2 = FrontPort(device=device, name=f'FP4:2', rear_port=cls.rear_port4, rear_port_position=2)
        cls.front_port4_3 = FrontPort(device=device, name=f'FP4:3', rear_port=cls.rear_port4, rear_port_position=3)
        cls.front_port4_4 = FrontPort(device=device, name=f'FP4:4', rear_port=cls.rear_port4, rear_port_position=4)
        cls.front_port5_1 = FrontPort(device=device, name=f'FP5:1', rear_port=cls.rear_port5, rear_port_position=1)
        cls.front_port6_1 = FrontPort(device=device, name=f'FP6:1', rear_port=cls.rear_port6, rear_port_position=1)
        FrontPort.objects.bulk_create([
            cls.front_port1_1,
            cls.front_port1_2,
            cls.front_port1_3,
            cls.front_port1_4,
            cls.front_port2_1,
            cls.front_port2_2,
            cls.front_port2_3,
            cls.front_port2_4,
            cls.front_port3_1,
            cls.front_port3_2,
            cls.front_port3_3,
            cls.front_port3_4,
            cls.front_port4_1,
            cls.front_port4_2,
            cls.front_port4_3,
            cls.front_port4_4,
            cls.front_port5_1,
            cls.front_port6_1,
        ])

        # Create a PowerFeed for testing
        powerpanel = PowerPanel.objects.create(site=site, name='Power Panel')
        cls.powerfeed1 = PowerFeed.objects.create(power_panel=powerpanel, name='Power Feed 1')

        # Create four CircuitTerminations for testing
        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        circuits = [
            Circuit(provider=provider, type=circuit_type, cid='Circuit 1'),
            Circuit(provider=provider, type=circuit_type, cid='Circuit 2'),
        ]
        Circuit.objects.bulk_create(circuits)
        cls.circuittermination1_A = CircuitTermination(circuit=circuits[0], site=site, term_side='A', port_speed=1000)
        cls.circuittermination1_Z = CircuitTermination(circuit=circuits[0], site=site, term_side='Z', port_speed=1000)
        cls.circuittermination2_A = CircuitTermination(circuit=circuits[1], site=site, term_side='A', port_speed=1000)
        cls.circuittermination2_Z = CircuitTermination(circuit=circuits[1], site=site, term_side='Z', port_speed=1000)
        CircuitTermination.objects.bulk_create([
            cls.circuittermination1_A,
            cls.circuittermination1_Z,
            cls.circuittermination2_A,
            cls.circuittermination2_Z,
        ])

    def assertPathExists(self, origin, destination, path=None, is_connected=None, msg=None):
        """
        Assert that a CablePath from origin to destination with a specific intermediate path exists.

        :param origin: Originating endpoint
        :param destination: Terminating endpoint, or None
        :param path: Sequence of objects comprising the intermediate path (optional)
        :param is_connected: Boolean indicating whether the end-to-end path is complete and active (optional)
        :param msg: Custom failure message (optional)

        :return: The matching CablePath (if any)
        """
        kwargs = {
            'origin_type': ContentType.objects.get_for_model(origin),
            'origin_id': origin.pk,
        }
        if destination is not None:
            kwargs['destination_type'] = ContentType.objects.get_for_model(destination)
            kwargs['destination_id'] = destination.pk
        else:
            kwargs['destination_type__isnull'] = True
            kwargs['destination_id__isnull'] = True
        if path is not None:
            kwargs['path'] = objects_to_path(*path)
        if is_connected is not None:
            kwargs['is_connected'] = is_connected
        if msg is None:
            if destination is not None:
                msg = f"Missing path from {origin} to {destination}"
            else:
                msg = f"Missing partial path originating from {origin}"

        cablepath = CablePath.objects.filter(**kwargs).first()
        self.assertIsNotNone(cablepath, msg=msg)

        return cablepath

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
        # Create cable 1
        cable1 = Cable(termination_a=self.interface1, termination_b=self.interface2)
        cable1.save()
        path1 = self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(cable1,),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.assertPathIsSet(self.interface1, path1)
        self.assertPathIsSet(self.interface2, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_102_consoleport_to_consoleserverport(self):
        """
        [CP1] --C1-- [CSP1]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.consoleport1, termination_b=self.consoleserverport1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=self.consoleport1,
            destination=self.consoleserverport1,
            path=(cable1,),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.consoleserverport1,
            destination=self.consoleport1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        self.consoleport1.refresh_from_db()
        self.consoleserverport1.refresh_from_db()
        self.assertPathIsSet(self.consoleport1, path1)
        self.assertPathIsSet(self.consoleserverport1, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_103_powerport_to_poweroutlet(self):
        """
        [PP1] --C1-- [PO1]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.powerport1, termination_b=self.poweroutlet1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=self.powerport1,
            destination=self.poweroutlet1,
            path=(cable1,),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.poweroutlet1,
            destination=self.powerport1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        self.powerport1.refresh_from_db()
        self.poweroutlet1.refresh_from_db()
        self.assertPathIsSet(self.powerport1, path1)
        self.assertPathIsSet(self.poweroutlet1, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_104_powerport_to_powerfeed(self):
        """
        [PP1] --C1-- [PF1]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.powerport1, termination_b=self.powerfeed1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=self.powerport1,
            destination=self.powerfeed1,
            path=(cable1,),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.powerfeed1,
            destination=self.powerport1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        self.powerport1.refresh_from_db()
        self.powerfeed1.refresh_from_db()
        self.assertPathIsSet(self.powerport1, path1)
        self.assertPathIsSet(self.powerfeed1, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_105_interface_to_circuittermination(self):
        """
        [PP1] --C1-- [CT1A]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.interface1, termination_b=self.circuittermination1_A)
        cable1.save()
        path1 = self.assertPathExists(
            origin=self.interface1,
            destination=self.circuittermination1_A,
            path=(cable1,),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.circuittermination1_A,
            destination=self.interface1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        self.interface1.refresh_from_db()
        self.circuittermination1_A.refresh_from_db()
        self.assertPathIsSet(self.interface1, path1)
        self.assertPathIsSet(self.circuittermination1_A, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_201_single_path_via_pass_through(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [IF2]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()

        # Create cable 1
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port5_1)
        cable1.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port5_1, self.rear_port5),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(termination_a=self.rear_port5, termination_b=self.interface2)
        cable2.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(cable1, self.front_port5_1, self.rear_port5, cable2),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(cable2, self.rear_port5, self.front_port5_1, cable1),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port5_1, self.rear_port5),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 1)
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.assertPathIsSet(self.interface1, path1)
        self.assertPathIsNotSet(self.interface2)

    def test_202_multiple_paths_via_pass_through(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:2] --C5-- [IF4]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.interface3.refresh_from_db()
        self.interface4.refresh_from_db()

        # Create cables 1-2
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1_1)
        cable1.save()
        cable2 = Cable(termination_a=self.interface2, termination_b=self.front_port1_2)
        cable2.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port1_1, self.rear_port1),
            is_connected=False
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=None,
            path=(cable2, self.front_port1_2, self.rear_port1),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(termination_a=self.rear_port1, termination_b=self.rear_port2)
        cable3.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port1_1, self.rear_port1, cable3, self.rear_port2, self.front_port2_1),
            is_connected=False
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=None,
            path=(cable2, self.front_port1_2, self.rear_port1, cable3, self.rear_port2, self.front_port2_2),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cables 4-5
        cable4 = Cable(termination_a=self.front_port2_1, termination_b=self.interface3)
        cable4.save()
        cable5 = Cable(termination_a=self.front_port2_2, termination_b=self.interface4)
        cable5.save()
        path1 = self.assertPathExists(
            origin=self.interface1,
            destination=self.interface3,
            path=(
                cable1, self.front_port1_1, self.rear_port1, cable3, self.rear_port2, self.front_port2_1,
                cable4,
            ),
            is_connected=True
        )
        path2 = self.assertPathExists(
            origin=self.interface2,
            destination=self.interface4,
            path=(
                cable2, self.front_port1_2, self.rear_port1, cable3, self.rear_port2, self.front_port2_2,
                cable5,
            ),
            is_connected=True
        )
        path3 = self.assertPathExists(
            origin=self.interface3,
            destination=self.interface1,
            path=(
                cable4, self.front_port2_1, self.rear_port2, cable3, self.rear_port1, self.front_port1_1,
                cable1
            ),
            is_connected=True
        )
        path4 = self.assertPathExists(
            origin=self.interface4,
            destination=self.interface2,
            path=(
                cable5, self.front_port2_2, self.rear_port2, cable3, self.rear_port1, self.front_port1_2,
                cable2
            ),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.interface3.refresh_from_db()
        self.interface4.refresh_from_db()
        self.assertPathIsSet(self.interface1, path1)
        self.assertPathIsSet(self.interface2, path2)
        self.assertPathIsSet(self.interface3, path3)
        self.assertPathIsSet(self.interface4, path4)

    def test_203_multiple_paths_via_nested_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP2:1] [RP2] --C4-- [RP3] [FP3:1] --C5-- [RP4] [FP4:1] --C6-- [IF3]
        [IF2] --C2-- [FP1:2]                                                              [FP4:2] --C7-- [IF4]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.interface3.refresh_from_db()
        self.interface4.refresh_from_db()

        # Create cables 1-2, 6-7
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1_1)
        cable1.save()
        cable2 = Cable(termination_a=self.interface2, termination_b=self.front_port1_2)
        cable2.save()
        cable6 = Cable(termination_a=self.interface3, termination_b=self.front_port4_1)
        cable6.save()
        cable7 = Cable(termination_a=self.interface4, termination_b=self.front_port4_2)
        cable7.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3 and 5
        cable3 = Cable(termination_a=self.rear_port1, termination_b=self.front_port2_1)
        cable3.save()
        cable5 = Cable(termination_a=self.rear_port4, termination_b=self.front_port3_1)
        cable5.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four (longer) partial paths; one from each interface

        # Create cable 4
        cable4 = Cable(termination_a=self.rear_port2, termination_b=self.rear_port3)
        cable4.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface3,
            path=(
                cable1, self.front_port1_1, self.rear_port1, cable3, self.front_port2_1, self.rear_port2,
                cable4, self.rear_port3, self.front_port3_1, cable5, self.rear_port4, self.front_port4_1,
                cable6
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface4,
            path=(
                cable2, self.front_port1_2, self.rear_port1, cable3, self.front_port2_1, self.rear_port2,
                cable4, self.rear_port3, self.front_port3_1, cable5, self.rear_port4, self.front_port4_2,
                cable7
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface3,
            destination=self.interface1,
            path=(
                cable6, self.front_port4_1, self.rear_port4, cable5, self.front_port3_1, self.rear_port3,
                cable4, self.rear_port2, self.front_port2_1, cable3, self.rear_port1, self.front_port1_1,
                cable1
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface4,
            destination=self.interface2,
            path=(
                cable7, self.front_port4_2, self.rear_port4, cable5, self.front_port3_1, self.rear_port3,
                cable4, self.rear_port2, self.front_port2_1, cable3, self.rear_port1, self.front_port1_2,
                cable2
            ),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)

    def test_204_multiple_paths_via_multiple_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [FP3:1] [RP3] --C6-- [RP4] [FP4:1] --C7-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:1] --C5-- [FP3:1]                    [FP4:2] --C8-- [IF4]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.interface3.refresh_from_db()
        self.interface4.refresh_from_db()

        # Create cables 1-3, 6-8
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1_1)
        cable1.save()
        cable2 = Cable(termination_a=self.interface2, termination_b=self.front_port1_2)
        cable2.save()
        cable3 = Cable(termination_a=self.rear_port1, termination_b=self.rear_port2)
        cable3.save()
        cable6 = Cable(termination_a=self.rear_port3, termination_b=self.rear_port4)
        cable6.save()
        cable7 = Cable(termination_a=self.interface3, termination_b=self.front_port4_1)
        cable7.save()
        cable8 = Cable(termination_a=self.interface4, termination_b=self.front_port4_2)
        cable8.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 4 and 5
        cable4 = Cable(termination_a=self.front_port2_1, termination_b=self.front_port3_1)
        cable4.save()
        cable5 = Cable(termination_a=self.front_port2_2, termination_b=self.front_port3_2)
        cable5.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface3,
            path=(
                cable1, self.front_port1_1, self.rear_port1, cable3, self.rear_port2, self.front_port2_1,
                cable4, self.front_port3_1, self.rear_port3, cable6, self.rear_port4, self.front_port4_1,
                cable7
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface4,
            path=(
                cable2, self.front_port1_2, self.rear_port1, cable3, self.rear_port2, self.front_port2_2,
                cable5, self.front_port3_2, self.rear_port3, cable6, self.rear_port4, self.front_port4_2,
                cable8
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface3,
            destination=self.interface1,
            path=(
                cable7, self.front_port4_1, self.rear_port4, cable6, self.rear_port3, self.front_port3_1,
                cable4, self.front_port2_1, self.rear_port2, cable3, self.rear_port1, self.front_port1_1,
                cable1
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface4,
            destination=self.interface2,
            path=(
                cable8, self.front_port4_2, self.rear_port4, cable6, self.rear_port3, self.front_port3_2,
                cable5, self.front_port2_2, self.rear_port2, cable3, self.rear_port1, self.front_port1_2,
                cable2
            ),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 5
        cable5.delete()

        # Check for two complete paths (IF1 <--> IF2) and two partial (IF3 <--> IF4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 2)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 2)

    def test_205_multiple_paths_via_patched_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP5] [RP5] --C4-- [RP2] [FP2:1] --C5-- [IF3]
        [IF2] --C2-- [FP1:2]                                       [FP2:2] --C6-- [IF4]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()
        self.interface3.refresh_from_db()
        self.interface4.refresh_from_db()

        # Create cables 1-2, 5-6
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1_1)  # IF1 -> FP1:1
        cable1.save()
        cable2 = Cable(termination_a=self.interface2, termination_b=self.front_port1_2)  # IF2 -> FP1:2
        cable2.save()
        cable5 = Cable(termination_a=self.interface3, termination_b=self.front_port2_1)  # IF3 -> FP2:1
        cable5.save()
        cable6 = Cable(termination_a=self.interface4, termination_b=self.front_port2_2)  # IF4 -> FP2:2
        cable6.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3-4
        cable3 = Cable(termination_a=self.rear_port1, termination_b=self.front_port5_1)  # RP1 -> FP5
        cable3.save()
        cable4 = Cable(termination_a=self.rear_port5, termination_b=self.rear_port2)  # RP5 -> RP2
        cable4.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface3,
            path=(
                cable1, self.front_port1_1, self.rear_port1, cable3, self.front_port5_1, self.rear_port5,
                cable4, self.rear_port2, self.front_port2_1, cable5
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface4,
            path=(
                cable2, self.front_port1_2, self.rear_port1, cable3, self.front_port5_1, self.rear_port5,
                cable4, self.rear_port2, self.front_port2_2, cable6
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface3,
            destination=self.interface1,
            path=(
                cable5, self.front_port2_1, self.rear_port2, cable4, self.rear_port5, self.front_port5_1,
                cable3, self.rear_port1, self.front_port1_1, cable1
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface4,
            destination=self.interface2,
            path=(
                cable6, self.front_port2_2, self.rear_port2, cable4, self.rear_port5, self.front_port5_1,
                cable3, self.rear_port1, self.front_port1_2, cable2
            ),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)

    def test_301_create_path_via_existing_cable(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [RP6] [FP6] --C3-- [IF2]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()

        # Create cable 2
        cable2 = Cable(termination_a=self.rear_port5, termination_b=self.rear_port6)
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port5_1)
        cable1.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port5_1, self.rear_port5, cable2, self.rear_port6, self.front_port6_1),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 3
        cable3 = Cable(termination_a=self.front_port6_1, termination_b=self.interface2)
        cable3.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(
                cable1, self.front_port5_1, self.rear_port5, cable2, self.rear_port6, self.front_port6_1,
                cable3,
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(
                cable3, self.front_port6_1, self.rear_port6, cable2, self.rear_port5, self.front_port5_1,
                cable1,
            ),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_302_update_path_on_cable_status_change(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [IF2]
        """
        self.interface1.refresh_from_db()
        self.interface2.refresh_from_db()

        # Create cables 1 and 2
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port5_1)
        cable1.save()
        cable2 = Cable(termination_a=self.rear_port5, termination_b=self.interface2)
        cable2.save()
        self.assertEqual(CablePath.objects.filter(is_connected=True).count(), 2)
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "planned"
        cable2.status = CableStatusChoices.STATUS_PLANNED
        cable2.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(cable1, self.front_port5_1, self.rear_port5, cable2),
            is_connected=False
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(cable2, self.rear_port5, self.front_port5_1, cable1),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "connected"
        cable2 = Cable.objects.get(pk=cable2.pk)
        cable2.status = CableStatusChoices.STATUS_CONNECTED
        cable2.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(cable1, self.front_port5_1, self.rear_port5, cable2),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(cable2, self.rear_port5, self.front_port5_1, cable1),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
