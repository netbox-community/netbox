from django.test import TestCase

from utilities.utils import deepmerge


class DeepMergeTest(TestCase):
    """
    Validate the behavior of the deepmerge() utility.
    """

    def setUp(self):
        return

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
