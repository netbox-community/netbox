from decimal import Decimal
from types import SimpleNamespace

from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from netaddr import IPNetwork

from account.models import UserToken
from circuits.choices import CircuitStatusChoices, VirtualCircuitTerminationRoleChoices
from circuits.models import (
    Provider,
    ProviderNetwork,
    VirtualCircuit,
    VirtualCircuitTermination,
    VirtualCircuitType,
)
from core.models import ConfigRevision, ObjectType
from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface, Region, Site
from netbox.ui import attrs
from netbox.ui.breadcrumbs import Breadcrumb
from netbox.ui.layout import SimpleLayout
from netbox.ui.panels import ObjectsTablePanel
from netbox.ui.utils import build_coords_url
from users.models import ObjectPermission, User
from utilities.testing import create_test_device
from utilities.views import get_view
from vpn.choices import (
    AuthenticationAlgorithmChoices,
    AuthenticationMethodChoices,
    DHGroupChoices,
    EncryptionAlgorithmChoices,
    IKEModeChoices,
    IKEVersionChoices,
    IPSecModeChoices,
)
from vpn.models import IKEPolicy, IKEProposal, IPSecPolicy, IPSecProfile


class ChoiceAttrTestCase(TestCase):
    """
    Test class for validating the behavior of ChoiceAttr attribute accessor.

    This test class verifies that the ChoiceAttr class correctly handles
    choice field attributes on Django model instances, including both direct
    field access and related object field access. It tests the retrieval of
    display values and associated context information such as color values
    for choice fields. The test data includes a network topology with devices,
    interfaces, providers, and virtual circuits to cover various scenarios of
    choice field access patterns.
    """

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        interface = Interface.objects.create(
            device=device,
            name='vlan.100',
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
        )

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(
            provider=provider,
            name='Provider Network 1',
        )
        virtual_circuit_type = VirtualCircuitType.objects.create(
            name='Virtual Circuit Type 1',
            slug='virtual-circuit-type-1',
        )
        virtual_circuit = VirtualCircuit.objects.create(
            cid='VC-100',
            provider_network=provider_network,
            type=virtual_circuit_type,
            status=CircuitStatusChoices.STATUS_ACTIVE,
        )

        cls.termination = VirtualCircuitTermination.objects.create(
            virtual_circuit=virtual_circuit,
            role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
            interface=interface,
        )

    def test_choice_attr_direct_accessor(self):
        attr = attrs.ChoiceAttr('role')

        self.assertEqual(
            attr.get_value(self.termination),
            self.termination.get_role_display(),
        )
        self.assertEqual(
            attr.get_context(self.termination, 'role', attr.get_value(self.termination), {}),
            {'bg_color': self.termination.get_role_color()},
        )

    def test_choice_attr_related_accessor(self):
        attr = attrs.ChoiceAttr('interface.type')

        self.assertEqual(
            attr.get_value(self.termination),
            self.termination.interface.get_type_display(),
        )
        self.assertEqual(
            attr.get_context(self.termination, 'interface.type', attr.get_value(self.termination), {}),
            {'bg_color': None},
        )

    def test_choice_attr_related_accessor_with_color(self):
        attr = attrs.ChoiceAttr('virtual_circuit.status')

        self.assertEqual(
            attr.get_value(self.termination),
            self.termination.virtual_circuit.get_status_display(),
        )
        self.assertEqual(
            attr.get_context(
                self.termination, 'virtual_circuit.status', attr.get_value(self.termination), {}
            ),
            {'bg_color': self.termination.virtual_circuit.get_status_color()},
        )


