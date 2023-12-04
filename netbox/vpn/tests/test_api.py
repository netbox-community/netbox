from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from ipam.models import VLAN
from utilities.testing import APITestCase, APIViewTestCases, create_test_device
from vpn.choices import *
from vpn.models import *


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('vpn-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class TunnelGroupTest(APIViewTestCases.APIViewTestCase):
    model = TunnelGroup
    brief_fields = ['display', 'id', 'name', 'slug', 'tunnel_count', 'url']
    create_data = (
        {
            'name': 'Tunnel Group 4',
            'slug': 'tunnel-group-4',
        },
        {
            'name': 'Tunnel Group 5',
            'slug': 'tunnel-group-5',
        },
        {
            'name': 'Tunnel Group 6',
            'slug': 'tunnel-group-6',
        },
    )
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        tunnel_groups = (
            TunnelGroup(name='Tunnel Group 1', slug='tunnel-group-1'),
            TunnelGroup(name='Tunnel Group 2', slug='tunnel-group-2'),
            TunnelGroup(name='Tunnel Group 3', slug='tunnel-group-3'),
        )
        TunnelGroup.objects.bulk_create(tunnel_groups)


class TunnelTest(APIViewTestCases.APIViewTestCase):
    model = Tunnel
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': TunnelStatusChoices.STATUS_PLANNED,
        'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        tunnel_groups = (
            TunnelGroup(name='Tunnel Group 1', slug='tunnel-group-1'),
            TunnelGroup(name='Tunnel Group 2', slug='tunnel-group-2'),
        )
        TunnelGroup.objects.bulk_create(tunnel_groups)

        tunnels = (
            Tunnel(
                name='Tunnel 1',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                group=tunnel_groups[0],
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
            Tunnel(
                name='Tunnel 2',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                group=tunnel_groups[0],
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
            Tunnel(
                name='Tunnel 3',
                status=TunnelStatusChoices.STATUS_ACTIVE,
                group=tunnel_groups[0],
                encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
            ),
        )
        Tunnel.objects.bulk_create(tunnels)

        cls.create_data = [
            {
                'name': 'Tunnel 4',
                'status': TunnelStatusChoices.STATUS_DISABLED,
                'group': tunnel_groups[1].pk,
                'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
            },
            {
                'name': 'Tunnel 5',
                'status': TunnelStatusChoices.STATUS_DISABLED,
                'group': tunnel_groups[1].pk,
                'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
            },
            {
                'name': 'Tunnel 6',
                'status': TunnelStatusChoices.STATUS_DISABLED,
                'group': tunnel_groups[1].pk,
                'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
            },
        ]


class TunnelTerminationTest(APIViewTestCases.APIViewTestCase):
    model = TunnelTermination
    brief_fields = ['display', 'id', 'url']
    bulk_update_data = {
        'role': TunnelTerminationRoleChoices.ROLE_PEER,
    }

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        interfaces = (
            Interface(device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 2', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 3', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 4', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 5', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=device, name='Interface 6', type=InterfaceTypeChoices.TYPE_VIRTUAL),
        )
        Interface.objects.bulk_create(interfaces)

        tunnel = Tunnel.objects.create(
            name='Tunnel 1',
            status=TunnelStatusChoices.STATUS_ACTIVE,
            encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP
        )

        tunnel_terminations = (
            TunnelTermination(
                tunnel=tunnel,
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                termination=interfaces[0]
            ),
            TunnelTermination(
                tunnel=tunnel,
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                termination=interfaces[1]
            ),
            TunnelTermination(
                tunnel=tunnel,
                role=TunnelTerminationRoleChoices.ROLE_HUB,
                termination=interfaces[2]
            ),
        )
        TunnelTermination.objects.bulk_create(tunnel_terminations)

        cls.create_data = [
            {
                'tunnel': tunnel.pk,
                'role': TunnelTerminationRoleChoices.ROLE_PEER,
                'termination_type': 'dcim.interface',
                'termination_id': interfaces[3].pk,
            },
            {
                'tunnel': tunnel.pk,
                'role': TunnelTerminationRoleChoices.ROLE_PEER,
                'termination_type': 'dcim.interface',
                'termination_id': interfaces[4].pk,
            },
            {
                'tunnel': tunnel.pk,
                'role': TunnelTerminationRoleChoices.ROLE_PEER,
                'termination_type': 'dcim.interface',
                'termination_id': interfaces[5].pk,
            },
        ]


class IKEProposalTest(APIViewTestCases.APIViewTestCase):
    model = IKEProposal
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
        'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
        'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_MD5,
        'group': DHGroupChoices.GROUP_19,
        'description': 'New description',
    }

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

        cls.create_data = [
            {
                'name': 'IKE Proposal 4',
                'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                'group': DHGroupChoices.GROUP_19,
            },
            {
                'name': 'IKE Proposal 5',
                'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                'group': DHGroupChoices.GROUP_19,
            },
            {
                'name': 'IKE Proposal 6',
                'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
                'group': DHGroupChoices.GROUP_19,
            },
        ]


class IKEPolicyTest(APIViewTestCases.APIViewTestCase):
    model = IKEPolicy
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'version': IKEVersionChoices.VERSION_1,
        'mode': IKEModeChoices.AGGRESSIVE,
        'description': 'New description',
        'preshared_key': 'New key',
    }

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
                version=IKEVersionChoices.VERSION_1,
                mode=IKEModeChoices.MAIN,
            ),
        )
        IKEPolicy.objects.bulk_create(ike_policies)
        for ike_policy in ike_policies:
            ike_policy.proposals.set(ike_proposals)

        cls.create_data = [
            {
                'name': 'IKE Policy 4',
                'version': IKEVersionChoices.VERSION_1,
                'mode': IKEModeChoices.MAIN,
                'proposals': [ike_proposals[0].pk, ike_proposals[1].pk],
            },
            {
                'name': 'IKE Policy 5',
                'version': IKEVersionChoices.VERSION_1,
                'mode': IKEModeChoices.MAIN,
                'proposals': [ike_proposals[0].pk, ike_proposals[1].pk],
            },
            {
                'name': 'IKE Policy 6',
                'version': IKEVersionChoices.VERSION_1,
                'mode': IKEModeChoices.MAIN,
                'proposals': [ike_proposals[0].pk, ike_proposals[1].pk],
            },
        ]


