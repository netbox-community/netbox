import netaddr
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ipam.choices import IPAddressRoleChoices, PrefixStatusChoices
from ipam.models import Aggregate, IPAddress, Prefix, RIR, VLAN, VLANGroup, VRF


class TestAggregate(TestCase):

    def test_get_utilization(self):
        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        aggregate = Aggregate(prefix=netaddr.IPNetwork('10.0.0.0/8'), rir=rir)
        aggregate.save()

        # 25% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/12')),
            Prefix(prefix=netaddr.IPNetwork('10.16.0.0/12')),
            Prefix(prefix=netaddr.IPNetwork('10.32.0.0/12')),
            Prefix(prefix=netaddr.IPNetwork('10.48.0.0/12')),
        ))
        self.assertEqual(aggregate.get_utilization(), 25)

        # 50% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.64.0.0/10')),
        ))
        self.assertEqual(aggregate.get_utilization(), 50)

        # 100% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.128.0.0/9')),
        ))
        self.assertEqual(aggregate.get_utilization(), 100)


class TestPrefix(TestCase):

    def test_get_duplicates(self):
        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24')),
            Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24')),
            Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24')),
        ))
        duplicate_prefix_pks = [p.pk for p in prefixes[0].get_duplicates()]

        self.assertSetEqual(set(duplicate_prefix_pks), {prefixes[1].pk, prefixes[2].pk})

    def test_get_child_prefixes(self):
        vrfs = VRF.objects.bulk_create((
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        ))
        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/16'), status=PrefixStatusChoices.STATUS_CONTAINER),
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/24'), vrf=None),
            Prefix(prefix=netaddr.IPNetwork('10.0.1.0/24'), vrf=vrfs[0]),
            Prefix(prefix=netaddr.IPNetwork('10.0.2.0/24'), vrf=vrfs[1]),
            Prefix(prefix=netaddr.IPNetwork('10.0.3.0/24'), vrf=vrfs[2]),
        ))
        child_prefix_pks = {p.pk for p in prefixes[0].get_child_prefixes()}

        # Global container should return all children
        self.assertSetEqual(child_prefix_pks, {prefixes[1].pk, prefixes[2].pk, prefixes[3].pk, prefixes[4].pk})

        prefixes[0].vrf = vrfs[0]
        prefixes[0].save()
        child_prefix_pks = {p.pk for p in prefixes[0].get_child_prefixes()}

        # VRF container is limited to its own VRF
        self.assertSetEqual(child_prefix_pks, {prefixes[2].pk})

    def test_get_child_ips(self):
        vrfs = VRF.objects.bulk_create((
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        ))
        parent_prefix = Prefix.objects.create(
            prefix=netaddr.IPNetwork('10.0.0.0/16'), status=PrefixStatusChoices.STATUS_CONTAINER
        )
        ips = IPAddress.objects.bulk_create((
            IPAddress(address=netaddr.IPNetwork('10.0.0.1/24'), vrf=None),
            IPAddress(address=netaddr.IPNetwork('10.0.1.1/24'), vrf=vrfs[0]),
            IPAddress(address=netaddr.IPNetwork('10.0.2.1/24'), vrf=vrfs[1]),
            IPAddress(address=netaddr.IPNetwork('10.0.3.1/24'), vrf=vrfs[2]),
        ))
        child_ip_pks = {p.pk for p in parent_prefix.get_child_ips()}

        # Global container should return all children
        self.assertSetEqual(child_ip_pks, {ips[0].pk, ips[1].pk, ips[2].pk, ips[3].pk})

        parent_prefix.vrf = vrfs[0]
        parent_prefix.save()
        child_ip_pks = {p.pk for p in parent_prefix.get_child_ips()}

        # VRF container is limited to its own VRF
        self.assertSetEqual(child_ip_pks, {ips[1].pk})

    def test_get_available_prefixes(self):

        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/16')),  # Parent prefix
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/20')),
            Prefix(prefix=netaddr.IPNetwork('10.0.32.0/20')),
            Prefix(prefix=netaddr.IPNetwork('10.0.128.0/18')),
        ))
        missing_prefixes = netaddr.IPSet([
            netaddr.IPNetwork('10.0.16.0/20'),
            netaddr.IPNetwork('10.0.48.0/20'),
            netaddr.IPNetwork('10.0.64.0/18'),
            netaddr.IPNetwork('10.0.192.0/18'),
        ])
        available_prefixes = prefixes[0].get_available_prefixes()

        self.assertEqual(available_prefixes, missing_prefixes)

    def test_get_available_ips(self):

        parent_prefix = Prefix.objects.create(prefix=netaddr.IPNetwork('10.0.0.0/28'))
        IPAddress.objects.bulk_create((
            IPAddress(address=netaddr.IPNetwork('10.0.0.1/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.3/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.5/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.7/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.9/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.11/26')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.13/26')),
        ))
        missing_ips = netaddr.IPSet([
            '10.0.0.2/32',
            '10.0.0.4/32',
            '10.0.0.6/32',
            '10.0.0.8/32',
            '10.0.0.10/32',
            '10.0.0.12/32',
            '10.0.0.14/32',
        ])
        available_ips = parent_prefix.get_available_ips()

        self.assertEqual(available_ips, missing_ips)

    def test_get_first_available_prefix(self):

        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/16')),  # Parent prefix
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/24')),
            Prefix(prefix=netaddr.IPNetwork('10.0.1.0/24')),
            Prefix(prefix=netaddr.IPNetwork('10.0.2.0/24')),
        ))
        self.assertEqual(prefixes[0].get_first_available_prefix(), netaddr.IPNetwork('10.0.3.0/24'))

        Prefix.objects.create(prefix=netaddr.IPNetwork('10.0.3.0/24'))
        self.assertEqual(prefixes[0].get_first_available_prefix(), netaddr.IPNetwork('10.0.4.0/22'))

    def test_get_first_available_ip(self):

        parent_prefix = Prefix.objects.create(prefix=netaddr.IPNetwork('10.0.0.0/24'))
        IPAddress.objects.bulk_create((
            IPAddress(address=netaddr.IPNetwork('10.0.0.1/24')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.2/24')),
            IPAddress(address=netaddr.IPNetwork('10.0.0.3/24')),
        ))
        self.assertEqual(parent_prefix.get_first_available_ip(), '10.0.0.4/24')

        IPAddress.objects.create(address=netaddr.IPNetwork('10.0.0.4/24'))
        self.assertEqual(parent_prefix.get_first_available_ip(), '10.0.0.5/24')

    def test_get_utilization(self):

        # Container Prefix
        prefix = Prefix.objects.create(
            prefix=netaddr.IPNetwork('10.0.0.0/24'),
            status=PrefixStatusChoices.STATUS_CONTAINER
        )
        Prefix.objects.bulk_create((
            Prefix(prefix=netaddr.IPNetwork('10.0.0.0/26')),
            Prefix(prefix=netaddr.IPNetwork('10.0.0.128/26')),
        ))
        self.assertEqual(prefix.get_utilization(), 50)

        # Non-container Prefix
        prefix.status = PrefixStatusChoices.STATUS_ACTIVE
        prefix.save()
        IPAddress.objects.bulk_create(
            # Create 32 IPAddresses within the Prefix
            [IPAddress(address=netaddr.IPNetwork('10.0.0.{}/24'.format(i))) for i in range(1, 33)]
        )
        self.assertEqual(prefix.get_utilization(), 12)  # ~= 12%

    #
    # Uniqueness enforcement tests
    #

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        Prefix.objects.create(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global_unique(self):
        Prefix.objects.create(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        Prefix.objects.create(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        Prefix.objects.create(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)


class TestIPAddress(TestCase):

    def test_get_duplicates(self):
        ips = IPAddress.objects.bulk_create((
            IPAddress(address=netaddr.IPNetwork('192.0.2.1/24')),
            IPAddress(address=netaddr.IPNetwork('192.0.2.1/24')),
            IPAddress(address=netaddr.IPNetwork('192.0.2.1/24')),
        ))
        duplicate_ip_pks = [p.pk for p in ips[0].get_duplicates()]

        self.assertSetEqual(set(duplicate_ip_pks), {ips[1].pk, ips[2].pk})

    #
    # Uniqueness enforcement tests
    #

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global_unique(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        IPAddress.objects.create(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        IPAddress.objects.create(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_nonunique_role(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)


class TestVLANGroup(TestCase):

    def test_get_next_available_vid(self):

        vlangroup = VLANGroup.objects.create(name='VLAN Group 1', slug='vlan-group-1')
        VLAN.objects.bulk_create((
            VLAN(name='VLAN 1', vid=1, group=vlangroup),
            VLAN(name='VLAN 2', vid=2, group=vlangroup),
            VLAN(name='VLAN 3', vid=3, group=vlangroup),
            VLAN(name='VLAN 5', vid=5, group=vlangroup),
        ))
        self.assertEqual(vlangroup.get_next_available_vid(), 4)

        VLAN.objects.bulk_create((
            VLAN(name='VLAN 4', vid=4, group=vlangroup),
        ))
        self.assertEqual(vlangroup.get_next_available_vid(), 6)
