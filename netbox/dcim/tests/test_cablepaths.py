from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.models import *
from dcim.choices import LinkStatusChoices
from dcim.models import *
from dcim.utils import object_to_path_node


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
        cls.site = Site.objects.create(name='Site', slug='site')

        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.device = Device.objects.create(site=cls.site, device_type=device_type, device_role=device_role, name='Test Device')

        cls.powerpanel = PowerPanel.objects.create(site=cls.site, name='Power Panel')

        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        cls.circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')

    def assertPathExists(self, origin, destination, path=None, is_active=None, msg=None):
        """
        Assert that a CablePath from origin to destination with a specific intermediate path exists.

        :param origin: Originating endpoint
        :param destination: Terminating endpoint, or None
        :param path: Sequence of objects comprising the intermediate path (optional)
        :param is_active: Boolean indicating whether the end-to-end path is complete and active (optional)
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
            kwargs['path'] = [object_to_path_node(obj) for obj in path]
        if is_active is not None:
            kwargs['is_active'] = is_active
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
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')

        # Create cable 1
        cable1 = Cable(termination_a=interface1, termination_b=interface2)
        cable1.save()
        path1 = self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1,),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable1,),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

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
        cable1 = Cable(termination_a=consoleport1, termination_b=consoleserverport1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=consoleport1,
            destination=consoleserverport1,
            path=(cable1,),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=consoleserverport1,
            destination=consoleport1,
            path=(cable1,),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        consoleport1.refresh_from_db()
        consoleserverport1.refresh_from_db()
        self.assertPathIsSet(consoleport1, path1)
        self.assertPathIsSet(consoleserverport1, path2)

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
        cable1 = Cable(termination_a=powerport1, termination_b=poweroutlet1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=powerport1,
            destination=poweroutlet1,
            path=(cable1,),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=poweroutlet1,
            destination=powerport1,
            path=(cable1,),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        powerport1.refresh_from_db()
        poweroutlet1.refresh_from_db()
        self.assertPathIsSet(powerport1, path1)
        self.assertPathIsSet(poweroutlet1, path2)

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
        cable1 = Cable(termination_a=powerport1, termination_b=powerfeed1)
        cable1.save()
        path1 = self.assertPathExists(
            origin=powerport1,
            destination=powerfeed1,
            path=(cable1,),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=powerfeed1,
            destination=powerport1,
            path=(cable1,),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        powerport1.refresh_from_db()
        powerfeed1.refresh_from_db()
        self.assertPathIsSet(powerport1, path1)
        self.assertPathIsSet(powerfeed1, path2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1)
        cable1.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1, rearport1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(termination_a=rearport1, termination_b=interface2)
        cable2.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1, frontport1, rearport1, cable2),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable2, rearport1, frontport1, cable1),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1, rearport1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsNotSet(interface2)

    def test_202_multiple_paths_via_pass_through(self):
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1_1)
        cable1.save()
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_2)
        cable2.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1_1, rearport1),
            is_active=False
        )
        self.assertPathExists(
            origin=interface2,
            destination=None,
            path=(cable2, frontport1_2, rearport1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cable 3
        cable3 = Cable(termination_a=rearport1, termination_b=rearport2)
        cable3.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1),
            is_active=False
        )
        self.assertPathExists(
            origin=interface2,
            destination=None,
            path=(cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Create cables 4-5
        cable4 = Cable(termination_a=frontport2_1, termination_b=interface3)
        cable4.save()
        cable5 = Cable(termination_a=frontport2_2, termination_b=interface4)
        cable5.save()
        path1 = self.assertPathExists(
            origin=interface1,
            destination=interface3,
            path=(
                cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1,
                cable4,
            ),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=interface2,
            destination=interface4,
            path=(
                cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2,
                cable5,
            ),
            is_active=True
        )
        path3 = self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(
                cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1,
                cable1
            ),
            is_active=True
        )
        path4 = self.assertPathExists(
            origin=interface4,
            destination=interface2,
            path=(
                cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2,
                cable2
            ),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        interface3.refresh_from_db()
        interface4.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)
        self.assertPathIsSet(interface3, path3)
        self.assertPathIsSet(interface4, path4)

    def test_203_multiple_paths_via_nested_pass_throughs(self):
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1_1)
        cable1.save()
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_2)
        cable2.save()
        cable6 = Cable(termination_a=interface3, termination_b=frontport4_1)
        cable6.save()
        cable7 = Cable(termination_a=interface4, termination_b=frontport4_2)
        cable7.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3 and 5
        cable3 = Cable(termination_a=rearport1, termination_b=frontport2)
        cable3.save()
        cable5 = Cable(termination_a=rearport4, termination_b=frontport3)
        cable5.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four (longer) partial paths; one from each interface

        # Create cable 4
        cable4 = Cable(termination_a=rearport2, termination_b=rearport3)
        cable4.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface3,
            path=(
                cable1, frontport1_1, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3, cable5, rearport4, frontport4_1,
                cable6
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface4,
            path=(
                cable2, frontport1_2, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3, cable5, rearport4, frontport4_2,
                cable7
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(
                cable6, frontport4_1, rearport4, cable5, frontport3, rearport3,
                cable4, rearport2, frontport2, cable3, rearport1, frontport1_1,
                cable1
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface4,
            destination=interface2,
            path=(
                cable7, frontport4_2, rearport4, cable5, frontport3, rearport3,
                cable4, rearport2, frontport2, cable3, rearport1, frontport1_2,
                cable2
            ),
            is_active=True
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1_1)
        cable1.save()
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_2)
        cable2.save()
        cable3 = Cable(termination_a=rearport1, termination_b=rearport2)
        cable3.save()
        cable6 = Cable(termination_a=rearport3, termination_b=rearport4)
        cable6.save()
        cable7 = Cable(termination_a=interface3, termination_b=frontport4_1)
        cable7.save()
        cable8 = Cable(termination_a=interface4, termination_b=frontport4_2)
        cable8.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 4 and 5
        cable4 = Cable(termination_a=frontport2_1, termination_b=frontport3_1)
        cable4.save()
        cable5 = Cable(termination_a=frontport2_2, termination_b=frontport3_2)
        cable5.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface3,
            path=(
                cable1, frontport1_1, rearport1, cable3, rearport2, frontport2_1,
                cable4, frontport3_1, rearport3, cable6, rearport4, frontport4_1,
                cable7
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface4,
            path=(
                cable2, frontport1_2, rearport1, cable3, rearport2, frontport2_2,
                cable5, frontport3_2, rearport3, cable6, rearport4, frontport4_2,
                cable8
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(
                cable7, frontport4_1, rearport4, cable6, rearport3, frontport3_1,
                cable4, frontport2_1, rearport2, cable3, rearport1, frontport1_1,
                cable1
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface4,
            destination=interface2,
            path=(
                cable8, frontport4_2, rearport4, cable6, rearport3, frontport3_2,
                cable5, frontport2_2, rearport2, cable3, rearport1, frontport1_2,
                cable2
            ),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 5
        cable5.delete()

        # Check for two complete paths (IF1 <--> IF2) and two partial (IF3 <--> IF4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 2)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 2)

    def test_205_multiple_paths_via_patched_pass_throughs(self):
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1_1)  # IF1 -> FP1:1
        cable1.save()
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_2)  # IF2 -> FP1:2
        cable2.save()
        cable5 = Cable(termination_a=interface3, termination_b=frontport3_1)  # IF3 -> FP3:1
        cable5.save()
        cable6 = Cable(termination_a=interface4, termination_b=frontport3_2)  # IF4 -> FP3:2
        cable6.save()
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths; one from each interface

        # Create cables 3-4
        cable3 = Cable(termination_a=rearport1, termination_b=frontport2)  # RP1 -> FP2
        cable3.save()
        cable4 = Cable(termination_a=rearport2, termination_b=rearport3)  # RP2 -> RP3
        cable4.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface3,
            path=(
                cable1, frontport1_1, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3_1, cable5
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface4,
            path=(
                cable2, frontport1_2, rearport1, cable3, frontport2, rearport2,
                cable4, rearport3, frontport3_2, cable6
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(
                cable5, frontport3_1, rearport3, cable4, rearport2, frontport2,
                cable3, rearport1, frontport1_1, cable1
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface4,
            destination=interface2,
            path=(
                cable6, frontport3_2, rearport3, cable4, rearport2, frontport2,
                cable3, rearport1, frontport1_2, cable2
            ),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cable 3
        cable3.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)

    def test_206_unidirectional_split_paths(self):
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
        cable1 = Cable(termination_a=interface1, termination_b=rearport1)
        cable1.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, rearport1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cables 2-3
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_1)
        cable2.save()
        cable3 = Cable(termination_a=interface3, termination_b=frontport1_2)
        cable3.save()
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable2, frontport1_1, rearport1, cable1),
            is_active=True
        )
        self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(cable3, frontport1_2, rearport1, cable1),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 3)

        # Delete cable 1
        cable1.delete()

        # Check that the partial path was deleted and the two complete paths are now partial
        self.assertPathExists(
            origin=interface2,
            destination=None,
            path=(cable2, frontport1_1, rearport1),
            is_active=False
        )
        self.assertPathExists(
            origin=interface3,
            destination=None,
            path=(cable3, frontport1_2, rearport1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

    def test_207_rearport_without_frontport(self):
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1)
        cable1.save()
        cable2 = Cable(termination_a=rearport1, termination_b=rearport2)
        cable2.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1, rearport1, cable2, rearport2),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

    def test_208_circuittermination(self):
        """
        [IF1] --C1-- [CT1]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')

        # Create cable 1
        cable1 = Cable(termination_a=interface1, termination_b=circuittermination1)
        cable1.save()

        # Check for incomplete path
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, circuittermination1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_209_circuit_to_interface(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')

        # Create cable 1
        cable1 = Cable(termination_a=interface1, termination_b=circuittermination1)
        cable1.save()

        # Check for partial path from interface1
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, circuittermination1),
            is_active=False
        )

        # Create CT2
        circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='Z')

        # Check for partial path to site
        self.assertPathExists(
            origin=interface1,
            destination=self.site,
            path=(cable1, circuittermination1, circuittermination2),
            is_active=True
        )

        # Create cable 2
        cable2 = Cable(termination_a=circuittermination2, termination_b=interface2)
        cable2.save()

        # Check for complete path in each direction
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1, circuittermination1, circuittermination2, cable2),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable2, circuittermination2, circuittermination1, cable1),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            origin=interface1,
            destination=self.site,
            path=(cable1, circuittermination1, circuittermination2),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsNotSet(interface2)

    def test_210_circuit_to_site(self):
        """
        [IF1] --C1-- [CT1] [CT2] --> [Site2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        site2 = Site.objects.create(name='Site 2', slug='site-2')
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')
        circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=site2, term_side='Z')

        # Create cable 1
        cable1 = Cable(termination_a=interface1, termination_b=circuittermination1)
        cable1.save()
        self.assertPathExists(
            origin=interface1,
            destination=site2,
            path=(cable1, circuittermination1, circuittermination2),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_211_circuit_to_providernetwork(self):
        """
        [IF1] --C1-- [CT1] [CT2] --> [PN1]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        providernetwork = ProviderNetwork.objects.create(name='Provider Network 1', provider=self.circuit.provider)
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')
        circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, provider_network=providernetwork, term_side='Z')

        # Create cable 1
        cable1 = Cable(termination_a=interface1, termination_b=circuittermination1)
        cable1.save()
        self.assertPathExists(
            origin=interface1,
            destination=providernetwork,
            path=(cable1, circuittermination1, circuittermination2),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface1.refresh_from_db()
        self.assertPathIsNotSet(interface1)

    def test_212_multiple_paths_via_circuit(self):
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
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')
        circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='Z')

        # Create cables
        cable1 = Cable(termination_a=interface1, termination_b=frontport1_1)  # IF1 -> FP1:1
        cable1.save()
        cable2 = Cable(termination_a=interface2, termination_b=frontport1_2)  # IF2 -> FP1:2
        cable2.save()
        cable3 = Cable(termination_a=rearport1, termination_b=circuittermination1)  # RP1 -> CT1
        cable3.save()
        cable4 = Cable(termination_a=rearport2, termination_b=circuittermination2)  # RP2 -> CT2
        cable4.save()
        cable5 = Cable(termination_a=interface3, termination_b=frontport2_1)  # IF3 -> FP2:1
        cable5.save()
        cable6 = Cable(termination_a=interface4, termination_b=frontport2_2)  # IF4 -> FP2:2
        cable6.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface3,
            path=(
                cable1, frontport1_1, rearport1, cable3, circuittermination1, circuittermination2,
                cable4, rearport2, frontport2_1, cable5
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface4,
            path=(
                cable2, frontport1_2, rearport1, cable3, circuittermination1, circuittermination2,
                cable4, rearport2, frontport2_2, cable6
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface3,
            destination=interface1,
            path=(
                cable5, frontport2_1, rearport2, cable4, circuittermination2, circuittermination1,
                cable3, rearport1, frontport1_1, cable1
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface4,
            destination=interface2,
            path=(
                cable6, frontport2_2, rearport2, cable4, circuittermination2, circuittermination1,
                cable3, rearport1, frontport1_2, cable2
            ),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        # Delete cables 3-4
        cable3.delete()
        cable4.delete()

        # Check for four partial paths; one from each interface
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=True).count(), 4)
        self.assertEqual(CablePath.objects.filter(destination_id__isnull=False).count(), 0)

    def test_213_multiple_circuits_to_interface(self):
        """
        [IF1] --C1-- [CT1] [CT2] --C2-- [CT3] [CT4] --C3-- [IF2]
        """
        interface1 = Interface.objects.create(device=self.device, name='Interface 1')
        interface2 = Interface.objects.create(device=self.device, name='Interface 2')
        circuit2 = Circuit.objects.create(provider=self.circuit.provider, type=self.circuit.type, cid='Circuit 2')
        circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='A')
        circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=self.site, term_side='Z')
        circuittermination3 = CircuitTermination.objects.create(circuit=circuit2, site=self.site, term_side='A')
        circuittermination4 = CircuitTermination.objects.create(circuit=circuit2, site=self.site, term_side='Z')

        # Create cables
        cable1 = Cable(termination_a=interface1, termination_b=circuittermination1)
        cable1.save()
        cable2 = Cable(termination_a=circuittermination2, termination_b=circuittermination3)
        cable2.save()
        cable3 = Cable(termination_a=circuittermination4, termination_b=interface2)
        cable3.save()

        # Check for paths
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(
                cable1, circuittermination1, circuittermination2, cable2, circuittermination3, circuittermination4,
                cable3
            ),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(
                cable3, circuittermination4, circuittermination3, cable2, circuittermination2, circuittermination1,
                cable1
            ),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 2
        cable2.delete()
        path1 = self.assertPathExists(
            origin=interface1,
            destination=self.site,
            path=(cable1, circuittermination1, circuittermination2),
            is_active=True
        )
        path2 = self.assertPathExists(
            origin=interface2,
            destination=self.site,
            path=(cable3, circuittermination4, circuittermination3),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interface1.refresh_from_db()
        interface2.refresh_from_db()
        self.assertPathIsSet(interface1, path1)
        self.assertPathIsSet(interface2, path2)

    def test_301_create_path_via_existing_cable(self):
        """
        [IF1] --C1-- [FP1] [RP2] --C2-- [RP2] [FP2] --C3-- [IF2]
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
        cable2 = Cable(termination_a=rearport1, termination_b=rearport2)
        cable2.save()
        self.assertEqual(CablePath.objects.count(), 0)

        # Create cable1
        cable1 = Cable(termination_a=interface1, termination_b=frontport1)
        cable1.save()
        self.assertPathExists(
            origin=interface1,
            destination=None,
            path=(cable1, frontport1, rearport1, cable2, rearport2, frontport2),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 3
        cable3 = Cable(termination_a=frontport2, termination_b=interface2)
        cable3.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1, frontport1, rearport1, cable2, rearport2, frontport2, cable3),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable3, frontport2, rearport2, cable2, rearport1, frontport1, cable1),
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
        cable1 = Cable(termination_a=interface1, termination_b=frontport1)
        cable1.save()
        cable2 = Cable(termination_a=rearport1, termination_b=interface2)
        cable2.save()
        self.assertEqual(CablePath.objects.filter(is_active=True).count(), 2)
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "planned"
        cable2.status = LinkStatusChoices.STATUS_PLANNED
        cable2.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1, frontport1, rearport1, cable2),
            is_active=False
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable2, rearport1, frontport1, cable1),
            is_active=False
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Change cable 2's status to "connected"
        cable2 = Cable.objects.get(pk=cable2.pk)
        cable2.status = LinkStatusChoices.STATUS_CONNECTED
        cable2.save()
        self.assertPathExists(
            origin=interface1,
            destination=interface2,
            path=(cable1, frontport1, rearport1, cable2),
            is_active=True
        )
        self.assertPathExists(
            origin=interface2,
            destination=interface1,
            path=(cable2, rearport1, frontport1, cable1),
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
