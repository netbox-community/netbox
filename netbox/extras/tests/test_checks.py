from django.test import TestCase

from core.events import OBJECT_CREATED
from core.models import ObjectType
from dcim.models import Site
from extras.checks import check_event_rule_actions
from extras.models import EventRule


class CheckEventRuleActionsTestCase(TestCase):
    """
    Tests for the extras.W001 system check (#22770): warn about EventRules whose action_type has
    no currently-registered provider.
    """

    def test_no_warnings_when_all_actions_registered(self):
        rule = EventRule.objects.create(name='Healthy Check Rule', event_types=[OBJECT_CREATED], action_type='webhook')
        rule.object_types.set([ObjectType.objects.get_for_model(Site)])

        self.assertEqual(check_event_rule_actions(app_configs=None), [])

    def test_warning_for_unregistered_action_type(self):
        rule = EventRule.objects.create(
            name='Unavailable Check Rule',
            event_types=[OBJECT_CREATED],
            action_type='someplugin.not_installed_check_test',
        )
        rule.object_types.set([ObjectType.objects.get_for_model(Site)])

        warnings = check_event_rule_actions(app_configs=None)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].id, 'extras.W001')
        self.assertIn('someplugin.not_installed_check_test', warnings[0].msg)
        self.assertIn('Unavailable Check Rule', warnings[0].msg)

    def test_one_aggregated_warning_per_missing_action_type(self):
        """Multiple rules sharing the same unregistered action_type produce one aggregated warning."""
        site_type = ObjectType.objects.get_for_model(Site)
        for i in range(3):
            rule = EventRule.objects.create(
                name=f'Shared Unavailable Rule {i}',
                event_types=[OBJECT_CREATED],
                action_type='someplugin.shared_unregistered',
            )
            rule.object_types.set([site_type])

        warnings = check_event_rule_actions(app_configs=None)
        self.assertEqual(len(warnings), 1)
        self.assertIn('3 event rule(s)', warnings[0].msg)
        for i in range(3):
            self.assertIn(f'Shared Unavailable Rule {i}', warnings[0].msg)

    def test_truncates_long_name_list(self):
        site_type = ObjectType.objects.get_for_model(Site)
        for i in range(12):
            rule = EventRule.objects.create(
                name=f'Truncation Rule {i}',
                event_types=[OBJECT_CREATED],
                action_type='someplugin.many_unregistered',
            )
            rule.object_types.set([site_type])

        warnings = check_event_rule_actions(app_configs=None)
        self.assertEqual(len(warnings), 1)
        self.assertIn('12 event rule(s)', warnings[0].msg)
        self.assertIn('and 2 more', warnings[0].msg)
