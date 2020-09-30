from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.models import *
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

        # Create 16 instances of each type of path-terminating component
        cls.console_ports = [
            ConsolePort(device=device, name=f'Console Port {i}')
            for i in range(1, 17)
        ]
        ConsolePort.objects.bulk_create(cls.console_ports)
        cls.console_server_ports = [
            ConsoleServerPort(device=device, name=f'Console Server Port {i}')
            for i in range(1, 17)
        ]
        ConsoleServerPort.objects.bulk_create(cls.console_server_ports)
        cls.power_ports = [
            PowerPort(device=device, name=f'Power Port {i}')
            for i in range(1, 17)
        ]
        PowerPort.objects.bulk_create(cls.power_ports)
        cls.power_outlets = [
            PowerOutlet(device=device, name=f'Power Outlet {i}')
            for i in range(1, 17)
        ]
        PowerOutlet.objects.bulk_create(cls.power_outlets)
        cls.interfaces = [
            Interface(device=device, name=f'Interface {i}')
            for i in range(1, 17)
        ]
        Interface.objects.bulk_create(cls.interfaces)

        # Create four RearPorts with four FrontPorts each
        cls.rear_ports = [
            RearPort(device=device, name=f'RP{i}', positions=4) for i in range(1, 5)
        ]
        RearPort.objects.bulk_create(cls.rear_ports)
        cls.front_ports = []
        for i, rear_port in enumerate(cls.rear_ports, start=1):
            cls.front_ports.extend(
                FrontPort(device=device, name=f'FP{i}:{j}', rear_port=rear_port, rear_port_position=j)
                for j in range(1, 5)
            )
        FrontPort.objects.bulk_create(cls.front_ports)

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

    def assertPathExists(self, origin, destination, path=None, msg=None):
        """
        Assert that a CablePath from origin to destination with a specific intermediate path exists.

        :param origin: Originating endpoint
        :param destination: Terminating endpoint, or None
        :param path: Sequence of objects comprising the intermediate path (optional)
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
        cable1 = Cable(termination_a=self.interfaces[0], termination_b=self.interfaces[1])
        cable1.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=self.interfaces[1],
            path=(cable1,)
        )
        self.assertPathExists(
            origin=self.interfaces[1],
            destination=self.interfaces[0],
            path=(cable1,)
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 1
        cable1.delete()
        self.assertEqual(CablePath.objects.count(), 0)

    def test_02_interface_to_interface_via_single_frontport(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C2-- [IF2]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.interfaces[0], termination_b=self.front_ports[0])
        cable1.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=None,
            path=(cable1, self.front_ports[0], self.rear_ports[0])
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(termination_a=self.rear_ports[0], termination_b=self.interfaces[1])
        cable2.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=self.interfaces[1],
            path=(cable1, self.front_ports[0], self.rear_ports[0], cable2)
        )
        self.assertPathExists(
            origin=self.interfaces[1],
            destination=self.interfaces[0],
            path=(cable2, self.rear_ports[0], self.front_ports[0], cable1)
        )
        self.assertEqual(CablePath.objects.count(), 5)  # Two complete + three partial paths

        # Delete cable 1
        cable1.delete()
        self.assertPathExists(
            origin=self.interfaces[1],
            destination=None,
            path=(cable2, self.rear_ports[0], self.front_ports[0])
        )
        self.assertEqual(CablePath.objects.count(), 4)  # Four partial paths from IF2 to FP1:[1-4]

    def test_03_interface_to_interface_via_rearport_pair(self):
        """
        [IF1] --C1-- [FP1:1] [RP1] --C2-- [RP2] [FP2:1] --C3-- [IF2]
        """
        # Create cable 1
        cable1 = Cable(termination_a=self.interfaces[0], termination_b=self.front_ports[0])
        cable1.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=None,
            path=(cable1, self.front_ports[0], self.rear_ports[0])
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 2
        cable2 = Cable(termination_a=self.rear_ports[0], termination_b=self.rear_ports[1])
        cable2.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=None,
            path=(cable1, self.front_ports[0], self.rear_ports[0], cable2, self.rear_ports[1], self.front_ports[4])
        )
        self.assertEqual(CablePath.objects.count(), 1)

        # Create cable 3
        cable3 = Cable(termination_a=self.front_ports[4], termination_b=self.interfaces[1])
        cable3.save()
        self.assertPathExists(
            origin=self.interfaces[0],
            destination=self.interfaces[1],
            path=(
                cable1, self.front_ports[0], self.rear_ports[0], cable2, self.rear_ports[1], self.front_ports[4],
                cable3,
            )
        )
        self.assertPathExists(
            origin=self.interfaces[1],
            destination=self.interfaces[0],
            path=(
                cable3, self.front_ports[4], self.rear_ports[1], cable2, self.rear_ports[0], self.front_ports[0],
                cable1
            )
        )
        self.assertEqual(CablePath.objects.count(), 2)

        # Delete cable 2
        cable2.delete()
        self.assertEqual(CablePath.objects.count(), 2)  # Two partial paths from IF1 and IF2