class RelatedObjectListAttrTestCase(TestCase):
    """
    Test suite for RelatedObjectListAttr functionality.

    This test class validates the behavior of the RelatedObjectListAttr class,
    which is used to render related objects as HTML lists. It tests various
    scenarios including direct accessor access, related accessor access through
    foreign keys, empty related object sets, and rendering with maximum item
    limits and overflow indicators. The tests use IKE and IPSec VPN policy
    models to verify proper rendering of one-to-many and many-to-many
    relationships between objects.
    """

    @classmethod
    def setUpTestData(cls):
        cls.proposals = (
            IKEProposal.objects.create(
                name='IKE Proposal 1',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14,
            ),
            IKEProposal.objects.create(
                name='IKE Proposal 2',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14,
            ),
            IKEProposal.objects.create(
                name='IKE Proposal 3',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14,
            ),
        )

        cls.ike_policy = IKEPolicy.objects.create(
            name='IKE Policy 1',
            version=IKEVersionChoices.VERSION_1,
            mode=IKEModeChoices.MAIN,
        )
        cls.ike_policy.proposals.set(cls.proposals)

        cls.empty_ike_policy = IKEPolicy.objects.create(
            name='IKE Policy 2',
            version=IKEVersionChoices.VERSION_1,
            mode=IKEModeChoices.MAIN,
        )

        cls.ipsec_policy = IPSecPolicy.objects.create(name='IPSec Policy 1')

        cls.profile = IPSecProfile.objects.create(
            name='IPSec Profile 1',
            mode=IPSecModeChoices.ESP,
            ike_policy=cls.ike_policy,
            ipsec_policy=cls.ipsec_policy,
        )
        cls.empty_profile = IPSecProfile.objects.create(
            name='IPSec Profile 2',
            mode=IPSecModeChoices.ESP,
            ike_policy=cls.empty_ike_policy,
            ipsec_policy=cls.ipsec_policy,
        )

    def test_related_object_list_attr_direct_accessor(self):
        attr = attrs.RelatedObjectListAttr('proposals', linkify=False)
        rendered = attr.render(self.ike_policy, {'name': 'proposals'})

        self.assertIn('list-unstyled mb-0', rendered)
        self.assertInHTML('<li>IKE Proposal 1</li>', rendered)
        self.assertInHTML('<li>IKE Proposal 2</li>', rendered)
        self.assertInHTML('<li>IKE Proposal 3</li>', rendered)
        self.assertEqual(rendered.count('<li'), 3)

    def test_related_object_list_attr_related_accessor(self):
        attr = attrs.RelatedObjectListAttr('ike_policy.proposals', linkify=False)
        rendered = attr.render(self.profile, {'name': 'proposals'})

        self.assertIn('list-unstyled mb-0', rendered)
        self.assertInHTML('<li>IKE Proposal 1</li>', rendered)
        self.assertInHTML('<li>IKE Proposal 2</li>', rendered)
        self.assertInHTML('<li>IKE Proposal 3</li>', rendered)
        self.assertEqual(rendered.count('<li'), 3)

    def test_related_object_list_attr_empty_related_accessor(self):
        attr = attrs.RelatedObjectListAttr('ike_policy.proposals', linkify=False)

        self.assertEqual(
            attr.render(self.empty_profile, {'name': 'proposals'}),
            attr.placeholder,
        )

    def test_related_object_list_attr_max_items(self):
        attr = attrs.RelatedObjectListAttr(
            'ike_policy.proposals',
            linkify=False,
            max_items=2,
            overflow_indicator='…',
        )
        rendered = attr.render(self.profile, {'name': 'proposals'})

        self.assertInHTML('<li>IKE Proposal 1</li>', rendered)
        self.assertInHTML('<li>IKE Proposal 2</li>', rendered)
        self.assertNotIn('IKE Proposal 3', rendered)
        self.assertIn('…', rendered)


class TextAttrTestCase(TestCase):

    def test_get_value_with_format_string(self):
        attr = attrs.TextAttr('asn', format_string='AS{}')
        obj = SimpleNamespace(asn=65000)
        self.assertEqual(attr.get_value(obj), 'AS65000')

    def test_get_value_without_format_string(self):
        attr = attrs.TextAttr('name')
        obj = SimpleNamespace(name='foo')
        self.assertEqual(attr.get_value(obj), 'foo')

    def test_get_value_none_skips_format_string(self):
        attr = attrs.TextAttr('name', format_string='prefix-{}')
        obj = SimpleNamespace(name=None)
        self.assertIsNone(attr.get_value(obj))

    def test_get_context(self):
        attr = attrs.TextAttr('name', style='text-monospace', copy_button=True)
        obj = SimpleNamespace(name='bar')
        context = attr.get_context(obj, 'name', 'bar', {})
        self.assertEqual(context['style'], 'text-monospace')
        self.assertTrue(context['copy_button'])


class ArrayAttrTestCase(TestCase):

    def test_get_value(self):
        attr = attrs.ArrayAttr('allowed_ips')
        obj = SimpleNamespace(allowed_ips=[IPNetwork('192.168.1.1/32'), IPNetwork('2001:db8::/64')])
        self.assertEqual(attr.get_value(obj), '192.168.1.1/32, 2001:db8::/64')

    def test_get_value_empty(self):
        attr = attrs.ArrayAttr('allowed_ips')
        obj = SimpleNamespace(allowed_ips=[])
        self.assertIsNone(attr.get_value(obj))

    def test_get_value_none(self):
        attr = attrs.ArrayAttr('allowed_ips')
        obj = SimpleNamespace(allowed_ips=None)
        self.assertIsNone(attr.get_value(obj))

    def test_get_value_with_format_string(self):
        attr = attrs.ArrayAttr('ports', format_string='{}/tcp')
        obj = SimpleNamespace(ports=[80, 443])
        self.assertEqual(attr.get_value(obj), '80/tcp, 443/tcp')


class NumericAttrTestCase(TestCase):

    def test_get_context_with_unit_accessor(self):
        attr = attrs.NumericAttr('speed', unit_accessor='speed_unit')
        obj = SimpleNamespace(speed=1000, speed_unit='Mbps')
        context = attr.get_context(obj, 'speed', 1000, {})
        self.assertEqual(context['unit'], 'Mbps')

    def test_get_context_without_unit_accessor(self):
        attr = attrs.NumericAttr('speed')
        obj = SimpleNamespace(speed=1000)
        context = attr.get_context(obj, 'speed', 1000, {})
        self.assertIsNone(context['unit'])

    def test_get_context_copy_button(self):
        attr = attrs.NumericAttr('speed', copy_button=True)
        obj = SimpleNamespace(speed=1000)
        context = attr.get_context(obj, 'speed', 1000, {})
        self.assertTrue(context['copy_button'])


