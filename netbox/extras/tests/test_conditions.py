from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from core.events import *
from dcim.choices import SiteStatusChoices
from dcim.models import Site
from extras.conditions import Condition, ConditionSet, InvalidCondition
from extras.events import serialize_for_event
from extras.forms import EventRuleForm
from extras.models import EventRule, Webhook


class ConditionTestCase(TestCase):

    def test_undefined_attr(self):
        c = Condition('x', 1, 'eq')
        self.assertTrue(c.eval({'x': 1}))
        with self.assertRaises(InvalidCondition):
            c.eval({})

    #
    # Validation tests
    #

    def test_invalid_op(self):
        with self.assertRaises(ValueError):
            # 'blah' is not a valid operator
            Condition('x', 1, 'blah')

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            # dict type is unsupported
            Condition('x', 1, dict())

    def test_invalid_op_types(self):
        with self.assertRaises(ValueError):
            # 'gt' supports only numeric values
            Condition('x', 'foo', 'gt')
        with self.assertRaises(ValueError):
            # 'in' supports only iterable values
            Condition('x', 123, 'in')

    #
    # Nested attrs tests
    #

    def test_nested(self):
        c = Condition('x.y.z', 1)
        self.assertTrue(c.eval({'x': {'y': {'z': 1}}}))
        self.assertFalse(c.eval({'x': {'y': {'z': 2}}}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': {'y': None}})
        with self.assertRaises(InvalidCondition):
            c.eval({'x': {'y': {'a': 1}}})

    #
    # Operator tests
    #

    def test_default_operator(self):
        c = Condition('x', 1)
        self.assertEqual(c.eval_func, c.eval_eq)

    def test_eq(self):
        c = Condition('x', 1, 'eq')
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 2}))

    def test_eq_negated(self):
        c = Condition('x', 1, 'eq', negate=True)
        self.assertFalse(c.eval({'x': 1}))
        self.assertTrue(c.eval({'x': 2}))

    def test_gt(self):
        c = Condition('x', 1, 'gt')
        self.assertTrue(c.eval({'x': 2}))
        self.assertFalse(c.eval({'x': 1}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': 'foo'})  # Invalid type

    def test_gte(self):
        c = Condition('x', 1, 'gte')
        self.assertTrue(c.eval({'x': 2}))
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 0}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': 'foo'})  # Invalid type

    def test_lt(self):
        c = Condition('x', 2, 'lt')
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 2}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': 'foo'})  # Invalid type

    def test_lte(self):
        c = Condition('x', 2, 'lte')
        self.assertTrue(c.eval({'x': 1}))
        self.assertTrue(c.eval({'x': 2}))
        self.assertFalse(c.eval({'x': 3}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': 'foo'})  # Invalid type

    def test_in(self):
        c = Condition('x', [1, 2, 3], 'in')
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 9}))

    def test_in_negated(self):
        c = Condition('x', [1, 2, 3], 'in', negate=True)
        self.assertFalse(c.eval({'x': 1}))
        self.assertTrue(c.eval({'x': 9}))

    def test_contains(self):
        c = Condition('x', 1, 'contains')
        self.assertTrue(c.eval({'x': [1, 2, 3]}))
        self.assertFalse(c.eval({'x': [2, 3, 4]}))
        with self.assertRaises(InvalidCondition):
            c.eval({'x': 123})  # Invalid type

    def test_contains_negated(self):
        c = Condition('x', 1, 'contains', negate=True)
        self.assertFalse(c.eval({'x': [1, 2, 3]}))
        self.assertTrue(c.eval({'x': [2, 3, 4]}))

    def test_regex(self):
        c = Condition('x', '[a-z]+', 'regex')
        self.assertTrue(c.eval({'x': 'abc'}))
        self.assertFalse(c.eval({'x': '123'}))

    def test_regex_negated(self):
        c = Condition('x', '[a-z]+', 'regex', negate=True)
        self.assertFalse(c.eval({'x': 'abc'}))
        self.assertTrue(c.eval({'x': '123'}))


