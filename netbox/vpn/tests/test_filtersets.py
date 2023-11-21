from django.test import TestCase

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from ipam.models import IPAddress
from vpn.choices import *
from vpn.filtersets import *
from vpn.models import *
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device


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

        tunnels = (
            Tunnel(
                name='Tunnel 1',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                encapsulation=TunnelEncapsulationChoices.ENCAP_GRE,
                ipsec_profile=ipsec_profiles[0],
                tunnel_id=100
            ),
            Tunnel(
                name='Tunnel 2',
                status=TunnelStatusChoices.STATUS_PLANNED,
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP,
                ipsec_profile=ipsec_profiles[0],
                tunnel_id=200
            ),
            Tunnel(
                name='Tunnel 3',
                status=TunnelStatusChoices.STATUS_DISABLED,
                encapsulation=TunnelEncapsulationChoices.ENCAP_IPSEC_TUNNEL,
                ipsec_profile=None,
                tunnel_id=300
            ),
        )
        Tunnel.objects.bulk_create(tunnels)

    def test_name(self):
        params = {'name': ['Tunnel 1', 'Tunnel 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [TunnelStatusChoices.STATUS_ACTIVE, TunnelStatusChoices.STATUS_PLANNED]}
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

        ip_addresses = (
            IPAddress(address='192.168.0.1/32'),
            IPAddress(address='192.168.0.2/32'),
            IPAddress(address='192.168.0.3/32'),
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
            TunnelTermination(
                tunnel=tunnels[0],
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                interface=interfaces[0],
                outside_ip=ip_addresses[0]
            ),
            TunnelTermination(
                tunnel=tunnels[1],
                role=TunnelTerminationRoleChoices.ROLE_SPOKE,
                interface=interfaces[1],
                outside_ip=ip_addresses[1]
            ),
            TunnelTermination(
                tunnel=tunnels[2],
                role=TunnelTerminationRoleChoices.ROLE_PEER,
                interface=interfaces[2],
                outside_ip=ip_addresses[2]
            ),
        )
        TunnelTermination.objects.bulk_create(tunnel_terminations)

    def test_tunnel(self):
        tunnels = Tunnel.objects.all()[:2]
        params = {'tunnel_id': [tunnels[0].pk, tunnels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tunnel': [tunnels[0].name, tunnels[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        params = {'role': [TunnelTerminationRoleChoices.ROLE_HUB, TunnelTerminationRoleChoices.ROLE_SPOKE]}
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
                sa_lifetime=1000
            ),
            IKEProposal(
                name='IKE Proposal 2',
                authentication_method=AuthenticationMethodChoices.CERTIFICATES,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                group=DHGroupChoices.GROUP_2,
                sa_lifetime=2000
            ),
            IKEProposal(
                name='IKE Proposal 3',
                authentication_method=AuthenticationMethodChoices.RSA_SIGNATURES,
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA512,
                group=DHGroupChoices.GROUP_5,
                sa_lifetime=3000
            ),
        )
        IKEProposal.objects.bulk_create(ike_proposals)

    def test_name(self):
        params = {'name': ['IKE Proposal 1', 'IKE Proposal 2']}
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
            ),
            IKEPolicy(
                name='IKE Policy 2',
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
            ),
            IKEPolicy(
                name='IKE Policy 3',
                version=IKEVersionChoices.VERSION_2,
                mode=IKEModeChoices.AGGRESSIVE,
            ),
        )
        IKEPolicy.objects.bulk_create(ike_policies)
        ike_policies[0].proposals.add(ike_proposals[0])
        ike_policies[1].proposals.add(ike_proposals[1])
        ike_policies[2].proposals.add(ike_proposals[2])

    def test_name(self):
        params = {'name': ['IKE Policy 1', 'IKE Policy 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_version(self):
        params = {'version': [IKEVersionChoices.VERSION_1]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mode(self):
        params = {'mode': [IKEModeChoices.MAIN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_proposal(self):
        proposals = IKEProposal.objects.all()[:2]
        params = {'proposal_id': [proposals[0].pk, proposals[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'proposal': [proposals[0].name, proposals[1].name]}
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
                sa_lifetime_data=1000
            ),
            IPSecProposal(
                name='IPSec Proposal 2',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                sa_lifetime_seconds=2000,
                sa_lifetime_data=2000
            ),
            IPSecProposal(
                name='IPSec Proposal 3',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA512,
                sa_lifetime_seconds=3000,
                sa_lifetime_data=3000
            ),
        )
        IPSecProposal.objects.bulk_create(ipsec_proposals)

    def test_name(self):
        params = {'name': ['IPSec Proposal 1', 'IPSec Proposal 2']}
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
                pfs_group=DHGroupChoices.GROUP_1
            ),
            IPSecPolicy(
                name='IPSec Policy 2',
                pfs_group=DHGroupChoices.GROUP_2
            ),
            IPSecPolicy(
                name='IPSec Policy 3',
                pfs_group=DHGroupChoices.GROUP_5
            ),
        )
        IPSecPolicy.objects.bulk_create(ipsec_policies)
        ipsec_policies[0].proposals.add(ipsec_proposals[0])
        ipsec_policies[1].proposals.add(ipsec_proposals[1])
        ipsec_policies[2].proposals.add(ipsec_proposals[2])

    def test_name(self):
        params = {'name': ['IPSec Policy 1', 'IPSec Policy 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_pfs_group(self):
        params = {'pfs_group': [DHGroupChoices.GROUP_1, DHGroupChoices.GROUP_2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_proposal(self):
        proposals = IPSecProposal.objects.all()[:2]
        params = {'proposal_id': [proposals[0].pk, proposals[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'proposal': [proposals[0].name, proposals[1].name]}
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
                ipsec_policy=ipsec_policies[0]
            ),
            IPSecProfile(
                name='IPSec Profile 2',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policies[1],
                ipsec_policy=ipsec_policies[1]
            ),
            IPSecProfile(
                name='IPSec Profile 3',
                mode=IPSecModeChoices.AH,
                ike_policy=ike_policies[2],
                ipsec_policy=ipsec_policies[2]
            ),
        )
        IPSecProfile.objects.bulk_create(ipsec_profiles)

    def test_name(self):
        params = {'name': ['IPSec Profile 1', 'IPSec Profile 2']}
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
