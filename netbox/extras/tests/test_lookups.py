from django.core.exceptions import FieldError
from django.test import TestCase

from extras.choices import CustomFieldChoiceSetBaseChoices
from extras.models import CustomFieldChoiceSet, EventRule


class ChoiceValueLookupTestCase(TestCase):

    def test_choice_value_matches_values_only(self):
        """choice_value matches the value element of a pair, never the label."""
        CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            extra_choices=[['sel1', 'Selection 1'], ['other', 'sel2']],
        )
        self.assertEqual(CustomFieldChoiceSet.objects.filter(extra_choices__choice_value='sel1').count(), 1)
        self.assertEqual(CustomFieldChoiceSet.objects.filter(extra_choices__choice_value='sel2').count(), 0)

    def test_choice_value_excludes_null_extra_choices(self):
        """Choice sets without extra choices are excluded without raising."""
        CustomFieldChoiceSet.objects.create(
            name='Base Only',
            base_choices=CustomFieldChoiceSetBaseChoices.IATA,
        )
        self.assertEqual(CustomFieldChoiceSet.objects.filter(extra_choices__choice_value='sel1').count(), 0)
        self.assertEqual(CustomFieldChoiceSet.objects.filter(extra_choices__len=2).count(), 0)

    def test_choice_value_not_registered_on_plain_array_fields(self):
        """choice_value is scoped to ChoiceSetField and unavailable on other ArrayFields."""
        with self.assertRaises(FieldError):
            EventRule.objects.filter(event_types__choice_value='x').exists()
