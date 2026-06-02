from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase

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
