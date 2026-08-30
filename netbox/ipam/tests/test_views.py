import datetime
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import RequestFactory
from django.urls import reverse
from netaddr import IPNetwork

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange, ObjectType
from dcim.constants import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField, SavedFilter
from ipam import filtersets
from ipam.choices import *
from ipam.models import *
from ipam.utils import AvailableIPSpace
from ipam.views import AggregatePrefixesView, PrefixPrefixesView
from netbox.choices import CSVDelimiterChoices, ImportFormatChoices
from tenancy.models import Tenant
from users.models import Group, ObjectPermission, Owner
from utilities.testing import ViewTestCases, create_tags


class ASNRangeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ASNRange

    @classmethod
    def setUpTestData(cls):
        rirs = [
            RIR(name='RIR 1', slug='rir-1', is_private=True),
            RIR(name='RIR 2', slug='rir-2', is_private=True),
        ]
        RIR.objects.bulk_create(rirs)

        tenants = [
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
        ]
        Tenant.objects.bulk_create(tenants)

        asn_ranges = (
            ASNRange(name='ASN Range 1', slug='asn-range-1', rir=rirs[0], tenant=tenants[0], start=100, end=199),
            ASNRange(name='ASN Range 2', slug='asn-range-2', rir=rirs[0], tenant=tenants[0], start=200, end=299),
            ASNRange(name='ASN Range 3', slug='asn-range-3', rir=rirs[0], tenant=tenants[0], start=300, end=399),
        )
        ASNRange.objects.bulk_create(asn_ranges)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'ASN Range X',
            'slug': 'asn-range-x',
            'rir': rirs[1].pk,
            'tenant': tenants[1].pk,
            'start': 1000,
            'end': 1099,
            'description': 'A new ASN range',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,rir,tenant,start,end,description",
            f"ASN Range 4,asn-range-4,{rirs[1].name},{tenants[1].name},400,499,Fourth range",
            f"ASN Range 5,asn-range-5,{rirs[1].name},{tenants[1].name},500,599,Fifth range",
            f"ASN Range 6,asn-range-6,{rirs[1].name},{tenants[1].name},600,699,Sixth range",
        )

        cls.csv_update_data = (
            "id,description",
            f"{asn_ranges[0].pk},New description 1",
            f"{asn_ranges[1].pk},New description 2",
            f"{asn_ranges[2].pk},New description 3",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'description': 'Next description',
        }


class ASNTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ASN

    @classmethod
    def setUpTestData(cls):
        rirs = [
            RIR(name='RIR 1', slug='rir-1', is_private=True),
            RIR(name='RIR 2', slug='rir-2', is_private=True),
        ]
        RIR.objects.bulk_create(rirs)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2')
        )
        Site.objects.bulk_create(sites)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        asns = (
            ASN(asn=65001, rir=rirs[0], role=roles[0], tenant=tenants[0]),
            ASN(asn=65002, rir=rirs[1], role=roles[1], tenant=tenants[1]),
            ASN(asn=4200000001, rir=rirs[0], role=roles[0], tenant=tenants[0]),
            ASN(asn=4200000002, rir=rirs[1], role=roles[1], tenant=tenants[1]),
        )
        ASN.objects.bulk_create(asns)

        asns[0].sites.set([sites[0]])
        asns[1].sites.set([sites[1]])
        asns[2].sites.set([sites[0]])
        asns[3].sites.set([sites[1]])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'asn': 65000,
            'rir': rirs[0].pk,
            'role': roles[0].pk,
            'tenant': tenants[0].pk,
            'site': sites[0].pk,
            'description': 'A new ASN',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "asn,rir,role",
            f"65003,RIR 1,{roles[0].name}",
            f"65004,RIR 2,{roles[1].name}",
            f"4200000003,RIR 1,{roles[0].name}",
            f"4200000004,RIR 2,{roles[1].name}",
        )

        cls.csv_update_data = (
            "id,description",
            f"{asns[0].pk},New description1",
            f"{asns[1].pk},New description2",
            f"{asns[2].pk},New description3",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'role': roles[1].pk,
            'description': 'Next description',
        }


class VRFTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VRF

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant A', slug='tenant-a'),
            Tenant(name='Tenant B', slug='tenant-b'),
        )
        Tenant.objects.bulk_create(tenants)

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        )
        VRF.objects.bulk_create(vrfs)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'VRF X',
            'rd': '65000:999',
            'tenant': tenants[0].pk,
            'enforce_unique': True,
            'description': 'A new VRF',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name",
            "VRF 4",
            "VRF 5",
            "VRF 6",
        )

        cls.csv_update_data = (
            "id,name",
            f"{vrfs[0].pk},VRF 7",
            f"{vrfs[1].pk},VRF 8",
            f"{vrfs[2].pk},VRF 9",
        )

        cls.bulk_edit_data = {
            'tenant': tenants[1].pk,
            'enforce_unique': False,
            'description': 'New description',
        }


class RouteTargetTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = RouteTarget

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant A', slug='tenant-a'),
            Tenant(name='Tenant B', slug='tenant-b'),
        )
        Tenant.objects.bulk_create(tenants)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        route_targets = (
            RouteTarget(name='65000:1001', tenant=tenants[0]),
            RouteTarget(name='65000:1002', tenant=tenants[1]),
            RouteTarget(name='65000:1003'),
        )
        RouteTarget.objects.bulk_create(route_targets)

        cls.form_data = {
            'name': '65000:100',
            'description': 'A new route target',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,tenant,description",
            "65000:1004,Tenant A,Foo",
            "65000:1005,Tenant B,Bar",
            "65000:1006,,No tenant",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{route_targets[0].pk},65000:1007,New description1",
            f"{route_targets[1].pk},65000:1008,New description2",
            f"{route_targets[2].pk},65000:1009,New description3",
        )

        cls.bulk_edit_data = {
            'tenant': tenants[1].pk,
            'description': 'New description',
        }


class RIRTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = RIR

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        )
        RIR.objects.bulk_create(rirs)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'RIR X',
            'slug': 'rir-x',
            'is_private': True,
            'description': 'A new RIR',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "RIR 4,rir-4,Fourth RIR",
            "RIR 5,rir-5,Fifth RIR",
            "RIR 6,rir-6,Sixth RIR",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{rirs[0].pk},RIR 7,Fourth RIR7",
            f"{rirs[1].pk},RIR 8,Fifth RIR8",
            f"{rirs[2].pk},RIR 9,Sixth RIR9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class AggregateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Aggregate

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
        )
        RIR.objects.bulk_create(rirs)

        aggregates = (
            Aggregate(prefix=IPNetwork('10.1.0.0/16'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('10.2.0.0/16'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('10.3.0.0/16'), rir=rirs[0]),
        )
        Aggregate.objects.bulk_create(aggregates)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'prefix': IPNetwork('10.99.0.0/16'),
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'A new aggregate',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "prefix,rir",
            "10.4.0.0/16,RIR 1",
            "10.5.0.0/16,RIR 1",
            "10.6.0.0/16,RIR 1",
        )

        cls.csv_update_data = (
            "id,description",
            f"{aggregates[0].pk},New description1",
            f"{aggregates[1].pk},New description2",
            f"{aggregates[2].pk},New description3",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'New description',
        }

    def test_aggregate_prefixes(self):
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        rir = RIR.objects.first()
        aggregate = Aggregate.objects.create(prefix=IPNetwork('192.168.0.0/16'), rir=rir)
        prefixes = (
            Prefix(prefix=IPNetwork('192.168.1.0/24')),
            Prefix(prefix=IPNetwork('192.168.2.0/24')),
            Prefix(prefix=IPNetwork('192.168.3.0/24')),
        )
        Prefix.objects.bulk_create(prefixes)
        self.assertEqual(aggregate.get_child_prefixes().count(), 3)

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    def test_aggregate_prefixes_filter_suppresses_available_prefixes(self):
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        tenants = (
            Tenant(name='Aggregate Tenant 1', slug='aggregate-tenant-1'),
            Tenant(name='Aggregate Tenant 2', slug='aggregate-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        aggregate = Aggregate.objects.create(
            prefix=IPNetwork('203.0.113.0/24'),
            rir=RIR.objects.first()
        )
        prefixes = (
            Prefix(prefix=IPNetwork('203.0.113.0/26'), tenant=tenants[0]),
            Prefix(prefix=IPNetwork('203.0.113.64/26'), tenant=tenants[1]),
        )
        Prefix.objects.bulk_create(prefixes)

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        response = self.client.get(url, {'tenant_id': tenants[0].pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '203.0.113.0/26')
        self.assertNotContains(response, '203.0.113.64/26')

    def test_aggregate_prefixes_saved_filter(self):
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        tenants = (
            Tenant(name='Aggregate Saved Tenant 1', slug='aggregate-saved-tenant-1'),
            Tenant(name='Aggregate Saved Tenant 2', slug='aggregate-saved-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        aggregate = Aggregate.objects.create(
            prefix=IPNetwork('203.0.114.0/24'),
            rir=RIR.objects.first()
        )
        prefixes = (
            Prefix(prefix=IPNetwork('203.0.114.0/26'), tenant=tenants[0]),
            Prefix(prefix=IPNetwork('203.0.114.64/26'), tenant=tenants[1]),
        )
        Prefix.objects.bulk_create(prefixes)

        saved_filter = SavedFilter.objects.create(
            name='Aggregate Tenant 1 prefixes',
            slug='aggregate-tenant-1-prefixes',
            parameters={
                'tenant_id': [str(tenants[0].pk)],
            },
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(Prefix))

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        response = self.client.get(url, {'filter_id': saved_filter.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '203.0.114.0/26')
        self.assertNotContains(response, '203.0.114.64/26')

    def test_aggregate_prefixes_custom_field_constraint_shows_available(self):
        """A tenant custom-field permission constraint does not suppress available-prefix rows."""
        cf = CustomField.objects.create(name='integerCustomField', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(Tenant)])
        tenant = Tenant.objects.create(
            name='Agg CF Tenant', slug='agg-cf-tenant', custom_field_data={'integerCustomField': 1}
        )

        aggregate = Aggregate.objects.create(prefix=IPNetwork('198.51.100.0/24'), rir=RIR.objects.first())
        child = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/26'), tenant=tenant)

        self.add_permissions('ipam.view_aggregate')
        obj_perm = ObjectPermission(
            name='View prefixes', actions=['view'], constraints={'tenant__custom_field_data__integerCustomField': 1}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        self.assertIn(child, Prefix.objects.restrict(self.user, 'view'))

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertTrue(response.context['show_available'])
        self.assertGreater(len(response.context['table'].data), 1)

    def has_active_child_filters(self, **params):
        """Run the child filter detector on a fresh view for the given query parameters."""
        view = AggregatePrefixesView()
        request = RequestFactory().get('/', params)
        request.user = self.user
        return view._has_active_child_filters(request)

    def test_has_active_child_filters_declared_filters(self):
        """A declared filter with a real value counts as active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        tenant = Tenant.objects.create(name='Declared Tenant', slug='declared-tenant')

        self.assertTrue(self.has_active_child_filters(tenant_id=tenant.pk))
        self.assertTrue(self.has_active_child_filters(q='test'))
        # A boolean false is a value, not an absent filter.
        self.assertTrue(self.has_active_child_filters(is_pool='false'))

    def test_has_active_child_filters_lookup_variants(self):
        """Lookup variants generated by get_filters() count as active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        self.assertTrue(self.has_active_child_filters(status__n=PrefixStatusChoices.STATUS_ACTIVE))
        self.assertTrue(self.has_active_child_filters(description__empty='true'))

    def test_has_active_child_filters_custom_field_filters(self):
        """Custom field filters registered on the filterset instance count as active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        cf = CustomField.objects.create(name='edge_cf', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(Prefix)])

        self.assertTrue(self.has_active_child_filters(cf_edge_cf='1'))
        self.assertTrue(self.has_active_child_filters(cf_edge_cf__gte='1'))

    def test_has_active_child_filters_saved_filter(self):
        """A populated saved filter counts as active filtering by slug or by id."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        tenant = Tenant.objects.create(name='Saved Ref Tenant', slug='saved-ref-tenant')
        saved_filter = SavedFilter.objects.create(
            name='Saved ref', slug='saved-ref', parameters={'tenant_id': [str(tenant.pk)]}
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(Prefix))

        self.assertTrue(self.has_active_child_filters(filter=saved_filter.slug))
        self.assertTrue(self.has_active_child_filters(filter_id=saved_filter.pk))

    def test_has_active_child_filters_unresolved_saved_filter(self):
        """A saved filter reference that expands to nothing is not active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        saved_filter = SavedFilter.objects.create(name='Empty', slug='empty-saved-filter', parameters={})
        saved_filter.object_types.add(ObjectType.objects.get_for_model(Prefix))

        self.assertFalse(self.has_active_child_filters(filter_id=saved_filter.pk))
        self.assertFalse(self.has_active_child_filters(filter_id='99999999'))

    def test_has_active_child_filters_without_values(self):
        """A request with no parameters or only empty ones is not active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        self.assertFalse(self.has_active_child_filters())
        self.assertFalse(self.has_active_child_filters(tenant_id=''))
        self.assertFalse(self.has_active_child_filters(q=''))

    def test_has_active_child_filters_invalid_value(self):
        """A filter value that fails validation is not applied, so it is not active filtering."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        self.assertFalse(self.has_active_child_filters(tenant_id='99999999'))

    def test_has_active_child_filters_valid_beside_invalid_value(self):
        """A valid filter is still active when another submitted value is invalid."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        tenant = Tenant.objects.create(name='Mixed Tenant', slug='mixed-tenant')

        self.assertTrue(self.has_active_child_filters(tenant_id=tenant.pk, status='not-a-valid-status'))

    def test_has_active_child_filters_non_filter_params(self):
        """Unknown parameters, display toggles, and table controls are not filters."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')

        self.assertFalse(self.has_active_child_filters(not_a_filter='x'))
        self.assertFalse(self.has_active_child_filters(show_available='false'))
        self.assertFalse(self.has_active_child_filters(show_assigned='true'))
        self.assertFalse(self.has_active_child_filters(page='2', per_page='100', sort='prefix', tableconfig_id='1'))

    def test_has_active_child_filters_control_beside_filter(self):
        """A table control submitted alongside a filter does not mask the filter."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        tenant = Tenant.objects.create(name='Control Tenant', slug='control-tenant')

        self.assertTrue(self.has_active_child_filters(page='2', tenant_id=tenant.pk))

    def test_has_active_child_filters_without_filterset(self):
        """A view without a filterset reports no active filters."""
        view = AggregatePrefixesView()
        view.filterset = None
        request = RequestFactory().get('/', {'tenant_id': '1'})
        request.user = self.user
        self.assertFalse(view._has_active_child_filters(request))

    def test_has_active_child_filters_reuses_view_filterset(self):
        """The detector evaluates the FilterSet already bound by the view, not a fresh one."""
        aggregate = Aggregate.objects.create(prefix=IPNetwork('203.0.115.0/24'), rir=RIR.objects.first())
        tenant = Tenant.objects.create(name='Reuse Tenant', slug='reuse-tenant')

        view = AggregatePrefixesView()
        request = RequestFactory().get('/')
        request.user = self.user

        # The bound FilterSet is authoritative: it reports a filter the request itself does not carry.
        view.filterset_instance = AggregatePrefixesView.filterset(
            {'tenant_id': [str(tenant.pk)]}, view.get_children(request, aggregate), request=request
        )

        request = RequestFactory().get('/', {'page': '2'})
        request.user = self.user
        self.assertTrue(view._has_active_child_filters(request))

    def test_child_tab_binds_filterset_once(self):
        """A filtered child tab binds the FilterSet once; the detector reuses it instead of rebuilding."""
        self.add_permissions('ipam.view_aggregate', 'ipam.view_prefix')
        aggregate = Aggregate.objects.create(prefix=IPNetwork('203.0.116.0/24'), rir=RIR.objects.first())
        tenant = Tenant.objects.create(name='Bind Once Tenant', slug='bind-once-tenant')
        Prefix.objects.create(prefix=IPNetwork('203.0.116.0/26'), tenant=tenant)

        # Count only data-bound instantiations: the filter form separately builds an unbound
        # FilterSet to resolve field modifiers, which is unrelated to filter detection.
        bound = []
        original_init = filtersets.PrefixFilterSet.__init__

        def counting_init(fs, *args, **kwargs):
            if args or 'data' in kwargs:
                bound.append(fs)
            original_init(fs, *args, **kwargs)

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        with patch.object(filtersets.PrefixFilterSet, '__init__', counting_init):
            response = self.client.get(url, {'tenant_id': tenant.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(bound), 1)
        self.assertFalse(response.context['show_available'])


class RoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Role

    @classmethod
    def setUpTestData(cls):

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Role X',
            'slug': 'role-x',
            'weight': 200,
            'description': 'A new role',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,weight",
            "Role 4,role-4,1000",
            "Role 5,role-5,1000",
            "Role 6,role-6,1000",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{roles[0].pk},Role 7,New description7",
            f"{roles[1].pk},Role 8,New description8",
            f"{roles[2].pk},Role 9,New description9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class PrefixTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Prefix

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        prefixes = (
            Prefix(prefix=IPNetwork('10.1.0.0/16'), vrf=vrfs[0], scope=sites[0], role=roles[0]),
            Prefix(prefix=IPNetwork('10.2.0.0/16'), vrf=vrfs[0], scope=sites[0], role=roles[0]),
            Prefix(prefix=IPNetwork('10.3.0.0/16'), vrf=vrfs[0], scope=sites[0], role=roles[0]),
        )
        Prefix.objects.bulk_create(prefixes)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'prefix': IPNetwork('192.0.2.0/24'),
            'scope_type': ContentType.objects.get_for_model(Site).pk,
            'scope': sites[1].pk,
            'vrf': vrfs[1].pk,
            'tenant': None,
            'vlan': None,
            'status': PrefixStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': True,
            'description': 'A new prefix',
            'tags': [t.pk for t in tags],
        }

        site = sites[0]
        cls.csv_data = {
            'default': (
                "vrf,prefix,status,scope_type,scope_id",
                f"VRF 1,10.4.0.0/16,active,dcim.site,{site.pk}",
                f"VRF 1,10.5.0.0/16,active,dcim.site,{site.pk}",
                f"VRF 1,10.6.0.0/16,active,dcim.site,{site.pk}",
            ),
            'scope_name': (
                "vrf,prefix,status,scope_type,scope_name",
                f"VRF 1,10.4.0.0/16,active,dcim.site,{site.name}",
                f"VRF 1,10.5.0.0/16,active,dcim.site,{site.name}",
                f"VRF 1,10.6.0.0/16,active,dcim.site,{site.name}",
            ),
        }

        cls.csv_update_data = (
            "id,description,status",
            f"{prefixes[0].pk},New description 7,{PrefixStatusChoices.STATUS_RESERVED}",
            f"{prefixes[1].pk},New description 8,{PrefixStatusChoices.STATUS_RESERVED}",
            f"{prefixes[2].pk},New description 9,{PrefixStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': PrefixStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': False,
            'description': 'New description',
        }

    def test_bulk_add_ipv4_prefixes(self):
        """Test bulk creating IPv4 prefixes using a pattern."""
        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        initial_count = Prefix.objects.count()
        url = reverse('ipam:prefix_bulk_add')
        data = {
            'pattern': '10.0.[0-2].0/24',
            'status': PrefixStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)
        self.assertEqual(Prefix.objects.count(), initial_count + 3)

        for i in range(3):
            self.assertTrue(Prefix.objects.filter(prefix=IPNetwork(f'10.0.{i}.0/24')).exists())

    def test_bulk_add_ipv6_prefixes(self):
        """Test bulk creating IPv6 prefixes using a pattern."""
        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        initial_count = Prefix.objects.count()
        url = reverse('ipam:prefix_bulk_add')
        data = {
            'pattern': 'fd00:db8:[0-3]::/48',
            'status': PrefixStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)
        self.assertEqual(Prefix.objects.count(), initial_count + 4)

        for i in range(4):
            self.assertTrue(Prefix.objects.filter(prefix=IPNetwork(f'fd00:db8:{i}::/48')).exists())

    def test_bulk_add_ipv6_prefixes_uppercase_hex(self):
        """Test bulk creating IPv6 prefixes using uppercase hex in the pattern."""
        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        initial_count = Prefix.objects.count()
        url = reverse('ipam:prefix_bulk_add')
        data = {
            'pattern': 'fd00:0:0:[48-4F]00::/56',
            'status': PrefixStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)
        self.assertEqual(Prefix.objects.count(), initial_count + 8)

        expected_hex = ['48', '49', '4a', '4b', '4c', '4d', '4e', '4f']
        for h in expected_hex:
            prefix_str = f'fd00:0:0:{h}00::/56'
            self.assertTrue(
                Prefix.objects.filter(prefix=IPNetwork(prefix_str)).exists(),
                f'Expected prefix {prefix_str} was not created'
            )

    def test_bulk_add_prefixes_with_changelog_message(self):
        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        changelog_message = 'Bulk-created prefixes'
        prefixes = [IPNetwork(f'198.18.{i}.0/24') for i in range(3)]
        url = reverse('ipam:prefix_bulk_add')
        data = {
            'pattern': '198.18.[0-2].0/24',
            'status': PrefixStatusChoices.STATUS_ACTIVE,
            'changelog_message': changelog_message,
        }

        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)

        created_prefixes = list(Prefix.objects.filter(prefix__in=prefixes))
        self.assertEqual(len(created_prefixes), len(prefixes))

        objectchanges = ObjectChange.objects.filter(
            action=ObjectChangeActionChoices.ACTION_CREATE,
            changed_object_type=ContentType.objects.get_for_model(Prefix),
            changed_object_id__in=[obj.pk for obj in created_prefixes],
        )
        self.assertEqual(objectchanges.count(), len(prefixes))
        for objectchange in objectchanges:
            self.assertEqual(objectchange.message, changelog_message)

    def test_prefix_prefixes(self):
        self.add_permissions('ipam.view_prefix')
        prefixes = (
            Prefix(prefix=IPNetwork('192.168.0.0/16')),
            Prefix(prefix=IPNetwork('192.168.1.0/24')),
            Prefix(prefix=IPNetwork('192.168.2.0/24')),
            Prefix(prefix=IPNetwork('192.168.3.0/24')),
        )
        Prefix.objects.bulk_create(prefixes)
        self.assertEqual(prefixes[0].get_child_prefixes().count(), 3)

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': prefixes[0].pk})
        self.assertHttpStatus(self.client.get(url), 200)

    def test_prefix_prefixes_filter_suppresses_available_prefixes(self):
        self.add_permissions('ipam.view_prefix')

        tenants = (
            Tenant(name='Prefix Tenant 1', slug='prefix-tenant-1'),
            Tenant(name='Prefix Tenant 2', slug='prefix-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        parent = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/24'))
        prefixes = (
            Prefix(prefix=IPNetwork('198.51.100.0/26'), tenant=tenants[0]),
            Prefix(prefix=IPNetwork('198.51.100.64/26'), tenant=tenants[1]),
        )
        Prefix.objects.bulk_create(prefixes)

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url, {'tenant_id': tenants[0].pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '198.51.100.0/26')
        self.assertNotContains(response, '198.51.100.64/26')

    def test_prefix_prefixes_saved_filter_suppresses_available_prefixes(self):
        self.add_permissions('ipam.view_prefix')

        tenants = (
            Tenant(name='Prefix Saved Tenant 1', slug='prefix-saved-tenant-1'),
            Tenant(name='Prefix Saved Tenant 2', slug='prefix-saved-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        parent = Prefix.objects.create(prefix=IPNetwork('198.51.101.0/24'))
        prefixes = (
            Prefix(prefix=IPNetwork('198.51.101.0/26'), tenant=tenants[0]),
            Prefix(prefix=IPNetwork('198.51.101.64/26'), tenant=tenants[1]),
        )
        Prefix.objects.bulk_create(prefixes)

        saved_filter = SavedFilter.objects.create(
            name='Prefix Tenant 1 prefixes',
            slug='prefix-tenant-1-prefixes',
            parameters={
                'tenant_id': [str(tenants[0].pk)],
            },
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(Prefix))

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url, {'filter_id': saved_filter.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '198.51.101.0/26')
        self.assertNotContains(response, '198.51.101.64/26')

    def test_prefix_ipranges(self):
        self.add_permissions('ipam.view_prefix', 'ipam.view_iprange')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/16'))
        ip_ranges = (
            IPRange(start_address='192.168.0.1/24', end_address='192.168.0.100/24', size=99),
            IPRange(start_address='192.168.1.1/24', end_address='192.168.1.100/24', size=99),
            IPRange(start_address='192.168.2.1/24', end_address='192.168.2.100/24', size=99),
        )
        IPRange.objects.bulk_create(ip_ranges)
        self.assertEqual(prefix.get_child_ranges().count(), 3)

        url = reverse('ipam:prefix_ipranges', kwargs={'pk': prefix.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    def test_prefix_ipaddresses(self):
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/16'))
        ip_addresses = (
            IPAddress(address=IPNetwork('192.168.0.1/16')),
            IPAddress(address=IPNetwork('192.168.0.2/16')),
            IPAddress(address=IPNetwork('192.168.0.3/16')),
        )
        IPAddress.objects.bulk_create(ip_addresses)
        self.assertEqual(prefix.get_child_ips().count(), 3)

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    def test_prefix_ipaddresses_filter(self):
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')

        tenants = (
            Tenant(name='IP Address Tenant 1', slug='ip-address-tenant-1'),
            Tenant(name='IP Address Tenant 2', slug='ip-address-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        ip_addresses = (
            IPAddress(address=IPNetwork('192.0.2.1/24'), tenant=tenants[0]),
            IPAddress(address=IPNetwork('192.0.2.2/24'), tenant=tenants[1]),
        )
        IPAddress.objects.bulk_create(ip_addresses)

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'tenant_id': tenants[0].pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '192.0.2.1/24')
        self.assertNotContains(response, '192.0.2.2/24')

    def test_prefix_ipaddresses_saved_filter(self):
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')

        tenants = (
            Tenant(name='Saved Filter Tenant 1', slug='saved-filter-tenant-1'),
            Tenant(name='Saved Filter Tenant 2', slug='saved-filter-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        ip_addresses = (
            IPAddress(address=IPNetwork('192.0.2.1/24'), tenant=tenants[0]),
            IPAddress(address=IPNetwork('192.0.2.2/24'), tenant=tenants[1]),
        )
        IPAddress.objects.bulk_create(ip_addresses)

        saved_filter = SavedFilter.objects.create(
            name='Tenant 1 IP addresses',
            slug='tenant-1-ip-addresses',
            parameters={
                'tenant_id': [str(tenants[0].pk)],
            },
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'filter_id': saved_filter.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '192.0.2.1/24')
        self.assertNotContains(response, '192.0.2.2/24')

    def assertIPAvailabilityShown(self, response, visible_ip):
        """The permitted IP renders as a real row and synthetic available-space rows are present."""
        records = list(response.context['table'].data)
        rendered_ip_pks = {r.pk for r in records if isinstance(r, IPAddress)}
        self.assertIn(visible_ip.pk, rendered_ip_pks)
        self.assertTrue(any(isinstance(r, AvailableIPSpace) for r in records))

    def test_prefix_ipaddresses_unfiltered_shows_available_space(self):
        """An unfiltered IP Addresses tab injects synthetic available-space rows."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_custom_field_constraint_shows_available(self):
        """A permission constraint on a related object's custom field data does not suppress the available-IP rows."""
        cf = CustomField.objects.create(name='integerCustomField', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(Tenant)])

        tenant = Tenant.objects.create(name='CF Tenant', slug='cf-tenant', custom_field_data={'integerCustomField': 1})
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), tenant=tenant)
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), tenant=tenant)

        # The issue reports the JSON string "1", but an integer custom field stores an int, so a
        # string constraint would not match and would hide the parent. Use 1 and prove access below.
        constraint = {'tenant__custom_field_data__integerCustomField': 1}
        for model in (Prefix, IPAddress):
            obj_perm = ObjectPermission(
                name=f'View {model._meta.verbose_name}', actions=['view'], constraints=constraint
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(model))

        # Self-verifying: the constraint must actually grant access to both objects, or the
        # availability assertion could pass through an unrestricted re-query instead of the fix.
        self.assertIn(prefix, Prefix.objects.restrict(self.user, 'view'))
        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_related_field_constraint_shows_available(self):
        """A permission constraint on a related object field does not suppress the available-IP rows."""
        tenant = Tenant.objects.create(name='Plain Constraint Tenant', slug='plain-constraint-tenant')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), tenant=tenant)
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), tenant=tenant)

        constraint = {'tenant__slug': 'plain-constraint-tenant'}
        for model in (Prefix, IPAddress):
            obj_perm = ObjectPermission(
                name=f'View {model._meta.verbose_name}', actions=['view'], constraints=constraint
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(model))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_constraint_with_direct_filter_suppresses(self):
        """A direct filter still suppresses available-IP rows for a constrained user."""
        tenants = (
            Tenant(name='Constraint Direct 1', slug='constraint-direct-1'),
            Tenant(name='Constraint Direct 2', slug='constraint-direct-2'),
        )
        Tenant.objects.bulk_create(tenants)
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        ip1 = IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), tenant=tenants[0])
        ip2 = IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'), tenant=tenants[1])

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs', actions=['view'], constraints={'tenant__slug__startswith': 'constraint-direct'}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        # Both IPs are visible under the constraint, so suppression below is due to the filter, not permissions.
        self.assertIn(ip1, IPAddress.objects.restrict(self.user, 'view'))
        self.assertIn(ip2, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'tenant_id': tenants[0].pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '192.0.2.1/24')
        self.assertNotContains(response, '192.0.2.2/24')

    def test_prefix_ipaddresses_constraint_with_saved_filter_suppresses(self):
        """A saved filter still suppresses available-IP rows for a constrained user."""
        tenants = (
            Tenant(name='Constraint Saved 1', slug='constraint-saved-1'),
            Tenant(name='Constraint Saved 2', slug='constraint-saved-2'),
        )
        Tenant.objects.bulk_create(tenants)
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        ip1 = IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), tenant=tenants[0])
        ip2 = IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'), tenant=tenants[1])

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs', actions=['view'], constraints={'tenant__slug__startswith': 'constraint-saved'}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        # Both IPs are visible under the constraint, so suppression below is due to the filter, not permissions.
        self.assertIn(ip1, IPAddress.objects.restrict(self.user, 'view'))
        self.assertIn(ip2, IPAddress.objects.restrict(self.user, 'view'))

        saved_filter = SavedFilter.objects.create(
            name='Constraint saved tenant 1', slug='constraint-saved-tenant-1',
            parameters={'tenant_id': [str(tenants[0].pk)]},
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'filter_id': saved_filter.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, '192.0.2.1/24')
        self.assertNotContains(response, '192.0.2.2/24')

    def test_prefix_ipaddresses_direct_field_constraint_shows_available(self):
        """A permission constraint on the IP Address status field does not suppress the available-IP rows."""
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), status=IPAddressStatusChoices.STATUS_ACTIVE)

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs', actions=['view'], constraints={'status': IPAddressStatusChoices.STATUS_ACTIVE}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_own_custom_field_constraint_shows_available(self):
        """A permission constraint on the IP Address custom field data does not suppress the available-IP rows."""
        cf = CustomField.objects.create(name='ip_cf', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(IPAddress)])

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), custom_field_data={'ip_cf': 1})

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(name='View IPs', actions=['view'], constraints={'custom_field_data__ip_cf': 1})
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_multikey_constraint_shows_available(self):
        """A permission constraint combining a direct and a related field does not suppress the available-IP rows."""
        tenant = Tenant.objects.create(name='Multi Key Tenant', slug='multi-key-tenant')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(
            address=IPNetwork('192.0.2.1/29'), status=IPAddressStatusChoices.STATUS_ACTIVE, tenant=tenant
        )

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs',
            actions=['view'],
            constraints={'status': IPAddressStatusChoices.STATUS_ACTIVE, 'tenant__slug': 'multi-key-tenant'},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_or_constraint_shows_available(self):
        """A permission granting access through either of two constraints does not suppress the available-IP rows."""
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), status=IPAddressStatusChoices.STATUS_ACTIVE)

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs',
            actions=['view'],
            constraints=[
                {'status': IPAddressStatusChoices.STATUS_ACTIVE},
                {'status': IPAddressStatusChoices.STATUS_RESERVED},
            ],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_address_startswith_constraint_shows_available(self):
        """The #22539 address__startswith constraint does not suppress the available-IP rows."""
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/24'))
        ip = IPAddress.objects.create(address=IPNetwork('192.168.0.1/24'))

        self.add_permissions('ipam.view_prefix')
        obj_perm = ObjectPermission(
            name='View IPs', actions=['view'], constraints={'address__startswith': '192.168.0.'}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_prefixes_show_available_false_skips_filter_detection(self):
        """With availability already off, the filter detector never runs."""
        self.add_permissions('ipam.view_prefix')
        parent = Prefix.objects.create(prefix=IPNetwork('198.51.104.0/24'))
        Prefix.objects.create(prefix=IPNetwork('198.51.104.0/26'))

        view = PrefixPrefixesView()
        request = RequestFactory().get('/', {'show_available': 'false'})
        request.user = self.user
        view.prep_table_data(request, view.get_children(request, parent), parent)

        self.assertFalse(hasattr(view, '_active_child_filters'))

    def test_prefix_ipaddresses_valid_plus_invalid_filter_suppresses(self):
        """A valid filter is applied and suppresses synthetic rows even when another filter value is invalid."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress')
        tenant = Tenant.objects.create(name='VPI Tenant', slug='vpi-tenant')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        matching = IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), tenant=tenant)
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'tenant_id': tenant.pk, 'status': 'not-a-valid-status'})

        self.assertHttpStatus(response, 200)
        records = list(response.context['table'].data)
        self.assertFalse(any(isinstance(r, AvailableIPSpace) for r in records))
        self.assertEqual({r.pk for r in records if isinstance(r, IPAddress)}, {matching.pk})

    def test_prefix_ipaddresses_htmx_direct_filter_suppresses(self):
        """An HTMX table refresh with a direct filter suppresses available-IP rows."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress')
        tenants = (
            Tenant(name='HTMX Tenant 1', slug='htmx-tenant-1'),
            Tenant(name='HTMX Tenant 2', slug='htmx-tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), tenant=tenants[0])
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'), tenant=tenants[1])

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'tenant_id': tenants[0].pk}, HTTP_HX_REQUEST='true')

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)

    def test_prefix_ipaddresses_htmx_unfiltered_shows_available(self):
        """An HTMX table refresh with no filter still injects available-IP rows."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, HTTP_HX_REQUEST='true')

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_group_constraint_shows_available(self):
        """A constraint granted through a group does not suppress the available-IP rows."""
        self.add_permissions('ipam.view_prefix')
        tenant = Tenant.objects.create(name='Group Grant', slug='group-grant')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), tenant=tenant)

        group = Group.objects.create(name='IP Viewers')
        self.user.groups.add(group)
        obj_perm = ObjectPermission(name='View IPs', actions=['view'], constraints={'tenant__slug': 'group-grant'})
        obj_perm.save()
        obj_perm.groups.add(group)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        # The group grant must resolve, or the assertion below would be vacuous.
        self.assertIn(ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_ipaddresses_partial_visibility_shows_available(self):
        """A constraint that hides one child IP keeps availability rows and omits the hidden IP."""
        self.add_permissions('ipam.view_prefix')
        visible_tenant = Tenant.objects.create(name='Partial Vis', slug='partial-vis')

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        visible_ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), tenant=visible_tenant)
        hidden_ip = IPAddress.objects.create(address=IPNetwork('192.0.2.6/29'))

        obj_perm = ObjectPermission(name='View IPs', actions=['view'], constraints={'tenant__slug': 'partial-vis'})
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        # Exactly one child IP is visible, so the constraint is doing real work.
        self.assertIn(visible_ip, IPAddress.objects.restrict(self.user, 'view'))
        self.assertNotIn(hidden_ip, IPAddress.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        # The hidden IP is omitted and its slot is counted as available space.
        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, visible_ip)
        records = list(response.context['table'].data)
        self.assertNotIn(hidden_ip.pk, {r.pk for r in records if isinstance(r, IPAddress)})
        self.assertEqual(sum(r.size for r in records if isinstance(r, AvailableIPSpace)), 5)

    def test_prefix_ipaddresses_partial_visibility_omits_hidden_range(self):
        """A constraint on child ranges keeps the permitted range and omits the hidden one."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress')

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))
        visible_range = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.2/29'),
            end_address=IPNetwork('192.0.2.3/29'),
            size=2,
            mark_populated=True,
            description='visible',
        )
        hidden_range = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.4/29'),
            end_address=IPNetwork('192.0.2.5/29'),
            size=2,
            mark_populated=True,
        )

        obj_perm = ObjectPermission(name='View ranges', actions=['view'], constraints={'description': 'visible'})
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPRange))

        # Exactly one child range is visible, so the constraint is doing real work.
        self.assertIn(visible_range, IPRange.objects.restrict(self.user, 'view'))
        self.assertNotIn(hidden_range, IPRange.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)
        records = list(response.context['table'].data)
        self.assertEqual({r.pk for r in records if isinstance(r, IPRange)}, {visible_range.pk})
        self.assertEqual(sum(r.size for r in records if isinstance(r, AvailableIPSpace)), 3)

    def test_prefix_ipaddresses_sorted_suppresses_available(self):
        """A sorted IP Addresses tab drops synthetic rows so ordering stays in SQL."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'sort': 'address'})

        self.assertHttpStatus(response, 200)
        records = list(response.context['table'].data)
        self.assertEqual({r.pk for r in records if isinstance(r, IPAddress)}, {ip.pk})
        self.assertFalse(any(isinstance(r, AvailableIPSpace) for r in records))

    def test_prefix_ipaddresses_empty_sort_shows_available(self):
        """An empty sort value is not an ordering, so synthetic rows survive."""
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'))
        ip = IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url, {'sort': ''})

        self.assertHttpStatus(response, 200)
        self.assertIPAvailabilityShown(response, ip)

    def test_prefix_prefixes_unfiltered_shows_available_prefixes(self):
        """An unfiltered Child Prefixes tab injects synthetic available-prefix rows."""
        self.add_permissions('ipam.view_prefix')

        parent = Prefix.objects.create(prefix=IPNetwork('198.51.102.0/24'))
        Prefix.objects.create(prefix=IPNetwork('198.51.102.0/26'))

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertGreater(len(response.context['table'].data), 1)

    def test_prefix_prefixes_custom_field_constraint_shows_available(self):
        """A tenant custom-field permission constraint does not suppress available child-prefix rows."""
        cf = CustomField.objects.create(name='integerCustomField', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(Tenant)])
        tenant = Tenant.objects.create(
            name='Child CF Tenant', slug='child-cf-tenant', custom_field_data={'integerCustomField': 1}
        )

        parent = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/24'), tenant=tenant)
        child = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/26'), tenant=tenant)

        obj_perm = ObjectPermission(
            name='View prefixes', actions=['view'], constraints={'tenant__custom_field_data__integerCustomField': 1}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        self.assertIn(child, Prefix.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertTrue(response.context['show_available'])
        self.assertGreater(len(response.context['table'].data), 1)

    def test_prefix_prefixes_available_only_shows_available(self):
        """The Available button's parameters render synthetic rows and no assigned rows."""
        self.add_permissions('ipam.view_prefix')
        parent = Prefix.objects.create(prefix=IPNetwork('198.51.104.0/24'))
        Prefix.objects.create(prefix=IPNetwork('198.51.104.0/26'))

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url, {'show_assigned': 'false', 'show_available': 'true'})

        self.assertHttpStatus(response, 200)
        rendered = list(response.context['table'].data)
        self.assertTrue([p for p in rendered if p.pk is None])
        self.assertFalse([p for p in rendered if p.pk is not None])

    def test_prefix_prefixes_partial_visibility_shows_available(self):
        """A constraint that hides one child prefix does not suppress the available-prefix rows."""
        visible_tenant = Tenant.objects.create(name='PP Partial', slug='pp-partial')

        # The parent carries the visible tenant, so the single constrained grant covers the tab itself.
        parent = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/24'), tenant=visible_tenant)
        visible_child = Prefix.objects.create(prefix=IPNetwork('198.51.100.0/26'), tenant=visible_tenant)
        hidden_child = Prefix.objects.create(prefix=IPNetwork('198.51.100.64/26'))

        obj_perm = ObjectPermission(
            name='View prefixes', actions=['view'], constraints={'tenant__slug': 'pp-partial'}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Prefix))

        self.assertIn(visible_child, Prefix.objects.restrict(self.user, 'view'))
        self.assertNotIn(hidden_child, Prefix.objects.restrict(self.user, 'view'))

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': parent.pk})
        response = self.client.get(url)

        # Pins that a constraint does not suppress availability, not how the hidden child is handled.
        self.assertHttpStatus(response, 200)
        self.assertTrue(response.context['show_available'])
        self.assertTrue([p for p in response.context['table'].data if p.pk is None])

    def test_prefix_ipaddresses_with_single_address_range(self):
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress', 'ipam.view_iprange')
        # The IP Addresses tab annotates child IP addresses alongside any
        # mark-populated child IP ranges. Make sure a single-address range
        # (start_address == end_address) renders without errors and is shown
        # in its range-like display form rather than as a plain IP address.
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/16'))
        IPAddress.objects.create(address=IPNetwork('192.168.0.1/16'))
        IPRange.objects.create(
            start_address=IPNetwork('192.168.0.50/16'),
            end_address=IPNetwork('192.168.0.50/16'),
            mark_populated=True,
        )

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        # The single-address range is rendered with both endpoints, not as
        # 192.168.0.50/16 (which would make it indistinguishable from an
        # IPAddress row in this mixed-record view).
        self.assertContains(response, '192.168.0.50-192.168.0.50/16')

    def test_prefix_import(self):
        """
        Custom import test for YAML-based imports (versus CSV)
        """
        self.add_permissions('dcim.view_site', 'ipam.view_vlan')
        site = Site.objects.get(name='Site 1')
        IMPORT_DATA = f"""
prefix: 10.1.1.0/24
status: active
vlan: 101
scope_type: dcim.site
scope_id: {site.pk}
"""
        # Note, a site is not tied to the VLAN to verify the fix for #12622
        VLAN.objects.create(vid=101, name='VLAN101')

        # Add all required permissions to the test user
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('ipam:prefix_bulk_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

        prefix = Prefix.objects.get(prefix='10.1.1.0/24')
        self.assertEqual(prefix.status, PrefixStatusChoices.STATUS_ACTIVE)
        self.assertEqual(prefix.vlan.vid, 101)
        self.assertEqual(prefix.scope, site)

    def test_prefix_import_with_scope_name(self):
        """
        Test YAML-based import using scope_name instead of scope_id.
        """
        self.add_permissions('dcim.view_site')
        site = Site.objects.get(name='Site 1')
        IMPORT_DATA = """
prefix: 10.1.3.0/24
status: active
scope_type: dcim.site
scope_name: Site 1
"""
        # Add all required permissions to the test user
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('ipam:prefix_bulk_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

        prefix = Prefix.objects.get(prefix='10.1.3.0/24')
        self.assertEqual(prefix.status, PrefixStatusChoices.STATUS_ACTIVE)
        self.assertEqual(prefix.scope, site)

    def test_prefix_import_with_vlan_group(self):
        """
        This test covers a unique import edge case where VLAN group is specified during the import.
        """
        self.add_permissions('dcim.view_site', 'ipam.view_vlan', 'ipam.view_vlangroup')
        site = Site.objects.get(name='Site 1')
        IMPORT_DATA = f"""
prefix: 10.1.2.0/24
status: active
scope_type: dcim.site
scope_id: {site.pk}
vlan_group: Group 1
vlan: 102
"""
        vlan_group = VLANGroup.objects.create(name='Group 1', slug='group-1', scope=Site.objects.get(name="Site 1"))
        VLAN.objects.create(vid=102, name='VLAN102', group=vlan_group)

        # Add all required permissions to the test user
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('ipam:prefix_bulk_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

        prefix = Prefix.objects.get(prefix='10.1.2.0/24')
        self.assertEqual(prefix.status, PrefixStatusChoices.STATUS_ACTIVE)
        self.assertEqual(prefix.vlan.vid, 102)
        self.assertEqual(prefix.scope, site)

    def test_prefix_import_with_vlan_site_multiple_vlans_same_vid(self):
        """
        Test import when multiple VLANs exist with the same vid but different sites.
        Ref: #20560
        """
        self.add_permissions('dcim.view_site', 'ipam.view_vlan')
        site1 = Site.objects.get(name='Site 1')
        site2 = Site.objects.get(name='Site 2')

        # Create VLANs with the same vid but different sites
        vlan1 = VLAN.objects.create(vid=1, name='VLAN1-Site1', site=site1)
        VLAN.objects.create(vid=1, name='VLAN1-Site2', site=site2)  # Create ambiguity

        # Import prefix with vlan_site specified
        IMPORT_DATA = f"""
prefix: 10.11.0.0/22
status: active
scope_type: dcim.site
scope_id: {site1.pk}
vlan_site: {site1.name}
vlan: 1
description: LOC02-MGMT
"""

        # Add all required permissions to the test user
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('ipam:prefix_bulk_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

        # Verify the prefix was created with the correct VLAN
        prefix = Prefix.objects.get(prefix='10.11.0.0/22')
        self.assertEqual(prefix.vlan, vlan1)

    def test_prefix_import_with_vlan_site_and_global_vlan(self):
        """
        Test import when a global VLAN (no site) and site-specific VLAN exist with same vid.
        When vlan_site is specified, should prefer the site-specific VLAN.
        Ref: #20560
        """
        self.add_permissions('dcim.view_site', 'ipam.view_vlan')
        site1 = Site.objects.get(name='Site 1')

        # Create a global VLAN (no site) and a site-specific VLAN with the same vid
        VLAN.objects.create(vid=10, name='VLAN10-Global', site=None)  # Create ambiguity
        vlan_site = VLAN.objects.create(vid=10, name='VLAN10-Site1', site=site1)

        # Import prefix with vlan_site specified
        IMPORT_DATA = f"""
prefix: 10.12.0.0/22
status: active
scope_type: dcim.site
scope_id: {site1.pk}
vlan_site: {site1.name}
vlan: 10
description: Test Site-Specific VLAN
"""

        # Add all required permissions to the test user
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('ipam:prefix_bulk_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

        # Verify the prefix was created with the site-specific VLAN (not the global one)
        prefix = Prefix.objects.get(prefix='10.12.0.0/22')
        self.assertEqual(prefix.vlan, vlan_site)


class IPRangeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPRange

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        ip_ranges = (
            IPRange(start_address='192.168.0.10/24', end_address='192.168.0.100/24', size=91),
            IPRange(start_address='192.168.1.10/24', end_address='192.168.1.100/24', size=91),
            IPRange(start_address='192.168.2.10/24', end_address='192.168.2.100/24', size=91),
            IPRange(start_address='192.168.3.10/24', end_address='192.168.3.100/24', size=91),
            IPRange(start_address='192.168.4.10/24', end_address='192.168.4.100/24', size=91),
        )
        IPRange.objects.bulk_create(ip_ranges)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'start_address': IPNetwork('192.0.5.10/24'),
            'end_address': IPNetwork('192.0.5.100/24'),
            'vrf': vrfs[1].pk,
            'tenant': None,
            'vlan': None,
            'status': IPRangeStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': True,
            'description': 'A new IP range',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vrf,start_address,end_address,status",
            "VRF 1,10.1.0.1/16,10.1.9.254/16,active",
            "VRF 1,10.2.0.1/16,10.2.9.254/16,active",
            "VRF 1,10.3.0.1/16,10.3.9.254/16,active",
            # Single-address range (start == end)
            "VRF 1,10.4.0.1/16,10.4.0.1/16,active",
        )

        cls.csv_update_data = (
            "id,description,status",
            f"{ip_ranges[0].pk},New description 7,{IPRangeStatusChoices.STATUS_RESERVED}",
            f"{ip_ranges[1].pk},New description 8,{IPRangeStatusChoices.STATUS_RESERVED}",
            f"{ip_ranges[2].pk},New description 9,{IPRangeStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': IPRangeStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'New description',
        }

    def test_iprange_ipaddresses(self):
        self.add_permissions('ipam.view_iprange', 'ipam.view_ipaddress')
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.168.0.1/24'),
            end_address=IPNetwork('192.168.0.100/24'),
            size=99
        )
        ip_addresses = (
            IPAddress(address=IPNetwork('192.168.0.1/24')),
            IPAddress(address=IPNetwork('192.168.0.2/24')),
            IPAddress(address=IPNetwork('192.168.0.3/24')),
        )
        IPAddress.objects.bulk_create(ip_addresses)
        self.assertEqual(iprange.get_child_ips().count(), 3)

        url = reverse('ipam:iprange_ipaddresses', kwargs={'pk': iprange.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    def test_create_single_address_range(self):
        # Exercise the UI form path with start_address == end_address. The
        # generic test_create_object_with_permission covers the multi-address
        # case via cls.form_data; this test mirrors that flow for the single-
        # address case so both paths stay covered.
        self.add_permissions('ipam.add_iprange')
        form_data = {
            'start_address': '192.0.6.10/24',
            'end_address': '192.0.6.10/24',
            'status': IPRangeStatusChoices.STATUS_ACTIVE,
        }
        initial_count = IPRange.objects.count()

        response = self.client.post(reverse('ipam:iprange_add'), data=form_data)
        self.assertHttpStatus(response, 302)
        self.assertEqual(IPRange.objects.count(), initial_count + 1)

        iprange = IPRange.objects.order_by('pk').last()
        self.assertEqual(str(iprange.start_address), '192.0.6.10/24')
        self.assertEqual(str(iprange.end_address), '192.0.6.10/24')
        self.assertEqual(iprange.size, 1)


class IPAddressTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPAddress

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        ipaddresses = (
            IPAddress(address=IPNetwork('192.0.2.1/24'), vrf=vrfs[0]),
            IPAddress(address=IPNetwork('192.0.2.2/24'), vrf=vrfs[0]),
            IPAddress(address=IPNetwork('192.0.2.3/24'), vrf=vrfs[0]),
        )
        IPAddress.objects.bulk_create(ipaddresses)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        fhrp_groups = (
            FHRPGroup(
                name='FHRP Group 1',
                protocol=FHRPGroupProtocolChoices.PROTOCOL_HSRP,
                group_id=10
            ),
            FHRPGroup(
                name='FHRP Group 2',
                protocol=FHRPGroupProtocolChoices.PROTOCOL_HSRP,
                group_id=20
            ),
            FHRPGroup(
                name='FHRP Group 3',
                protocol=FHRPGroupProtocolChoices.PROTOCOL_HSRP,
                group_id=30
            ),
        )
        FHRPGroup.objects.bulk_create(fhrp_groups)
        cls.form_data = {
            'vrf': vrfs[1].pk,
            'address': IPNetwork('192.0.2.99/24'),
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'nat_inside': None,
            'dns_name': 'example',
            'description': 'A new IP address',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vrf,address,status,fhrp_group",
            "VRF 1,192.0.2.4/24,active,FHRP Group 1",
            "VRF 1,192.0.2.5/24,active,FHRP Group 2",
            "VRF 1,192.0.2.6/24,active,FHRP Group 3",
        )

        cls.csv_update_data = (
            "id,description,status",
            f"{ipaddresses[0].pk},New description 7,{IPAddressStatusChoices.STATUS_RESERVED}",
            f"{ipaddresses[1].pk},New description 8,{IPAddressStatusChoices.STATUS_RESERVED}",
            f"{ipaddresses[2].pk},New description 9,{IPAddressStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'dns_name': 'example',
            'description': 'New description',
        }

    def test_bulk_add_ipaddresses_with_changelog_message(self):
        self.add_permissions('ipam.view_ipaddress', 'ipam.view_vrf')
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(IPAddress))

        vrf = VRF.objects.get(name='VRF 1')
        changelog_message = 'Bulk-created IP addresses'
        addresses = [IPNetwork(f'198.51.100.{i}/24') for i in range(10, 13)]
        url = reverse('ipam:ipaddress_bulk_add')
        data = {
            'pattern': '198.51.100.[10-12]/24',
            'vrf': vrf.pk,
            'status': IPAddressStatusChoices.STATUS_ACTIVE,
            'changelog_message': changelog_message,
        }

        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)

        created_addresses = list(IPAddress.objects.filter(address__in=addresses, vrf=vrf))
        self.assertEqual(len(created_addresses), len(addresses))

        objectchanges = ObjectChange.objects.filter(
            action=ObjectChangeActionChoices.ACTION_CREATE,
            changed_object_type=ContentType.objects.get_for_model(IPAddress),
            changed_object_id__in=[obj.pk for obj in created_addresses],
        )
        self.assertEqual(objectchanges.count(), len(addresses))
        for objectchange in objectchanges:
            self.assertEqual(objectchange.message, changelog_message)


class FHRPGroupTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = FHRPGroup

    @classmethod
    def setUpTestData(cls):
        fhrp_groups = (
            FHRPGroup(
                protocol=FHRPGroupProtocolChoices.PROTOCOL_VRRP2,
                group_id=10,
                auth_type=FHRPGroupAuthTypeChoices.AUTHENTICATION_PLAINTEXT,
                auth_key='foobar123',
            ),
            FHRPGroup(
                protocol=FHRPGroupProtocolChoices.PROTOCOL_VRRP3,
                group_id=20,
                auth_type=FHRPGroupAuthTypeChoices.AUTHENTICATION_MD5,
                auth_key='foobar123',
            ),
            FHRPGroup(
                protocol=FHRPGroupProtocolChoices.PROTOCOL_HSRP,
                group_id=30
            ),
        )
        FHRPGroup.objects.bulk_create(fhrp_groups)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'protocol': FHRPGroupProtocolChoices.PROTOCOL_VRRP2,
            'group_id': 99,
            'auth_type': FHRPGroupAuthTypeChoices.AUTHENTICATION_MD5,
            'auth_key': 'abc123def456',
            'description': 'Blah blah blah',
            'name': 'test123 name',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "protocol,group_id,auth_type,auth_key,description",
            "vrrp2,40,plaintext,foobar123,Foo",
            "vrrp3,50,md5,foobar123,Bar",
            "hsrp,60,,,",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{fhrp_groups[0].pk},FHRP Group 1,New description 1",
            f"{fhrp_groups[1].pk},FHRP Group 2,New description 2",
            f"{fhrp_groups[2].pk},FHRP Group 3,New description 3",
        )

        cls.bulk_edit_data = {
            'protocol': FHRPGroupProtocolChoices.PROTOCOL_CARP,
        }


class VLANGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = VLANGroup

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vlan_groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sites[0]),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', scope=sites[0]),
        )
        VLANGroup.objects.bulk_create(vlan_groups)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'VLAN Group X',
            'slug': 'vlan-group-x',
            'description': 'A new VLAN group',
            'vid_ranges': '100-199,300-399',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = {
            'default': (
                "name,slug,scope_type,scope_id,description",
                "VLAN Group 4,vlan-group-4,,,Fourth VLAN group",
                f"VLAN Group 5,vlan-group-5,dcim.site,{sites[0].pk},Fifth VLAN group",
                f"VLAN Group 6,vlan-group-6,dcim.site,{sites[1].pk},Sixth VLAN group",
            ),
            'scope_name': (
                "name,slug,scope_type,scope_name,description",
                "VLAN Group 4,vlan-group-4,,,Fourth VLAN group",
                f"VLAN Group 5,vlan-group-5,dcim.site,{sites[0].name},Fifth VLAN group",
                f"VLAN Group 6,vlan-group-6,dcim.site,{sites[1].name},Sixth VLAN group",
            ),
        }

        cls.csv_update_data = (
            "id,name,description",
            f"{vlan_groups[0].pk},VLAN Group 7,Fourth VLAN group7",
            f"{vlan_groups[1].pk},VLAN Group 8,Fifth VLAN group8",
            f"{vlan_groups[2].pk},VLAN Group 9,Sixth VLAN group9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }

    def test_vlans_filter_suppresses_available_vlans(self):
        self.add_permissions('ipam.view_vlangroup', 'ipam.view_vlan')

        group = VLANGroup.objects.create(
            name='Filtered VLAN Group',
            slug='filtered-vlan-group'
        )
        vlans = (
            VLAN(group=group, vid=100, name='VLAN100'),
            VLAN(group=group, vid=200, name='VLAN200'),
        )
        VLAN.objects.bulk_create(vlans)

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url, {'vid': 100})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, 'VLAN100')
        self.assertNotContains(response, 'VLAN200')

    def test_vlans_saved_filter_suppresses_available_vlans(self):
        self.add_permissions('ipam.view_vlangroup', 'ipam.view_vlan')

        group = VLANGroup.objects.create(
            name='Saved Filter VLAN Group',
            slug='saved-filter-vlan-group'
        )
        vlans = (
            VLAN(group=group, vid=100, name='VLAN100'),
            VLAN(group=group, vid=200, name='VLAN200'),
        )
        VLAN.objects.bulk_create(vlans)

        saved_filter = SavedFilter.objects.create(
            name='VLAN 100',
            slug='vlan-100',
            parameters={
                'vid': ['100'],
            },
        )
        saved_filter.object_types.add(ObjectType.objects.get_for_model(VLAN))

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url, {'filter_id': saved_filter.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(len(response.context['table'].data), 1)
        self.assertContains(response, 'VLAN100')
        self.assertNotContains(response, 'VLAN200')

    def test_vlans_unfiltered_shows_available_vlans(self):
        """An unfiltered VLANs tab injects synthetic available-VLAN rows."""
        self.add_permissions('ipam.view_vlangroup', 'ipam.view_vlan')

        group = VLANGroup.objects.create(name='Unfiltered VLAN Group', slug='unfiltered-vlan-group')
        VLAN.objects.create(group=group, vid=1, name='VLAN0001')

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertGreater(len(response.context['table'].data), 1)

    def test_vlans_custom_field_constraint_shows_available(self):
        """A tenant custom-field permission constraint does not suppress available-VLAN rows."""
        cf = CustomField.objects.create(name='integerCustomField', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.object_types.set([ObjectType.objects.get_for_model(Tenant)])
        tenant = Tenant.objects.create(
            name='VLAN CF Tenant', slug='vlan-cf-tenant', custom_field_data={'integerCustomField': 1}
        )

        group = VLANGroup.objects.create(name='CF VLAN Group', slug='cf-vlan-group')
        vlan = VLAN.objects.create(group=group, vid=10, name='VLAN0010', tenant=tenant)

        self.add_permissions('ipam.view_vlangroup')
        obj_perm = ObjectPermission(
            name='View VLANs', actions=['view'], constraints={'tenant__custom_field_data__integerCustomField': 1}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(VLAN))

        self.assertIn(vlan, VLAN.objects.restrict(self.user, 'view'))

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertGreater(len(response.context['table'].data), 1)

    def test_vlans_partial_visibility_shows_available(self):
        """A constraint that hides one VLAN does not suppress the available-VLAN rows."""
        self.add_permissions('ipam.view_vlangroup')
        visible_tenant = Tenant.objects.create(name='VLAN Partial', slug='vlan-partial')

        group = VLANGroup.objects.create(name='Partial VLAN Group', slug='partial-vlan-group')
        visible_vlan = VLAN.objects.create(group=group, vid=10, name='VLAN0010', tenant=visible_tenant)
        hidden_vlan = VLAN.objects.create(group=group, vid=20, name='VLAN0020')

        obj_perm = ObjectPermission(name='View VLANs', actions=['view'], constraints={'tenant__slug': 'vlan-partial'})
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(VLAN))

        self.assertIn(visible_vlan, VLAN.objects.restrict(self.user, 'view'))
        self.assertNotIn(hidden_vlan, VLAN.objects.restrict(self.user, 'view'))

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url)

        # Pins that a constraint does not suppress availability, not how the hidden child is handled.
        self.assertHttpStatus(response, 200)
        rendered = list(response.context['table'].data)
        self.assertIn(visible_vlan.vid, {r.vid for r in rendered if isinstance(r, VLAN)})
        self.assertTrue([r for r in rendered if isinstance(r, dict)])  # synthetic available VLANs present

    def test_vlans_sorted_suppresses_available(self):
        """A sorted VLANs tab drops synthetic available-VLAN rows."""
        self.add_permissions('ipam.view_vlangroup', 'ipam.view_vlan')
        group = VLANGroup.objects.create(name='Sorted VLAN Group', slug='sorted-vlan-group')
        vlan = VLAN.objects.create(group=group, vid=10, name='VLAN0010')

        url = reverse('ipam:vlangroup_vlans', kwargs={'pk': group.pk})
        response = self.client.get(url, {'sort': 'vid'})

        self.assertHttpStatus(response, 200)
        rendered = list(response.context['table'].data)
        self.assertEqual({r.vid for r in rendered if isinstance(r, VLAN)}, {vlan.vid})
        self.assertFalse([r for r in rendered if isinstance(r, dict)])  # no synthetic available VLANs


class VLANTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VLAN

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vlangroups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sites[1]),
        )
        VLANGroup.objects.bulk_create(vlangroups)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        vlans = (
            VLAN(group=vlangroups[0], vid=101, name='VLAN101', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=102, name='VLAN102', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=103, name='VLAN103', site=sites[0], role=roles[0]),
        )
        VLAN.objects.bulk_create(vlans)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'vid': 999,
            'name': 'VLAN999',
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'A new VLAN',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vid,name,status",
            "104,VLAN104,active",
            "105,VLAN105,active",
            "106,VLAN106,active",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{vlans[0].pk},VLAN107,New description 7",
            f"{vlans[1].pk},VLAN108,New description 8",
            f"{vlans[2].pk},VLAN109,New description 9",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'New description',
        }

    def test_bulk_add_vlans(self):
        self.add_permissions('ipam.add_vlan')

        group = VLANGroup.objects.get(name='VLAN Group 1')
        initial_count = VLAN.objects.count()
        expected_vids = (110, 120, 121, 122)

        form_data = {
            'pattern': '110,120-122',
            'group': group.pk,
            'name': 'Pool-{vid}',
            'status': VLANStatusChoices.STATUS_RESERVED,
        }

        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 302)
        self.assertEqual(VLAN.objects.count(), initial_count + len(expected_vids))

        for vid in expected_vids:
            self.assertTrue(
                VLAN.objects.filter(
                    group=group,
                    vid=vid,
                    name=f'Pool-{vid}'
                ).exists()
            )

    def test_bulk_add_vlans_rolls_back_on_duplicate_name(self):
        self.add_permissions('ipam.add_vlan')

        group = VLANGroup.objects.get(name='VLAN Group 1')
        initial_count = VLAN.objects.count()

        form_data = {
            'pattern': '110-112',
            'group': group.pk,
            'name': 'Duplicate name',
            'status': VLANStatusChoices.STATUS_RESERVED,
        }

        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLAN.objects.count(), initial_count)
        self.assertFalse(VLAN.objects.filter(group=group, vid=110).exists())

    def test_bulk_add_vlans_rolls_back_when_any_id_outside_group_range(self):
        self.add_permissions('ipam.add_vlan')

        group = VLANGroup.objects.create(
            name='Restricted VLAN Group',
            slug='restricted-vlan-group',
            vid_ranges=[NumericRange(200, 204)]  # Valid VIDs: 200-203
        )
        initial_count = VLAN.objects.count()

        form_data = {
            'pattern': '200-203,500',
            'group': group.pk,
            'name': 'Restricted-{vid}',
            'status': VLANStatusChoices.STATUS_RESERVED,
        }

        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLAN.objects.count(), initial_count)
        self.assertFalse(VLAN.objects.filter(group=group, vid=200).exists())
        self.assertFalse(VLAN.objects.filter(group=group, vid=203).exists())
        self.assertFalse(VLAN.objects.filter(group=group, vid=500).exists())

    def test_bulk_add_vlans_pattern_shapes(self):
        """Single values, multiple values, ranges, and combinations create the expected VLANs."""
        self.add_permissions('ipam.add_vlan')
        # The combination runs against a second group: subTests share one transaction, and VIDs
        # 10 & 20 would otherwise collide with the multiple-values case via the (group, vid) constraint.
        cases = (
            ('500', (500,), 'VLAN Group 1'),
            ('5,10,20', (5, 10, 20), 'VLAN Group 1'),
            ('600-605', tuple(range(600, 606)), 'VLAN Group 1'),
            ('1,10-20,300-305', (1, *range(10, 21), *range(300, 306)), 'VLAN Group 2'),
        )
        for pattern, expected_vids, group_name in cases:
            with self.subTest(pattern=pattern):
                group = VLANGroup.objects.get(name=group_name)
                initial_count = VLAN.objects.count()
                form_data = {
                    'pattern': pattern,
                    'group': group.pk,
                    'name': 'Pool-{vid}',
                    'status': VLANStatusChoices.STATUS_ACTIVE,
                }
                response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)
                self.assertHttpStatus(response, 302)
                self.assertEqual(VLAN.objects.count(), initial_count + len(expected_vids))
                for vid in expected_vids:
                    self.assertTrue(VLAN.objects.filter(group=group, vid=vid, name=f'Pool-{vid}').exists())

    def test_bulk_add_vlans_invalid_pattern(self):
        """An invalid pattern re-renders the form with a pattern error and creates nothing."""
        self.add_permissions('ipam.add_vlan')
        initial_count = VLAN.objects.count()

        for pattern in ('abc', '20-10', '0', '4095', '10-'):
            with self.subTest(pattern=pattern):
                form_data = {
                    'pattern': pattern,
                    'name': 'Pool-{vid}',
                    'status': VLANStatusChoices.STATUS_ACTIVE,
                }
                response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)
                self.assertHttpStatus(response, 200)
                self.assertIn('pattern', response.context['form'].errors)
                self.assertEqual(VLAN.objects.count(), initial_count)

    def test_bulk_add_vlans_static_name_without_group(self):
        """A static name (no {vid} placeholder) is permitted across VLANs not assigned to a group."""
        self.add_permissions('ipam.add_vlan')
        initial_count = VLAN.objects.count()

        form_data = {
            'pattern': '710-712',
            'name': 'Same name',
            'status': VLANStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 302)
        self.assertEqual(VLAN.objects.count(), initial_count + 3)
        self.assertEqual(VLAN.objects.filter(name='Same name').count(), 3)

    def test_bulk_add_vlans_rolls_back_on_constrained_permission(self):
        """Bulk creation rolls back when a generated VLAN falls outside the user's add constraints."""
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add'],
            constraints={'vid__lt': 120}
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(VLAN))

        initial_count = VLAN.objects.count()
        form_data = {
            'pattern': '110,120-122',
            'name': 'Pool-{vid}',
            'status': VLANStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLAN.objects.count(), initial_count)
        self.assertTrue(response.context['form'].non_field_errors())

    def test_bulk_add_vlans_propagates_field_errors(self):
        """A per-object validation error on a non-pattern field is reported on the bulk-create form."""
        self.add_permissions('ipam.add_vlan')
        initial_count = VLAN.objects.count()

        form_data = {
            'pattern': '800',
            'name': 'Pool-{vid}',
            'status': VLANStatusChoices.STATUS_ACTIVE,
            'qinq_role': VLANQinQRoleChoices.ROLE_CUSTOMER,  # Requires an SVLAN
        }
        response = self.client.post(reverse('ipam:vlan_bulk_add'), form_data)

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLAN.objects.count(), initial_count)
        self.assertTrue(response.context['form'].non_field_errors())


class VLANTranslationPolicyTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VLANTranslationPolicy

    @classmethod
    def setUpTestData(cls):

        vlan_translation_policies = (
            VLANTranslationPolicy(
                name='Policy 1',
                description='foobar1',
            ),
            VLANTranslationPolicy(
                name='Policy 2',
                description='foobar2',
            ),
            VLANTranslationPolicy(
                name='Policy 3',
                description='foobar3',
            ),
        )
        VLANTranslationPolicy.objects.bulk_create(vlan_translation_policies)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Policy999',
            'description': 'A new VLAN Translation Policy',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description",
            "Policy101,foobar1",
            "Policy102,foobar2",
            "Policy103,foobar3",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{vlan_translation_policies[0].pk},Policy101,New description 1",
            f"{vlan_translation_policies[1].pk},Policy102,New description 2",
            f"{vlan_translation_policies[2].pk},Policy103,New description 3",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class VLANTranslationRuleTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VLANTranslationRule

    @classmethod
    def setUpTestData(cls):

        vlan_translation_policies = (
            VLANTranslationPolicy(
                name='Policy 1',
                description='foobar1',
            ),
            VLANTranslationPolicy(
                name='Policy 2',
                description='foobar2',
            ),
            VLANTranslationPolicy(
                name='Policy 3',
                description='foobar3',
            ),
        )
        VLANTranslationPolicy.objects.bulk_create(vlan_translation_policies)

        vlan_translation_rules = (
            VLANTranslationRule(
                policy=vlan_translation_policies[0],
                local_vid=100,
                remote_vid=200,
            ),
            VLANTranslationRule(
                policy=vlan_translation_policies[0],
                local_vid=101,
                remote_vid=201,
            ),
            VLANTranslationRule(
                policy=vlan_translation_policies[1],
                local_vid=102,
                remote_vid=202,
            ),
        )
        VLANTranslationRule.objects.bulk_create(vlan_translation_rules)

        cls.form_data = {
            'policy': vlan_translation_policies[0].pk,
            'local_vid': 300,
            'remote_vid': 400,
        }

        cls.csv_data = (
            "policy,local_vid,remote_vid",
            f"{vlan_translation_policies[0].name},103,203",
            f"{vlan_translation_policies[0].name},104,204",
            f"{vlan_translation_policies[1].name},105,205",
        )

        cls.csv_update_data = (
            "id,local_vid,remote_vid",
            f"{vlan_translation_rules[0].pk},105,205",
            f"{vlan_translation_rules[1].pk},106,206",
            f"{vlan_translation_rules[2].pk},107,207",
        )

        cls.bulk_edit_data = {
            'policy': vlan_translation_policies[2].pk,
        }


class ServiceTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ServiceTemplate

    @classmethod
    def setUpTestData(cls):
        service_templates = (
            ServiceTemplate(name='Service Template 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[101]),
            ServiceTemplate(name='Service Template 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[102]),
            ServiceTemplate(name='Service Template 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[103]),
        )
        ServiceTemplate.objects.bulk_create(service_templates)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Service Template X',
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '104,105',
            'description': 'A new service template',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,protocol,ports,description",
            "Service Template 4,tcp,1,First service template",
            "Service Template 5,tcp,2,Second service template",
            "Service Template 6,tcp,3,Third service template",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{service_templates[0].pk},Service Template 7,First service template7",
            f"{service_templates[1].pk},Service Template 8,Second service template8",
            f"{service_templates[2].pk},Service Template 9,Third service template9",
        )

        cls.bulk_edit_data = {
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '106,107',
            'description': 'New description',
        }


class ServiceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Service
    # TODO, related to #9816, cannot validate GFK
    validation_excluded_fields = ('device',)

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        device = Device.objects.create(name='Device 1', site=site, device_type=devicetype, role=role)
        interface = Interface.objects.create(device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_VIRTUAL)
        fhrp_group = FHRPGroup.objects.create(
            name='Group 1', group_id=1234, protocol=FHRPGroupProtocolChoices.PROTOCOL_CARP
        )

        services = (
            Service(parent=device, name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[101]),
            Service(parent=device, name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[102]),
            Service(parent=device, name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[103]),
        )
        Service.objects.bulk_create(services)

        ip_addresses = (
            IPAddress(assigned_object=interface, address='192.0.2.1/24'),
            IPAddress(assigned_object=interface, address='192.0.2.2/24'),
            IPAddress(assigned_object=fhrp_group, address='192.0.2.3/24'),
        )
        IPAddress.objects.bulk_create(ip_addresses)

        owner = Owner.objects.create(name='Owner 1')

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'parent_object_type': ContentType.objects.get_for_model(Device).pk,
            'parent': device.pk,
            'name': 'Service X',
            'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
            'ports': '104,105',
            'ipaddresses': [],
            'description': 'A new service',
            'owner': owner.pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "parent_object_type,parent,name,protocol,ports,ipaddresses,description",
            "dcim.device,Device 1,Service 1,tcp,1,192.0.2.1/24,First service",
            "dcim.device,Device 1,Service 2,tcp,2,192.0.2.2/24,Second service",
            "dcim.device,Device 1,Service 3,udp,3,,Third service",
            "ipam.fhrpgroup,Group 1,Service 4,udp,4,192.0.2.3/24,Fourth service",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{services[0].pk},Service 7,First service7",
            f"{services[1].pk},Service 8,Second service8",
            f"{services[2].pk},Service 9,Third service9",
        )

        cls.bulk_edit_data = {
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '106,107',
            'description': 'New description',
        }

    def test_unassigned_ip_addresses(self):
        self.add_permissions('ipam.view_service', 'dcim.view_device', 'ipam.view_ipaddress')
        device = Device.objects.first()
        addr = IPAddress.objects.create(address='192.0.2.4/24')
        csv_data = (
            "parent_object_type,parent_object_id,name,protocol,ports,ipaddresses,description",
            f"dcim.device,{device.pk},Service 11,tcp,10,{addr.address},Eleventh service",
        )

        initial_count = self._get_queryset().count()
        data = {
            'data': '\n'.join(csv_data),
            'format': ImportFormatChoices.CSV,
            'csv_delimiter': CSVDelimiterChoices.AUTO,
        }

        # Assign model-level permission
        obj_perm = ObjectPermission.objects.create(name='Test permission', actions=['add'])
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Test POST with permission
        response = self.client.post(self._get_url('bulk_import'), data)

        self.assertHttpStatus(response, 200)
        form_errors = response.context['form'].errors
        self.assertEqual(len(form_errors), 1)
        self.assertIn(addr.address, form_errors['__all__'][0])
        self.assertEqual(self._get_queryset().count(), initial_count)

    def test_alternate_csv_import(self):
        self.add_permissions('ipam.view_service', 'dcim.view_device', 'ipam.view_ipaddress')
        device = Device.objects.first()
        interface = device.interfaces.first()
        addr = IPAddress.objects.create(assigned_object=interface, address='192.0.2.3/24')
        csv_data = (
            "parent_object_type,parent_object_id,name,protocol,ports,ipaddresses,description",
            f"dcim.device,{device.pk},Service 11,tcp,10,{addr.address},Eleventh service",
        )

        initial_count = self._get_queryset().count()
        data = {
            'data': '\n'.join(csv_data),
            'format': ImportFormatChoices.CSV,
            'csv_delimiter': CSVDelimiterChoices.AUTO,
        }

        # Assign model-level permission
        obj_perm = ObjectPermission.objects.create(name='Test permission', actions=['add'])
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Test POST with permission
        response = self.client.post(self._get_url('bulk_import'), data)

        if response.status_code != 302:
            self.assertEqual(response.context['form'].errors, {})  # debugging aid
        self.assertHttpStatus(response, 302)
        self.assertEqual(self._get_queryset().count(), initial_count + len(csv_data) - 1)

    def test_create_from_template(self):
        self.add_permissions(
            'ipam.view_service',
            'ipam.add_service',
            'dcim.view_device',
            'ipam.view_servicetemplate',
        )

        device = Device.objects.first()
        service_template = ServiceTemplate.objects.create(
            name='HTTP',
            protocol=ServiceProtocolChoices.PROTOCOL_TCP,
            ports=[80],
            description='Hypertext transfer protocol'
        )

        request = {
            'path': self._get_url('add'),
            'data': {
                'parent_object_type': ContentType.objects.get_for_model(Device).pk,
                'parent': device.pk,
                'service_template': service_template.pk,
            },
        }

        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.parent, device)
        self.assertEqual(instance.name, service_template.name)
        self.assertEqual(instance.protocol, service_template.protocol)
        self.assertEqual(instance.ports, service_template.ports)
        self.assertEqual(instance.description, service_template.description)
