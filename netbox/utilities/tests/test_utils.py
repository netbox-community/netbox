from django.http import QueryDict
from django.test import TestCase

from utilities.utils import deepmerge, dict_to_filter_params, normalize_querydict


class DictToFilterParamsTest(TestCase):
    """
    Validate the operation of dict_to_filter_params().
    """
    def test_dict_to_filter_params(self):

        input = {
            'a': True,
            'foo': {
                'bar': 123,
                'baz': 456,
            },
            'x': {
                'y': {
                    'z': False
                }
            }
        }

        output = {
            'a': True,
            'foo__bar': 123,
            'foo__baz': 456,
            'x__y__z': False,
        }

        self.assertEqual(dict_to_filter_params(input), output)

        input['x']['y']['z'] = True

        self.assertNotEqual(dict_to_filter_params(input), output)


class NormalizeQueryDictTest(TestCase):
    """
    Validate normalize_querydict() utility function.
    """
    def test_normalize_querydict(self):
        self.assertDictEqual(
            normalize_querydict(QueryDict('foo=1&bar=2&bar=3&baz=')),
            {'foo': '1', 'bar': ['2', '3'], 'baz': ''}
        )


class DeepMergeTest(TestCase):
    """
    Validate the behavior of the deepmerge() utility.
    """
    def test_deepmerge(self):

        dict1 = {
            'active': True,
            'foo': 123,
            'fruits': {
                'orange': 1,
                'apple': 2,
                'pear': 3,
            },
            'vegetables': None,
            'dairy': {
                'milk': 1,
                'cheese': 2,
            },
            'deepnesting': {
                'foo': {
                    'a': 10,
                    'b': 20,
                    'c': 30,
                },
            },
        }

        dict2 = {
            'active': False,
            'bar': 456,
            'fruits': {
                'banana': 4,
                'grape': 5,
            },
            'vegetables': {
                'celery': 1,
                'carrots': 2,
                'corn': 3,
            },
            'dairy': None,
            'deepnesting': {
                'foo': {
                    'a': 100,
                    'd': 40,
                },
            },
        }

        merged = {
            'active': False,
            'foo': 123,
            'bar': 456,
            'fruits': {
                'orange': 1,
                'apple': 2,
                'pear': 3,
                'banana': 4,
                'grape': 5,
            },
            'vegetables': {
                'celery': 1,
                'carrots': 2,
                'corn': 3,
            },
            'dairy': None,
            'deepnesting': {
                'foo': {
                    'a': 100,
                    'b': 20,
                    'c': 30,
                    'd': 40,
                },
            },
        }

        self.assertEqual(
            deepmerge(dict1, dict2),
            merged
        )
