from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.constants import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Location, Manufacturer, Region, Site, SiteGroup
from ipam.forms import PrefixForm
from ipam.forms.bulk_import import IPAddressImportForm


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


class IPAddressImportFormTestCase(TestCase):
    """Tests for IPAddressImportForm bulk import behavior."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        cls.device = Device.objects.create(
            name='Device 1',
            site=site,
            device_type=device_type,
            role=device_role,
        )
        cls.interface = Interface.objects.create(
            device=cls.device,
            name='eth0',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

    def test_oob_import_not_cleared_by_subsequent_non_oob_row(self):
        """
        Regression test for #21440: importing a second IP with is_oob=False should
        not clear the OOB IP set by a previous row with is_oob=True.
        """
        form1 = IPAddressImportForm(data={
            'address': '10.10.10.1/24',
            'status': 'active',
            'device': 'Device 1',
            'interface': 'eth0',
            'is_oob': True,
        })
        self.assertTrue(form1.is_valid(), form1.errors)
        ip1 = form1.save()

        self.device.refresh_from_db()
        self.assertEqual(self.device.oob_ip, ip1)

        form2 = IPAddressImportForm(data={
            'address': '2001:db8::1/64',
            'status': 'active',
            'device': 'Device 1',
            'interface': 'eth0',
            'is_oob': False,
        })
        self.assertTrue(form2.is_valid(), form2.errors)
        form2.save()

        self.device.refresh_from_db()
        self.assertEqual(self.device.oob_ip, ip1, "OOB IP was incorrectly cleared by a row with is_oob=False")
