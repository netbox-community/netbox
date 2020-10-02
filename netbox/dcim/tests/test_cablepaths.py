from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.models import *
from dcim.choices import CableStatusChoices
from dcim.models import *
from dcim.utils import objects_to_path


class CablePathTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Create a single device that will hold all components
        site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        device = Device.objects.create(site=site, device_type=device_type, device_role=device_role, name='Test Device')

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

        # Create four circuits with two terminations (A and Z) each (8 total)
        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        circuits = [
            Circuit(provider=provider, type=circuit_type, cid=f'Circuit {i}') for i in range(1, 5)
        ]
        Circuit.objects.bulk_create(circuits)
        cls.circuit_terminations = [
            *[CircuitTermination(circuit=circuit, site=site, term_side='A', port_speed=1000) for circuit in circuits],
            *[CircuitTermination(circuit=circuit, site=site, term_side='Z', port_speed=1000) for circuit in circuits],
        ]
        CircuitTermination.objects.bulk_create(cls.circuit_terminations)

    def assertPathExists(self, origin, destination, path=None, is_connected=None, msg=None):
        """
        Assert that a CablePath from origin to destination with a specific intermediate path exists.

        :param origin: Originating endpoint
        :param destination: Terminating endpoint, or None
        :param path: Sequence of objects comprising the intermediate path (optional)
        :param is_connected: Boolean indicating whether the end-to-end path is complete and active (optional)
        :param msg: Custom failure message (optional)
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
        self.assertEqual(CablePath.objects.filter(**kwargs).count(), 1, msg=msg)

    def test_01_interface_to_interface(self):
        """
        [IF1] --C1-- [IF2]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.interface1, termination_b=self.interface2)
        cable1.save()
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface2,
            path=(cable1,),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface1,
            path=(cable1,),
            is_connected=True
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_02_interface_to_interface_via_pass_through(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [IF2]
        """
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
        self.assertPathExists(
            origin=self.interface1,
            destination=None,
            path=(cable1, self.front_port5_1, self.rear_port5),
            is_connected=False
        )
        self.assertEqual(CablePath.objects.count(), 1)

    def test_03_interfaces_to_interfaces_via_pass_through(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:2] --C5-- [IF4]
        """
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
        self.assertPathExists(
            origin=self.interface1,
            destination=self.interface3,
            path=(
                cable1, self.front_port1_1, self.rear_port1, cable3, self.rear_port2, self.front_port2_1,
                cable4,
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface2,
            destination=self.interface4,
            path=(
                cable2, self.front_port1_2, self.rear_port1, cable3, self.rear_port2, self.front_port2_2,
                cable5,
            ),
            is_connected=True
        )
        self.assertPathExists(
            origin=self.interface3,
            destination=self.interface1,
            path=(
                cable4, self.front_port2_1, self.rear_port2, cable3, self.rear_port1, self.front_port1_1,
                cable1
            ),
            is_connected=True
        )
        self.assertPathExists(
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

    def test_04_interfaces_to_interfaces_via_nested_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP2:1] [RP2] --C4-- [RP3] [FP3:1] --C5-- [RP4] [FP4:1] --C6-- [IF3]
        [IF2] --C2-- [FP1:2]                                                              [FP4:2] --C7-- [IF4]
        """
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

    def test_05_interfaces_to_interfaces_via_multiple_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [RP2] [FP2:1] --C4-- [FP3:1] [RP3] --C6-- [RP4] [FP4:1] --C7-- [IF3]
        [IF2] --C2-- [FP1:2]                    [FP2:1] --C5-- [FP3:1]                    [FP4:2] --C8-- [IF4]
        """
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

    def test_06_interfaces_to_interfaces_via_patched_pass_throughs(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C3-- [FP5] [RP5] --C4-- [RP2] [FP2:1] --C5-- [IF3]
        [IF2] --C2-- [FP1:2]                                       [FP2:2] --C6-- [IF4]
        """
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

    def test_07_interface_to_interface_via_existing_cable(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [RP6] [FP6] --C3-- [IF2]
        """
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

    def test_08_change_cable_status(self):
        """
        [IF1] --C1-- [FP5] [RP5] --C2-- [IF2]
        """
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
