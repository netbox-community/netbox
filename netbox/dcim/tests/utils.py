from django.test import TestCase

from circuits.models import *
from dcim.models import *
from dcim.utils import object_to_path_node

__all__ = (
    'CablePathTestCase',
)


class CablePathTestCase(TestCase):
    """
    Base class for test cases for cable paths.
    """
    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')

        # Create reusable test objects
        cls.site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(site=cls.site, device_type=device_type, role=role, name='Test Device')
        cls.powerpanel = PowerPanel.objects.create(site=cls.site, name='Power Panel')
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
