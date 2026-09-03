from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from utilities.choices import Choice, ChoiceSet


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


class ChoiceDataclassTestCase(TestCase):
    """
    Validate that a Choice behaves as a (value, label) two-tuple for backward compatibility.
    """
    def test_choice_is_tuple_compatible(self):
        choice = Choice('a', 'A', color='red', description='desc')
        self.assertEqual(list(choice), ['a', 'A'])
        self.assertEqual(choice[0], 'a')
        self.assertEqual(choice[1], 'A')
        self.assertEqual(len(choice), 2)

    def test_choice_unpacking(self):
        value, label = Choice('a', 'A', color='red')
        self.assertEqual(value, 'a')
        self.assertEqual(label, 'A')

    def test_choice_attributes(self):
        choice = Choice('a', 'A')
        self.assertIsNone(choice.color)
        self.assertIsNone(choice.description)

    def test_choice_is_copyable_and_picklable(self):
        """A Choice must survive copy/deepcopy/pickle with all of its attributes intact."""
        import copy
        import pickle

        choice = Choice('a', 'A', color='red', description='desc')
        for clone in (copy.copy(choice), copy.deepcopy(choice), pickle.loads(pickle.dumps(choice))):
            self.assertIsInstance(clone, Choice)
            self.assertEqual(tuple(clone), ('a', 'A'))
            self.assertEqual(clone.color, 'red')
            self.assertEqual(clone.description, 'desc')


class ChoiceSetTestCase(TestCase):

    def test_values(self):
        self.assertListEqual(ExampleChoices.values(), ['a', 'b', 'c', 1, 2, 3])

    def test_choice_objects_preserved_and_populate_colors(self):
        """A ChoiceSet built from Choice objects preserves them in _choices and derives the colors map."""
        class ChoiceObjectChoices(ChoiceSet):
            CHOICES = [
                Choice('a', 'A', color='red', description='First'),
                Choice('b', 'B', color='green'),
                Choice('c', 'C'),
            ]

        # Choice objects are preserved (and remain (value, label)-compatible)
        entries = list(ChoiceObjectChoices)
        self.assertTrue(all(isinstance(c, Choice) for c in entries))
        self.assertEqual([tuple(c) for c in entries], [('a', 'A'), ('b', 'B'), ('c', 'C')])
        self.assertEqual(entries[0].description, 'First')
        self.assertEqual(ChoiceObjectChoices.colors, {'a': 'red', 'b': 'green'})

    def test_dict_choices_normalized_to_choice(self):
        """A ChoiceSet may define choices as dicts (e.g. from config), which normalize to Choice objects."""
        class DictChoices(ChoiceSet):
            CHOICES = [
                {'value': 'a', 'label': 'A', 'color': 'red', 'description': 'First'},
                {'value': 'b', 'label': 'B'},
            ]

        entries = list(DictChoices)
        self.assertTrue(all(isinstance(c, Choice) for c in entries))
        self.assertEqual([tuple(c) for c in entries], [('a', 'A'), ('b', 'B')])
        self.assertEqual(entries[0].description, 'First')
        self.assertEqual(DictChoices.colors, {'a': 'red'})

    def test_dict_choice_with_invalid_key_raises(self):
        """A choice dict with an unrecognized key raises a clear error."""
        with self.assertRaises(TypeError):
            class BadChoices(ChoiceSet):
                CHOICES = [{'value': 'a', 'label': 'A', 'colour': 'red'}]

    def test_legacy_tuples_populate_colors(self):
        """Plain 2-/3-tuples continue to reduce to (value, label) and build the colors map."""
        class LegacyChoices(ChoiceSet):
            CHOICES = [
                ('a', 'A', 'red'),
                ('b', 'B'),
            ]

        self.assertEqual(list(LegacyChoices), [('a', 'A'), ('b', 'B')])
        self.assertEqual(LegacyChoices.colors, {'a': 'red'})

    def test_grouped_choices_with_choice_objects(self):
        """Grouped choices normalize whether members are Choice objects or tuples."""
        class GroupedChoices(ChoiceSet):
            CHOICES = (
                ('Group 1', (
                    Choice('a', 'A', color='red', description='First'),
                    ('b', 'B'),
                )),
            )

        group_label, members = list(GroupedChoices)[0]
        self.assertEqual(group_label, 'Group 1')
        self.assertEqual([tuple(m) for m in members], [('a', 'A'), ('b', 'B')])
        self.assertEqual(members[0].description, 'First')
        self.assertEqual(GroupedChoices.colors, {'a': 'red'})
        self.assertEqual(GroupedChoices.values(), ['a', 'b'])

    def test_key_with_non_list_choices_raises(self):
        """A ChoiceSet declaring a key must define CHOICES as a list."""
        with self.assertRaises(ImproperlyConfigured):
            type(
                'InvalidChoices',
                (ChoiceSet,),
                {
                    '__module__': __name__,
                    'key': 'invalid_choices',
                    'CHOICES': (('foo', 'Foo'),),
                },
            )


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

    def test_config_choices_as_choice_objects(self):
        """FIELD_CHOICES may provide Choice objects to define colors and descriptions."""
        config = {'utilities.teststatus': [Choice('new', 'New', color='red', description='A new thing')]}
        with override_settings(FIELD_CHOICES=config):
            class TestStatusChoices(ChoiceSet):
                key = 'TestStatus'
                CHOICES = [('old', 'Old')]

            entries = list(TestStatusChoices)
            self.assertEqual([tuple(c) for c in entries], [('new', 'New')])
            self.assertEqual(entries[0].description, 'A new thing')
            self.assertEqual(TestStatusChoices.colors, {'new': 'red'})

    def test_config_choices_as_dicts(self):
        """FIELD_CHOICES may provide plain dicts, avoiding any import in configuration.py."""
        choice = {'value': 'new', 'label': 'New', 'color': 'red', 'description': 'A new thing'}
        with override_settings(FIELD_CHOICES={'utilities.teststatus': [choice]}):
            class TestStatusChoices(ChoiceSet):
                key = 'TestStatus'
                CHOICES = [('old', 'Old')]

            entries = list(TestStatusChoices)
            self.assertEqual([tuple(c) for c in entries], [('new', 'New')])
            self.assertEqual(entries[0].description, 'A new thing')
            self.assertEqual(TestStatusChoices.colors, {'new': 'red'})
