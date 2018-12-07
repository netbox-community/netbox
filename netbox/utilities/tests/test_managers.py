from django.test import TestCase

from dcim.models import Site


class NaturalOrderByManagerTest(TestCase):
    """
    Ensure consistent natural ordering given myriad sample data. We use dcim.Site as our guinea pig because it's simple.
    """

    def setUp(self):
        return

    def evaluate_ordering(self, names):

        # Create the Sites
        Site.objects.bulk_create(
            Site(name=name, slug=name.lower()) for name in names
        )

        # Validate forward ordering
        self.assertEqual(
            names,
            list(Site.objects.values_list('name', flat=True))
        )

        # Validate reverse ordering
        self.assertEqual(
            list(reversed(names)),
            list(Site.objects.reverse().values_list('name', flat=True))
        )

    def test_leading_digits(self):

        self.evaluate_ordering([
            '1Alpha',
            '1Bravo',
            '1Charlie',
            '9Alpha',
            '9Bravo',
            '9Charlie',
            '10Alpha',
            '10Bravo',
            '10Charlie',
            '99Alpha',
            '99Bravo',
            '99Charlie',
            '100Alpha',
            '100Bravo',
            '100Charlie',
            '999Alpha',
            '999Bravo',
            '999Charlie',
        ])

    def test_trailing_digits(self):

        self.evaluate_ordering([
            'Alpha1',
            'Alpha9',
            'Alpha10',
            'Alpha99',
            'Alpha100',
            'Alpha999',
            'Bravo1',
            'Bravo9',
            'Bravo10',
            'Bravo99',
            'Bravo100',
            'Bravo999',
            'Charlie1',
            'Charlie9',
            'Charlie10',
            'Charlie99',
            'Charlie100',
            'Charlie999',
        ])

    def test_leading_and_trailing_digits(self):

        self.evaluate_ordering([
            '1Alpha1',
            '1Alpha9',
            '1Alpha10',
            '1Alpha99',
            '1Alpha100',
            '1Alpha999',
            '1Bravo1',
            '1Bravo9',
            '1Bravo10',
            '1Bravo99',
            '1Bravo100',
            '1Bravo999',
            '1Charlie1',
            '1Charlie9',
            '1Charlie10',
            '1Charlie99',
            '1Charlie100',
            '1Charlie999',
            '9Alpha1',
            '9Alpha9',
            '9Alpha10',
            '9Alpha99',
            '9Alpha100',
            '9Alpha999',
            '9Bravo1',
            '9Bravo9',
            '9Bravo10',
            '9Bravo99',
            '9Bravo100',
            '9Bravo999',
            '9Charlie1',
            '9Charlie9',
            '9Charlie10',
            '9Charlie99',
            '9Charlie100',
            '9Charlie999',
            '10Alpha1',
            '10Alpha9',
            '10Alpha10',
            '10Alpha99',
            '10Alpha100',
            '10Alpha999',
            '10Bravo1',
            '10Bravo9',
            '10Bravo10',
            '10Bravo99',
            '10Bravo100',
            '10Bravo999',
            '10Charlie1',
            '10Charlie9',
            '10Charlie10',
            '10Charlie99',
            '10Charlie100',
            '10Charlie999',
            '99Alpha1',
            '99Alpha9',
            '99Alpha10',
            '99Alpha99',
            '99Alpha100',
            '99Alpha999',
            '99Bravo1',
            '99Bravo9',
            '99Bravo10',
            '99Bravo99',
            '99Bravo100',
            '99Bravo999',
            '99Charlie1',
            '99Charlie9',
            '99Charlie10',
            '99Charlie99',
            '99Charlie100',
            '99Charlie999',
            '100Alpha1',
            '100Alpha9',
            '100Alpha10',
            '100Alpha99',
            '100Alpha100',
            '100Alpha999',
            '100Bravo1',
            '100Bravo9',
            '100Bravo10',
            '100Bravo99',
            '100Bravo100',
            '100Bravo999',
            '100Charlie1',
            '100Charlie9',
            '100Charlie10',
            '100Charlie99',
            '100Charlie100',
            '100Charlie999',
            '999Alpha1',
            '999Alpha9',
            '999Alpha10',
            '999Alpha99',
            '999Alpha100',
            '999Alpha999',
            '999Bravo1',
            '999Bravo9',
            '999Bravo10',
            '999Bravo99',
            '999Bravo100',
            '999Bravo999',
            '999Charlie1',
            '999Charlie9',
            '999Charlie10',
            '999Charlie99',
            '999Charlie100',
            '999Charlie999',
        ])
