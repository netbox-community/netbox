from django.test import TestCase

from utilities.choices import ChoiceSet


class ExampleChoices(ChoiceSet):

    CHOICE_A = 'a'
    CHOICE_B = 'b'
    CHOICE_C = 'c'
    CHOICE_1 = 1
    CHOICE_2 = 2
    CHOICE_3 = 3

    CHOICES = (
        ('Letters', (
            (CHOICE_A, 'A'),
            (CHOICE_B, 'B'),
            (CHOICE_C, 'C'),
        )),
        ('Digits', (
            (CHOICE_1, 'One'),
            (CHOICE_2, 'Two'),
            (CHOICE_3, 'Three'),
        )),
    )


class ChoiceSetTestCase(TestCase):

    def test_values(self):
        self.assertListEqual(ExampleChoices.values(), ['a', 'b', 'c', 1, 2, 3])

    def test_as_dict(self):
        self.assertEqual(ExampleChoices.as_dict(), {
            'a': 'A', 'b': 'B', 'c': 'C', 1: 'One', 2: 'Two', 3: 'Three'
        })