class BooleanAttrTestCase(TestCase):

    def test_false_value_shown_by_default(self):
        attr = attrs.BooleanAttr('enabled')
        obj = SimpleNamespace(enabled=False)
        self.assertIs(attr.get_value(obj), False)

    def test_false_value_hidden_when_display_false_disabled(self):
        attr = attrs.BooleanAttr('enabled', display_false=False)
        obj = SimpleNamespace(enabled=False)
        self.assertIsNone(attr.get_value(obj))

    def test_true_value_always_shown(self):
        attr = attrs.BooleanAttr('enabled', display_false=False)
        obj = SimpleNamespace(enabled=True)
        self.assertIs(attr.get_value(obj), True)


class ImageAttrTestCase(TestCase):

    def test_invalid_decoding_raises_value_error(self):
        with self.assertRaises(ValueError):
            attrs.ImageAttr('image', decoding='invalid')

    def test_default_decoding_for_lazy_image(self):
        attr = attrs.ImageAttr('image')
        self.assertTrue(attr.load_lazy)
        self.assertEqual(attr.decoding, 'async')

    def test_default_decoding_for_non_lazy_image(self):
        attr = attrs.ImageAttr('image', load_lazy=False)
        self.assertFalse(attr.load_lazy)
        self.assertIsNone(attr.decoding)

    def test_explicit_decoding_value(self):
        attr = attrs.ImageAttr('image', load_lazy=False, decoding='sync')
        self.assertEqual(attr.decoding, 'sync')

    def test_get_context(self):
        attr = attrs.ImageAttr('image', load_lazy=False, decoding='async')
        obj = SimpleNamespace(image='test.png')
        context = attr.get_context(obj, 'image', 'test.png', {})
        self.assertEqual(context['decoding'], 'async')
        self.assertFalse(context['load_lazy'])


class RelatedObjectAttrTestCase(TestCase):

    def test_get_context_with_grouped_by(self):
        region = SimpleNamespace(name='Region 1')
        site = SimpleNamespace(name='Site 1', region=region)
        obj = SimpleNamespace(site=site)
        attr = attrs.RelatedObjectAttr('site', grouped_by='region')
        context = attr.get_context(obj, 'site', site, {})
        self.assertEqual(context['group'], region)

    def test_get_context_without_grouped_by(self):
        site = SimpleNamespace(name='Site 1')
        obj = SimpleNamespace(site=site)
        attr = attrs.RelatedObjectAttr('site')
        context = attr.get_context(obj, 'site', site, {})
        self.assertIsNone(context['group'])

    def test_get_context_linkify(self):
        site = SimpleNamespace(name='Site 1')
        obj = SimpleNamespace(site=site)
        attr = attrs.RelatedObjectAttr('site', linkify=True)
        context = attr.get_context(obj, 'site', site, {})
        self.assertTrue(context['linkify'])


class GenericForeignKeyAttrTestCase(TestCase):

    class TreeNode:
        def __init__(self, name, ancestors=()):
            self.name = name
            self.ancestors = list(ancestors)
            self.include_self = None
            self._meta = SimpleNamespace(verbose_name='location')

        def __str__(self):
            return self.name

        def get_ancestors(self, include_self=False):
            self.include_self = include_self

            if include_self:
                return [*self.ancestors, self]
            return self.ancestors

    def test_get_context_content_type(self):
        value = SimpleNamespace(_meta=SimpleNamespace(verbose_name='provider'))
        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object')
        context = attr.get_context(obj, 'assigned_object', value, {})
        self.assertEqual(context['content_type'], 'provider')

    def test_get_context_linkify(self):
        value = SimpleNamespace(_meta=SimpleNamespace(verbose_name='provider'))
        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object', linkify=True)
        context = attr.get_context(obj, 'assigned_object', value, {})
        self.assertTrue(context['linkify'])

    def test_get_context_nested_disabled(self):
        root = self.TreeNode('Root')
        child = self.TreeNode('Child', ancestors=[root])

        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object')
        context = attr.get_context(obj, 'assigned_object', child, {})

        self.assertIsNone(context['nodes'])

    def test_get_context_nested_non_hierarchical_object(self):
        value = SimpleNamespace(_meta=SimpleNamespace(verbose_name='site'))
        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object', nested=True)
        context = attr.get_context(obj, 'assigned_object', value, {})

        self.assertIsNone(context['nodes'])

    def test_get_context_nested_hierarchical_object(self):
        root = self.TreeNode('Root')
        parent = self.TreeNode('Parent', ancestors=[root])
        child = self.TreeNode('Child', ancestors=[root, parent])

        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object', nested=True)
        context = attr.get_context(obj, 'assigned_object', child, {})

        self.assertEqual(context['nodes'], [root, parent, child])
        self.assertTrue(child.include_self)

    def test_get_context_nested_max_depth(self):
        root = self.TreeNode('Root')
        parent = self.TreeNode('Parent', ancestors=[root])
        child = self.TreeNode('Child', ancestors=[root, parent])

        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object', nested=True, max_depth=2)
        context = attr.get_context(obj, 'assigned_object', child, {})

        self.assertEqual(context['nodes'], [parent, child])

    def test_get_context_nested_null_value(self):
        obj = SimpleNamespace()
        attr = attrs.GenericForeignKeyAttr('assigned_object', nested=True)
        context = attr.get_context(obj, 'assigned_object', None, {})

        self.assertIsNone(context['content_type'])
        self.assertIsNone(context['nodes'])


