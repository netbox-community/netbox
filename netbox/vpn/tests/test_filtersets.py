from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, Interface, Site
from ipam.models import IPAddress, VLAN, RouteTarget
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device, create_test_virtualmachine
from virtualization.models import VirtualMachine, VMInterface
from vpn.choices import *
from vpn.filtersets import *
from vpn.models import *


class TunnelGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = TunnelGroup.objects.all()
    filterset = TunnelGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        TunnelGroup.objects.bulk_create((
            TunnelGroup(name='Tunnel Group 1', slug='tunnel-group-1', description='foobar1'),
            TunnelGroup(name='Tunnel Group 2', slug='tunnel-group-2', description='foobar2'),
            TunnelGroup(name='Tunnel Group 3', slug='tunnel-group-3'),
        ))

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Tunnel Group 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_slug(self):
        params = {'slug': ['tunnel-group-1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TunnelTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Tunnel.objects.all()
    filterset = TunnelFilterSet

    @classmethod
    def setUpTestData(cls):
        ike_proposal = IKEProposal.objects.create(
            name='IKE Proposal 1',
            authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
            encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
            authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
            group=DHGroupChoices.GROUP_14
        )
        ike_policy = IKEPolicy.objects.create(
            name='IKE Policy 1',
            version=IKEVersionChoices.VERSION_1,
            mode=IKEModeChoices.MAIN,
        )
        ike_policy.proposals.add(ike_proposal)
        ipsec_proposal = IPSecProposal.objects.create(
            name='IPSec Proposal 1',
            encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
            authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1
        )
        ipsec_policy = IPSecPolicy.objects.create(
            name='IPSec Policy 1',
            pfs_group=DHGroupChoices.GROUP_14
        )
        ipsec_policy.proposals.add(ipsec_proposal)
        ipsec_profiles = (
            IPSecProfile(
                name='IPSec Profile 1',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policy,
                ipsec_policy=ipsec_policy
            ),
            IPSecProfile(
                name='IPSec Profile 2',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policy,
                ipsec_policy=ipsec_policy
            ),
        )
        IPSecProfile.objects.bulk_create(ipsec_profiles)

        tunnel_groups = (
            TunnelGroup(name='Tunnel Group 1', slug='tunnel-group-1'),
            TunnelGroup(name='Tunnel Group 2', slug='tunnel-group-2'),
            TunnelGroup(name='Tunnel Group 3', slug='tunnel-group-3'),
        )
        TunnelGroup.objects.bulk_create(tunnel_groups)

        tunnels = (
            Tunnel(
                name='Tunnel 1',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                group=tunnel_groups[0],
                encapsulation=TunnelEncapsulationChoices.ENCAP_GRE,
                ipsec_profile=ipsec_profiles[0],
                tunnel_id=100,
                description='foobar1'
            ),
            Tunnel(
                name='Tunnel 2',
                status=TunnelStatusChoices.STATUS_PLANNED,
                group=tunnel_groups[1],
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP,
                ipsec_profile=ipsec_profiles[0],
                tunnel_id=200,
                description='foobar2'
            ),
            Tunnel(
                name='Tunnel 3',
                status=TunnelStatusChoices.STATUS_DISABLED,
                group=tunnel_groups[2],
                encapsulation=TunnelEncapsulationChoices.ENCAP_IPSEC_TUNNEL,
                ipsec_profile=None,
                tunnel_id=300,
                description='foobar3'
            ),
        )
        Tunnel.objects.bulk_create(tunnels)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Tunnel 1', 'Tunnel 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [TunnelStatusChoices.STATUS_ACTIVE, TunnelStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        tunnel_groups = TunnelGroup.objects.all()[:2]
        params = {'group_id': [tunnel_groups[0].pk, tunnel_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [tunnel_groups[0].slug, tunnel_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_encapsulation(self):
        params = {'encapsulation': [TunnelEncapsulationChoices.ENCAP_GRE, TunnelEncapsulationChoices.ENCAP_IP_IP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ipsec_profile(self):
        ipsec_profiles = IPSecProfile.objects.all()[:2]
        params = {'ipsec_profile_id': [ipsec_profiles[0].pk, ipsec_profiles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ipsec_profile': [ipsec_profiles[0].name, ipsec_profiles[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tunnel_id(self):
        params = {'tunnel_id': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TunnelTerminationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = TunnelTermination.objects.all()
    filterset = TunnelTerminationFilterSet

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        interfaces = (
            Interface(device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 2', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 3', type=InterfaceTypeChoices.TYPE_VIRTUAL),
        )
        Interface.objects.bulk_create(interfaces)

        virtual_machine = create_test_virtualmachine('Virtual Machine 1')
        vm_interfaces = (
            VMInterface(virtual_machine=virtual_machine, name='Interface 1'),
            VMInterface(virtual_machine=virtual_machine, name='Interface 2'),
            VMInterface(virtual_machine=virtual_machine, name='Interface 3'),
        )
        VMInterface.objects.bulk_create(vm_interfaces)

        ip_addresses = (
            IPAddress(address='192.168.0.1/32'),
            IPAddress(address='192.168.0.2/32'),
            IPAddress(address='192.168.0.3/32'),
            IPAddress(address='192.168.0.4/32'),
            IPAddress(address='192.168.0.5/32'),
            IPAddress(address='192.168.0.6/32'),
        )
        IPAddress.objects.bulk_create(ip_addresses)

        tunnels = (
            Tunnel(
                name='Tunnel 1',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
            Tunnel(
                name='Tunnel 2',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
            Tunnel(
                name='Tunnel 3',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
        )
        Tunnel.objects.bulk_create(tunnels)

        tunnel_terminations = (
            # Tunnel 1
            TunnelTermination(
                tunnel=tunnels[0],
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                termination=interfaces[0],
                outside_ip=ip_addresses[0]
            ),
            TunnelTermination(
                tunnel=tunnels[0],
                role=TunnelTerminationRoleChoices.ROLE_SPOKE,
                termination=vm_interfaces[0],
                outside_ip=ip_addresses[1]
            ),
            # Tunnel 2
            TunnelTermination(
                tunnel=tunnels[1],
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                termination=interfaces[1],
                outside_ip=ip_addresses[2]
            ),
            TunnelTermination(
                tunnel=tunnels[1],
                role=TunnelTerminationRoleChoices.ROLE_SPOKE,
                termination=vm_interfaces[1],
                outside_ip=ip_addresses[3]
            ),
            # Tunnel 3
            TunnelTermination(
                tunnel=tunnels[2],
                role=TunnelTerminationRoleChoices.ROLE_PEER,
                termination=interfaces[2],
                outside_ip=ip_addresses[4]
            ),
            TunnelTermination(
                tunnel=tunnels[2],
                role=TunnelTerminationRoleChoices.ROLE_PEER,
                termination=vm_interfaces[2],
                outside_ip=ip_addresses[5]
            ),
        )
        TunnelTermination.objects.bulk_create(tunnel_terminations)

    def test_tunnel(self):
        tunnels = Tunnel.objects.all()[:2]
        params = {'tunnel_id': [tunnels[0].pk, tunnels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tunnel': [tunnels[0].name, tunnels[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_role(self):
        params = {'role': [TunnelTerminationRoleChoices.ROLE_HUB, TunnelTerminationRoleChoices.ROLE_SPOKE]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_termination_type(self):
        params = {'termination_type': 'dcim.interface'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'termination_type': 'virtualization.vminterface'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interface': [interfaces[0].name, interfaces[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vminterface(self):
        vm_interfaces = VMInterface.objects.all()[:2]
        params = {'vminterface_id': [vm_interfaces[0].pk, vm_interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vminterface': [vm_interfaces[0].name, vm_interfaces[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outside_ip(self):
        ip_addresses = IPAddress.objects.all()[:2]
        params = {'outside_ip_id': [ip_addresses[0].pk, ip_addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class IKEProposalTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = IKEProposal.objects.all()
    filterset = IKEProposalFilterSet

    @classmethod
    def setUpTestData(cls):
        ike_proposals = (
            IKEProposal(
                name='IKE Proposal 1',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_1,
                sa_lifetime=1000,
                description='foobar1'
            ),
            IKEProposal(
                name='IKE Proposal 2',
                authentication_method=AuthenticationMethodChoices.CERTIFICATES,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                group=DHGroupChoices.GROUP_2,
                sa_lifetime=2000,
                description='foobar2'
            ),
            IKEProposal(
                name='IKE Proposal 3',
                authentication_method=AuthenticationMethodChoices.RSA_SIGNATURES,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA512,
                group=DHGroupChoices.GROUP_5,
                sa_lifetime=3000,
                description='foobar3'
            ),
        )
        IKEProposal.objects.bulk_create(ike_proposals)

        ike_policies = (
            IKEPolicy(name='IKE Policy 1'),
            IKEPolicy(name='IKE Policy 2'),
            IKEPolicy(name='IKE Policy 3'),
        )
        IKEPolicy.objects.bulk_create(ike_policies)
        ike_policies[0].proposals.add(ike_proposals[0])
        ike_policies[1].proposals.add(ike_proposals[1])
        ike_policies[2].proposals.add(ike_proposals[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['IKE Proposal 1', 'IKE Proposal 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ike_policy(self):
        ike_policies = IKEPolicy.objects.all()[:2]
        params = {'ike_policy_id': [ike_policies[0].pk, ike_policies[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ike_policy': [ike_policies[0].name, ike_policies[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_authentication_method(self):
        params = {'authentication_method': [
            AuthenticationMethodChoices.PRESHARED_KEYS, AuthenticationMethodChoices.CERTIFICATES
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_encryption_algorithm(self):
        params = {'encryption_algorithm': [
            EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC, EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_authentication_algorithm(self):
        params = {'authentication_algorithm': [
            AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1, AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        params = {'group': [DHGroupChoices.GROUP_1, DHGroupChoices.GROUP_2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_sa_lifetime(self):
        params = {'sa_lifetime': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class IKEPolicyTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = IKEPolicy.objects.all()
    filterset = IKEPolicyFilterSet

    @classmethod
    def setUpTestData(cls):
        ike_proposals = (
            IKEProposal(
                name='IKE Proposal 1',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14
            ),
            IKEProposal(
                name='IKE Proposal 2',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14
            ),
            IKEProposal(
                name='IKE Proposal 3',
                authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                group=DHGroupChoices.GROUP_14
            ),
        )
        IKEProposal.objects.bulk_create(ike_proposals)

        ike_policies = (
            IKEPolicy(
                name='IKE Policy 1',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
                description='foobar1'
            ),
            IKEPolicy(
                name='IKE Policy 2',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
                description='foobar2'
            ),
            IKEPolicy(
                name='IKE Policy 3',
                version=IKEVersionChoices.VERSION_2,
                mode=IKEModeChoices.AGGRESSIVE,
                description='foobar3'
            ),
        )
        IKEPolicy.objects.bulk_create(ike_policies)
        ike_policies[0].proposals.add(ike_proposals[0])
        ike_policies[1].proposals.add(ike_proposals[1])
        ike_policies[2].proposals.add(ike_proposals[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['IKE Policy 1', 'IKE Policy 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_version(self):
        params = {'version': [IKEVersionChoices.VERSION_1]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mode(self):
        params = {'mode': [IKEModeChoices.MAIN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ike_proposal(self):
        proposals = IKEProposal.objects.all()[:2]
        params = {'ike_proposal_id': [proposals[0].pk, proposals[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ike_proposal': [proposals[0].name, proposals[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class IPSecProposalTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = IPSecProposal.objects.all()
    filterset = IPSecProposalFilterSet

    @classmethod
    def setUpTestData(cls):
        ipsec_proposals = (
            IPSecProposal(
                name='IPSec Proposal 1',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
                sa_lifetime_seconds=1000,
                sa_lifetime_data=1000,
                description='foobar1'
            ),
            IPSecProposal(
                name='IPSec Proposal 2',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                sa_lifetime_seconds=2000,
                sa_lifetime_data=2000,
                description='foobar2'
            ),
            IPSecProposal(
                name='IPSec Proposal 3',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA512,
                sa_lifetime_seconds=3000,
                sa_lifetime_data=3000,
                description='foobar3'
            ),
        )
        IPSecProposal.objects.bulk_create(ipsec_proposals)

        ipsec_policies = (
            IPSecPolicy(name='IPSec Policy 1'),
            IPSecPolicy(name='IPSec Policy 2'),
            IPSecPolicy(name='IPSec Policy 3'),
        )
        IPSecPolicy.objects.bulk_create(ipsec_policies)
        ipsec_policies[0].proposals.add(ipsec_proposals[0])
        ipsec_policies[1].proposals.add(ipsec_proposals[1])
        ipsec_policies[2].proposals.add(ipsec_proposals[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['IPSec Proposal 1', 'IPSec Proposal 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ipsec_policy(self):
        ipsec_policies = IPSecPolicy.objects.all()[:2]
        params = {'ipsec_policy_id': [ipsec_policies[0].pk, ipsec_policies[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ipsec_policy': [ipsec_policies[0].name, ipsec_policies[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_encryption_algorithm(self):
        params = {'encryption_algorithm': [
            EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC, EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_authentication_algorithm(self):
        params = {'authentication_algorithm': [
            AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1, AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_sa_lifetime_seconds(self):
        params = {'sa_lifetime_seconds': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_sa_lifetime_data(self):
        params = {'sa_lifetime_data': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class IPSecPolicyTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = IPSecPolicy.objects.all()
    filterset = IPSecPolicyFilterSet

    @classmethod
    def setUpTestData(cls):
        ipsec_proposals = (
            IPSecProposal(
                name='IPSec Policy 1',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1
            ),
            IPSecProposal(
                name='IPSec Proposal 2',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1
            ),
            IPSecProposal(
                name='IPSec Proposal 3',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1
            ),
        )
        IPSecProposal.objects.bulk_create(ipsec_proposals)

        ipsec_policies = (
            IPSecPolicy(
                name='IPSec Policy 1',
                pfs_group=DHGroupChoices.GROUP_1,
                description='foobar1'
            ),
            IPSecPolicy(
                name='IPSec Policy 2',
                pfs_group=DHGroupChoices.GROUP_2,
                description='foobar2'
            ),
            IPSecPolicy(
                name='IPSec Policy 3',
                pfs_group=DHGroupChoices.GROUP_5,
                description='foobar3'
            ),
        )
        IPSecPolicy.objects.bulk_create(ipsec_policies)
        ipsec_policies[0].proposals.add(ipsec_proposals[0])
        ipsec_policies[1].proposals.add(ipsec_proposals[1])
        ipsec_policies[2].proposals.add(ipsec_proposals[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['IPSec Policy 1', 'IPSec Policy 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_pfs_group(self):
        params = {'pfs_group': [DHGroupChoices.GROUP_1, DHGroupChoices.GROUP_2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ipsec_proposal(self):
        proposals = IPSecProposal.objects.all()[:2]
        params = {'ipsec_proposal_id': [proposals[0].pk, proposals[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ipsec_proposal': [proposals[0].name, proposals[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class IPSecProfileTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = IPSecProfile.objects.all()
    filterset = IPSecProfileFilterSet

    @classmethod
    def setUpTestData(cls):
        ike_proposal = IKEProposal.objects.create(
            name='IKE Proposal 1',
            authentication_method=AuthenticationMethodChoices.PRESHARED_KEYS,
            encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
            authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
            group=DHGroupChoices.GROUP_14
        )
        ipsec_proposal = IPSecProposal.objects.create(
            name='IPSec Proposal 1',
            encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
            authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1
        )

        ike_policies = (
            IKEPolicy(
                name='IKE Policy 1',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
            ),
            IKEPolicy(
                name='IKE Policy 2',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
            ),
            IKEPolicy(
                name='IKE Policy 3',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
            ),
        )
        IKEPolicy.objects.bulk_create(ike_policies)
        for ike_policy in ike_policies:
            ike_policy.proposals.add(ike_proposal)

        ipsec_policies = (
            IPSecPolicy(
                name='IPSec Policy 1',
                pfs_group=DHGroupChoices.GROUP_14
            ),
            IPSecPolicy(
                name='IPSec Policy 2',
                pfs_group=DHGroupChoices.GROUP_14
            ),
            IPSecPolicy(
                name='IPSec Policy 3',
                pfs_group=DHGroupChoices.GROUP_14
            ),
        )
        IPSecPolicy.objects.bulk_create(ipsec_policies)
        for ipsec_policy in ipsec_policies:
            ipsec_policy.proposals.add(ipsec_proposal)

        ipsec_profiles = (
            IPSecProfile(
                name='IPSec Profile 1',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policies[0],
                ipsec_policy=ipsec_policies[0],
                description='foobar1'
            ),
            IPSecProfile(
                name='IPSec Profile 2',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policies[1],
                ipsec_policy=ipsec_policies[1],
                description='foobar2'
            ),
            IPSecProfile(
                name='IPSec Profile 3',
                mode=IPSecModeChoices.AH,
                ike_policy=ike_policies[2],
                ipsec_policy=ipsec_policies[2],
                description='foobar3'
            ),
        )
        IPSecProfile.objects.bulk_create(ipsec_profiles)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['IPSec Profile 1', 'IPSec Profile 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mode(self):
        params = {'mode': [IPSecModeChoices.ESP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ike_policy(self):
        ike_policies = IKEPolicy.objects.all()[:2]
        params = {'ike_policy_id': [ike_policies[0].pk, ike_policies[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ike_policy': [ike_policies[0].name, ike_policies[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ipsec_policy(self):
        ipsec_policies = IPSecPolicy.objects.all()[:2]
        params = {'ipsec_policy_id': [ipsec_policies[0].pk, ipsec_policies[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'ipsec_policy': [ipsec_policies[0].name, ipsec_policies[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class L2VPNTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = L2VPN.objects.all()
    filterset = L2VPNFilterSet

    def get_m2m_filter_name(self, field):
        # Override filter names for import & export RouteTargets
        if field.name == 'import_targets':
            return 'import_target'
        if field.name == 'export_targets':
            return 'export_target'
        return ChangeLoggedFilterSetTests.get_m2m_filter_name(field)

    @classmethod
    def setUpTestData(cls):

        route_targets = (
            RouteTarget(name='1:1'),
            RouteTarget(name='1:2'),
            RouteTarget(name='1:3'),
            RouteTarget(name='2:1'),
            RouteTarget(name='2:2'),
            RouteTarget(name='2:3'),
        )
        RouteTarget.objects.bulk_create(route_targets)

        l2vpns = (
            L2VPN(
                name='L2VPN 1',
                slug='l2vpn-1',
                type=L2VPNTypeChoices.TYPE_VXLAN,
                identifier=65001,
                description='foobar1'
            ),
            L2VPN(
                name='L2VPN 2',
                slug='l2vpn-2',
                type=L2VPNTypeChoices.TYPE_VPWS,
                identifier=65002,
                description='foobar2'
            ),
            L2VPN(
                name='L2VPN 3',
                slug='l2vpn-3',
                type=L2VPNTypeChoices.TYPE_VPLS,
                description='foobar3'
            ),
        )
        L2VPN.objects.bulk_create(l2vpns)
        l2vpns[0].import_targets.add(route_targets[0])
        l2vpns[1].import_targets.add(route_targets[1])
        l2vpns[2].import_targets.add(route_targets[2])
        l2vpns[0].export_targets.add(route_targets[3])
        l2vpns[1].export_targets.add(route_targets[4])
        l2vpns[2].export_targets.add(route_targets[5])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['L2VPN 1', 'L2VPN 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['l2vpn-1', 'l2vpn-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_identifier(self):
        params = {'identifier': ['65001', '65002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [L2VPNTypeChoices.TYPE_VXLAN, L2VPNTypeChoices.TYPE_VPWS]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_import_targets(self):
        route_targets = RouteTarget.objects.filter(name__in=['1:1', '1:2'])
        params = {'import_target_id': [route_targets[0].pk, route_targets[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'import_target': [route_targets[0].name, route_targets[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_export_targets(self):
        route_targets = RouteTarget.objects.filter(name__in=['2:1', '2:2'])
        params = {'export_target_id': [route_targets[0].pk, route_targets[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'export_target': [route_targets[0].name, route_targets[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class L2VPNTerminationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = L2VPNTermination.objects.all()
    filterset = L2VPNTerminationFilterSet

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        interfaces = (
            Interface(name='Interface 1', device=device, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(name='Interface 2', device=device, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(name='Interface 3', device=device, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(interfaces)

        vm = create_test_virtualmachine('Virtual Machine 1')
        vminterfaces = (
            VMInterface(name='Interface 1', virtual_machine=vm),
            VMInterface(name='Interface 2', virtual_machine=vm),
            VMInterface(name='Interface 3', virtual_machine=vm),
        )
        VMInterface.objects.bulk_create(vminterfaces)

        vlans = (
            VLAN(name='VLAN 1', vid=101),
            VLAN(name='VLAN 2', vid=102),
            VLAN(name='VLAN 3', vid=103),
        )
        VLAN.objects.bulk_create(vlans)

        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type='vxlan', identifier=65001),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type='vpws', identifier=65002),
            L2VPN(name='L2VPN 3', slug='l2vpn-3', type='vpls'),  # No RD,
        )
        L2VPN.objects.bulk_create(l2vpns)

        l2vpnterminations = (
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[0]),
            L2VPNTermination(l2vpn=l2vpns[1], assigned_object=vlans[1]),
            L2VPNTermination(l2vpn=l2vpns[2], assigned_object=vlans[2]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=interfaces[0]),
            L2VPNTermination(l2vpn=l2vpns[1], assigned_object=interfaces[1]),
            L2VPNTermination(l2vpn=l2vpns[2], assigned_object=interfaces[2]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vminterfaces[0]),
            L2VPNTermination(l2vpn=l2vpns[1], assigned_object=vminterfaces[1]),
            L2VPNTermination(l2vpn=l2vpns[2], assigned_object=vminterfaces[2]),
        )
        L2VPNTermination.objects.bulk_create(l2vpnterminations)

    def test_l2vpn(self):
        l2vpns = L2VPN.objects.all()[:2]
        params = {'l2vpn_id': [l2vpns[0].pk, l2vpns[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'l2vpn': [l2vpns[0].slug, l2vpns[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_termination_type(self):
        params = {'assigned_object_type': 'ipam.vlan'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vminterface(self):
        vminterfaces = VMInterface.objects.all()[:2]
        params = {'vminterface_id': [vminterfaces[0].pk, vminterfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vlan(self):
        vlans = VLAN.objects.all()[:2]
        params = {'vlan_id': [vlans[0].pk, vlans[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vlan': ['VLAN 1', 'VLAN 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        site = Site.objects.all().first()
        params = {'site_id': [site.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'site': ['site-1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device(self):
        device = Device.objects.all().first()
        params = {'device_id': [device.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'device': ['Device 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_virtual_machine(self):
        virtual_machine = VirtualMachine.objects.all().first()
        params = {'virtual_machine_id': [virtual_machine.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'virtual_machine': ['Virtual Machine 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
