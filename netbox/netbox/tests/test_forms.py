from django import forms
from django.test import TestCase

from circuits.forms import CircuitGroupAssignmentForm, CircuitTerminationForm
from core.forms import DataSourceForm
from dcim.choices import InterfaceTypeChoices
from dcim.forms import CableForm, InterfaceForm, InterfaceImportForm, ModuleTypeForm
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from extras.forms import CustomFieldForm, EventRuleForm
from ipam.forms import PrefixForm, ServiceForm, VLANGroupForm
from utilities.forms.widgets import HTMXSelect
from virtualization.forms import ClusterForm, VirtualMachineForm, VMInterfaceForm
from vpn.forms import TunnelCreateForm, TunnelTerminationForm
from wireless.forms import WirelessLANForm


class NetBoxModelImportFormCleanTestCase(TestCase):
    """
    Test the clean() method of NetBoxModelImportForm to ensure it properly converts
    empty strings to None for nullable fields during CSV import.
    Uses InterfaceImportForm as the concrete implementation to test.
    """

    @classmethod
    def setUpTestData(cls):
        # Create minimal test fixtures for Interface
        cls.site = Site.objects.create(name='Test Site', slug='test-site')
        cls.manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        cls.device_type = DeviceType.objects.create(
            manufacturer=cls.manufacturer, model='Test Device Type', slug='test-device-type'
        )
        cls.device_role = DeviceRole.objects.create(name='Test Role', slug='test-role', color='ff0000')
        cls.device = Device.objects.create(
            name='Test Device', device_type=cls.device_type, role=cls.device_role, site=cls.site
        )
        # Create parent interfaces for ForeignKey testing
        cls.parent_interface = Interface.objects.create(
            device=cls.device, name='Parent Interface', type=InterfaceTypeChoices.TYPE_1GE_GBIC
        )
        cls.lag_interface = Interface.objects.create(
            device=cls.device, name='LAG Interface', type=InterfaceTypeChoices.TYPE_LAG
        )

    def test_empty_string_to_none_nullable_charfield(self):
        """Empty strings should convert to None for nullable CharField"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 1',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'duplex': '',  # nullable CharField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['duplex'])

    def test_empty_string_to_none_nullable_integerfield(self):
        """Empty strings should convert to None for nullable PositiveIntegerField"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 2',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': '',  # nullable PositiveIntegerField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['speed'])

    def test_empty_string_to_none_nullable_smallintegerfield(self):
        """Empty strings should convert to None for nullable SmallIntegerField"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 3',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'tx_power': '',  # nullable SmallIntegerField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['tx_power'])

    def test_empty_string_to_none_nullable_decimalfield(self):
        """Empty strings should convert to None for nullable DecimalField"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 4',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'rf_channel_frequency': '',  # nullable DecimalField
                'rf_channel_width': '',  # nullable DecimalField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['rf_channel_frequency'])
        self.assertIsNone(form.cleaned_data['rf_channel_width'])

    def test_empty_string_to_none_nullable_foreignkey(self):
        """Empty strings should convert to None for nullable ForeignKey"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 5',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'lag': '',  # nullable ForeignKey
                'parent': '',  # nullable ForeignKey
                'bridge': '',  # nullable ForeignKey
                'vrf': '',  # nullable ForeignKey
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['lag'])
        self.assertIsNone(form.cleaned_data['parent'])
        self.assertIsNone(form.cleaned_data['bridge'])
        self.assertIsNone(form.cleaned_data['vrf'])

    def test_empty_string_preserved_non_nullable_charfield(self):
        """Empty strings should be preserved for non-nullable CharField (blank=True only)"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 6',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'label': '',  # CharField with blank=True (not null=True)
                'description': '',  # CharField with blank=True (not null=True)
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        # label and description are NOT nullable in the model, so empty string remains
        self.assertEqual(form.cleaned_data['label'], '')
        self.assertEqual(form.cleaned_data['description'], '')

    def test_empty_string_not_converted_for_required_fields(self):
        """Empty strings should NOT be converted for required fields"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': '',  # required field, empty string should remain and cause error
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            }
        )
        # Form should be invalid because name is required
        self.assertFalse(form.is_valid())
        if form.errors:
            self.assertIn('name', form.errors)

    def test_non_string_none_value_preserved(self):
        """None values should be preserved (not modified)"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 7',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': None,  # Already None
                'tx_power': None,  # Already None
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['speed'])
        self.assertIsNone(form.cleaned_data['tx_power'])

    def test_non_string_numeric_values_preserved(self):
        """Numeric values (including 0) should not be modified"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 8',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': 0,  # nullable PositiveIntegerField with value 0
                'tx_power': 0,  # nullable SmallIntegerField with value 0
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertEqual(form.cleaned_data['speed'], 0)
        self.assertEqual(form.cleaned_data['tx_power'], 0)

    def test_manytomany_fields_skipped(self):
        """ManyToMany fields should be skipped and not cause errors"""
        # Interface has 'vdcs' and 'wireless_lans' as M2M fields
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 9',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                # vdcs and wireless_lans fields are M2M, handled by parent class
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')

    def test_fields_not_in_cleaned_data_skipped(self):
        """Fields not present in cleaned_data should be skipped gracefully"""
        # Create minimal form data - some nullable fields won't be in cleaned_data
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 10',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                # lag, parent, bridge, vrf, speed, etc. not provided
            }
        )
        # Should not raise KeyError when checking fields not in form data
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')

    def test_valid_string_values_preserved(self):
        """Non-empty string values should be properly converted to their target types"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 11',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': '1000000',  # Valid speed value (string will be converted to int)
                'mtu': '1500',  # Valid mtu value (string will be converted to int)
                'description': 'Test description',
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        # speed and mtu are converted to int
        self.assertEqual(form.cleaned_data['speed'], 1000000)
        self.assertEqual(form.cleaned_data['mtu'], 1500)
        self.assertEqual(form.cleaned_data['description'], 'Test description')

    def test_multiple_nullable_fields_with_empty_strings(self):
        """Multiple nullable fields with empty strings should all convert to None"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 12',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': '',  # nullable
                'duplex': '',  # nullable
                'tx_power': '',  # nullable
                'vrf': '',  # nullable ForeignKey
                'poe_mode': '',  # nullable
                'poe_type': '',  # nullable
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        # All nullable fields should convert to None
        self.assertIsNone(form.cleaned_data['speed'])
        self.assertIsNone(form.cleaned_data['duplex'])
        self.assertIsNone(form.cleaned_data['tx_power'])
        self.assertIsNone(form.cleaned_data['vrf'])
        self.assertIsNone(form.cleaned_data['poe_mode'])
        self.assertIsNone(form.cleaned_data['poe_type'])

    def test_mixed_nullable_and_non_nullable_empty_strings(self):
        """Combination of nullable and non-nullable fields with empty strings"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 13',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'speed': '',  # nullable, should become None
                'label': '',  # NOT nullable (blank=True only), should remain empty string
                'duplex': '',  # nullable, should become None
                'description': '',  # NOT nullable (blank=True only), should remain empty string
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        # Nullable fields convert to None
        self.assertIsNone(form.cleaned_data['speed'])
        self.assertIsNone(form.cleaned_data['duplex'])
        # Non-nullable fields remain empty strings
        self.assertEqual(form.cleaned_data['label'], '')
        self.assertEqual(form.cleaned_data['description'], '')

    def test_wireless_fields_nullable(self):
        """Wireless-specific nullable fields should convert empty strings to None"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 14',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'rf_role': '',  # nullable CharField
                'rf_channel': '',  # nullable CharField
                'rf_channel_frequency': '',  # nullable DecimalField
                'rf_channel_width': '',  # nullable DecimalField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['rf_role'])
        self.assertIsNone(form.cleaned_data['rf_channel'])
        self.assertIsNone(form.cleaned_data['rf_channel_frequency'])
        self.assertIsNone(form.cleaned_data['rf_channel_width'])

    def test_poe_fields_nullable(self):
        """PoE-specific nullable fields should convert empty strings to None"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 15',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'poe_mode': '',  # nullable CharField
                'poe_type': '',  # nullable CharField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['poe_mode'])
        self.assertIsNone(form.cleaned_data['poe_type'])

    def test_wwn_field_nullable(self):
        """WWN field (special field type) should convert empty string to None"""
        form = InterfaceImportForm(
            data={
                'device': self.device,
                'name': 'Interface 16',
                'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
                'wwn': '',  # nullable WWNField
            }
        )
        self.assertTrue(form.is_valid(), f'Form errors: {form.errors}')
        self.assertIsNone(form.cleaned_data['wwn'])