class IPSecProposalTest(APIViewTestCases.APIViewTestCase):
    model = IPSecProposal
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
        'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_MD5,
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        ipsec_proposals = (
            IPSecProposal(
                name='IPSec Proposal 1',
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

        cls.create_data = [
            {
                'name': 'IPSec Proposal 4',
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            },
            {
                'name': 'IPSec Proposal 5',
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            },
            {
                'name': 'IPSec Proposal 6',
                'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES256_CBC,
                'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            },
        ]


class IPSecPolicyTest(APIViewTestCases.APIViewTestCase):
    model = IPSecPolicy
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'pfs_group': DHGroupChoices.GROUP_5,
        'description': 'New description',
    }

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
        )
        IPSecProposal.objects.bulk_create(ipsec_proposals)

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
            ipsec_policy.proposals.set(ipsec_proposals)

        cls.create_data = [
            {
                'name': 'IPSec Policy 4',
                'pfs_group': DHGroupChoices.GROUP_16,
                'proposals': [ipsec_proposals[0].pk, ipsec_proposals[1].pk],
            },
            {
                'name': 'IPSec Policy 5',
                'pfs_group': DHGroupChoices.GROUP_16,
                'proposals': [ipsec_proposals[0].pk, ipsec_proposals[1].pk],
            },
            {
                'name': 'IPSec Policy 6',
                'pfs_group': DHGroupChoices.GROUP_16,
                'proposals': [ipsec_proposals[0].pk, ipsec_proposals[1].pk],
            },
        ]


class IPSecProfileTest(APIViewTestCases.APIViewTestCase):
    model = IPSecProfile
    brief_fields = ['display', 'id', 'name', 'url']

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
                ike_policy=ike_policies[0],
                ipsec_policy=ipsec_policies[0]
            ),
            IPSecProfile(
                name='IPSec Profile 3',
                mode=IPSecModeChoices.ESP,
                ike_policy=ike_policies[0],
                ipsec_policy=ipsec_policies[0]
            ),
        )
        IPSecProfile.objects.bulk_create(ipsec_profiles)

        cls.create_data = [
            {
                'name': 'IPSec Profile 4',
                'mode': IPSecModeChoices.AH,
                'ike_policy': ike_policies[1].pk,
                'ipsec_policy': ipsec_policies[1].pk,
            },
        ]

        cls.bulk_update_data = {
            'mode': IPSecModeChoices.AH,
            'ike_policy': ike_policies[1].pk,
            'ipsec_policy': ipsec_policies[1].pk,
            'description': 'New description',
        }


class L2VPNTest(APIViewTestCases.APIViewTestCase):
    model = L2VPN
    brief_fields = ['display', 'id', 'identifier', 'name', 'slug', 'type', 'url']
    create_data = [
        {
            'name': 'L2VPN 4',
            'slug': 'l2vpn-4',
            'type': 'vxlan',
            'identifier': 33343344
        },
        {
            'name': 'L2VPN 5',
            'slug': 'l2vpn-5',
            'type': 'vxlan',
            'identifier': 33343345
        },
        {
            'name': 'L2VPN 6',
            'slug': 'l2vpn-6',
            'type': 'vpws',
            'identifier': 33343346
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type='vxlan', identifier=650001),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type='vpws', identifier=650002),
            L2VPN(name='L2VPN 3', slug='l2vpn-3', type='vpls'),  # No RD
        )
        L2VPN.objects.bulk_create(l2vpns)


class L2VPNTerminationTest(APIViewTestCases.APIViewTestCase):
    model = L2VPNTermination
    brief_fields = ['display', 'id', 'l2vpn', 'url']

    @classmethod
    def setUpTestData(cls):

        vlans = (
            VLAN(name='VLAN 1', vid=651),
            VLAN(name='VLAN 2', vid=652),
            VLAN(name='VLAN 3', vid=653),
            VLAN(name='VLAN 4', vid=654),
            VLAN(name='VLAN 5', vid=655),
            VLAN(name='VLAN 6', vid=656),
            VLAN(name='VLAN 7', vid=657)
        )
        VLAN.objects.bulk_create(vlans)

        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type='vxlan', identifier=650001),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type='vpws', identifier=650002),
            L2VPN(name='L2VPN 3', slug='l2vpn-3', type='vpls'),  # No RD
        )
        L2VPN.objects.bulk_create(l2vpns)

        l2vpnterminations = (
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[0]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[1]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[2])
        )
        L2VPNTermination.objects.bulk_create(l2vpnterminations)

        cls.create_data = [
            {
                'l2vpn': l2vpns[0].pk,
                'assigned_object_type': 'ipam.vlan',
                'assigned_object_id': vlans[3].pk,
            },
            {
                'l2vpn': l2vpns[0].pk,
                'assigned_object_type': 'ipam.vlan',
                'assigned_object_id': vlans[4].pk,
            },
            {
                'l2vpn': l2vpns[0].pk,
                'assigned_object_type': 'ipam.vlan',
                'assigned_object_id': vlans[5].pk,
            },
        ]

        cls.bulk_update_data = {
            'l2vpn': l2vpns[2].pk
        }
