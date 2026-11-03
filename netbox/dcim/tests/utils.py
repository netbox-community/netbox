import uuid

from django.test import RequestFactory, TestCase

from circuits.models import *
from core.models import ObjectChange
from dcim.models import *
from dcim.utils import object_to_path_node
from netbox.context_managers import event_tracking
from utilities.testing.utils import create_test_user

__all__ = (
    'BaseCablePathTestCase',
)


class BaseCablePathTestCase(TestCase):
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

    def assertCurrentPathExists(self, nodes, **kwargs):
        """
        Assert that the first node references a CablePath with the given route via _path, and return it.

        :param nodes: Iterable of steps, the first being the originating path endpoint object
        """
        origin = type(nodes[0]).objects.get(pk=nodes[0].pk)
        self.assertIsNotNone(origin._path_id, msg=f'No path set on originating endpoint {origin}')
        # Matched on the route alone, so a flag mismatch does not report itself as a wrong route
        cablepath = self._get_cablepath(nodes, pk=origin._path_id)
        self.assertIsNotNone(cablepath, msg=f'Path #{origin._path_id} on {origin} does not match the expected route')
        for attr, expected in kwargs.items():
            self.assertEqual(getattr(cablepath, attr), expected, msg=f'Path #{cablepath.pk} on {origin}: {attr}')
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

    def update_dependent_objects(self, obj):
        """
        Call update_dependent_objects() on a fresh copy of obj twice under change tracking, asserting that neither
        call records an ObjectChange and that the second call leaves the CablePaths unchanged.
        """
        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = create_test_user()

        def get_paths():
            return sorted((p.path, p.is_complete, p.is_active, p.is_split) for p in CablePath.objects.all())

        with event_tracking(request):
            type(obj).objects.get(pk=obj.pk).update_dependent_objects()
            paths = get_paths()
            type(obj).objects.get(pk=obj.pk).update_dependent_objects()
        self.assertEqual(get_paths(), paths)
        self.assertFalse(ObjectChange.objects.filter(request_id=request.id).exists())
