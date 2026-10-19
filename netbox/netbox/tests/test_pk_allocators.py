from unittest.mock import patch

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, connection, models, transaction
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from dcim.models import Manufacturer, Site
from extras.models import Tag
from netbox.constants import CORE_APPS
from netbox.registry import registry
from netbox.utils import allocate_pks, register_pk_allocator
from utilities.fields import NetBoxAutoField


def get_sequential_allocator(model, start=1_000_000):
    """
    Return an allocator which supplies sequential primary keys for `model` only, along with a list recording the
    arguments of each call it receives.
    """
    calls = []
    next_pk = start

    def allocator(model_, count):
        nonlocal next_pk
        calls.append((model_, count))
        if model_ is not model:
            return None
        pks = list(range(next_pk, next_pk + count))
        next_pk += count
        return pks

    return allocator, calls


class PKAllocatorTestCase(TestCase):

    def setUp(self):
        # Start each test with no registered allocators
        patcher = patch.dict(registry, {'pk_allocators': []})
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_table_writes(self, queries, model):
        """
        Return the INSERT and UPDATE statements issued against the given model's table.
        """
        table = connection.ops.quote_name(model._meta.db_table)
        sql = [q['sql'] for q in queries]
        inserts = [s for s in sql if s.startswith(f'INSERT INTO {table}')]
        updates = [s for s in sql if s.startswith(f'UPDATE {table}')]
        return inserts, updates

    def test_register_pk_allocator(self):
        def allocator(model, count):
            return None

        self.assertIs(register_pk_allocator(allocator), allocator)
        self.assertEqual(registry['pk_allocators'], [allocator])

    def test_allocate_pks_without_allocators(self):
        self.assertIsNone(allocate_pks(Site))
        self.assertIsNone(allocate_pks(Site, 5))

    def test_allocate_pks_consults_allocators_in_order(self):
        calls = []

        @register_pk_allocator
        def first(model, count):
            # Returns None to defer to the next allocator
            calls.append('first')

        @register_pk_allocator
        def second(model, count):
            calls.append('second')
            return [100 + i for i in range(count)]

        @register_pk_allocator
        def third(model, count):
            calls.append('third')
            return [200 + i for i in range(count)]

        self.assertEqual(allocate_pks(Site, 3), [100, 101, 102])
        self.assertEqual(calls, ['first', 'second'])

    def test_allocate_pks_iterable(self):
        register_pk_allocator(lambda model, count: (100 + i for i in range(count)))

        self.assertEqual(allocate_pks(Site, 2), [100, 101])

    def test_allocate_pks_wrong_count(self):
        register_pk_allocator(lambda model, count: [1])

        with self.assertRaises(ValueError):
            allocate_pks(Site, 2)

    def test_deconstruct(self):
        # NetBoxAutoField must present as BigAutoField to avoid generating migrations
        for field in (Site._meta.pk, Tag._meta.pk):
            name, path, args, kwargs = field.deconstruct()
            self.assertEqual(path, 'django.db.models.BigAutoField')

    def test_core_models_use_netbox_autofield(self):
        for model in apps.get_models(include_auto_created=True):
            if model._meta.app_label in CORE_APPS and isinstance(model._meta.pk, models.AutoField):
                with self.subTest(model=model._meta.label):
                    self.assertIsInstance(model._meta.pk, NetBoxAutoField)

    def test_save_without_allocator(self):
        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        self.assertIsNone(manufacturer.pk)

        with CaptureQueriesContext(connection) as ctx:
            manufacturer.save()

        # The database assigns the primary key on a single INSERT
        self.assertIsNotNone(manufacturer.pk)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(len(updates), 0)

    def test_save_with_allocator(self):
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)
        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')

        with CaptureQueriesContext(connection) as ctx:
            manufacturer.save()

        # The allocated primary key is used on a single INSERT, without first attempting an UPDATE
        self.assertEqual(manufacturer.pk, 1_000_000)
        self.assertIn((Manufacturer, 1), calls)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(len(updates), 0)
        self.assertTrue(Manufacturer.objects.filter(pk=1_000_000, name='Manufacturer 1').exists())

    def test_save_cloned_instance_with_allocator(self):
        # A fetched instance whose primary key has been cleared (e.g. to clone it) is also inserted directly
        source = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)
        clone = Manufacturer.objects.get(pk=source.pk)
        clone.pk = None
        clone.name, clone.slug = 'Manufacturer 2', 'manufacturer-2'

        with CaptureQueriesContext(connection) as ctx:
            clone.save()

        self.assertEqual(clone.pk, 1_000_000)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(len(updates), 0)
        self.assertEqual(Manufacturer.objects.count(), 2)

    def test_save_with_colliding_allocator(self):
        # An allocated primary key which is already in use fails on INSERT, rather than overwriting the existing row
        source = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        register_pk_allocator(lambda model, count: [source.pk] if model is Manufacturer else None)
        clone = Manufacturer.objects.get(pk=source.pk)
        clone.pk = None
        clone.name, clone.slug = 'Manufacturer 2', 'manufacturer-2'

        with self.assertRaises(IntegrityError), transaction.atomic():
            clone.save()
        source.refresh_from_db()
        self.assertEqual(source.name, 'Manufacturer 1')

    def test_save_with_declining_allocator(self):
        # The allocator supplies primary keys only for Site, so the database assigns one for the Manufacturer
        allocator, calls = get_sequential_allocator(Site)
        register_pk_allocator(allocator)
        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        self.assertIn((Manufacturer, 1), calls)
        self.assertIsNotNone(manufacturer.pk)
        self.assertLess(manufacturer.pk, 1_000_000)

    def test_bulk_create_with_allocator(self):
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)
        manufacturers = [
            Manufacturer(name=f'Manufacturer {i}', slug=f'manufacturer-{i}') for i in range(1, 4)
        ]

        with CaptureQueriesContext(connection) as ctx:
            Manufacturer.objects.bulk_create(manufacturers)

        # Each object is assigned an allocated primary key, and all are inserted in one statement
        pks = [1_000_000, 1_000_001, 1_000_002]
        self.assertEqual([m.pk for m in manufacturers], pks)
        self.assertEqual(calls, [(Manufacturer, 1)] * 3)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(sorted(Manufacturer.objects.values_list('pk', flat=True)), pks)

    def test_many_to_many_with_allocator(self):
        # Auto-created many-to-many through models also use NetBoxAutoField
        through_model = Tag.object_types.through
        allocator, calls = get_sequential_allocator(through_model)
        register_pk_allocator(allocator)
        tag = Tag.objects.create(name='Tag 1', slug='tag-1')
        tag.object_types.add(ContentType.objects.get_for_model(Site))

        self.assertIn((through_model, 1), calls)
        self.assertEqual(list(through_model.objects.filter(tag=tag).values_list('pk', flat=True)), [1_000_000])

    def test_save_new_instance_with_existing_pk(self):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        # A raw save (e.g. when loading deserialized data) updates the existing row
        Manufacturer(pk=manufacturer.pk, name='Manufacturer 2', slug='manufacturer-2').save_base(raw=True)
        manufacturer.refresh_from_db()
        self.assertEqual(manufacturer.name, 'Manufacturer 2')

        # A forced update updates the existing row
        Manufacturer(pk=manufacturer.pk, name='Manufacturer 3', slug='manufacturer-3').save(force_update=True)
        manufacturer.refresh_from_db()
        self.assertEqual(manufacturer.name, 'Manufacturer 3')

        # Otherwise, saving a new instance always attempts an INSERT
        with self.assertRaises(IntegrityError), transaction.atomic():
            Manufacturer(pk=manufacturer.pk, name='Manufacturer 4', slug='manufacturer-4').save()
