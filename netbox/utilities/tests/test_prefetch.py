from unittest.mock import PropertyMock, patch

from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models import FETCH_ONE, FETCH_RAISE

from circuits.models import Circuit, Provider
from core.models import ObjectType
from dcim.choices import PortTypeChoices
from dcim.models import Cable, CablePath, ConsolePort, ConsoleServerPort, FrontPort, PortMapping, RearPort
from extras.models import CachedValue
from utilities.prefetch import get_prefetchable_fields
from utilities.querysets import RestrictedPrefetch
from utilities.testing.base import TestCase
from utilities.testing.utils import create_test_device


class GetPrefetchableFieldsTestCase(TestCase):
    """
    Verify the operation of get_prefetchable_fields()
    """
    def test_get_prefetchable_fields(self):
        field_names = get_prefetchable_fields(Provider)
        self.assertIn('asns', field_names)  # ManyToManyField
        self.assertIn('circuits', field_names)  # Reverse relation
        self.assertIn('tags', field_names)  # Tags

        field_names = get_prefetchable_fields(Circuit)
        self.assertIn('group_assignments', field_names)  # Generic relation


class RestrictedGenericForeignKeyTestCase(TestCase):
    """
    Verify the prefetching behavior of RestrictedGenericForeignKey.
    """
    user_permissions = ('circuits.view_provider',)

    def setUp(self):
        super().setUp()

        self.provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        CachedValue.objects.create(
            object_type=ObjectType.objects.get_for_model(Provider),
            object_id=self.provider.pk,
            field='name',
            type='string',
            value=self.provider.name,
        )

    def _prefetch_object(self, queryset):
        cached_value = list(queryset.prefetch_related(RestrictedPrefetch('object', self.user, 'view')))[0]
        return cached_value.object

    def test_prefetch_propagates_fetch_mode(self):
        """
        The fetch mode of the objects being prefetched is carried over to the objects prefetched
        onto them, as Django's GenericForeignKeyDescriptor does.
        """
        obj = self._prefetch_object(CachedValue.objects.fetch_mode(FETCH_RAISE))

        self.assertEqual(obj, self.provider)
        self.assertIs(obj._state.fetch_mode, FETCH_RAISE)

    def test_prefetch_default_fetch_mode(self):
        """
        A queryset which sets no fetch mode yields prefetched objects using the default mode.
        """
        obj = self._prefetch_object(CachedValue.objects.all())

        self.assertEqual(obj, self.provider)
        self.assertIs(obj._state.fetch_mode, FETCH_ONE)

    def test_prefetch_resolves_target_without_objects_manager(self):
        """
        A target model which names its manager something other than `objects` resolves through
        the default manager.
        """
        with patch.object(Provider, 'objects', new_callable=PropertyMock, side_effect=AttributeError):
            cached_value = list(CachedValue.objects.prefetch_related('object'))[0]
            # A resolved prefetch leaves nothing for the relation access to fetch
            with self.assertNumQueries(0):
                obj = cached_value.object

        self.assertEqual(obj, self.provider)


class GenericArrayForeignKeyTestCase(TestCase):
    """
    Verify the prefetching behavior of GenericArrayForeignKey.
    """
    def setUp(self):
        super().setUp()

        # A cable path through a patch panel, whose array holds five object types
        console_port = ConsolePort.objects.create(device=create_test_device('Device 1'), name='Console Port 1')
        panel = create_test_device('Panel 1')
        front_port = FrontPort.objects.create(device=panel, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C)
        rear_port = RearPort.objects.create(device=panel, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C)
        PortMapping.objects.create(device=panel, front_port=front_port, rear_port=rear_port)
        console_server_port = ConsoleServerPort.objects.create(
            device=create_test_device('Peer 1'), name='Console Server Port 1'
        )
        Cable(a_terminations=[console_port], b_terminations=[front_port]).save()
        Cable(a_terminations=[rear_port], b_terminations=[console_server_port]).save()
        console_port.refresh_from_db()
        self.cable_path_id = console_port._path_id

    def _prefetch_path_objects(self, queryset, lookup='path_objects'):
        cable_path = list(queryset.filter(pk=self.cable_path_id).prefetch_related(lookup))[0]
        return [obj for objects in cable_path.path_objects for obj in objects]

    def test_prefetch_propagates_fetch_mode(self):
        """
        The fetch mode of the instances being prefetched is carried over to every object prefetched onto them,
        whatever its type.
        """
        objects = self._prefetch_path_objects(CablePath.objects.fetch_mode(FETCH_RAISE))

        self.assertEqual({type(obj) for obj in objects}, {ConsolePort, Cable, FrontPort, RearPort, ConsoleServerPort})
        for obj in objects:
            self.assertIs(obj._state.fetch_mode, FETCH_RAISE)

    def test_prefetch_default_fetch_mode(self):
        """
        A queryset which sets no fetch mode yields prefetched objects using the default mode.
        """
        objects = self._prefetch_path_objects(CablePath.objects.all())

        self.assertEqual(len(objects), 6)
        for obj in objects:
            self.assertIs(obj._state.fetch_mode, FETCH_ONE)

    def test_prefetch_custom_queryset_fetch_mode(self):
        """
        Objects from a custom queryset take the fetch mode of the instances and keep the queryset's related objects.
        """
        lookup = GenericPrefetch('path_objects', [ConsoleServerPort.objects.select_related('device')])
        console_server_port = self._prefetch_path_objects(CablePath.objects.fetch_mode(FETCH_RAISE), lookup)[-1]

        self.assertIsInstance(console_server_port, ConsoleServerPort)
        self.assertIs(console_server_port._state.fetch_mode, FETCH_RAISE)
        # FETCH_RAISE would block a device fetch the custom queryset had not loaded
        self.assertEqual(console_server_port.device.name, 'Peer 1')
