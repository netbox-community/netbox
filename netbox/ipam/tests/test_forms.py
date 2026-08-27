from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.constants import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Location, Manufacturer, Region, Site, SiteGroup
from ipam.choices import PrefixStatusChoices
from ipam.constants import VLANGROUP_SCOPE_TYPES
from ipam.forms import PrefixForm, VLANGroupBulkEditForm, VLANGroupForm, VLANIDBulkCreateForm
from ipam.forms.bulk_import import IPAddressImportForm
from ipam.models import Prefix, VLANGroup


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

    def test_vlan_field_sets_dynamic_params_for_scope_site_group(self):
        """data-dynamic-params present with available_at_site_group when scope type is Site Group"""
        site_group = SiteGroup.objects.create(name='Site Group 1', slug='site-group-1')
        form = PrefixForm(data={
            'scope_type': ContentType.objects.get_for_model(SiteGroup).id,
            'scope': site_group,
        })
        expected = '[{"fieldName":"scope","queryParam":"available_at_site_group"}]'
        assert form.fields['vlan'].widget.attrs['data-dynamic-params'] == expected

    def test_vlan_field_does_not_set_dynamic_params_for_other_scopes(self):
        """data-dynamic-params not present when scope type is not Site or Site Group"""
        cases = [
            Region(name='Region 1', slug='region-1'),
            Location(site=self.site, name='Location 1', slug='location-1'),
        ]
        for case in cases:
            form = PrefixForm(data={
                'scope_type': ContentType.objects.get_for_model(case._meta.model).id,
                'scope': case,
            })
            assert 'data-dynamic-params' not in form.fields['vlan'].widget.attrs

    def test_scope_type_change_without_scope(self):
        """Changing the scope type without selecting a scope is reported on the scope field."""
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Site),
            scope_id=self.site.pk,
        )
        form = PrefixForm(
            data={
                'prefix': '10.0.0.0/24',
                'status': PrefixStatusChoices.STATUS_ACTIVE,
                'scope_type': ContentType.objects.get_for_model(Location).pk,
                'scope': '',
            },
            instance=prefix,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('scope', form.errors)


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

    def test_import_with_empty_is_primary_column_no_device(self):
        """
        Regression test for #22561: importing an IP where the is_primary/is_oob columns are
        present but empty (and no device/VM specified) should succeed, not raise AttributeError.
        """
        form = IPAddressImportForm(data={
            'address': '172.16.0.1/20',
            'status': 'active',
            'device': '',
            'virtual_machine': '',
            'interface': '',
            'is_primary': '',
            'is_oob': '',
            'description': 'gateway for group A - Site 01',
        })
        self.assertTrue(form.is_valid(), form.errors)
        ip = form.save()
        self.assertEqual(str(ip.address), '172.16.0.1/20')

    def test_import_with_false_is_primary_no_device(self):
        """
        Regression test for #22561: importing an IP with an explicit is_primary=false (and no
        device/VM specified) should succeed as a no-op, not raise AttributeError. An explicit
        falsy boolean is not caught by clean_is_primary()'s "column absent" check.
        """
        form = IPAddressImportForm(data={
            'address': '172.16.0.1/20',
            'status': 'active',
            'is_primary': 'false',
            'is_oob': 'false',
            'description': 'no parent specified',
        })
        self.assertTrue(form.is_valid(), form.errors)
        ip = form.save()
        self.assertEqual(str(ip.address), '172.16.0.1/20')

    def test_primary_not_cleared_by_subsequent_non_primary_row_with_device(self):
        """
        Guard against re-breaking #21440 while fixing #22561: importing a second IP with
        is_primary=false (device specified) must not clear the primary IP set by a previous
        row. The save-side parent guard must leave the conservative "only clear if currently
        primary" behavior intact.
        """
        form1 = IPAddressImportForm(data={
            'address': '10.10.10.1/24',
            'status': 'active',
            'device': 'Device 1',
            'interface': 'eth0',
            'is_primary': True,
        })
        self.assertTrue(form1.is_valid(), form1.errors)
        ip1 = form1.save()

        self.device.refresh_from_db()
        self.assertEqual(self.device.primary_ip4, ip1)

        form2 = IPAddressImportForm(data={
            'address': '10.10.10.2/24',
            'status': 'active',
            'device': 'Device 1',
            'interface': 'eth0',
            'is_primary': False,
        })
        self.assertTrue(form2.is_valid(), form2.errors)
        form2.save()

        self.device.refresh_from_db()
        self.assertEqual(
            self.device.primary_ip4, ip1, "primary IP was incorrectly cleared by a row with is_primary=False"
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


class VLANFormTestCase(TestCase):

    def test_bulk_create_valid_patterns(self):
        """Single values, ranges, and combinations expand to sorted, deduplicated VLAN IDs."""
        cases = (
            ('100', [100]),
            ('5,10,20', [5, 10, 20]),
            ('10-20', list(range(10, 21))),
            ('1,10-20,300-305', [1, *range(10, 21), *range(300, 306)]),
            (' 5 , 7 - 9 ', [5, 7, 8, 9]),
            ('5,5,4-6', [4, 5, 6]),
        )
        for pattern, expected in cases:
            with self.subTest(pattern=pattern):
                form = VLANIDBulkCreateForm({'pattern': pattern})
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data['pattern'], expected)

    def test_bulk_create_invalid_patterns(self):
        """Malformed, descending, or out-of-range patterns are rejected with an error on the pattern field."""
        cases = ('', 'abc', '10,abc', '20-10', '10-', '5,', '-5', '0', '4095')
        for pattern in cases:
            with self.subTest(pattern=pattern):
                form = VLANIDBulkCreateForm({'pattern': pattern})
                self.assertFalse(form.is_valid())
                self.assertIn('pattern', form.errors)


class VLANGroupFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')
        cls.site_type = ContentType.objects.get_for_model(Site)
        cls.location_type = ContentType.objects.get_for_model(Location)
        cls.vlan_group = VLANGroup.objects.create(
            name='VLAN Group 1',
            slug='vlan-group-1',
            scope=cls.site,
        )

    def test_scope_can_be_cleared(self):
        """Clearing scope type and scope on an existing group nulls the assignment."""
        form = VLANGroupForm(
            data=self.get_form_data(scope_type='', scope=''),
            instance=VLANGroup.objects.get(pk=self.vlan_group.pk),
        )
        self.assertTrue(form.is_valid(), form.errors)

        vlan_group = form.save()
        vlan_group.refresh_from_db()
        self.assertIsNone(vlan_group.scope_type_id)
        self.assertIsNone(vlan_group.scope_id)

    def test_scope_required_with_scope_type(self):
        """A scope type without a scope is reported on the scope field."""
        forms = {
            'existing group': VLANGroupForm(
                data=self.get_form_data(scope=''),
                instance=VLANGroup.objects.get(pk=self.vlan_group.pk),
            ),
            'new group': VLANGroupForm(
                data=self.get_form_data(name='VLAN Group 2', slug='vlan-group-2', scope=''),
            ),
            'retyped group': VLANGroupForm(
                data=self.get_form_data(scope_type=self.location_type.pk, scope=''),
                instance=VLANGroup.objects.get(pk=self.vlan_group.pk),
            ),
        }
        for case, form in forms.items():
            with self.subTest(case=case):
                self.assertFalse(form.is_valid())
                self.assertIn('scope', form.errors)

    def test_scope_initial_retained_for_new_group(self):
        """A prepopulated scope survives instantiation of an unsaved group."""
        form = VLANGroupForm(initial={'scope_type': self.site_type.pk, 'scope': self.site.pk})

        self.assertEqual(form.initial['scope'], self.site.pk)

    def test_scope_type_choices(self):
        """Both VLAN group forms offer every VLAN group scope type."""
        for form_class in (VLANGroupForm, VLANGroupBulkEditForm):
            with self.subTest(form=form_class.__name__):
                form = form_class()
                models = set(form.fields['scope_type'].queryset.values_list('model', flat=True))
                self.assertEqual(models, set(VLANGROUP_SCOPE_TYPES))

    def get_form_data(self, **overrides):
        return {
            'name': self.vlan_group.name,
            'slug': self.vlan_group.slug,
            'vid_ranges': '1-4094',
            'scope_type': self.site_type.pk,
            'scope': self.site.pk,
            **overrides,
        }
