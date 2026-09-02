from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from core.events import *
from dcim.choices import SiteStatusChoices
from dcim.models import Site
from extras.conditions import AbsentData, Condition, ConditionSet, InvalidCondition
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

    def test_nested_within_list(self):
        c = Condition('tags.slug', 'exempt', 'contains')
        self.assertTrue(c.eval({'tags': [{'slug': 'exempt'}, {'slug': 'other'}]}))
        self.assertFalse(c.eval({'tags': [{'slug': 'other'}]}))

    def test_nested_within_empty_list(self):
        """
        Descending into an empty list resolves to an empty list, not an absent attribute: an
        object with no tags is a legitimate non-match for the documented 'tags.slug contains'
        condition, not a malformed path. Raising here would abort the whole condition set,
        which for an 'or' set means a matching sibling condition never gets evaluated.
        """
        self.assertFalse(Condition('tags.slug', 'exempt', 'contains').eval({'tags': []}))
        self.assertTrue(Condition('tags.slug', 'exempt', 'contains', negate=True).eval({'tags': []}))
        self.assertTrue(Condition('tags.slug', [], 'eq').eval({'tags': []}))
        # The list is carried through the remainder of the path, just as a populated one is
        self.assertFalse(Condition('tags.parent.slug', 'exempt', 'contains').eval({'tags': []}))

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

    def test_untagged_object_does_not_veto_sibling_conditions(self):
        """
        The documented "status is active and primary_ip4 is defined, or the exempt tag is
        applied" example, evaluated for an object with no tags at all. The tag condition is a
        plain non-match: it must not abort the set before its sibling is reached, whichever
        order the two are listed in.
        """
        tag_rule = {'attr': 'tags.slug', 'value': 'exempt', 'op': 'contains'}
        status_rule = {'and': [
            {'attr': 'status.value', 'value': 'active'},
            {'attr': 'primary_ip4', 'value': None, 'negate': True},
        ]}
        data = {'status': {'value': 'active'}, 'primary_ip4': {'address': '192.0.2.1/32'}, 'tags': []}

        self.assertTrue(ConditionSet({'or': [tag_rule, status_rule]}).eval(data))
        self.assertTrue(ConditionSet({'or': [status_rule, tag_rule]}).eval(data))

        # Neither condition matches: still False rather than an error
        self.assertFalse(ConditionSet({'or': [tag_rule, status_rule]}).eval({
            'status': {'value': 'planned'}, 'primary_ip4': None, 'tags': []
        }))

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


