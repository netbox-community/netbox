from django.test import TestCase

from dcim.models import Site
from tenancy.models import Tenant
from users.models import Owner, User, UserConfig
from utilities.relations import get_related_models


class GetRelatedModelsTestCase(TestCase):
    """
    Validate the operation of get_related_models().
    """
    def test_visible_relationships_are_returned(self):
        """An ordinary reverse ForeignKey relationship is reported."""
        self.assertIn((Site, 'tenant'), get_related_models(Tenant))

    def test_hidden_relationships_are_omitted_by_default(self):
        """Relationships declared with related_name='+' are not reported unless requested."""
        self.assertEqual(get_related_models(Owner), [])

    def test_hidden_relationships_are_returned_on_request(self):
        """include_hidden reports the relationships hidden by related_name='+'."""
        self.assertIn((Site, 'owner'), get_related_models(Owner, include_hidden=True))

    def test_intermediary_models_are_excluded(self):
        """The auto-created models behind Owner's many-to-many fields are not reported."""
        related = get_related_models(Owner, include_hidden=True)

        self.assertEqual([model for model, _ in related if model._meta.auto_created], [])

    def test_private_models_are_excluded(self):
        """A model flagged _netbox_private is not reported even when hidden relationships are requested."""
        related = get_related_models(User, include_hidden=True)

        self.assertNotIn(UserConfig, [model for model, _ in related])

    def test_results_are_sorted_by_verbose_name(self):
        """Ordered results are sorted by the related model's verbose name."""
        related = get_related_models(Owner, include_hidden=True)

        self.assertEqual(related, sorted(related, key=lambda x: x[0]._meta.verbose_name.lower()))
