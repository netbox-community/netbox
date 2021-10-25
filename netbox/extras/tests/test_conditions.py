from django.test import TestCase

from extras.conditions import Condition, ConditionSet


class ConditionTestCase(TestCase):

    def test_dotted_path_access(self):
        c = Condition('a.b.c', 1, 'eq')
        self.assertTrue(c.eval({'a': {'b': {'c': 1}}}))
        self.assertFalse(c.eval({'a': {'b': {'c': 2}}}))
        self.assertFalse(c.eval({'a': {'b': {'x': 1}}}))

    def test_undefined_attr(self):
        c = Condition('x', 1, 'eq')
        self.assertFalse(c.eval({}))
        self.assertTrue(c.eval({'x': 1}))

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

    def test_invalid_op_type(self):
        with self.assertRaises(ValueError):
            # 'gt' supports only numeric values
            Condition('x', 'foo', 'gt')

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

    def test_gte(self):
        c = Condition('x', 1, 'gte')
        self.assertTrue(c.eval({'x': 2}))
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 0}))

    def test_lt(self):
        c = Condition('x', 2, 'lt')
        self.assertTrue(c.eval({'x': 1}))
        self.assertFalse(c.eval({'x': 2}))

    def test_lte(self):
        c = Condition('x', 2, 'lte')
        self.assertTrue(c.eval({'x': 1}))
        self.assertTrue(c.eval({'x': 2}))
        self.assertFalse(c.eval({'x': 3}))

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

    def test_contains_negated(self):
        c = Condition('x', 1, 'contains', negate=True)
        self.assertFalse(c.eval({'x': [1, 2, 3]}))
        self.assertTrue(c.eval({'x': [2, 3, 4]}))


class ConditionSetTest(TestCase):

    def test_empty(self):
        with self.assertRaises(ValueError):
            ConditionSet({})

    def test_invalid_logic(self):
        with self.assertRaises(ValueError):
            ConditionSet({'foo': []})

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