class GPSCoordinatesAttrTestCase(TestCase):

    def test_missing_latitude_returns_placeholder(self):
        attr = attrs.GPSCoordinatesAttr()
        obj = SimpleNamespace(latitude=None, longitude=-74.006)
        self.assertEqual(attr.render(obj, {'name': 'coordinates'}), attr.placeholder)

    def test_missing_longitude_returns_placeholder(self):
        attr = attrs.GPSCoordinatesAttr()
        obj = SimpleNamespace(latitude=40.712, longitude=None)
        self.assertEqual(attr.render(obj, {'name': 'coordinates'}), attr.placeholder)

    def test_both_missing_returns_placeholder(self):
        attr = attrs.GPSCoordinatesAttr()
        obj = SimpleNamespace(latitude=None, longitude=None)
        self.assertEqual(attr.render(obj, {'name': 'coordinates'}), attr.placeholder)

    def test_build_coords_url_legacy_prefix(self):
        url = build_coords_url('https://maps.google.com/?q=', 48.858, 2.294)
        self.assertEqual(url, 'https://maps.google.com/?q=48.858,2.294')

    def test_build_coords_url_lat_lon_placeholders(self):
        url = build_coords_url(
            'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}',
            48.858,
            2.294,
        )
        self.assertEqual(url, 'https://www.openstreetmap.org/?mlat=48.858&mlon=2.294#map=16/48.858/2.294')

    def test_build_coords_url_lat_placeholder_only(self):
        url = build_coords_url('https://example.com/?lat={lat}', 48.858, 2.294)
        self.assertEqual(url, 'https://example.com/?lat=48.858')

    def test_build_coords_url_lon_placeholder_only(self):
        url = build_coords_url('https://example.com/?lon={lon}', 48.858, 2.294)
        self.assertEqual(url, 'https://example.com/?lon=2.294')

    def test_build_coords_url_unknown_placeholder_falls_back_to_legacy(self):
        # URL with only an unknown placeholder (no {lat}/{lon}) → legacy append
        url = build_coords_url('https://example.com/?q={unknown}', 48.858, 2.294)
        self.assertEqual(url, 'https://example.com/?q={unknown}48.858,2.294')

    def test_build_coords_url_known_and_unknown_placeholder(self):
        # {lat} is substituted; unknown key is left as a literal placeholder
        url = build_coords_url(
            'https://example.com/?lat={lat}&layer={layer}', 48.858, 2.294
        )
        self.assertEqual(url, 'https://example.com/?lat=48.858&layer={layer}')

    def test_build_coords_url_decimal_values_no_locale_separator(self):
        # Decimal field values must format with '.' as the decimal separator regardless of locale;
        # a locale-style comma separator would produce e.g. '48,858258' and break the URL
        url = build_coords_url(
            'https://maps.google.com/?q=',
            Decimal('48.858258'),
            Decimal('2.294498'),
        )
        self.assertEqual(url, 'https://maps.google.com/?q=48.858258,2.294498')

    def test_build_coords_url_decimal_with_placeholders_no_locale_separator(self):
        url = build_coords_url(
            'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}',
            Decimal('48.858258'),
            Decimal('2.294498'),
        )
        self.assertEqual(url, 'https://www.openstreetmap.org/?mlat=48.858258&mlon=2.294498')


class AddressAttrTestCase(TestCase):

    def test_plain_prefix_map_url_is_passed_through(self):
        attr = attrs.AddressAttr('address', map_url='https://maps.google.com/?q=')
        obj = SimpleNamespace(address='1 Main St')
        context = attr.get_context(obj, 'address', '1 Main St', {})
        self.assertEqual(context['map_url'], 'https://maps.google.com/?q=')

    def test_gps_format_map_url_is_suppressed_for_addresses(self):
        # A GPS-format URL cannot render address links; map_url should be None
        attr = attrs.AddressAttr('address', map_url='https://maps.example.com/?mlat={lat}&mlon={lon}')
        obj = SimpleNamespace(address='1 Main St')
        context = attr.get_context(obj, 'address', '1 Main St', {})
        self.assertIsNone(context['map_url'])

    def test_no_map_url(self):
        attr = attrs.AddressAttr('address', map_url=False)
        obj = SimpleNamespace(address='1 Main St')
        context = attr.get_context(obj, 'address', '1 Main St', {})
        self.assertIsNone(context['map_url'])


class DateTimeAttrTestCase(TestCase):

    def test_default_spec(self):
        attr = attrs.DateTimeAttr('created')
        obj = SimpleNamespace(created='2024-01-01')
        context = attr.get_context(obj, 'created', '2024-01-01', {})
        self.assertEqual(context['spec'], 'seconds')

    def test_date_spec(self):
        attr = attrs.DateTimeAttr('created', spec='date')
        obj = SimpleNamespace(created='2024-01-01')
        context = attr.get_context(obj, 'created', '2024-01-01', {})
        self.assertEqual(context['spec'], 'date')

    def test_minutes_spec(self):
        attr = attrs.DateTimeAttr('created', spec='minutes')
        obj = SimpleNamespace(created='2024-01-01')
        context = attr.get_context(obj, 'created', '2024-01-01', {})
        self.assertEqual(context['spec'], 'minutes')


