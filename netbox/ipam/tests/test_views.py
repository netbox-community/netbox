from netaddr import IPNetwork
import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.constants import IP_PROTOCOL_TCP
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from utilities.testing import create_test_user


class VRFTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_vrf'])
        self.client = Client()
        self.client.force_login(user)

        VRF.objects.bulk_create([
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        ])

    def test_vrf_list(self):

        url = reverse('ipam:vrf_list')
        params = {
            "q": "65000",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_configcontext(self):

        vrf = VRF.objects.first()
        response = self.client.get(vrf.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class RIRTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_rir'])
        self.client = Client()
        self.client.force_login(user)

        RIR.objects.bulk_create([
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        ])

    def test_rir_list(self):

        url = reverse('ipam:rir_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AggregateTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_aggregate'])
        self.client = Client()
        self.client.force_login(user)

        rir = RIR(name='RIR 1', slug='rir-1')
        rir.save()

        Aggregate.objects.bulk_create([
            Aggregate(family=4, prefix=IPNetwork('10.1.0.0/16'), rir=rir),
            Aggregate(family=4, prefix=IPNetwork('10.2.0.0/16'), rir=rir),
            Aggregate(family=4, prefix=IPNetwork('10.3.0.0/16'), rir=rir),
        ])

    def test_aggregate_list(self):

        url = reverse('ipam:aggregate_list')
        params = {
            "rir": RIR.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_aggregate(self):

        aggregate = Aggregate.objects.first()
        response = self.client.get(aggregate.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class RoleTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_role'])
        self.client = Client()
        self.client.force_login(user)

        Role.objects.bulk_create([
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        ])

    def test_role_list(self):

        url = reverse('ipam:role_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PrefixTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_prefix'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        Prefix.objects.bulk_create([
            Prefix(family=4, prefix=IPNetwork('10.1.0.0/16'), site=site),
            Prefix(family=4, prefix=IPNetwork('10.2.0.0/16'), site=site),
            Prefix(family=4, prefix=IPNetwork('10.3.0.0/16'), site=site),
        ])

    def test_prefix_list(self):

        url = reverse('ipam:prefix_list')
        params = {
            "site": Site.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_prefix(self):

        prefix = Prefix.objects.first()
        response = self.client.get(prefix.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class IPAddressTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_ipaddress'])
        self.client = Client()
        self.client.force_login(user)

        vrf = VRF(name='VRF 1', rd='65000:1')
        vrf.save()

        IPAddress.objects.bulk_create([
            IPAddress(family=4, address=IPNetwork('10.1.0.0/16'), vrf=vrf),
            IPAddress(family=4, address=IPNetwork('10.2.0.0/16'), vrf=vrf),
            IPAddress(family=4, address=IPNetwork('10.3.0.0/16'), vrf=vrf),
        ])

    def test_ipaddress_list(self):

        url = reverse('ipam:ipaddress_list')
        params = {
            "vrf": VRF.objects.first().rd,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_ipaddress(self):

        ipaddress = IPAddress.objects.first()
        response = self.client.get(ipaddress.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class VLANGroupTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_vlangroup'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        VLANGroup.objects.bulk_create([
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', site=site),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', site=site),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', site=site),
        ])

    def test_vlangroup_list(self):

        url = reverse('ipam:vlangroup_list')
        params = {
            "site": Site.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)


class VLANTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_vlan'])
        self.client = Client()
        self.client.force_login(user)

        vlangroup = VLANGroup(name='VLAN Group 1', slug='vlan-group-1')
        vlangroup.save()

        VLAN.objects.bulk_create([
            VLAN(group=vlangroup, vid=101, name='VLAN101'),
            VLAN(group=vlangroup, vid=102, name='VLAN102'),
            VLAN(group=vlangroup, vid=103, name='VLAN103'),
        ])

    def test_vlan_list(self):

        url = reverse('ipam:vlan_list')
        params = {
            "group": VLANGroup.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_vlan(self):

        vlan = VLAN.objects.first()
        response = self.client.get(vlan.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class ServiceTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['ipam.view_service'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(manufacturer=manufacturer, model='Device Type 1')
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device.save()

        Service.objects.bulk_create([
            Service(device=device, name='Service 1', protocol=IP_PROTOCOL_TCP, port=101),
            Service(device=device, name='Service 2', protocol=IP_PROTOCOL_TCP, port=102),
            Service(device=device, name='Service 3', protocol=IP_PROTOCOL_TCP, port=103),
        ])

    def test_service_list(self):

        url = reverse('ipam:service_list')
        params = {
            "device_id": Device.objects.first(),
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_service(self):

        service = Service.objects.first()
        response = self.client.get(service.get_absolute_url())
        self.assertEqual(response.status_code, 200)