class ConditionSetTestCase(TestCase):

    def test_empty(self):
        with self.assertRaises(ValueError):
            ConditionSet({})

    def test_invalid_logic(self):
        with self.assertRaises(ValueError):
            ConditionSet({'foo': []})

    def test_null_value(self):
        cs = ConditionSet({
            'and': [
                {'attr': 'a', 'value': None, 'op': 'eq', 'negate': True},
            ]
        })
        self.assertFalse(cs.eval({'a': None}))
        self.assertTrue(cs.eval({'a': "string"}))
        self.assertTrue(cs.eval({'a': {"key": "value"}}))

    def test_and_single_depth(self):
        cs = ConditionSet({
            'and': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'attr': 'b', 'value': 1, 'op': 'eq', 'negate': True},
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 2}))
        self.assertFalse(cs.eval({'a': 1, 'b': 1}))

    def test_or_single_depth(self):
        cs = ConditionSet({
            'or': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'attr': 'b', 'value': 1, 'op': 'eq'},
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 2}))
        self.assertTrue(cs.eval({'a': 2, 'b': 1}))
        self.assertFalse(cs.eval({'a': 2, 'b': 2}))

    def test_and_multi_depth(self):
        cs = ConditionSet({
            'and': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'and': [
                    {'attr': 'b', 'value': 2, 'op': 'eq'},
                    {'attr': 'c', 'value': 3, 'op': 'eq'},
                ]}
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 2, 'c': 3}))
        self.assertFalse(cs.eval({'a': 9, 'b': 2, 'c': 3}))
        self.assertFalse(cs.eval({'a': 1, 'b': 9, 'c': 3}))
        self.assertFalse(cs.eval({'a': 1, 'b': 2, 'c': 9}))

    def test_or_multi_depth(self):
        cs = ConditionSet({
            'or': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'or': [
                    {'attr': 'b', 'value': 2, 'op': 'eq'},
                    {'attr': 'c', 'value': 3, 'op': 'eq'},
                ]}
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 9, 'c': 9}))
        self.assertTrue(cs.eval({'a': 9, 'b': 2, 'c': 9}))
        self.assertTrue(cs.eval({'a': 9, 'b': 9, 'c': 3}))
        self.assertFalse(cs.eval({'a': 9, 'b': 9, 'c': 9}))

    def test_mixed_and(self):
        cs = ConditionSet({
            'and': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'or': [
                    {'attr': 'b', 'value': 2, 'op': 'eq'},
                    {'attr': 'c', 'value': 3, 'op': 'eq'},
                ]}
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 2, 'c': 9}))
        self.assertTrue(cs.eval({'a': 1, 'b': 9, 'c': 3}))
        self.assertFalse(cs.eval({'a': 1, 'b': 9, 'c': 9}))
        self.assertFalse(cs.eval({'a': 9, 'b': 2, 'c': 3}))

    def test_mixed_or(self):
        cs = ConditionSet({
            'or': [
                {'attr': 'a', 'value': 1, 'op': 'eq'},
                {'and': [
                    {'attr': 'b', 'value': 2, 'op': 'eq'},
                    {'attr': 'c', 'value': 3, 'op': 'eq'},
                ]}
            ]
        })
        self.assertTrue(cs.eval({'a': 1, 'b': 9, 'c': 9}))
        self.assertTrue(cs.eval({'a': 9, 'b': 2, 'c': 3}))
        self.assertTrue(cs.eval({'a': 1, 'b': 2, 'c': 9}))
        self.assertFalse(cs.eval({'a': 9, 'b': 2, 'c': 9}))
        self.assertFalse(cs.eval({'a': 9, 'b': 9, 'c': 3}))

    def test_event_rule_conditions_without_logic_operator(self):
        """
        Test evaluation of EventRule conditions without logic operator.
        """
        event_rule = EventRule(
            name='Event Rule 1',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                'attr': 'status.value',
                'value': 'active',
            }
        )

        # Create a Site to evaluate - Status = active
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE)
        data = serialize_for_event(site)

        # Evaluate the conditions (status='active')
        self.assertTrue(event_rule.eval_conditions(data))

    def test_event_rule_conditions_with_logical_operation(self):
        """
        Test evaluation of EventRule conditions without logic operator, but with logical operation (in).
        """
        event_rule = EventRule(
            name='Event Rule 1',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                "attr": "status.value",
                "value": ["planned", "staging"],
                "op": "in",
            }
        )

        # Create a Site to evaluate - Status = active
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE)
        data = serialize_for_event(site)

        # Evaluate the conditions (status in ['planned, 'staging'])
        self.assertFalse(event_rule.eval_conditions(data))

    def test_event_rule_conditions_with_logical_operation_and_negate(self):
        """
        Test evaluation of EventRule with logical operation (in) and negate.
        """
        event_rule = EventRule(
            name='Event Rule 1',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                "attr": "status.value",
                "value": ["planned", "staging"],
                "op": "in",
                "negate": True,
            }
        )

        # Create a Site to evaluate - Status = active
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE)
        data = serialize_for_event(site)

        # Evaluate the conditions (status NOT in ['planned, 'staging'])
        self.assertTrue(event_rule.eval_conditions(data))

    def test_event_rule_conditions_with_incorrect_key_must_return_false(self):
        """
        Test Event Rule with incorrect condition (key "foo" is wrong). Must return false.
        """

        ct = ContentType.objects.get_by_natural_key('extras', 'webhook')
        site_ct = ContentType.objects.get_for_model(Site)
        webhook = Webhook.objects.create(name='Webhook 100', payload_url='http://example.com/?1', http_method='POST')
        form = EventRuleForm({
            "name": "Event Rule 1",
            "event_types": [OBJECT_CREATED, OBJECT_UPDATED],
            "action_object_type": ct.pk,
            "action_type": "webhook",
            "action_choice": webhook.pk,
            "content_types": [site_ct.pk],
            "conditions": {
                "foo": "status.value",
                "value": "active"
            }
        })

        self.assertFalse(form.is_valid())