class WeightAttrTestCase(SimpleTestCase):

    def _ctx(self, system=''):
        return {'name': 'weight', 'preferences': {'ui.measurement_system': system}}

    def _obj(self, weight, unit, abs_g, display=None):
        display_fn = (lambda: display) if display else (lambda: unit)
        return SimpleNamespace(
            weight=weight,
            weight_unit=unit,
            _abs_weight=abs_g,
            get_weight_unit_display=display_fn,
        )

    def test_none_returns_placeholder(self):
        attr = attrs.WeightAttr('weight')
        obj = SimpleNamespace(weight=None)
        self.assertEqual(attr.render(obj, self._ctx()), attr.placeholder)

    def test_inherit_shows_stored_value(self):
        attr = attrs.WeightAttr('weight')
        obj = self._obj(5, 'kg', 5000, 'Kilograms')
        result = attr.render(obj, self._ctx(system=''))
        self.assertIn('5', result)
        self.assertIn('kg', result)

    def test_metric_converts_lbs_to_kg(self):
        # 10 lb = 4535.92 g → 4535.92 / 1000 = 4.54 kg
        attr = attrs.WeightAttr('weight')
        obj = self._obj(10, 'lb', 4535.92, 'Pounds')
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('4.54', result)
        self.assertIn('kg', result)

    def test_metric_no_conversion_for_metric_unit(self):
        attr = attrs.WeightAttr('weight')
        obj = self._obj(5, 'kg', 5000, 'Kilograms')
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('5', result)
        self.assertIn('kg', result)

    def test_imperial_converts_kg_to_lbs(self):
        # 1 kg = 1000 g → 1000 / 453.592 = 2.2 lbs
        attr = attrs.WeightAttr('weight')
        obj = self._obj(1, 'kg', 1000, 'Kilograms')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('2.2', result)
        self.assertIn('lbs', result)

    def test_imperial_converts_kg_to_singular_lb(self):
        # 453.592 g = exactly 1.0 lb → singular 'lb'
        attr = attrs.WeightAttr('weight')
        obj = self._obj(1, 'kg', 453.592, 'Kilograms')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('1.0', result)
        self.assertIn('lb', result)
        self.assertNotIn('lbs', result)

    def test_imperial_no_conversion_for_imperial_unit(self):
        attr = attrs.WeightAttr('weight')
        obj = self._obj(10, 'lb', 4535.92, 'Pounds')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('10', result)
        self.assertIn('lbs', result)

    def test_metric_no_conversion_when_abs_weight_is_none(self):
        # abs_weight=None → falsy → falls through to stored value
        attr = attrs.WeightAttr('weight')
        obj = SimpleNamespace(weight=10, weight_unit='lb', _abs_weight=None)
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('10', result)
        self.assertIn('lbs', result)


class DistanceAttrTestCase(SimpleTestCase):

    def _ctx(self, system=''):
        return {'name': 'distance', 'preferences': {'ui.measurement_system': system}}

    def _obj(self, distance, unit, abs_m, display=None):
        display_fn = (lambda: display) if display else (lambda: unit)
        return SimpleNamespace(
            distance=distance,
            distance_unit=unit,
            _abs_distance=abs_m,
            get_distance_unit_display=display_fn,
        )

    def test_none_returns_placeholder(self):
        attr = attrs.DistanceAttr('distance')
        obj = SimpleNamespace(distance=None)
        self.assertEqual(attr.render(obj, self._ctx()), attr.placeholder)

    def test_inherit_shows_stored_value(self):
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(10, 'km', 10000, 'Kilometers')
        result = attr.render(obj, self._ctx(system=''))
        self.assertIn('10', result)
        self.assertIn('km', result)

    def test_metric_converts_ft_to_m_under_threshold(self):
        # 500 ft = 152.4 m (< 1000) → display in m
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(500, 'ft', 152.4, 'Feet')
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('152.4', result)
        self.assertNotIn('km', result)
        self.assertIn('m', result)

    def test_metric_converts_mi_to_km_over_threshold(self):
        # 5 mi = 8046.72 m (>= 1000) → 8046.72 / 1000 = 8.05 km
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(5, 'mi', 8046.72, 'Miles')
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('8.05', result)
        self.assertIn('km', result)

    def test_imperial_converts_m_to_ft_under_threshold(self):
        # 500 m (< 1609.344) → 500 / 0.3048 = 1640.42 ft
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(500, 'm', 500, 'Meters')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('1640.42', result)
        self.assertIn('ft', result)

    def test_imperial_converts_km_to_mi_over_threshold(self):
        # 10 km = 10000 m (>= 1609.344) → 10000 / 1609.344 = 6.21 mi
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(10, 'km', 10000, 'Kilometers')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('6.21', result)
        self.assertIn('mi', result)

    def test_metric_no_conversion_for_metric_unit(self):
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(10, 'km', 10000, 'Kilometers')
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('10', result)
        self.assertIn('km', result)

    def test_imperial_no_conversion_for_imperial_unit(self):
        attr = attrs.DistanceAttr('distance')
        obj = self._obj(10, 'mi', 16093.44, 'Miles')
        result = attr.render(obj, self._ctx(system='imperial'))
        self.assertIn('10', result)
        self.assertIn('mi', result)

    def test_metric_no_conversion_when_abs_distance_is_none(self):
        # abs_distance=None → falls through to stored value
        attr = attrs.DistanceAttr('distance')
        obj = SimpleNamespace(distance=10, distance_unit='ft', _abs_distance=None)
        result = attr.render(obj, self._ctx(system='metric'))
        self.assertIn('10', result)
        self.assertIn('ft', result)


