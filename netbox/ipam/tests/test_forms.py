from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import Location, Region, Site, SiteGroup
from ipam.forms import PrefixForm


class PrefixFormTestCase(TestCase):
    default_dynamic_params = '[{"fieldName":"scope","queryParam":"available_at_site"}]'

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def test_vlan_field_sets_dynamic_params_by_default(self):
        """data-dynamic-params present when no scope_type selected"""
        form = PrefixForm(data={})

        assert form.fields['vlan'].widget.attrs['data-dynamic-params'] == self.default_dynamic_params

    def test_vlan_field_sets_dynamic_params_for_scope_site(self):
        """data-dynamic-params present when scope type is Site and when scope is specifc site"""
        form = PrefixForm(data={
            'scope_type': ContentType.objects.get_for_model(Site).id,
            'scope': self.site,
        })

        assert form.fields['vlan'].widget.attrs['data-dynamic-params'] == self.default_dynamic_params

    def test_vlan_field_does_not_set_dynamic_params_for_other_scopes(self):
        """data-dynamic-params not present when scope type is populated by is not Site"""
        cases = [
            Region(name='Region 1', slug='region-1'),
            Location(site=self.site, name='Location 1', slug='location-1'),
            SiteGroup(name='Site Group 1', slug='site-group-1'),
        ]
        for case in cases:
            form = PrefixForm(data={
                'scope_type': ContentType.objects.get_for_model(case._meta.model).id,
                'scope': case,
            })

            assert 'data-dynamic-params' not in form.fields['vlan'].widget.attrs