class HTMXPartialSwapRenderingTestCase(TestCase):
    """
    Verify that each form field's HTMX swap wiring resolves to the widget actually bound to the
    field. An explicitly declared form field silently overrides a widget set via Meta.widgets, so
    a field can have HTMXSelect assigned in Meta yet end up with a plain widget carrying no HTMX
    wiring. Unit-testing the widget in isolation cannot see that, which is how the interface 802.1Q
    mode swap regressed unnoticed. These tests read the bound field's widget attrs directly so a
    shadowed field is caught.
    """
    # (form, bound field name, target fieldset id) — the field's change must swap only that fieldset.
    PARTIAL_SWAP_FIELDS = (
        (InterfaceForm, 'mode', 'dot1q-switching'),
        (VMInterfaceForm, 'mode', 'dot1q-switching'),
        (ModuleTypeForm, 'profile', 'profile-attributes'),
        (CableForm, 'a_terminations_type', 'cable-side-a'),
        (CableForm, 'b_terminations_type', 'cable-side-b'),
        (VLANGroupForm, 'scope', 'scope'),
        (ServiceForm, 'parent', 'service'),
        (CircuitTerminationForm, 'termination', 'circuit-termination'),
        (CircuitGroupAssignmentForm, 'member', 'circuit-group-assignment'),
        (TunnelCreateForm, 'termination1_type', 'tunnel-termination1'),
        (TunnelCreateForm, 'termination2_type', 'tunnel-termination2'),
        (TunnelTerminationForm, 'type', 'tunnel-termination'),
        (EventRuleForm, 'action_type', 'event-rule-action'),
        (ClusterForm, 'scope', 'scope'),
        (WirelessLANForm, 'scope', 'scope'),
        (PrefixForm, 'scope', 'scope'),
    )

    # These fields intentionally re-render the whole form rather than a single fieldset, because
    # changing them adds or removes entire fieldsets that a targeted swap would miss. The guard
    # ensures they keep targeting #form_fields and are not "optimized" into a partial swap that
    # would silently drop the added/removed fieldsets.
    FULL_FORM_FIELDS = (
        (CustomFieldForm, 'type'),
        (DataSourceForm, 'type'),
        (VirtualMachineForm, 'virtual_machine_type'),
    )

    @staticmethod
    def _hx_widget(field):
        """
        Return the HTMXSelect carrying the field's HTMX attrs. For a plain HTMXSelect field that is
        the field's own widget; for a generic-object selector (a MultiWidget) it is the HTMXSelect
        subwidget, located by type rather than position so a change in subwidget ordering can't
        silently select the wrong one.
        """
        widget = field.widget
        if isinstance(widget, forms.MultiWidget):
            return next(w for w in widget.widgets if isinstance(w, HTMXSelect))
        return widget

    def test_partial_swap_fields_target_their_fieldset(self):
        for form_class, field_name, target_id in self.PARTIAL_SWAP_FIELDS:
            with self.subTest(form=form_class.__name__, field=field_name):
                form = form_class()
                self.assertIn(field_name, form.fields)
                attrs = self._hx_widget(form.fields[field_name]).attrs
                # A verb (hx-get) is what actually issues the request; hx-target/hx-select alone
                # are inert. Its absence was the reported symptom ("changing mode fires no request").
                self.assertIn('hx-get', attrs)
                self.assertEqual(attrs.get('hx-select'), f'#{target_id}')
                self.assertEqual(attrs.get('hx-target'), f'#{target_id}')

    def test_interface_mode_retains_option_descriptions(self):
        # The mode field must keep its 802.1Q Mode option descriptions (a description-aware widget
        # feature) alongside the restored partial swap; the two must coexist on the same field.
        for form_class in (InterfaceForm, VMInterfaceForm):
            with self.subTest(form=form_class.__name__):
                self.assertTrue(form_class().fields['mode'].widget.descriptions)

    def test_full_form_fields_do_not_partial_swap(self):
        for form_class, field_name in self.FULL_FORM_FIELDS:
            with self.subTest(form=form_class.__name__, field=field_name):
                form = form_class()
                self.assertIn(field_name, form.fields)
                attrs = self._hx_widget(form.fields[field_name]).attrs
                self.assertIn('hx-get', attrs)
                self.assertEqual(attrs.get('hx-target'), '#form_fields')
                self.assertNotIn('hx-select', attrs)