class DisplayWeightTagTestCase(SimpleTestCase):
    TEMPLATE = Template('{% load helpers %}{% display_weight weight weight_unit abs_weight %}')

    def _render(self, weight, weight_unit, abs_weight, system=''):
        ctx = Context({
            'preferences': {'ui.measurement_system': system},
            'weight': weight,
            'weight_unit': weight_unit,
            'abs_weight': abs_weight,
        })
        return self.TEMPLATE.render(ctx).strip()

    def test_none_weight_returns_empty(self):
        self.assertEqual(self._render(None, 'kg', None), '')

    def test_zero_weight_is_not_suppressed(self):
        self.assertEqual(self._render(0, 'kg', 0), '0 kg')

    def test_inherit_stores_kg(self):
        self.assertEqual(self._render(5, 'kg', 5000), '5 kg')

    def test_inherit_stores_lb_plural(self):
        self.assertEqual(self._render(10, 'lb', 4535.92), '10 lbs')

    def test_inherit_stores_lb_singular(self):
        self.assertEqual(self._render(1, 'lb', 453.592), '1 lb')

    def test_metric_converts_lb_to_kg(self):
        # 10 lb = 4535.92 g → round(4535.92/1000, 2) = 4.54 kg
        result = self._render(10, 'lb', 4535.92, system='metric')
        self.assertEqual(result, '4.54 kg')

    def test_imperial_converts_kg_to_lbs(self):
        # 1 kg = 1000 g → round(1000/453.592, 2) = 2.2 lbs
        result = self._render(1, 'kg', 1000, system='imperial')
        self.assertEqual(result, '2.2 lbs')

    def test_imperial_converts_kg_to_singular_lb(self):
        # 453.592 g = 1.0 lb → singular
        result = self._render(1, 'kg', 453.592, system='imperial')
        self.assertEqual(result, '1 lb')

    def test_metric_no_conversion_for_metric_unit(self):
        result = self._render(5, 'kg', 5000, system='metric')
        self.assertEqual(result, '5 kg')

    def test_imperial_no_conversion_for_imperial_unit(self):
        result = self._render(10, 'lb', 4535.92, system='imperial')
        self.assertEqual(result, '10 lbs')


class DisplayDistanceTagTestCase(SimpleTestCase):
    TEMPLATE = Template('{% load helpers %}{% display_distance distance distance_unit abs_distance %}')

    def _render(self, distance, distance_unit, abs_distance, system=''):
        ctx = Context({
            'preferences': {'ui.measurement_system': system},
            'distance': distance,
            'distance_unit': distance_unit,
            'abs_distance': abs_distance,
        })
        return self.TEMPLATE.render(ctx).strip()

    def test_none_distance_returns_empty(self):
        self.assertEqual(self._render(None, 'km', None), '')

    def test_inherit_stores_km(self):
        self.assertEqual(self._render(10, 'km', 10000), '10 km')

    def test_metric_converts_ft_to_m_under_threshold(self):
        # 500 ft = 152.4 m (< 1000)
        self.assertEqual(self._render(500, 'ft', 152.4, system='metric'), '152.4 m')

    def test_metric_converts_mi_to_km_over_threshold(self):
        # 5 mi = 8046.72 m (>= 1000) → 8.05 km
        self.assertEqual(self._render(5, 'mi', 8046.72, system='metric'), '8.05 km')

    def test_imperial_converts_m_to_ft_under_threshold(self):
        # 500 m (< 1609.344) → 500/0.3048 = 1640.42 ft
        self.assertEqual(self._render(500, 'm', 500, system='imperial'), '1640.42 ft')

    def test_imperial_converts_km_to_mi_over_threshold(self):
        # 10 km = 10000 m (>= 1609.344) → 6.21 mi
        self.assertEqual(self._render(10, 'km', 10000, system='imperial'), '6.21 mi')

    def test_metric_no_conversion_for_metric_unit(self):
        self.assertEqual(self._render(10, 'km', 10000, system='metric'), '10 km')

    def test_imperial_no_conversion_for_imperial_unit(self):
        self.assertEqual(self._render(10, 'mi', 16093.44, system='imperial'), '10 mi')


