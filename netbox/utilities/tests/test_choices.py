from django.test import TestCase, override_settings

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


class FieldChoicesCaseInsensitiveTestCase(TestCase):
    """
    Integration tests for FIELD_CHOICES case-insensitive key lookup.
    """

    def test_replace_choices_with_different_casing(self):
        """Test that replacement works when config key casing differs."""
        # Config uses lowercase, but code constructs PascalCase key
        with override_settings(FIELD_CHOICES={'utilities.teststatus': [('new', 'New')]}):
            class TestStatusChoices(ChoiceSet):
                key = 'TestStatus'  # Code will look up 'utilities.TestStatus'
                CHOICES = [('old', 'Old')]

            self.assertEqual(TestStatusChoices.CHOICES, [('new', 'New')])

    def test_extend_choices_with_different_casing(self):
        """Test that extension works with the + suffix under casing differences."""
        # Config uses lowercase with + suffix
        with override_settings(FIELD_CHOICES={'utilities.teststatus+': [('extra', 'Extra')]}):
            class TestStatusChoices(ChoiceSet):
                key = 'TestStatus'  # Code will look up 'utilities.TestStatus+'
                CHOICES = [('base', 'Base')]

            self.assertEqual(TestStatusChoices.CHOICES, [('base', 'Base'), ('extra', 'Extra')])
