from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.constants import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Location, Manufacturer, Region, Site, SiteGroup
from ipam.constants import SERVICE_PORT_MAX
from ipam.forms import PrefixForm, VLANIDBulkCreateForm
from ipam.forms.bulk_import import IPAddressImportForm, ServiceTemplateImportForm
from ipam.forms.fields import PortMappingField
from ipam.forms.widgets import PortMappingWidget


class PrefixFormTestCase(TestCase):
    default_dynamic_params = '[{"fieldName":"scope_object_id","queryParam":"available_at_site"}]'

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
            'scope_content_type': ContentType.objects.get_for_model(Site).id,
            'scope_object_id': self.site.pk,
        })

        assert form.fields['vlan'].widget.attrs['data-dynamic-params'] == self.default_dynamic_params

    def test_vlan_field_sets_dynamic_params_for_scope_site_group(self):
        """data-dynamic-params present with available_at_site_group when scope type is Site Group"""
        site_group = SiteGroup.objects.create(name='Site Group 1', slug='site-group-1')
        form = PrefixForm(data={
            'scope_content_type': ContentType.objects.get_for_model(SiteGroup).id,
            'scope_object_id': site_group.pk,
        })
        expected = '[{"fieldName":"scope_object_id","queryParam":"available_at_site_group"}]'
        assert form.fields['vlan'].widget.attrs['data-dynamic-params'] == expected

    def test_vlan_field_does_not_set_dynamic_params_for_other_scopes(self):
        """data-dynamic-params not present when scope type is not Site or Site Group"""
        cases = [
            Region(name='Region 1', slug='region-1'),
            Location(site=self.site, name='Location 1', slug='location-1'),
        ]
        for case in cases:
            case.save()
            form = PrefixForm(data={
                'scope_content_type': ContentType.objects.get_for_model(case._meta.model).id,
                'scope_object_id': case.pk,
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


class PortMappingFieldTestCase(TestCase):

    def test_ports_and_ranges_expand(self):
        """A protocol row's comma/range port string expands into individual protocol/port mappings."""
        field = PortMappingField()
        value = field.clean('[{"protocol": "tcp", "ports": "80,443,8000-8002"}]')
        self.assertEqual(value, ['tcp/80', 'tcp/443', 'tcp/8000', 'tcp/8001', 'tcp/8002'])

    def test_out_of_range_rejected_without_expanding(self):
        """
        An out-of-bounds range is rejected before it is expanded, so a pathological range cannot
        exhaust memory (regression guard for the unbounded parse_numeric_range expansion).
        """
        field = PortMappingField()
        with self.assertRaises(ValidationError):
            field.clean('[{"protocol": "tcp", "ports": "1-9999999999"}]')
        with self.assertRaises(ValidationError):
            field.clean(f'[{{"protocol": "tcp", "ports": "1-{SERVICE_PORT_MAX + 1}"}}]')

    def test_malformed_payload_rejected(self):
        """
        The hidden input is ordinary POST data, so a hand-crafted payload need not be the list of
        {protocol, ports} objects the widget's JS produces. Anything else must raise a ValidationError
        (a 400) rather than an unhandled AttributeError/TypeError (a 500).
        """
        field = PortMappingField()
        for value in (
            '5',                                        # a JSON scalar
            '"tcp/80"',                                 # a JSON string
            '{"protocol": "tcp", "ports": "80"}',       # an object rather than a list of them
            '[5]',                                      # a list of non-objects
            '[[1, 2]]',                                 # a list of lists
            '[null]',                                   # a null row
            '[{"protocol": "tcp", "ports": {"a": 1}}]',  # ports of the wrong type
            '[{"protocol": ["tcp"], "ports": "80"}]',   # protocol of the wrong type
        ):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                field.clean(value)

    def test_widget_tolerates_malformed_value(self):
        """
        Re-rendering an invalid bound form hands the widget back the raw POST value, which may be valid
        JSON of the wrong shape. It must fall back to a blank row rather than raise while rendering.
        """
        widget = PortMappingWidget()
        for value in ('5', '"tcp/80"', '{"a": 1}', '[5]', '[[1, 2]]', 'not json at all'):
            with self.subTest(value=value):
                context = widget.get_context('port_mappings', value, {})
                self.assertEqual(context['widget']['rows'], [{'protocol': '', 'ports': ''}])

    def test_ports_as_list_requires_protocol(self):
        """
        A programmatically-set list of ports still gets the blank-protocol check, rather than emitting a
        '/80' token that surfaces as a blank "Invalid protocol:" message.
        """
        field = PortMappingField()
        self.assertEqual(field.clean('[{"protocol": "tcp", "ports": [80, 443]}]'), ['tcp/80', 'tcp/443'])
        with self.assertRaises(ValidationError) as ctx:
            field.clean('[{"protocol": "", "ports": [80]}]')
        self.assertTrue(any('protocol' in msg.lower() for msg in ctx.exception.messages))
        self.assertFalse(any(msg.strip().endswith('Invalid protocol:') for msg in ctx.exception.messages))

    def test_protocol_without_ports_reports_clear_error(self):
        """A protocol chosen with no ports reports the 'protocol/port' error, not 'Range \"\" is invalid'."""
        field = PortMappingField()
        with self.assertRaises(ValidationError) as ctx:
            field.clean('[{"protocol": "tcp", "ports": ""}]')
        self.assertTrue(any('tcp/' in msg for msg in ctx.exception.messages))

    def test_ports_without_protocol_reports_clear_error(self):
        """Ports entered with no protocol (e.g. the blank initial row) report a clear protocol error."""
        field = PortMappingField()
        with self.assertRaises(ValidationError) as ctx:
            field.clean('[{"protocol": "", "ports": "80"}]')
        self.assertTrue(any('protocol' in msg.lower() for msg in ctx.exception.messages))
        # Specifically not the confusing blank "Invalid protocol:" message.
        self.assertFalse(any(msg.strip().endswith('Invalid protocol:') for msg in ctx.exception.messages))

    def test_row_errors_identify_the_row(self):
        """
        A per-row error names the offending row, since the widget renders one row per protocol and an
        unqualified message gives no clue which of several rows to fix.
        """
        field = PortMappingField()
        # A row with ports but no protocol
        rows = '[{"protocol": "tcp", "ports": "80"}, {"protocol": "", "ports": "53"}]'
        with self.assertRaises(ValidationError) as ctx:
            field.clean(rows)
        self.assertTrue(
            any(msg.startswith('Row 2:') for msg in ctx.exception.messages), ctx.exception.messages
        )
        # A row whose port range is invalid
        rows = '[{"protocol": "tcp", "ports": "80"}, {"protocol": "udp", "ports": "9000-53"}]'
        with self.assertRaises(ValidationError) as ctx:
            field.clean(rows)
        self.assertTrue(
            any(msg.startswith('Row 2:') for msg in ctx.exception.messages), ctx.exception.messages
        )

    def test_whole_field_errors_are_not_row_attributed(self):
        """
        Errors raised by validate_port_mappings() are left unqualified: each already quotes the offending
        mapping, and a duplicate spans two rows so attributing it to one would be misleading.
        """
        field = PortMappingField()
        with self.assertRaises(ValidationError) as ctx:
            field.clean('[{"protocol": "tcp", "ports": "80"}, {"protocol": "udp", "ports": ""}]')
        self.assertFalse(any(msg.startswith('Row ') for msg in ctx.exception.messages))
        self.assertTrue(any('udp/' in msg for msg in ctx.exception.messages), ctx.exception.messages)

    def test_reversed_range_rejected(self):
        """A reversed range must raise rather than silently expanding to an empty (dropped) list."""
        field = PortMappingField()
        with self.assertRaises(ValidationError):
            field.clean('[{"protocol": "tcp", "ports": "9000-53"}]')

    def test_invalid_subrange_alongside_valid_rejected(self):
        """
        An invalid range combined with a valid one must raise rather than silently dropping the
        invalid sub-range (the valid range would otherwise mask the empty expansion).
        """
        field = PortMappingField()
        with self.assertRaises(ValidationError):
            field.clean('[{"protocol": "tcp", "ports": "80,9000-53"}]')
        with self.assertRaises(ValidationError):
            field.clean('[{"protocol": "tcp", "ports": "80,70000-80"}]')

    def test_normalizes_leading_zero_ports(self):
        """Leading-zero ports are normalized so they remain matchable by the port filter."""
        field = PortMappingField()
        self.assertEqual(field.clean('[{"protocol": "tcp", "ports": "080"}]'), ['tcp/80'])

    def test_prepare_value_grouped_json_passthrough(self):
        """An already-grouped JSON string (bound-form re-render) is passed to the widget unchanged."""
        field = PortMappingField()
        self.assertEqual(
            field.prepare_value('[{"protocol": "tcp", "ports": "80"}]'),
            '[{"protocol": "tcp", "ports": "80"}]',
        )

    def test_prepare_value_flat_list_grouped(self):
        """A flat protocol/port list (e.g. a multi-mapping clone) is grouped into widget rows."""
        field = PortMappingField()
        self.assertEqual(
            field.prepare_value(['tcp/80', 'tcp/443']),
            '[{"protocol": "tcp", "ports": "80,443"}]',
        )

    def test_prepare_value_bare_string_grouped(self):
        """
        Cloning a single-mapping object collapses port_mappings to a bare 'protocol/port' string
        (normalize_querydict single-value collapse); it must group into a row, not blank the widget.
        Regression guard for the single-protocol clone losing its port mapping.
        """
        field = PortMappingField()
        self.assertEqual(
            field.prepare_value('tcp/80'),
            '[{"protocol": "tcp", "ports": "80"}]',
        )


class ServiceTemplateImportFormTestCase(TestCase):

    def test_valid_port_mappings_parsed_and_normalized(self):
        form = ServiceTemplateImportForm(data={'name': 'X', 'port_mappings': 'tcp/080,tcp/443,udp/53'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['port_mappings'], ['tcp/80', 'tcp/443', 'udp/53'])

    def test_protocol_lowercased(self):
        """Protocols may be given in any case; the input is lowercased before validation."""
        form = ServiceTemplateImportForm(data={'name': 'X', 'port_mappings': 'TCP/80,UDP/53'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['port_mappings'], ['tcp/80', 'udp/53'])

    def test_invalid_protocol_rejected(self):
        form = ServiceTemplateImportForm(data={'name': 'X', 'port_mappings': 'tcp/80,bogus/53'})
        self.assertFalse(form.is_valid())
        self.assertIn('port_mappings', form.errors)

    def test_duplicate_mapping_rejected(self):
        form = ServiceTemplateImportForm(data={'name': 'X', 'port_mappings': 'tcp/80,tcp/080'})
        self.assertFalse(form.is_valid())
        self.assertIn('port_mappings', form.errors)

    def test_empty_port_rejected(self):
        form = ServiceTemplateImportForm(data={'name': 'X', 'port_mappings': 'tcp/'})
        self.assertFalse(form.is_valid())
        self.assertIn('port_mappings', form.errors)