class ObjectsTablePanelTestCase(TestCase):
    """
    Verify that ObjectsTablePanel.should_render() hides the panel when
    the requesting user lacks view permission for the panel's model.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test_user', password='test_password')

        # Grant view permission only for Site
        obj_perm = ObjectPermission.objects.create(
            name='View sites only',
            actions=['view'],
        )
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Site))
        obj_perm.users.add(cls.user)

    def setUp(self):
        self.factory = RequestFactory()
        self.panel = ObjectsTablePanel(model='dcim.site')
        self.panel_no_perm = ObjectsTablePanel(model='dcim.location')

    def _make_context(self, user=None):
        if user is None:
            return {}
        request = self.factory.get('/')
        request.user = user
        return {'request': request}

    def test_should_render_without_request(self):
        """
        Panel should render when no request is present in context.
        """
        context = self.panel.get_context({})
        self.assertTrue(self.panel.should_render(context))

    def test_should_render_with_permission(self):
        """
        Panel should render when the user has view permission for the panel's model.
        """
        context = self.panel.get_context(self._make_context(self.user))
        self.assertTrue(self.panel.should_render(context))

    def test_should_not_render_without_permission(self):
        """
        Panel should be hidden when the user lacks view permission for the panel's model.
        """
        context = self.panel_no_perm.get_context(self._make_context(self.user))
        self.assertFalse(self.panel_no_perm.should_render(context))


class BreadcrumbTestCase(SimpleTestCase):
    """
    Validate the rendering behavior of the Breadcrumb class.
    """
    class _LinkedObject:
        def __init__(self, label, url, pk=None):
            self.label = label
            self._url = url
            self.pk = pk

        def __str__(self):
            return self.label

        def get_absolute_url(self):
            return self._url

    class _PlainObject:
        def __str__(self):
            return 'Plain'

    @staticmethod
    def _render(breadcrumb, instance):
        return breadcrumb.render({'object': instance})

    def test_accessor_absolute_url(self):
        """
        A string accessor resolves the related object, which links to its get_absolute_url() by default.
        """
        instance = SimpleNamespace(region=self._LinkedObject('Region 1', '/region/1/'))
        html = self._render(Breadcrumb('region'), instance)
        self.assertInHTML('<li class="breadcrumb-item"><a href="/region/1/">Region 1</a></li>', html)

    def test_explicit_url_string(self):
        """
        An explicit url string overrides the resolved object's get_absolute_url().
        """
        instance = SimpleNamespace(region=self._LinkedObject('Region 1', '/region/1/'))
        html = self._render(Breadcrumb('region', url='/explicit/'), instance)
        self.assertInHTML('<li class="breadcrumb-item"><a href="/explicit/">Region 1</a></li>', html)

    def test_url_callable(self):
        """
        A callable url is invoked with the resolved object.
        """
        instance = SimpleNamespace(region=self._LinkedObject('Region 1', '/region/1/', pk=7))
        html = self._render(Breadcrumb('region', url=lambda o: f'/list/?region_id={o.pk}'), instance)
        self.assertInHTML('<li class="breadcrumb-item"><a href="/list/?region_id=7">Region 1</a></li>', html)

    def test_callable_accessor_iterable(self):
        """
        A callable accessor resolving to an iterable renders one breadcrumb per object.
        """
        a = self._LinkedObject('A', '/a/')
        b = self._LinkedObject('B', '/b/')
        html = self._render(Breadcrumb(lambda o: [a, b]), SimpleNamespace())
        self.assertInHTML('<li class="breadcrumb-item"><a href="/a/">A</a></li>', html)
        self.assertInHTML('<li class="breadcrumb-item"><a href="/b/">B</a></li>', html)

    def test_no_link(self):
        """
        An object with neither an explicit url nor get_absolute_url() renders as a plain label.
        """
        html = self._render(Breadcrumb('thing'), SimpleNamespace(thing=self._PlainObject()))
        self.assertNotIn('<a', html)
        self.assertInHTML('<li class="breadcrumb-item">Plain</li>', html)

    def test_unresolved_accessor(self):
        """
        A breadcrumb whose accessor resolves to None renders as an empty string (and is therefore omitted).
        """
        self.assertEqual(self._render(Breadcrumb('region'), SimpleNamespace(region=None)), '')

    def test_empty_iterable(self):
        """
        A callable accessor resolving to an empty iterable renders as an empty string.
        """
        self.assertEqual(self._render(Breadcrumb(lambda o: []), SimpleNamespace()), '')

    def test_no_instance(self):
        """
        With no object in context, the breadcrumb renders as an empty string.
        """
        self.assertEqual(Breadcrumb('region').render({}), '')

    def test_static_label_linked(self):
        """
        A breadcrumb with a static label and explicit url renders a single fixed crumb, independent of the object.
        """
        html = self._render(Breadcrumb(label='My API Tokens', url='/account/tokens/'), SimpleNamespace())
        self.assertInHTML('<li class="breadcrumb-item"><a href="/account/tokens/">My API Tokens</a></li>', html)

    def test_static_label_no_instance(self):
        """
        A static breadcrumb renders even with no object in context.
        """
        html = Breadcrumb(label='My API Tokens', url='/account/tokens/').render({})
        self.assertInHTML('<li class="breadcrumb-item"><a href="/account/tokens/">My API Tokens</a></li>', html)

    def test_static_label_unlinked(self):
        """
        A static breadcrumb without a url renders as a plain label and does not fall back to the object's URL.
        """
        instance = self._LinkedObject('Token', '/account/tokens/1/')
        html = self._render(Breadcrumb(label='My API Tokens'), instance)
        self.assertNotIn('<a', html)
        self.assertInHTML('<li class="breadcrumb-item">My API Tokens</li>', html)

    def test_callable_label_static(self):
        """
        An accessor-less breadcrumb may derive its label from the viewed instance via a callable.
        """
        instance = SimpleNamespace(unit_list='1-5')
        html = self._render(Breadcrumb(label=lambda o: f'Units {o.unit_list}'), instance)
        self.assertNotIn('<a', html)
        self.assertInHTML('<li class="breadcrumb-item">Units 1-5</li>', html)

    def test_callable_label_with_accessor(self):
        """
        With an accessor, a callable label receives the resolved related object (overriding its string value).
        """
        instance = SimpleNamespace(rack=self._LinkedObject('Rack 1', '/rack/1/'))
        html = self._render(Breadcrumb('rack', label=lambda o: f'Rack: {o}'), instance)
        self.assertInHTML('<li class="breadcrumb-item"><a href="/rack/1/">Rack: Rack 1</a></li>', html)

    def test_no_accessor_or_label_raises(self):
        """
        A breadcrumb must define either an accessor or a static label.
        """
        with self.assertRaises(ValueError):
            Breadcrumb()


class LayoutBreadcrumbsTestCase(SimpleTestCase):
    """
    Validate that a layout stores and validates the breadcrumbs declared on it.
    """
    def test_breadcrumbs_stored(self):
        crumbs = [Breadcrumb('region'), Breadcrumb('group')]
        self.assertEqual(SimpleLayout(breadcrumbs=crumbs).breadcrumbs, crumbs)

    def test_breadcrumbs_default_empty(self):
        self.assertEqual(SimpleLayout().breadcrumbs, [])

    def test_invalid_breadcrumb_raises(self):
        with self.assertRaises(TypeError):
            SimpleLayout(breadcrumbs=['not a breadcrumb'])

    def test_root_breadcrumb_default_true(self):
        self.assertTrue(SimpleLayout().root_breadcrumb)

    def test_root_breadcrumb_opt_out(self):
        self.assertFalse(SimpleLayout(root_breadcrumb=False).root_breadcrumb)


class GetViewTestCase(SimpleTestCase):
    """
    Validate the get_view() utility used to resolve a model's registered views.
    """
    def test_base_view(self):
        view = get_view(Site)
        self.assertIsNotNone(view)
        self.assertEqual(view.queryset.model, Site)

    def test_accepts_instance(self):
        # A model instance resolves to the same view as its class
        self.assertIs(get_view(Site(name='Site 1')), get_view(Site))

    def test_unknown_name_returns_none(self):
        self.assertIsNone(get_view(Site, 'this-view-does-not-exist'))


class RenderBreadcrumbsTagTestCase(SimpleTestCase):
    """
    Validate the render_breadcrumbs template tag's handling of objects without a breadcrumb trail.
    """
    @staticmethod
    def _render(obj):
        template = Template('{% render_breadcrumbs %}')
        return template.render(Context({'object': obj}))

    def test_none_object(self):
        self.assertEqual(self._render(None), '')

    def test_non_model_object(self):
        # An object lacking _meta (e.g. an RQ worker) must not raise
        self.assertEqual(self._render(SimpleNamespace(name='not a model')), '')

    def test_default_root_breadcrumb(self):
        # A model whose base view declares no custom breadcrumbs still renders the default root crumb:
        # a link to its list view, labeled with the model's plural name.
        html = self._render(ObjectPermission())
        self.assertInHTML('<li class="breadcrumb-item"><a href="/users/permissions/">Permissions</a></li>', html)

    def test_opt_out_root_breadcrumb(self):
        # A layout with root_breadcrumb=False suppresses the default root crumb, leaving only its own
        # breadcrumbs (here UserTokenView's static "My API Tokens" crumb) to stand in its place.
        html = self._render(UserToken())
        self.assertEqual(html.count('breadcrumb-item'), 1)
        self.assertInHTML(
            f'<li class="breadcrumb-item"><a href="{reverse("account:usertoken_list")}">My API Tokens</a></li>', html
        )

    def test_opt_out_without_breadcrumbs(self):
        # A layout with root_breadcrumb=False and no breadcrumbs of its own (e.g. ConfigRevisionView) renders
        # an empty trail.
        self.assertEqual(self._render(ConfigRevision()), '')


class RenderBreadcrumbsTagRenderTestCase(TestCase):
    """
    Validate that the render_breadcrumbs tag resolves and renders the trail declared on a model's base view layout.
    """
    @staticmethod
    def _render(instance):
        template = Template('{% render_breadcrumbs %}')
        return template.render(Context({'object': instance}))

    def test_region_ancestor_breadcrumbs(self):
        grandparent = Region.objects.create(name='Grandparent Region', slug='grandparent-region')
        parent = Region.objects.create(name='Parent Region', slug='parent-region', parent=grandparent)
        child = Region.objects.create(name='Child Region', slug='child-region', parent=parent)

        html = self._render(child)
        list_url = reverse('dcim:region_list')
        # The default root crumb is rendered ahead of the layout-defined ancestor crumbs
        self.assertInHTML(f'<li class="breadcrumb-item"><a href="{list_url}">Regions</a></li>', html)
        self.assertInHTML(
            f'<li class="breadcrumb-item"><a href="{list_url}?parent_id={grandparent.pk}">{grandparent}</a></li>', html
        )
        self.assertInHTML(
            f'<li class="breadcrumb-item"><a href="{list_url}?parent_id={parent.pk}">{parent}</a></li>', html
        )

    def test_region_without_ancestors(self):
        # A top-level object's ancestor accessor resolves to an empty queryset, leaving only the default root crumb
        region = Region.objects.create(name='Top Region', slug='top-region')
        html = self._render(region)
        self.assertEqual(html.count('breadcrumb-item'), 1)
        self.assertInHTML(
            f'<li class="breadcrumb-item"><a href="{reverse("dcim:region_list")}">Regions</a></li>', html
        )
