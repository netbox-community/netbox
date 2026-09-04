from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from dcim.models import Region
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

    def test_rejects_a_model_which_is_not_hierarchical(self):
        with self.assertRaises(CommandError):
            call_command('rebuild_ltree_paths', 'dcim.site')