class AbsentDataTestCase(TestCase):
    """
    Tests for conditions evaluated against an AbsentData payload, i.e. event data which is
    absent altogether (a job which recorded no data) rather than merely lacking the
    referenced attribute.
    """

    def _absent_data(self, **kwargs):
        """Return an absent payload as produced by process_event_rules()."""
        data = AbsentData()
        data['snapshots'] = kwargs.get('snapshots')
        return data

    def test_absent_data_is_a_non_match(self):
        """
        An absent payload carries nothing to match against, so a reference to any attribute of
        it is a non-match rather than a resolved null. Matching would enqueue the rule's action
        on an event which recorded no data at all.
        """
        data = self._absent_data()
        self.assertFalse(Condition('status', value=None).eval(data))
        self.assertFalse(Condition('status', value='completed').eval(data))
        # A nested path is equally unresolvable, and equally not an error
        self.assertFalse(Condition('output.result', value='x').eval(data))
        self.assertFalse(Condition('output.result', value=None).eval(data))

    def test_absent_data_is_a_non_match_for_every_operator(self):
        data = self._absent_data()
        for op, value in (
            ('eq', None), ('eq', 'foo'), ('in', ['foo']), ('contains', 'foo'), ('regex', '^foo'),
            ('gt', 1), ('gte', 1), ('lt', 1), ('lte', 1),
        ):
            with self.subTest(op=op, value=value):
                self.assertFalse(Condition('status', value=value, op=op).eval(data))

    def test_negate_cannot_turn_an_absent_payload_into_a_match(self):
        """
        Negation inverts the result of a comparison, and against an absent payload no
        comparison takes place. Inverting the non-match would make 'negate' a fail-open switch,
        firing the rule on an empty payload - for a misspelled attribute as readily as a real
        one, since neither resolves.
        """
        data = self._absent_data()
        for attr in ('status', 'stauts', 'output.result'):
            for value in (None, 'completed'):
                with self.subTest(attr=attr, value=value):
                    self.assertFalse(Condition(attr, value=value, negate=True).eval(data))
        self.assertFalse(Condition('status', value='foo', op='contains', negate=True).eval(data))

    def test_absent_data_does_not_veto_sibling_conditions(self):
        """
        An absent payload must not abort evaluation of the whole condition set: the other
        conditions, including a snapshot path drawn from the surrounding context, are still
        evaluated on their own merits.
        """
        data = self._absent_data(snapshots={'prechange': {'status': 'planned'}, 'postchange': None})
        ruleset = {'or': [
            {'attr': 'status', 'value': 'foo', 'op': 'regex'},
            {'attr': 'snapshots.prechange.status', 'value': 'planned'},
        ]}
        self.assertTrue(ConditionSet(ruleset).eval(data))
        self.assertFalse(ConditionSet({'and': list(ruleset['or'])}).eval(data))

    def test_present_data_missing_attr_still_fails_closed(self):
        """
        Only data which is absent altogether resolves to None; a payload which is present
        but lacks the attribute remains a fail-closed error, so that a typo is logged.
        """
        with self.assertRaises(InvalidCondition):
            Condition('status', value='completed').eval({'other': 1})

    def test_snapshot_path_against_absent_data(self):
        """
        The absent-payload marker must not short-circuit a snapshot path: the snapshots key
        is part of the evaluation context, not of the payload.
        """
        data = self._absent_data(snapshots={'prechange': {'status': 'planned'}, 'postchange': None})
        self.assertTrue(Condition('snapshots.prechange.status', value='planned').eval(data))
        self.assertTrue(Condition('snapshots.postchange.status', value=None).eval(data))


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

    def test_changed_raises_when_both_snapshots_missing_attr(self):
        # An attr absent from both snapshots leaves nothing to compare: report it rather than
        # returning a non-match, which negate would turn into a match
        c = Condition('nonexistent', op='changed')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_changed_raises_when_path_traverses_scalar(self):
        # Snapshot choice fields are raw strings, not nested dicts. A REST API-style path
        # like 'status.value' cannot be walked at all, which is a malformed condition
        # rather than an absent attribute: it must raise so that the mistake is logged,
        # not silently evaluate False on every event.
        c = Condition('status.value', op='changed')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_changed_raises_when_path_traverses_falsy_scalar(self):
        # Walkability is a property of the value's type, not its truthiness: an empty string
        # is exactly as unwalkable as a populated one, and must not be mistaken for an absent
        # attribute. (description and comments default to an empty string on most models, so
        # this is the common case rather than an edge case.)
        c = Condition('description.value', op='changed')
        snapshots = {
            'prechange': {'description': ''},
            'postchange': {'description': 'foo'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_unchanged_raises_when_path_traverses_scalar(self):
        c = Condition('status.value', op='unchanged')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_changed_raises_when_path_traverses_scalar_in_list(self):
        # Snapshot list fields hold raw values (e.g. tag names), so a path descending
        # into a list element is equally unwalkable.
        c = Condition('tags.name', op='changed')
        snapshots = {
            'prechange': {'tags': ['Alpha']},
            'postchange': {'tags': ['Alpha', 'Beta']},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_changed_raises_when_counterpart_snapshot_resolves_to_nothing(self):
        """
        Only a snapshot which actually yields a value excuses an unwalkable path in the
        other. A snapshot which merely resolves to nothing - an empty list, an absent key -
        is no evidence that the path is well-formed, so the malformed condition must still
        be reported rather than evaluating (and possibly firing) until the data fills in.
        """
        for snapshots in (
            # Tagging a previously untagged object: the likely first evaluation of the rule
            {'prechange': {'tags': []}, 'postchange': {'tags': ['Alpha']}},
            {'prechange': {'tags': ['Alpha']}, 'postchange': {'tags': []}},
        ):
            with self.subTest(snapshots=snapshots):
                with self.assertRaises(InvalidCondition):
                    Condition('tags.name', op='changed').eval({'snapshots': snapshots})

        with self.assertRaises(InvalidCondition):
            Condition('status.value', op='changed').eval({
                'snapshots': {'prechange': {}, 'postchange': {'status': 'active'}}
            })

    def test_changed_when_path_is_walkable_in_only_one_snapshot(self):
        """
        A path which resolves in one snapshot but not the other is not malformed: it
        describes a real difference between them, such as a JSON attribute whose value
        changed shape. The unwalkable side counts as missing and the comparison proceeds,
        rather than raising and reporting the attribute as unchanged.
        """
        snapshots = {
            'prechange': {'custom_fields': {'blob': 'legacy'}},
            'postchange': {'custom_fields': {'blob': {'key': 1}}},
        }
        reversed_snapshots = {'prechange': snapshots['postchange'], 'postchange': snapshots['prechange']}
        self.assertTrue(Condition('custom_fields.blob.key', op='changed').eval({'snapshots': snapshots}))
        self.assertTrue(Condition('custom_fields.blob.key', op='changed').eval({'snapshots': reversed_snapshots}))
        self.assertFalse(Condition('custom_fields.blob.key', op='unchanged').eval({'snapshots': snapshots}))

    def test_changed_raises_when_only_available_snapshot_traverses_scalar(self):
        """
        On create and delete events only one snapshot is available, so an unwalkable path is
        unwalkable everywhere it can be evaluated: still malformed, and still raises.
        """
        with self.assertRaises(InvalidCondition):
            Condition('status.value', op='changed').eval({
                'snapshots': {'prechange': None, 'postchange': {'status': 'active'}}
            })
        with self.assertRaises(InvalidCondition):
            Condition('status.value', op='changed').eval({
                'snapshots': {'prechange': {'status': 'active'}, 'postchange': None}
            })

    def test_changed_raises_when_no_snapshot_is_available(self):
        """
        With neither snapshot available there is nothing to compare, whether the path is
        malformed or not. Reporting the condition is the only way to fail closed: a boolean
        would be a verdict on data the event never carried, and negate would turn it into a
        match.
        """
        snapshots = {'prechange': None, 'postchange': None}
        for attr, op, negate in (
            ('status', 'changed', False),
            ('status', 'changed', True),
            ('status', 'unchanged', True),
            ('status.value', 'changed', False),
            ('status.value', 'unchanged', False),
        ):
            with self.subTest(attr=attr, op=op, negate=negate):
                with self.assertRaises(InvalidCondition):
                    Condition(attr, op=op, negate=negate).eval({'snapshots': snapshots})

    def test_changed_raises_when_attr_resolves_in_neither_snapshot(self):
        # An attribute absent from both snapshots is indistinguishable from a typo, so it
        # cannot be reported as an ordinary non-match
        c = Condition('nonexistent', op='changed')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active', 'description': 'x'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_changed_negated(self):
        c = Condition('status', op='changed', negate=True)
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        self.assertFalse(c.eval({'snapshots': snapshots}))
        self.assertTrue(c.eval({'snapshots': {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }}))

    def test_negate_cannot_turn_an_unresolved_attr_into_a_match(self):
        """
        A misspelled attribute must not fire the rule, whichever operator it is used with and
        whether or not the condition is negated. Returning False for the unresolved state
        would make 'negate' a fail-open switch.
        """
        snapshots = {'prechange': {'status': 'planned'}, 'postchange': {'status': 'active'}}
        for op in ('changed', 'unchanged'):
            for negate in (False, True):
                with self.subTest(op=op, negate=negate):
                    with self.assertRaises(InvalidCondition):
                        Condition('statsu', op=op, negate=negate).eval({'snapshots': snapshots})

    def test_changed_raises_when_no_snapshots(self):
        c = Condition('status', op='changed')
        with self.assertRaises(InvalidCondition):
            c.eval({'status': {'value': 'active'}})

    def test_changed_raises_when_snapshots_is_not_a_dict(self):
        """
        A snapshots value which is not a dict holds no snapshot to compare. It must be reported
        as an invalid condition, matching a direct snapshot path against the same data, rather
        than raising an uncaught AttributeError which would abort event processing entirely.
        """
        for snapshots in ('oops', ['prechange'], 42):
            with self.subTest(snapshots=snapshots):
                with self.assertRaises(InvalidCondition):
                    Condition('status', op='changed').eval({'snapshots': snapshots})
                with self.assertRaises(InvalidCondition):
                    Condition('snapshots.prechange.status', value='active').eval({'snapshots': snapshots})

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

    def test_unchanged_raises_when_both_snapshots_missing_attr(self):
        # Fail-closed: a typo or non-existent attr resolves on neither side, so 'unchanged'
        # must report it rather than silently passing (or, negated, matching)
        c = Condition('statsu', op='unchanged')
        snapshots = {
            'prechange': {'status': 'active'},
            'postchange': {'status': 'active'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

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

    def test_snapshot_path_rest_api_style_attr_raises_invalid_condition(self):
        """
        Snapshots store raw values (e.g. status="planned"), not REST API-style nested
        dicts (status={"value": "planned"}). A '.value' suffix on a snapshot path must
        fail closed with InvalidCondition rather than raising a raw TypeError.
        """
        c = Condition('snapshots.prechange.status.value', value='planned', op='eq')
        snapshots = {
            'prechange': {'status': 'planned'},
            'postchange': {'status': 'active'},
        }
        with self.assertRaises(InvalidCondition):
            c.eval({'snapshots': snapshots})

    def test_snapshot_path_resolves_to_none_when_prechange_absent(self):
        """
        On a create event there is no prechange snapshot. That is a property of the event,
        not a malformed condition, so the path resolves to None rather than raising.
        """
        snapshots = {'prechange': None, 'postchange': {'status': 'active'}}
        self.assertFalse(Condition('snapshots.prechange.status', value='planned').eval({'snapshots': snapshots}))
        self.assertTrue(Condition('snapshots.prechange.status', value=None).eval({'snapshots': snapshots}))
        self.assertTrue(
            Condition('snapshots.prechange.status', value='planned', negate=True).eval({'snapshots': snapshots})
        )

    def test_snapshot_path_resolves_to_none_when_postchange_absent(self):
        """As above, for the postchange snapshot on a delete event."""
        snapshots = {'prechange': {'status': 'active'}, 'postchange': None}
        self.assertFalse(Condition('snapshots.postchange.status', value='active').eval({'snapshots': snapshots}))
        self.assertTrue(Condition('snapshots.postchange.status', value=None).eval({'snapshots': snapshots}))

    def test_absent_snapshot_is_a_non_match_for_every_operator(self):
        """
        An absent snapshot resolves to None, which satisfies only a comparison against null.
        Operators which raise a TypeError on None must report a plain non-match rather than
        aborting evaluation, so that the guarantee holds for all operators and not just
        those which happen to tolerate None.
        """
        data = {'snapshots': {'prechange': None, 'postchange': {'description': 'foo'}}}
        attr = 'snapshots.prechange.description'
        for op, value in (('contains', 'foo'), ('regex', '^foo'), ('gt', 1), ('gte', 1), ('lt', 1), ('lte', 1)):
            with self.subTest(op=op):
                self.assertFalse(Condition(attr, value=value, op=op).eval(data))
                self.assertTrue(Condition(attr, value=value, op=op, negate=True).eval(data))

    def test_absent_snapshot_does_not_veto_sibling_conditions(self):
        """
        Regression: an absent prechange snapshot must not abort evaluation of the whole
        condition set, which would suppress a sibling condition that does match. The
        result must also not depend on the order of the conditions, nor on which operator
        the snapshot condition uses.
        """
        data = {'name': 'Site 1', 'snapshots': {'prechange': None, 'postchange': {'status': 'active'}}}
        name_rule = {'attr': 'name', 'value': 'Site 1'}
        for snapshot_rule in (
            {'attr': 'snapshots.prechange.status', 'value': 'planned'},
            {'attr': 'snapshots.prechange.status', 'value': 'plan', 'op': 'contains'},
            {'attr': 'snapshots.prechange.status', 'value': '^plan', 'op': 'regex'},
        ):
            with self.subTest(op=snapshot_rule.get('op', 'eq')):
                self.assertTrue(ConditionSet({'or': [snapshot_rule, name_rule]}).eval(data))
                self.assertTrue(ConditionSet({'or': [name_rule, snapshot_rule]}).eval(data))

    def test_snapshot_path_typo_still_fails_closed(self):
        """
        A path naming a snapshot that exists but lacks the attribute is a genuine typo and
        must still raise, so that it is logged rather than silently evaluating.
        """
        snapshots = {'prechange': {'status': 'planned'}, 'postchange': {'status': 'active'}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.stauts', value='planned').eval({'snapshots': snapshots})
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.bogus.status', value='planned').eval({'snapshots': snapshots})

        # A misnamed snapshot which happens to be null names no snapshot the event could have
        # recorded, so it has no absence to excuse it: it must fail closed like any other typo,
        # rather than resolving to null and firing the rule
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.bogus.status', value=None).eval({'snapshots': {'bogus': None}})

    def test_absent_snapshot_path_traversing_scalar_still_fails_closed(self):
        """
        An absent snapshot excuses only the absence of the data, not a path which cannot be
        walked at all. A REST API-style 'status.value' must fail closed on create and delete
        events exactly as it does on updates, rather than resolving to null (which would fire
        the rule on every create) with nothing logged.
        """
        create = {'snapshots': {'prechange': None, 'postchange': {'status': 'active', 'tags': ['Alpha']}}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.status.value', value='active').eval(create)
        with self.assertRaises(InvalidCondition):
            # A test for null must not escape the check either
            Condition('snapshots.prechange.status.value', value=None).eval(create)
        with self.assertRaises(InvalidCondition):
            # Snapshot list fields hold raw values, so descending into an element is
            # equally unwalkable
            Condition('snapshots.prechange.tags.name', value='Alpha').eval(create)

        delete = {'snapshots': {'prechange': {'status': 'active'}, 'postchange': None}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.postchange.status.value', value='active').eval(delete)

        # An empty string is exactly as unwalkable as a populated one, so the check must not
        # turn on the truthiness of the value in the opposite snapshot
        blank = {'snapshots': {'prechange': None, 'postchange': {'description': ''}}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.description.value', value=None).eval(blank)

    def test_absent_snapshot_path_unknown_to_opposite_snapshot_fails_closed(self):
        """
        An absent snapshot excuses only a path the opposite snapshot shows to describe the
        data. A path which resolves to nothing there either is not shown to describe it, so it
        must fail closed rather than resolving to null - which would let an unknown path fire
        the rule on every create or delete, with nothing logged, even though the same path
        raises on an update event. Testing for the absent snapshot itself remains available
        as 'snapshots.prechange' with no remainder.
        """
        create = {'snapshots': {'prechange': None, 'postchange': {'custom_fields': {'cf1': 'x'}, 'tags': []}}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.nonexistent.attr', value=None).eval(create)
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.custom_fields.cf2', value=None).eval(create)
        # An empty list holds no element in which to find 'name', so it cannot show the path
        # to describe the data any more than an absent key can
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.tags.name', value=None).eval(create)

        delete = {'snapshots': {'prechange': {'status': 'active'}, 'postchange': None}}
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.postchange.nonexistent.attr', value=None).eval(delete)

    def test_absent_snapshot_path_resolves_to_none_when_shape_is_valid(self):
        """
        A nested path which the opposite snapshot resolves is a genuine absence, so it
        resolves to null. So is the absent snapshot itself, and a path which cannot be checked
        at all because the opposite snapshot is null too: the event then carries no data
        anywhere to check against, so treating it as absent is the only alternative to logging
        an error for every rule on every such event.
        """
        create = {'snapshots': {'prechange': None, 'postchange': {'custom_fields': {'cf1': 'x'}, 'tags': []}}}
        self.assertTrue(Condition('snapshots.prechange.custom_fields.cf1', value=None).eval(create))
        self.assertTrue(Condition('snapshots.prechange', value=None).eval(create))
        # A resolved value is a resolved value, whatever its own shape
        self.assertTrue(Condition('snapshots.prechange.tags', value=None).eval(create))

        both_absent = {'snapshots': {'prechange': None, 'postchange': None}}
        self.assertTrue(Condition('snapshots.prechange.status.value', value=None).eval(both_absent))
        self.assertTrue(Condition('snapshots.prechange.nonexistent.attr', value=None).eval(both_absent))

    def test_snapshot_path_without_snapshot_context_fails_closed(self):
        """
        A snapshot path used where there is no snapshot context at all (e.g. a job event)
        is a mismatched rule and must fail closed rather than resolving to None.
        """
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.status', value='planned').eval({'snapshots': None})
        with self.assertRaises(InvalidCondition):
            Condition('snapshots.prechange.status', value='planned').eval({'name': 'Site 1'})

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

    def test_event_rule_snapshot_path_rest_api_style_attr_must_return_false(self):
        """
        An EventRule condition mistakenly using a REST API-style '.value' suffix on a
        snapshot path must fail closed (return False) rather than crashing evaluation.
        """
        event_rule = EventRule(
            name='Was planned (REST-style mistake)',
            event_types=[OBJECT_UPDATED],
            conditions={
                'attr': 'snapshots.prechange.status.value',
                'value': SiteStatusChoices.STATUS_PLANNED,
            }
        )
        site = Site.objects.create(name='Site 4', slug='site-4', status=SiteStatusChoices.STATUS_ACTIVE)
        data = self._make_condition_data(site, {
            'prechange': {'status': SiteStatusChoices.STATUS_PLANNED},
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        self.assertFalse(event_rule.eval_conditions(data))

    def test_event_rule_snapshot_path_rest_api_style_attr_on_create_is_logged(self):
        """
        The same mistake must behave identically on a create event, where the prechange
        snapshot is absent: fail closed and log, rather than resolving to null and firing
        the rule for every object created.
        """
        event_rule = EventRule(
            name='Was planned (REST-style mistake)',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                'attr': 'snapshots.prechange.status.value',
                'value': None,
            }
        )
        site = Site.objects.create(name='Site 6', slug='site-6', status=SiteStatusChoices.STATUS_ACTIVE)
        data = self._make_condition_data(site, {
            'prechange': None,
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        with self.assertLogs('netbox.event_rules', level='ERROR') as cm:
            self.assertFalse(event_rule.eval_conditions(data))
        self.assertIn('snapshots.prechange.status.value', cm.output[0])

    def test_event_rule_changed_operator_rest_api_style_attr_is_logged(self):
        """
        The same REST API-style mistake made with a snapshot operator must also fail
        closed *and* be logged. Silently evaluating False would leave the rule dead with
        no indication of why, even though the watched attribute really did change.
        """
        event_rule = EventRule(
            name='Activated (REST-style mistake)',
            event_types=[OBJECT_UPDATED],
            conditions={'attr': 'status.value', 'op': 'changed'}
        )
        site = Site.objects.create(name='Site 5', slug='site-5', status=SiteStatusChoices.STATUS_ACTIVE)
        data = self._make_condition_data(site, {
            'prechange': {'status': SiteStatusChoices.STATUS_PLANNED},
            'postchange': {'status': SiteStatusChoices.STATUS_ACTIVE},
        })
        with self.assertLogs('netbox.event_rules', level='ERROR') as cm:
            self.assertFalse(event_rule.eval_conditions(data))
        self.assertIn('status.value', cm.output[0])
