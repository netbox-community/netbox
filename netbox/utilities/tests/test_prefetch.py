from django.db.models import FETCH_ONE, FETCH_RAISE

from circuits.models import Circuit, Provider
from core.models import ObjectType
from extras.models import CachedValue
from utilities.prefetch import get_prefetchable_fields
from utilities.querysets import RestrictedPrefetch
from utilities.testing.base import TestCase


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
