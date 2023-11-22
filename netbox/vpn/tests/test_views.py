from django.contrib.contenttypes.models import ContentType

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from vpn.choices import *
from vpn.models import *
from utilities.testing import ViewTestCases, create_tags, create_test_device


class TunnelTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Tunnel

    @classmethod
    def setUpTestData(cls):

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Tunnel X',
            'description': 'New tunnel',
            'status': TunnelStatusChoices.STATUS_PLANNED,
            'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,status,encapsulation",
            "Tunnel 4,planned,gre",
            "Tunnel 5,planned,gre",
            "Tunnel 6,planned,gre",
        )

        cls.csv_update_data = (
            "id,status,encapsulation",
            f"{tunnels[0].pk},active,ip-ip",
            f"{tunnels[1].pk},active,ip-ip",
            f"{tunnels[2].pk},active,ip-ip",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'status': TunnelStatusChoices.STATUS_DISABLED,
            'encapsulation': TunnelEncapsulationChoices.ENCAP_GRE,
        }


class TunnelTerminationTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = TunnelTermination
    # TODO: Workaround for conflict between form field and GFK
    validation_excluded_fields = ('interface',)

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
            Interface(device=device, name='Interface 7', type=InterfaceTypeChoices.TYPE_VIRTUAL),
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
                interface=interfaces[0]
            ),
            TunnelTermination(
                tunnel=tunnel,
                role=TunnelTerminationRoleChoices.ROLE_SPOKE,
                interface=interfaces[1]
            ),
            TunnelTermination(
                tunnel=tunnel,
                role=TunnelTerminationRoleChoices.ROLE_SPOKE,
                interface=interfaces[2]
            ),
        )
        TunnelTermination.objects.bulk_create(tunnel_terminations)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'tunnel': tunnel.pk,
            'role': TunnelTerminationRoleChoices.ROLE_PEER,
            'type': TunnelTerminationTypeChoices.TYPE_DEVICE,
            'parent': device.pk,
            'interface': interfaces[6].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "tunnel,role,device,interface",
            "Tunnel 1,peer,Device 1,Interface 4",
            "Tunnel 1,peer,Device 1,Interface 5",
            "Tunnel 1,peer,Device 1,Interface 6",
        )

        cls.csv_update_data = (
            "id,role",
            f"{tunnel_terminations[0].pk},peer",
            f"{tunnel_terminations[1].pk},peer",
            f"{tunnel_terminations[2].pk},peer",
        )

        cls.bulk_edit_data = {
            'role': TunnelTerminationRoleChoices.ROLE_PEER,
        }


class IKEProposalTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IKEProposal

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'IKE Proposal X',
            'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
            'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
            'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            'group': DHGroupChoices.GROUP_19,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,authentication_method,encryption_algorithm,authentication_algorithm,group",
            "IKE Proposal 4,preshared-keys,aes-128-cbc,hmac-sha1,14",
            "IKE Proposal 5,preshared-keys,aes-128-cbc,hmac-sha1,14",
            "IKE Proposal 6,preshared-keys,aes-128-cbc,hmac-sha1,14",
        )

        cls.csv_update_data = (
            "id,description",
            f"{ike_proposals[0].pk},New description",
            f"{ike_proposals[1].pk},New description",
            f"{ike_proposals[2].pk},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'authentication_method': AuthenticationMethodChoices.CERTIFICATES,
            'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
            'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            'group': DHGroupChoices.GROUP_19
        }


class IKEPolicyTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IKEPolicy

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'IKE Policy X',
            'version': IKEVersionChoices.VERSION_2,
            'mode': IKEModeChoices.AGGRESSIVE,
            'proposals': [p.pk for p in ike_proposals],
            'tags': [t.pk for t in tags],
        }

        ike_proposal_names = ','.join([p.name for p in ike_proposals])
        cls.csv_data = (
            "name,version,mode,proposals",
            f"IKE Proposal 4,2,aggressive,\"{ike_proposal_names}\"",
            f"IKE Proposal 5,2,aggressive,\"{ike_proposal_names}\"",
            f"IKE Proposal 6,2,aggressive,\"{ike_proposal_names}\"",
        )

        cls.csv_update_data = (
            "id,description",
            f"{ike_policies[0].pk},New description",
            f"{ike_policies[1].pk},New description",
            f"{ike_policies[2].pk},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'version': IKEVersionChoices.VERSION_2,
            'mode': IKEModeChoices.AGGRESSIVE,
        }


class IPSecProposalTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPSecProposal

    @classmethod
    def setUpTestData(cls):

        ipsec_proposals = (
            IPSecProposal(
                name='IPSec Proposal 1',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
            ),
            IPSecProposal(
                name='IPSec Proposal 2',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
            ),
            IPSecProposal(
                name='IPSec Proposal 3',
                encryption_algorithm=EncryptionAlgorithmChoices.ENCRYPTION_AES128_CBC,
                authentication_algorithm=AuthenticationAlgorithmChoices.AUTH_HMAC_SHA1,
            ),
        )
        IPSecProposal.objects.bulk_create(ipsec_proposals)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'IPSec Proposal X',
            'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
            'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            'sa_lifetime_seconds': 3600,
            'sa_lifetime_data': 1000000,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,encryption_algorithm,authentication_algorithm,sa_lifetime_seconds,sa_lifetime_data",
            "IKE Proposal 4,aes-128-cbc,hmac-sha1,3600,1000000",
            "IKE Proposal 5,aes-128-cbc,hmac-sha1,3600,1000000",
            "IKE Proposal 6,aes-128-cbc,hmac-sha1,3600,1000000",
        )

        cls.csv_update_data = (
            "id,description",
            f"{ipsec_proposals[0].pk},New description",
            f"{ipsec_proposals[1].pk},New description",
            f"{ipsec_proposals[2].pk},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'encryption_algorithm': EncryptionAlgorithmChoices.ENCRYPTION_AES192_CBC,
            'authentication_algorithm': AuthenticationAlgorithmChoices.AUTH_HMAC_SHA256,
            'sa_lifetime_seconds': 3600,
            'sa_lifetime_data': 1000000,
        }


class IPSecPolicyTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPSecPolicy

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'IPSec Policy X',
            'pfs_group': DHGroupChoices.GROUP_5,
            'proposals': [p.pk for p in ipsec_proposals],
            'tags': [t.pk for t in tags],
        }

        ipsec_proposal_names = ','.join([p.name for p in ipsec_proposals])
        cls.csv_data = (
            "name,pfs_group,proposals",
            f"IKE Proposal 4,19,\"{ipsec_proposal_names}\"",
            f"IKE Proposal 5,19,\"{ipsec_proposal_names}\"",
            f"IKE Proposal 6,19,\"{ipsec_proposal_names}\"",
        )

        cls.csv_update_data = (
            "id,description",
            f"{ipsec_policies[0].pk},New description",
            f"{ipsec_policies[1].pk},New description",
            f"{ipsec_policies[2].pk},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'pfs_group': DHGroupChoices.GROUP_5,
        }


class IPSecProfileTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPSecProfile

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'IPSec Profile X',
            'mode': IPSecModeChoices.AH,
            'ike_policy': ike_policies[1].pk,
            'ipsec_policy': ipsec_policies[1].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,mode,ike_policy,ipsec_policy",
            f"IKE Proposal 4,ah,IKE Policy 2,IPSec Policy 2",
            f"IKE Proposal 5,ah,IKE Policy 2,IPSec Policy 2",
            f"IKE Proposal 6,ah,IKE Policy 2,IPSec Policy 2",
        )

        cls.csv_update_data = (
            "id,description",
            f"{ipsec_profiles[0].pk},New description",
            f"{ipsec_profiles[1].pk},New description",
            f"{ipsec_profiles[2].pk},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'mode': IPSecModeChoices.AH,
            'ike_policy': ike_policies[1].pk,
            'ipsec_policy': ipsec_policies[1].pk,
        }
