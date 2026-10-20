import inspect
from unittest.mock import patch

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, IntegrityError, connection, router, transaction
from django.db.migrations.state import ProjectState
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from account.models import UserToken
from core.models import ObjectType
from dcim.models import Manufacturer, Site
from extras.models import Tag
from netbox.registry import registry
from netbox.utils import allocate_pks, register_pk_allocator
from tenancy.models import Tenant
from users.models import Token, User
from utilities import pk_allocation


def get_sequential_allocator(model, start=1_000_000):
    """
    Return an allocator which supplies sequential primary keys for `model` only, along with a list recording the
    arguments of each call it receives. Models are matched by table rather than by class, so that the historical
    models used by data migrations match too.
    """
    calls = []
    next_pk = start

    def allocator(model_, count, using):
        nonlocal next_pk
        calls.append((model_, count, using))
        if model_._meta.db_table != model._meta.db_table:
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
        def allocator(model, count, using):
            return None

        self.assertIs(register_pk_allocator(allocator), allocator)
        self.assertEqual(registry['pk_allocators'], [allocator])

        # Registering the same allocator again has no effect
        register_pk_allocator(allocator)
        self.assertEqual(registry['pk_allocators'], [allocator])

    def test_allocate_pks_without_allocators(self):
        self.assertIsNone(allocate_pks(Site))
        self.assertIsNone(allocate_pks(Site, 5))

    def test_allocate_pks_consults_allocators_in_order(self):
        calls = []

        @register_pk_allocator
        def first(model, count, using):
            # Returns None to defer to the next allocator
            calls.append('first')

        @register_pk_allocator
        def second(model, count, using):
            calls.append('second')
            return [100 + i for i in range(count)]

        @register_pk_allocator
        def third(model, count, using):
            calls.append('third')
            return [200 + i for i in range(count)]

        self.assertEqual(allocate_pks(Site, 3), [100, 101, 102])
        self.assertEqual(calls, ['first', 'second'])

    def test_allocate_pks_using(self):
        allocator, calls = get_sequential_allocator(Site)
        register_pk_allocator(allocator)

        # Without an explicit database, the router's choice for writing the model is assumed
        with patch.object(router, 'db_for_write', return_value='elsewhere'):
            allocate_pks(Site)
            allocate_pks(Site, using='other')
        self.assertEqual(calls, [(Site, 1, 'elsewhere'), (Site, 1, 'other')])

    def test_allocate_pks_iterable(self):
        register_pk_allocator(lambda model, count, using: (100 + i for i in range(count)))

        self.assertEqual(allocate_pks(Site, 2), [100, 101])

    def test_allocate_pks_wrong_count(self):
        register_pk_allocator(lambda model, count, using: [1])

        with self.assertRaises(ValueError):
            allocate_pks(Site, 2)

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
        self.assertEqual(calls.count((Manufacturer, 1, DEFAULT_DB_ALIAS)), 1)
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
        register_pk_allocator(lambda model, count, using: [source.pk] if model is Manufacturer else None)
        clone = Manufacturer.objects.get(pk=source.pk)
        clone.pk = None
        clone.name, clone.slug = 'Manufacturer 2', 'manufacturer-2'

        with self.assertRaises(IntegrityError), transaction.atomic():
            clone.save()
        source.refresh_from_db()
        self.assertEqual(source.name, 'Manufacturer 1')

    def test_save_retry_after_colliding_allocator(self):
        # A failed INSERT withdraws the allocated primary key, so that saving the object again consults the allocators
        # again, rather than updating the existing row which has the allocated primary key
        source = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        pks = iter([source.pk, 1_000_000])
        register_pk_allocator(lambda model, count, using: [next(pks)] if model is Manufacturer else None)
        manufacturer = Manufacturer(name='Manufacturer 2', slug='manufacturer-2')

        with self.assertRaises(IntegrityError), transaction.atomic():
            manufacturer.save()
        self.assertIsNone(manufacturer.pk)

        with CaptureQueriesContext(connection) as ctx:
            manufacturer.save()

        self.assertEqual(manufacturer.pk, 1_000_000)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(len(updates), 0)
        source.refresh_from_db()
        self.assertEqual(source.name, 'Manufacturer 1')

    def test_save_with_declining_allocator(self):
        # The allocator supplies primary keys only for Site, so the database assigns one for the Manufacturer
        allocator, calls = get_sequential_allocator(Site)
        register_pk_allocator(allocator)
        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        # The allocator is consulted only once
        self.assertEqual(calls.count((Manufacturer, 1, DEFAULT_DB_ALIAS)), 1)
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

        # All three primary keys are requested in a single call, and all objects are inserted in one statement
        pks = [1_000_000, 1_000_001, 1_000_002]
        self.assertEqual([m.pk for m in manufacturers], pks)
        self.assertEqual(calls, [(Manufacturer, 3, DEFAULT_DB_ALIAS)])
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)
        self.assertEqual(sorted(Manufacturer.objects.values_list('pk', flat=True)), pks)

    def test_bulk_create_with_some_preset_pks(self):
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)
        manufacturers = [
            Manufacturer(pk=500, name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        ]

        with CaptureQueriesContext(connection) as ctx:
            Manufacturer.objects.bulk_create(manufacturers)

        # Primary keys are requested only for the objects without one, and every object is inserted together
        self.assertEqual(calls, [(Manufacturer, 2, DEFAULT_DB_ALIAS)])
        self.assertEqual([m.pk for m in manufacturers], [500, 1_000_000, 1_000_001])
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 1)

    def test_bulk_create_with_declining_allocator(self):
        allocator, calls = get_sequential_allocator(Site)
        register_pk_allocator(allocator)
        manufacturers = [
            Manufacturer(name=f'Manufacturer {i}', slug=f'manufacturer-{i}') for i in range(1, 4)
        ]

        Manufacturer.objects.bulk_create(manufacturers)

        # The allocator is consulted once for all three objects, and the database assigns their primary keys
        self.assertEqual(calls, [(Manufacturer, 3, DEFAULT_DB_ALIAS)])
        self.assertTrue(all(m.pk is not None and m.pk < 1_000_000 for m in manufacturers))

    def test_bulk_create_using(self):
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)
        manufacturers = [
            Manufacturer(name=f'Manufacturer {i}', slug=f'manufacturer-{i}') for i in range(1, 3)
        ]

        # The allocator is told the database the queryset writes to, not the router's choice
        with patch.object(router, 'db_for_write', return_value='elsewhere'):
            Manufacturer.objects.using(DEFAULT_DB_ALIAS).bulk_create(manufacturers)

        self.assertEqual(calls, [(Manufacturer, 2, DEFAULT_DB_ALIAS)])

    def test_bulk_create_with_colliding_allocator(self):
        # A failed INSERT withdraws the allocated primary keys from every object
        source = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        register_pk_allocator(lambda model, count, using: [source.pk, 1_000_000] if model is Manufacturer else None)
        manufacturers = [
            Manufacturer(name=f'Manufacturer {i}', slug=f'manufacturer-{i}') for i in range(2, 4)
        ]

        with self.assertRaises(IntegrityError), transaction.atomic():
            Manufacturer.objects.bulk_create(manufacturers)

        self.assertEqual([m.pk for m in manufacturers], [None, None])
        self.assertTrue(all(m._state.adding for m in manufacturers))

    def test_bulk_create_ignoring_conflicts(self):
        # When conflicting rows are ignored, bulk_create() can't tell which objects were inserted, so allocated primary
        # keys are withdrawn from every object. Otherwise, a skipped object would refer to a row it doesn't represent.
        source = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        register_pk_allocator(lambda model, count, using: [source.pk, 1_000_000] if model is Manufacturer else None)
        manufacturers = [
            Manufacturer(name=f'Manufacturer {i}', slug=f'manufacturer-{i}') for i in range(2, 4)
        ]

        Manufacturer.objects.bulk_create(manufacturers, ignore_conflicts=True)

        # The first object conflicts with the existing row and is skipped, while the second is inserted
        self.assertEqual([m.pk for m in manufacturers], [None, None])
        self.assertTrue(all(m._state.adding for m in manufacturers))
        self.assertEqual(
            sorted(Manufacturer.objects.values_list('pk', 'name')),
            [(source.pk, 'Manufacturer 1'), (1_000_000, 'Manufacturer 3')]
        )

    def test_bulk_create_with_unsaved_related_object(self):
        # Allocators aren't consulted until the objects have been validated, so a failed validation consumes no keys
        allocator, calls = get_sequential_allocator(Site)
        register_pk_allocator(allocator)
        site = Site(name='Site 1', slug='site-1', tenant=Tenant(name='Tenant 1', slug='tenant-1'))

        with self.assertRaisesRegex(ValueError, 'unsaved related object'):
            Site.objects.bulk_create([site])

        self.assertEqual(calls, [])
        self.assertIsNone(site.pk)

    def test_many_to_many_with_allocator(self):
        # Auto-created many-to-many through models are also supported
        through_model = Tag.object_types.through
        allocator, calls = get_sequential_allocator(through_model)
        register_pk_allocator(allocator)
        tag = Tag.objects.create(name='Tag 1', slug='tag-1')
        tag.object_types.add(ContentType.objects.get_for_model(Site))

        self.assertIn((through_model, 1, DEFAULT_DB_ALIAS), calls)
        self.assertEqual(list(through_model.objects.filter(tag=tag).values_list('pk', flat=True)), [1_000_000])

    def test_third_party_model_with_allocator(self):
        # Models of other Django apps, which use their own default_auto_field, are also supported
        allocator, calls = get_sequential_allocator(ContentType)
        register_pk_allocator(allocator)
        content_type = ContentType.objects.create(app_label='test', model='test')

        self.assertEqual(content_type.pk, 1_000_000)

    def test_multi_table_inheritance_with_allocator(self):
        # The allocator receives the parent model, which owns the primary key column, and the primary key it supplies
        # is shared by the parent and child rows
        allocator, calls = get_sequential_allocator(ContentType)
        register_pk_allocator(allocator)
        object_type = ObjectType(app_label='test', model='test')
        object_type.save()

        self.assertEqual(
            [call for call in calls if call[0] in (ContentType, ObjectType)],
            [(ContentType, 1, DEFAULT_DB_ALIAS)]
        )
        self.assertEqual(object_type.pk, 1_000_000)
        self.assertTrue(ContentType.objects.filter(pk=1_000_000, app_label='test', model='test').exists())
        self.assertTrue(ObjectType.objects.filter(pk=1_000_000).exists())

    def test_proxy_model_with_allocator(self):
        # The allocator receives the concrete model of a proxy model
        user = User.objects.create_user(username='user1')
        allocator, calls = get_sequential_allocator(Token)
        register_pk_allocator(allocator)
        token = UserToken.objects.create(user=user)

        self.assertEqual(
            [call for call in calls if call[0] in (Token, UserToken)],
            [(Token, 1, DEFAULT_DB_ALIAS)]
        )
        self.assertEqual(token.pk, 1_000_000)

    def test_historical_model_with_allocator(self):
        # The historical models used by data migrations are also supported, via both save() and bulk_create()
        HistoricalManufacturer = ProjectState.from_apps(apps).apps.get_model('dcim', 'Manufacturer')
        self.assertIsNot(HistoricalManufacturer, Manufacturer)
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)

        manufacturer = HistoricalManufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        manufacturers = HistoricalManufacturer.objects.bulk_create([
            HistoricalManufacturer(name='Manufacturer 2', slug='manufacturer-2'),
        ])

        self.assertEqual(manufacturer.pk, 1_000_000)
        self.assertEqual(manufacturers[0].pk, 1_000_001)
        self.assertEqual(sorted(Manufacturer.objects.values_list('pk', flat=True)), [1_000_000, 1_000_001])

    def test_save_new_instance_with_existing_pk(self):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)

        # Allocators aren't consulted for an instance with a preset primary key, which updates the existing row
        with CaptureQueriesContext(connection) as ctx:
            Manufacturer(pk=manufacturer.pk, name='Manufacturer 2', slug='manufacturer-2').save()

        self.assertNotIn((Manufacturer, 1, DEFAULT_DB_ALIAS), calls)
        inserts, updates = self.get_table_writes(ctx.captured_queries, Manufacturer)
        self.assertEqual(len(inserts), 0)
        self.assertEqual(len(updates), 1)
        manufacturer.refresh_from_db()
        self.assertEqual(manufacturer.name, 'Manufacturer 2')

    def test_forced_update_without_pk(self):
        allocator, calls = get_sequential_allocator(Manufacturer)
        register_pk_allocator(allocator)

        # Allocators aren't consulted for a forced update, which requires a primary key
        for kwargs in ({'force_update': True}, {'update_fields': ['name']}):
            with self.subTest(**kwargs), self.assertRaises(ValueError), transaction.atomic():
                Manufacturer(name='Manufacturer 1', slug='manufacturer-1').save(**kwargs)
        self.assertNotIn((Manufacturer, 1, DEFAULT_DB_ALIAS), calls)

    def test_replaced_method_signatures(self):
        # Each replacement must accept the same arguments as the stock Django method it replaces. If this fails after
        # upgrading Django, update the replacement in utilities.pk_allocation to match the method's new signature.
        def get_params(func):
            # Omit the first parameter, which the replacements name differently (e.g. "instance" rather than "self")
            return [(p.name, p.kind, p.default) for p in list(inspect.signature(func).parameters.values())[1:]]

        replacements = (
            (pk_allocation._save_table, pk_allocation.save_table_with_pk_allocation),
            (pk_allocation._prepare_for_bulk_create, pk_allocation.prepare_for_bulk_create_with_pk_allocation),
            (pk_allocation._bulk_create, pk_allocation.bulk_create_with_pk_allocation),
        )
        for method, replacement in replacements:
            with self.subTest(method=method.__qualname__):
                self.assertEqual(get_params(replacement), get_params(method))
