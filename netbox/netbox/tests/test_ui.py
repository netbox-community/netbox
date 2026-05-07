from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from circuits.choices import CircuitStatusChoices, VirtualCircuitTerminationRoleChoices
from circuits.models import (
    Provider,
    ProviderNetwork,
    VirtualCircuit,
    VirtualCircuitTermination,
    VirtualCircuitType,
)
from core.models import ObjectType
from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface, Site
from netbox.ui import attrs
from netbox.ui.panels import ObjectsTablePanel
from users.models import ObjectPermission, User
from utilities.testing import create_test_device
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


class ChoiceAttrTest(TestCase):
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


class RelatedObjectListAttrTest(TestCase):
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


class TextAttrTest(TestCase):

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


class NumericAttrTest(TestCase):

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


class BooleanAttrTest(TestCase):

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


class ImageAttrTest(TestCase):

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


class RelatedObjectAttrTest(TestCase):

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


class GenericForeignKeyAttrTest(TestCase):

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


class GPSCoordinatesAttrTest(TestCase):

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


class DateTimeAttrTest(TestCase):

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


class ObjectsTablePanelTest(TestCase):
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
