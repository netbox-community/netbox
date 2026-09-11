from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase

from dcim.models import Region
from tenancy.models import TenantGroup
from utilities.management.commands.calculate_cached_counts import Command


class CalculateCachedCountsTestCase(TestCase):
    def test_updates_registered_counter_fields(self):
        class ParentModel:
            pass

        out = StringIO()

        with (
            patch.object(
                Command,
                'collect_models',
                return_value={ParentModel: {'interface_count': 'interfaces'}},
            ),
            patch('utilities.management.commands.calculate_cached_counts.update_counts') as update_counts,
        ):
            call_command('calculate_cached_counts', stdout=out)

        update_counts.assert_called_once_with(ParentModel, 'interface_count', 'interfaces')
        self.assertIn('Finished.', out.getvalue())

    def test_collect_models_returns_counter_field_mappings_by_parent_model(self):
        class ParentModel:
            pass

        class ChildModel:
            pass

        fk_field = MagicMock()
        fk_field.related_model = ParentModel
        fk_field.related_query_name.return_value = 'children'
        ChildModel._meta = MagicMock()
        ChildModel._meta.get_field.return_value = fk_field

        with patch(
            'utilities.management.commands.calculate_cached_counts.registry',
            {'counter_fields': {ChildModel: {'parent': 'child_count'}}},
        ):
            models = Command.collect_models()

        ChildModel._meta.get_field.assert_called_once_with('parent')
        fk_field.related_query_name.assert_called_once_with()
        self.assertEqual(dict(models), {ParentModel: {'child_count': 'children'}})