class SnapshotConditionTestCase(TestCase):
    """
    Tests for snapshot-aware conditions: the 'changed'/'unchanged' operators and
    direct snapshot attribute access via the snapshots.prechange.* / snapshots.postchange.*
    dot-path syntax.
    """

    def _make_condition_data(self, site, snapshots):
        """Return a condition evaluation context as produced by process_event_rules()."""
        return {**serialize_for_event(site), 'snapshots': snapshots}

    #
    # Validation
    #

    def test_changed_operator_rejects_value(self):
        with self.assertRaises(ValueError):
            Condition('status', value='active', op='changed')

    def test_unchanged_operator_rejects_value(self):
        with self.assertRaises(ValueError):
            Condition('status', value='active', op='unchanged')

    def test_snapshot_operator_rejects_snapshot_path_attr(self):
        """Snapshot operators must not use a snapshots.prechange.* path — that's only for standard operators."""
        with self.assertRaises(ValueError):
            Condition('snapshots.prechange.status', op='changed')
        with self.assertRaises(ValueError):
            Condition('snapshots.postchange.status', op='unchanged')

    def test_standard_operator_requires_value(self):
        with self.assertRaises(ValueError):
            Condition('status', op='eq')

    #
    # 'changed' operator
    #

    def test_changed_true_when_attr_differs(self):
        c = Condition('status', op='changed')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    def test_changed_false_when_attr_same(self):
        c = Condition('status', op='changed')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    def test_changed_true_when_prechange_missing_attr(self):
        # attr present in postchange but absent from prechange snapshot
        c = Condition('description', op='changed')
        snapshots = {
            'prechange': {},
            'postchange': {'description': 'hello'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    def test_changed_true_when_prechange_is_none(self):
        # OBJECT_CREATED events have no prechange snapshot
        c = Condition('status', op='changed')
        snapshots = {
            'prechange': None,
            'postchange': {'status': 'active'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    def test_changed_false_when_both_snapshots_missing_attr(self):
        # If neither snapshot has the attr, nothing changed
        c = Condition('nonexistent', op='changed')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    def test_changed_false_when_path_traverses_scalar(self):
        # Snapshot choice fields are raw strings, not nested dicts. A path like
        # 'status.value' hits a TypeError when traversing into the string; both
        # sides resolve to _MISSING and the operator returns False (no change).
        c = Condition('status.value', op='changed')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    def test_changed_negated(self):
        c = Condition('status', op='changed', negate=True)
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    def test_changed_raises_when_no_snapshots(self):
        c = Condition('status', op='changed')
        with self.assertRaises(InvalidCondition):
            c.eval({'status': {'value': 'active'}})

    #
    # 'unchanged' operator
    #

    def test_unchanged_true_when_attr_same(self):
        c = Condition('status', op='unchanged')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    def test_unchanged_false_when_attr_differs(self):
        c = Condition('status', op='unchanged')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    def test_unchanged_false_when_both_snapshots_missing_attr(self):
        # Fail-closed: a typo or non-existent attr resolves to _MISSING on both
        # sides; unchanged must return False rather than silently passing.
        c = Condition('statsu', op='unchanged')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))

    #
    # Direct snapshot path access (snapshots.prechange.* / snapshots.postchange.*)
    #

    def test_snapshot_path_access_prechange(self):
        c = Condition('snapshots.prechange.status', value='planned', op='eq')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    def test_snapshot_path_access_postchange(self):
        c = Condition('snapshots.postchange.status', value='active', op='eq')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertTrue(c.eval({'snapshots': snapshots}))

    #
    # EventRule.eval_conditions integration
    #

    def test_event_rule_changed_operator(self):
        """
        Verify the canonical use case: fire only when status changes to active.
        """
        event_rule = EventRule(
            name='Notify on activation',
            event_types=[OBJECT_UPDATED],
            conditions={
                'and': [
                    {'attr': 'status.value', 'value': 'active'},
                    {'attr': 'status', 'op': 'changed'},
                ]
            }
        )
        site = Site.objects.create(name='Site 2', slug='site-2', status=SiteStatusChoices.STATUS_ACTIVE)

        # status changed planned → active: should fire
        data_changed = self._make_condition_data(site, {
            'prechange': {'status': SiteStatusChoices.STATUS_PLANNED},
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        self.assertTrue(event_rule.eval_conditions(data_changed))

        # status already active, description updated: should NOT fire
        data_unchanged = self._make_condition_data(site, {
            'prechange': {'status': SiteStatusChoices.STATUS_ACTIVE},
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        self.assertFalse(event_rule.eval_conditions(data_unchanged))

    def test_event_rule_snapshot_path_with_existing_operator(self):
        """
        Conditions can reference prechange/postchange data using the standard
        snapshots.prechange.<attr> dot-path and existing operators.
        Note: snapshot values use model serializer format (raw strings, not nested
        dicts), so 'status' not 'status.value'.
        """
        event_rule = EventRule(
            name='Was planned',
            event_types=[OBJECT_UPDATED],
            conditions={
                'attr': 'snapshots.prechange.status',
                'value': SiteStatusChoices.STATUS_PLANNED,
            }
        )
        site = Site.objects.create(name='Site 3', slug='site-3', status=SiteStatusChoices.STATUS_ACTIVE)
        data = self._make_condition_data(site, {
            'prechange': {'status': SiteStatusChoices.STATUS_PLANNED},
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        self.assertTrue(event_rule.eval_conditions(data))
