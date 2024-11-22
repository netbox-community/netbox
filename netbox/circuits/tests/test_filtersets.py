from django.test import TestCase

from circuits.choices import *
from circuits.filtersets import *
from circuits.models import *
from dcim.choices import InterfaceTypeChoices
from dcim.models import Cable, Device, DeviceRole, DeviceType, Interface, Manufacturer, Region, Site, SiteGroup
from ipam.models import ASN, RIR
from netbox.choices import DistanceUnitChoices
from tenancy.models import Tenant, TenantGroup
from utilities.testing import ChangeLoggedFilterSetTests


class ProviderTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Provider.objects.all()
    filterset = ProviderFilterSet

    @classmethod
    def setUpTestData(cls):

        rir = RIR.objects.create(name='RFC 6996', is_private=True)
        asns = (
            ASN(asn=64512, rir=rir),
            ASN(asn=64513, rir=rir),
            ASN(asn=64514, rir=rir),
        )
        ASN.objects.bulk_create(asns)

        providers = (
            Provider(name='Provider 1', slug='provider-1', description='foobar1'),
            Provider(name='Provider 2', slug='provider-2', description='foobar2'),
            Provider(name='Provider 3', slug='provider-3'),
            Provider(name='Provider 4', slug='provider-4'),
            Provider(name='Provider 5', slug='provider-5'),
        )
        Provider.objects.bulk_create(providers)
        providers[0].asns.set([asns[0]])
        providers[1].asns.set([asns[1]])
        providers[2].asns.set([asns[2]])

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
        )
        Site.objects.bulk_create(sites)

        circuit_types = (
            CircuitType(name='Test Circuit Type 1', slug='test-circuit-type-1'),
            CircuitType(name='Test Circuit Type 2', slug='test-circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(provider=providers[0], type=circuit_types[0], cid='Circuit 1'),
            Circuit(provider=providers[1], type=circuit_types[1], cid='Circuit 2'),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = (
            CircuitTermination(circuit=circuits[0], termination=sites[0], term_side='A'),
            CircuitTermination(circuit=circuits[1], termination=sites[0], term_side='A'),
        )
        for ct in circuit_terminations:
            ct.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Provider 1', 'Provider 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['provider-1', 'provider-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        asns = ASN.objects.all()[:2]
        params = {'asn_id': [asns[0].pk, asns[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'asn': [asns[0].asn, asns[1].asn]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CircuitTypeTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CircuitType.objects.all()
    filterset = CircuitTypeFilterSet

    @classmethod
    def setUpTestData(cls):

        CircuitType.objects.bulk_create((
            CircuitType(name='Circuit Type 1', slug='circuit-type-1', description='foobar1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2', description='foobar2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        ))

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Circuit Type 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_slug(self):
        params = {'slug': ['circuit-type-1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CircuitTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Circuit.objects.all()
    filterset = CircuitFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2], group=site_groups[2]),
        )
        Site.objects.bulk_create(sites)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        circuit_types = (
            CircuitType(name='Test Circuit Type 1', slug='test-circuit-type-1'),
            CircuitType(name='Test Circuit Type 2', slug='test-circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='A'),
            ProviderAccount(name='Provider Account 2', provider=providers[1], account='B'),
            ProviderAccount(name='Provider Account 3', provider=providers[2], account='C'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[1]),
            ProviderNetwork(name='Provider Network 2', provider=providers[1]),
            ProviderNetwork(name='Provider Network 3', provider=providers[1]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        circuits = (
            Circuit(
                provider=providers[0],
                provider_account=provider_accounts[0],
                tenant=tenants[0],
                type=circuit_types[0],
                cid='Test Circuit 1',
                install_date='2020-01-01',
                termination_date='2021-01-01',
                commit_rate=1000,
                status=CircuitStatusChoices.STATUS_ACTIVE,
                description='foobar1',
                distance=10,
                distance_unit=DistanceUnitChoices.UNIT_FOOT,
            ),
            Circuit(
                provider=providers[0],
                provider_account=provider_accounts[0],
                tenant=tenants[0],
                type=circuit_types[0],
                cid='Test Circuit 2',
                install_date='2020-01-02',
                termination_date='2021-01-02',
                commit_rate=2000,
                status=CircuitStatusChoices.STATUS_ACTIVE,
                description='foobar2',
                distance=20,
                distance_unit=DistanceUnitChoices.UNIT_METER,
            ),
            Circuit(
                provider=providers[0],
                provider_account=provider_accounts[1],
                tenant=tenants[1],
                type=circuit_types[0],
                cid='Test Circuit 3',
                install_date='2020-01-03',
                termination_date='2021-01-03',
                commit_rate=3000,
                status=CircuitStatusChoices.STATUS_PLANNED,
                distance=30,
                distance_unit=DistanceUnitChoices.UNIT_METER,
            ),
            Circuit(
                provider=providers[1],
                provider_account=provider_accounts[1],
                tenant=tenants[1],
                type=circuit_types[1],
                cid='Test Circuit 4',
                install_date='2020-01-04',
                termination_date='2021-01-04',
                commit_rate=4000,
                status=CircuitStatusChoices.STATUS_PLANNED,
            ),
            Circuit(
                provider=providers[1],
                provider_account=provider_accounts[2],
                tenant=tenants[2],
                type=circuit_types[1],
                cid='Test Circuit 5',
                install_date='2020-01-05',
                termination_date='2021-01-05',
                commit_rate=5000,
                status=CircuitStatusChoices.STATUS_OFFLINE,
            ),
            Circuit(
                provider=providers[1],
                provider_account=provider_accounts[2],
                tenant=tenants[2],
                type=circuit_types[1],
                cid='Test Circuit 6',
                install_date='2020-01-06',
                termination_date='2021-01-06',
                commit_rate=6000,
                status=CircuitStatusChoices.STATUS_OFFLINE,
            ),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = ((
            CircuitTermination(circuit=circuits[0], termination=sites[0], term_side='A'),
            CircuitTermination(circuit=circuits[1], termination=sites[1], term_side='A'),
            CircuitTermination(circuit=circuits[2], termination=sites[2], term_side='A'),
            CircuitTermination(circuit=circuits[3], termination=provider_networks[0], term_side='A'),
            CircuitTermination(circuit=circuits[4], termination=provider_networks[1], term_side='A'),
            CircuitTermination(circuit=circuits[5], termination=provider_networks[2], term_side='A'),
        ))
        for ct in circuit_terminations:
            ct.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_cid(self):
        params = {'cid': ['Test Circuit 1', 'Test Circuit 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_install_date(self):
        params = {'install_date': ['2020-01-01', '2020-01-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_termination_date(self):
        params = {'termination_date': ['2021-01-01', '2021-01-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_commit_rate(self):
        params = {'commit_rate': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider(self):
        provider = Provider.objects.first()
        params = {'provider_id': [provider.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'provider': [provider.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_provider_account(self):
        provider_accounts = ProviderAccount.objects.all()[:2]
        params = {'provider_account_id': [provider_accounts[0].pk, provider_accounts[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider_network(self):
        provider_networks = ProviderNetwork.objects.all()[:2]
        params = {'provider_network_id': [provider_networks[0].pk, provider_networks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        circuit_type = CircuitType.objects.first()
        params = {'type_id': [circuit_type.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'type': [circuit_type.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_status(self):
        params = {'status': [CircuitStatusChoices.STATUS_ACTIVE, CircuitStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_distance(self):
        params = {'distance': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_distance_unit(self):
        params = {'distance_unit': DistanceUnitChoices.UNIT_FOOT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class CircuitTerminationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CircuitTermination.objects.all()
    filterset = CircuitTerminationFilterSet
    ignore_fields = ('cable',)

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        circuit_types = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[0]),
            ProviderNetwork(name='Provider Network 2', provider=providers[1]),
            ProviderNetwork(name='Provider Network 3', provider=providers[2]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        circuits = (
            Circuit(provider=providers[0], type=circuit_types[0], cid='Circuit 1'),
            Circuit(provider=providers[1], type=circuit_types[0], cid='Circuit 2'),
            Circuit(provider=providers[2], type=circuit_types[0], cid='Circuit 3'),
            Circuit(provider=providers[0], type=circuit_types[0], cid='Circuit 4'),
            Circuit(provider=providers[1], type=circuit_types[0], cid='Circuit 5'),
            Circuit(provider=providers[2], type=circuit_types[0], cid='Circuit 6'),
            Circuit(provider=providers[2], type=circuit_types[0], cid='Circuit 7'),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = (
            CircuitTermination(
                circuit=circuits[0],
                termination=sites[0],
                term_side='A',
                port_speed=1000,
                upstream_speed=1000,
                xconnect_id='ABC',
                description='foobar1',
            ),
            CircuitTermination(
                circuit=circuits[0],
                termination=sites[1],
                term_side='Z',
                port_speed=1000,
                upstream_speed=1000,
                xconnect_id='DEF',
                description='foobar2',
            ),
            CircuitTermination(
                circuit=circuits[1],
                termination=sites[1],
                term_side='A',
                port_speed=2000,
                upstream_speed=2000,
                xconnect_id='GHI',
            ),
            CircuitTermination(
                circuit=circuits[1],
                termination=sites[2],
                term_side='Z',
                port_speed=2000,
                upstream_speed=2000,
                xconnect_id='JKL',
            ),
            CircuitTermination(
                circuit=circuits[2],
                termination=sites[2],
                term_side='A',
                port_speed=3000,
                upstream_speed=3000,
                xconnect_id='MNO',
            ),
            CircuitTermination(
                circuit=circuits[2],
                termination=sites[0],
                term_side='Z',
                port_speed=3000,
                upstream_speed=3000,
                xconnect_id='PQR',
            ),
            CircuitTermination(circuit=circuits[3], termination=provider_networks[0], term_side='A'),
            CircuitTermination(circuit=circuits[4], termination=provider_networks[1], term_side='A'),
            CircuitTermination(circuit=circuits[5], termination=provider_networks[2], term_side='A'),
            CircuitTermination(
                circuit=circuits[6], termination=provider_networks[0], term_side='A', mark_connected=True
            ),
        )
        for ct in circuit_terminations:
            ct.save()

        Cable(a_terminations=[circuit_terminations[0]], b_terminations=[circuit_terminations[1]]).save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_term_side(self):
        params = {'term_side': 'A'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 7)

    def test_port_speed(self):
        params = {'port_speed': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_upstream_speed(self):
        params = {'upstream_speed': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_xconnect_id(self):
        params = {'xconnect_id': ['ABC', 'DEF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_circuit_id(self):
        circuits = Circuit.objects.filter(cid__in=['Circuit 1', 'Circuit 2'])
        params = {'circuit_id': [circuits[0].pk, circuits[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider_network(self):
        provider_networks = ProviderNetwork.objects.all()[:2]
        params = {'provider_network_id': [provider_networks[0].pk, provider_networks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 7)


class CircuitGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CircuitGroup.objects.all()
    filterset = CircuitGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        CircuitGroup.objects.bulk_create((
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1', description='foobar1', tenant=tenants[0]),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2', description='foobar2', tenant=tenants[1]),
            CircuitGroup(name='Circuit Group 3', slug='circuit-group-3', tenant=tenants[1]),
        ))

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Circuit Group 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_slug(self):
        params = {'slug': ['circuit-group-1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class CircuitGroupAssignmentTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CircuitGroupAssignment.objects.all()
    filterset = CircuitGroupAssignmentFilterSet

    @classmethod
    def setUpTestData(cls):

        circuit_groups = (
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1'),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2'),
            CircuitGroup(name='Circuit Group 3', slug='circuit-group-3'),
            CircuitGroup(name='Circuit Group 4', slug='circuit-group-4'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)

        providers = Provider.objects.bulk_create((
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
            Provider(name='Provider 4', slug='provider-4'),
        ))
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        circuits = (
            Circuit(cid='Circuit 1', provider=providers[0], type=circuittype),
            Circuit(cid='Circuit 2', provider=providers[1], type=circuittype),
            Circuit(cid='Circuit 3', provider=providers[2], type=circuittype),
            Circuit(cid='Circuit 4', provider=providers[3], type=circuittype),
        )
        Circuit.objects.bulk_create(circuits)

        assignments = (
            CircuitGroupAssignment(
                group=circuit_groups[0],
                circuit=circuits[0],
                priority=CircuitPriorityChoices.PRIORITY_PRIMARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[1],
                circuit=circuits[1],
                priority=CircuitPriorityChoices.PRIORITY_SECONDARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[2],
                circuit=circuits[2],
                priority=CircuitPriorityChoices.PRIORITY_TERTIARY
            ),
        )
        CircuitGroupAssignment.objects.bulk_create(assignments)

    def test_group_id(self):
        groups = CircuitGroup.objects.filter(name__in=['Circuit Group 1', 'Circuit Group 2'])
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_circuit(self):
        circuits = Circuit.objects.all()[:2]
        params = {'circuit_id': [circuits[0].pk, circuits[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'circuit': [circuits[0].cid, circuits[1].cid]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ProviderNetworkTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ProviderNetwork.objects.all()
    filterset = ProviderNetworkFilterSet

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[0], description='foobar1'),
            ProviderNetwork(name='Provider Network 2', provider=providers[1], description='foobar2'),
            ProviderNetwork(name='Provider Network 3', provider=providers[2]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Provider Network 1', 'Provider Network 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ProviderAccountTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ProviderAccount.objects.all()
    filterset = ProviderAccountFilterSet

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], description='foobar1', account='1234'),
            ProviderAccount(name='Provider Account 2', provider=providers[1], description='foobar2', account='2345'),
            ProviderAccount(name='Provider Account 3', provider=providers[2], account='3456'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Provider Account 1', 'Provider Account 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_account(self):
        params = {'account': ['1234', '3456']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class VirtualCircuitTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = VirtualCircuit.objects.all()
    filterset = VirtualCircuitFilterSet

    @classmethod
    def setUpTestData(cls):

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='A'),
            ProviderAccount(name='Provider Account 2', provider=providers[1], account='B'),
            ProviderAccount(name='Provider Account 3', provider=providers[2], account='C'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[0]),
            ProviderNetwork(name='Provider Network 2', provider=providers[1]),
            ProviderNetwork(name='Provider Network 3', provider=providers[2]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        virutal_circuits = (
            VirtualCircuit(
                provider_network=provider_networks[0],
                provider_account=provider_accounts[0],
                tenant=tenants[0],
                cid='Virtual Circuit 1',
                status=CircuitStatusChoices.STATUS_PLANNED,
                description='virtualcircuit1',
            ),
            VirtualCircuit(
                provider_network=provider_networks[1],
                provider_account=provider_accounts[1],
                tenant=tenants[1],
                cid='Virtual Circuit 2',
                status=CircuitStatusChoices.STATUS_ACTIVE,
                description='virtualcircuit2',
            ),
            VirtualCircuit(
                provider_network=provider_networks[2],
                provider_account=provider_accounts[2],
                tenant=tenants[2],
                cid='Virtual Circuit 3',
                status=CircuitStatusChoices.STATUS_DEPROVISIONING,
                description='virtualcircuit3',
            ),
        )
        VirtualCircuit.objects.bulk_create(virutal_circuits)

    def test_q(self):
        params = {'q': 'virtualcircuit1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_cid(self):
        params = {'cid': ['Virtual Circuit 1', 'Virtual Circuit 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider_account(self):
        provider_accounts = ProviderAccount.objects.all()[:2]
        params = {'provider_account_id': [provider_accounts[0].pk, provider_accounts[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_provider_network(self):
        provider_networks = ProviderNetwork.objects.all()[:2]
        params = {'provider_network_id': [provider_networks[0].pk, provider_networks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [CircuitStatusChoices.STATUS_ACTIVE, CircuitStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['virtualcircuit1', 'virtualcircuit2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class VirtualCircuitTerminationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = VirtualCircuitTermination.objects.all()
    filterset = VirtualCircuitTerminationFilterSet

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        site = Site.objects.create(name='Site 1', slug='site-1')

        devices = (
            Device(site=site, name='Device 1', device_type=device_type, role=device_role),
            Device(site=site, name='Device 2', device_type=device_type, role=device_role),
            Device(site=site, name='Device 3', device_type=device_type, role=device_role),
        )
        Device.objects.bulk_create(devices)

        virtual_interfaces = (
            # Device 1
            Interface(
                device=devices[0],
                name='eth0.1',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[0],
                name='eth0.2',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            # Device 2
            Interface(
                device=devices[1],
                name='eth0.1',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[1],
                name='eth0.2',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            # Device 3
            Interface(
                device=devices[2],
                name='eth0.1',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[2],
                name='eth0.2',
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
        )
        Interface.objects.bulk_create(virtual_interfaces)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)
        provider_networks = (
            ProviderNetwork(provider=providers[0], name='Provider Network 1'),
            ProviderNetwork(provider=providers[1], name='Provider Network 2'),
            ProviderNetwork(provider=providers[2], name='Provider Network 3'),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)
        provider_accounts = (
            ProviderAccount(provider=providers[0], account='Provider Account 1'),
            ProviderAccount(provider=providers[1], account='Provider Account 2'),
            ProviderAccount(provider=providers[2], account='Provider Account 3'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        virtual_circuits = (
            VirtualCircuit(
                provider_network=provider_networks[0],
                provider_account=provider_accounts[0],
                cid='Virtual Circuit 1'
            ),
            VirtualCircuit(
                provider_network=provider_networks[1],
                provider_account=provider_accounts[1],
                cid='Virtual Circuit 2'
            ),
            VirtualCircuit(
                provider_network=provider_networks[2],
                provider_account=provider_accounts[2],
                cid='Virtual Circuit 3'
            ),
        )
        VirtualCircuit.objects.bulk_create(virtual_circuits)

        virtual_circuit_terminations = (
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[0],
                role=VirtualCircuitTerminationRoleChoices.ROLE_HUB,
                interface=virtual_interfaces[0],
                description='termination1'
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[0],
                role=VirtualCircuitTerminationRoleChoices.ROLE_SPOKE,
                interface=virtual_interfaces[3],
                description='termination2'
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[1],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[1],
                description='termination3'
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[1],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[4],
                description='termination4'
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[2],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[2],
                description='termination5'
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[2],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[5],
                description='termination6'
            ),
        )
        VirtualCircuitTermination.objects.bulk_create(virtual_circuit_terminations)

    def test_q(self):
        params = {'q': 'termination1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['termination1', 'termination2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_circuit_id(self):
        virtual_circuits = VirtualCircuit.objects.filter()[:2]
        params = {'virtual_circuit_id': [virtual_circuits[0].pk, virtual_circuits[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider(self):
        providers = Provider.objects.all()[:2]
        params = {'provider_id': [providers[0].pk, providers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'provider': [providers[0].slug, providers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider_network(self):
        provider_networks = ProviderNetwork.objects.all()[:2]
        params = {'provider_network_id': [provider_networks[0].pk, provider_networks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_provider_account(self):
        provider_accounts = ProviderAccount.objects.all()[:2]
        params = {'provider_account_id': [provider_accounts[0].pk, provider_accounts[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'provider_account': [provider_accounts[0].account, provider_accounts[1].account]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