class RebuildLtreePathsTestCase(TestCase):
    """
    The command must repair path/sort_path values the triggers did not maintain.

    Corruption is injected by writing the path columns directly: the triggers fire on
    parent_id and the name column, so a raw UPDATE of path bypasses them, reproducing a
    database whose cascade trigger went missing across a restore.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = Region.objects.create(name='Alpha', slug='alpha-rlp')
        cls.child = Region.objects.create(name='Beta', slug='beta-rlp', parent=cls.parent)

    @staticmethod
    def _set_parent_bypassing_triggers(pk, parent_pk):
        """
        Repoint a row's parent_id without firing the ltree triggers.

        The BEFORE trigger recomputes `path` and rejects a move which its own cycle guard
        can see, so the ORM cannot produce these states directly. Suppressing the triggers
        for the statement reproduces what #23130 leaves behind: a database whose parent_id
        graph has drifted from the paths stored alongside it.

        `ALTER TABLE ... DISABLE TRIGGER` needs only ownership of the table, which the
        role running the tests has, where `session_replication_role` needs SUPERUSER or an
        explicit grant. It does refuse while the transaction holds pending trigger events,
        which the rows created in setUpTestData leave behind, so flush those first: the
        events are the deferred foreign key checks, and firing them early is harmless.
        `netbox/tests/test_search.py` does the same to reach its own schema states.
        """
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute('ALTER TABLE dcim_region DISABLE TRIGGER USER')
            try:
                cursor.execute(
                    'UPDATE dcim_region SET parent_id = %s WHERE id = %s', [parent_pk, pk]
                )
            finally:
                cursor.execute('ALTER TABLE dcim_region ENABLE TRIGGER USER')

    def test_rebuilds_stale_path_and_sort_path(self):
        Region.objects.filter(pk=self.child.pk).update(
            path='9999999999999999999', sort_path='stale',
        )

        call_command('rebuild_ltree_paths', 'dcim.region', stdout=StringIO())

        self.child.refresh_from_db()
        self.assertEqual(
            self.child.path,
            f'{str(self.parent.pk).zfill(19)}.{str(self.child.pk).zfill(19)}',
        )
        self.assertEqual(self.child.sort_path, f'Alpha{chr(9)}Beta')

    def test_rebuilds_a_stale_sort_path_alone(self):
        # What a rename leaves behind: the renamed row's own sort_path is rewritten by the
        # BEFORE trigger, its descendants' are not, and no path changes.
        Region.objects.filter(pk=self.child.pk).update(sort_path='stale')

        call_command('rebuild_ltree_paths', 'dcim.region', stdout=StringIO())

        self.child.refresh_from_db()
        self.assertEqual(self.child.sort_path, f'Alpha{chr(9)}Beta')

    def test_rebuilds_every_core_hierarchical_model_by_default(self):
        out = StringIO()

        call_command('rebuild_ltree_paths', stdout=out)

        output = out.getvalue()
        for label in ('dcim.region', 'dcim.inventoryitem', 'dcim.inventoryitemtemplate',
                      'tenancy.tenantgroup', 'wireless.wirelesslangroup'):
            self.assertIn(label, output)
        self.assertIn('Finished.', output)

    def test_check_reports_a_model_needing_a_rebuild(self):
        Region.objects.filter(pk=self.child.pk).update(sort_path='stale')
        out = StringIO()

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=out)

        output = out.getvalue()
        self.assertIn('sort_path', output)
        self.assertIn('Needs rebuilding: dcim.region', output)

    def test_check_reports_a_healthy_model_as_ok(self):
        out = StringIO()

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=out)

        self.assertIn('dcim.region: OK', out.getvalue())
        self.assertIn('Nothing to rebuild.', out.getvalue())

    def test_check_modifies_nothing(self):
        Region.objects.filter(pk=self.child.pk).update(sort_path='stale')

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=StringIO())

        self.child.refresh_from_db()
        self.assertEqual(self.child.sort_path, 'stale')

    def test_check_reports_a_stale_path_where_sort_path_is_correct(self):
        # A reparent leaves path wrong on its own, so the two counts are separate.
        Region.objects.filter(pk=self.child.pk).update(path='9999999999999999999')
        out = StringIO()

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=out)

        self.assertIn('1 path', out.getvalue())

    def test_check_reports_a_stale_root(self):
        """
        A root has no parent to be compared against, so a check which only joins children
        to parents never examines it and reports a corrupt root as clean.
        """
        root = Region.objects.create(name='Solo', slug='solo-rlp')
        Region.objects.filter(pk=root.pk).update(
            path='9999999999999999999', sort_path='WRONG',
        )
        out = StringIO()

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=out)

        output = out.getvalue()
        self.assertIn('1 path, 1 sort_path', output)
        self.assertNotIn('dcim.region: OK', output)

    def test_rebuilds_a_stale_root(self):
        root = Region.objects.create(name='Solo', slug='solo-rlp')
        Region.objects.filter(pk=root.pk).update(
            path='9999999999999999999', sort_path='WRONG',
        )

        call_command('rebuild_ltree_paths', 'dcim.region', stdout=StringIO())

        root.refresh_from_db()
        self.assertEqual(root.path, str(root.pk).zfill(19))
        self.assertEqual(root.sort_path, 'Solo')

    def test_check_reports_a_stale_root_whose_child_agrees_with_it(self):
        """
        The child of a corrupt root can be consistent with that root, so a parent-only
        comparison sees nothing wrong anywhere in the subtree.
        """
        root = Region.objects.create(name='Solo', slug='solo-rlp')
        child = Region.objects.create(name='Sub', slug='sub-rlp', parent=root)
        Region.objects.filter(pk=root.pk).update(path='9999999999999999999')
        Region.objects.filter(pk=child.pk).update(
            path=f'9999999999999999999.{str(child.pk).zfill(19)}',
        )
        out = StringIO()

        call_command('rebuild_ltree_paths', 'dcim.region', '--check', stdout=out)

        self.assertIn('1 path', out.getvalue())

    def test_rejects_a_model_which_is_not_hierarchical(self):
        with self.assertRaises(CommandError):
            call_command('rebuild_ltree_paths', 'dcim.site')

    def test_refuses_a_table_containing_a_cycle(self):
        """
        A rebuild walks down from the roots, so rows in a cycle are never reached and keep
        whatever paths they have. Refuse rather than report success, and name the rows to
        start from: "correct the parent relationships" is not actionable without them.
        """
        self._set_parent_bypassing_triggers(self.parent.pk, self.child.pk)

        with self.assertRaises(CommandError) as ctx:
            call_command('rebuild_ltree_paths', 'dcim.region')

        message = str(ctx.exception)
        self.assertIn(str(self.parent.pk), message)
        self.assertIn(str(self.child.pk), message)

    def test_refuses_a_table_containing_a_self_parented_row(self):
        self._set_parent_bypassing_triggers(self.child.pk, self.child.pk)

        with self.assertRaises(CommandError):
            call_command('rebuild_ltree_paths', 'dcim.region')

    def test_refuses_a_table_whose_parent_id_references_a_missing_row(self):
        """
        Not a cycle, but equally unreachable, so a cycle-specific check would miss it.

        Disabling the triggers leaves the foreign key enforced, so drop it for this row as
        well. Such a row does occur in practice: `pg_restore --disable-triggers` and
        logical replication both load rows without enforcing it.
        """
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute(
                "SELECT conname FROM pg_constraint "
                "WHERE conrelid = 'dcim_region'::regclass AND contype = 'f' "
                "AND conkey = ARRAY[(SELECT attnum FROM pg_attribute "
                "WHERE attrelid = 'dcim_region'::regclass AND attname = 'parent_id')]"
            )
            constraint = cursor.fetchone()[0]
            cursor.execute(f'ALTER TABLE dcim_region DROP CONSTRAINT "{constraint}"')
        self._set_parent_bypassing_triggers(self.child.pk, self.parent.pk + 10000)

        with self.assertRaises(CommandError):
            call_command('rebuild_ltree_paths', 'dcim.region')

    def test_refusing_a_table_leaves_that_table_untouched(self):
        """
        A refusal rolls back the transaction it was raised in, so the refused table keeps
        the paths it had. Tables already rebuilt stay rebuilt: each is its own transaction,
        which is what keeps one table's row locks from being held while the rest run.
        """
        group = TenantGroup.objects.create(name='Unrelated', slug='unrelated-rlp')
        TenantGroup.objects.filter(pk=group.pk).update(sort_path='stale')
        Region.objects.filter(pk=self.child.pk).update(sort_path='also-stale')
        # dcim.region is named second and is the table which fails the check.
        self._set_parent_bypassing_triggers(self.parent.pk, self.child.pk)

        with self.assertRaises(CommandError):
            call_command('rebuild_ltree_paths', 'tenancy.tenantgroup', 'dcim.region')

        # The refused table is untouched: no partial rebuild, nothing to undo by hand.
        self.child.refresh_from_db()
        self.assertEqual(self.child.sort_path, 'also-stale')

        # The table which passed its own check was rebuilt and committed.
        group.refresh_from_db()
        self.assertEqual(group.sort_path, 'Unrelated')
