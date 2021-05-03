import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import DeviceRole, DeviceType, Manufacturer, Platform, Rack, Region, Site, SiteGroup
from extras.choices import JournalEntryKindChoices, ObjectChangeActionChoices
from extras.filtersets import *
from extras.models import *
from ipam.models import IPAddress
from tenancy.models import Tenant, TenantGroup
from utilities.testing import BaseFilterSetTests
from virtualization.models import Cluster, ClusterGroup, ClusterType


class WebhookTestCase(TestCase, BaseFilterSetTests):
    queryset = Webhook.objects.all()
    filterset = WebhookFilterSet

    @classmethod
    def setUpTestData(cls):
        content_types = ContentType.objects.filter(model__in=['site', 'rack', 'device'])

        webhooks = (
            Webhook(
                name='Webhook 1',
                type_create=True,
                payload_url='http://example.com/?1',
                enabled=True,
                http_method='GET',
                ssl_verification=True,
            ),
            Webhook(
                name='Webhook 2',
                type_update=True,
                payload_url='http://example.com/?2',
                enabled=True,
                http_method='POST',
                ssl_verification=True,
            ),
            Webhook(
                name='Webhook 3',
                type_delete=True,
                payload_url='http://example.com/?3',
                enabled=False,
                http_method='PATCH',
                ssl_verification=False,
            ),
        )
        Webhook.objects.bulk_create(webhooks)
        webhooks[0].content_types.add(content_types[0])
        webhooks[1].content_types.add(content_types[1])
        webhooks[2].content_types.add(content_types[2])

    def test_name(self):
        params = {'name': ['Webhook 1', 'Webhook 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_types(self):
        params = {'content_types': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_type_create(self):
        params = {'type_create': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_type_update(self):
        params = {'type_update': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_type_delete(self):
        params = {'type_delete': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_http_method(self):
        params = {'http_method': ['GET', 'POST']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ssl_verification(self):
        params = {'ssl_verification': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CustomLinkTestCase(TestCase, BaseFilterSetTests):
    queryset = CustomLink.objects.all()
    filterset = CustomLinkFilterSet

    @classmethod
    def setUpTestData(cls):
        content_types = ContentType.objects.filter(model__in=['site', 'rack', 'device'])

        custom_links = (
            CustomLink(
                name='Custom Link 1',
                content_type=content_types[0],
                weight=100,
                new_window=False,
                link_text='Link 1',
                link_url='http://example.com/?1'
            ),
            CustomLink(
                name='Custom Link 2',
                content_type=content_types[1],
                weight=200,
                new_window=False,
                link_text='Link 1',
                link_url='http://example.com/?2'
            ),
            CustomLink(
                name='Custom Link 3',
                content_type=content_types[2],
                weight=300,
                new_window=True,
                link_text='Link 1',
                link_url='http://example.com/?3'
            ),
        )
        CustomLink.objects.bulk_create(custom_links)

    def test_name(self):
        params = {'name': ['Custom Link 1', 'Custom Link 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type(self):
        params = {'content_type': ContentType.objects.get(model='site').pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_weight(self):
        params = {'weight': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_new_window(self):
        params = {'new_window': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'new_window': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ExportTemplateTestCase(TestCase, BaseFilterSetTests):
    queryset = ExportTemplate.objects.all()
    filterset = ExportTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        content_types = ContentType.objects.filter(model__in=['site', 'rack', 'device'])

        export_templates = (
            ExportTemplate(name='Export Template 1', content_type=content_types[0], template_code='TESTING'),
            ExportTemplate(name='Export Template 2', content_type=content_types[1], template_code='TESTING'),
            ExportTemplate(name='Export Template 3', content_type=content_types[2], template_code='TESTING'),
        )
        ExportTemplate.objects.bulk_create(export_templates)

    def test_name(self):
        params = {'name': ['Export Template 1', 'Export Template 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type(self):
        params = {'content_type': ContentType.objects.get(model='site').pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ImageAttachmentTestCase(TestCase, BaseFilterSetTests):
    queryset = ImageAttachment.objects.all()
    filterset = ImageAttachmentFilterSet

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get(app_label='dcim', model='site')
        rack_ct = ContentType.objects.get(app_label='dcim', model='rack')

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        image_attachments = (
            ImageAttachment(
                content_type=site_ct,
                object_id=sites[0].pk,
                name='Image Attachment 1',
                image='http://example.com/image1.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                content_type=site_ct,
                object_id=sites[1].pk,
                name='Image Attachment 2',
                image='http://example.com/image2.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                content_type=rack_ct,
                object_id=racks[0].pk,
                name='Image Attachment 3',
                image='http://example.com/image3.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                content_type=rack_ct,
                object_id=racks[1].pk,
                name='Image Attachment 4',
                image='http://example.com/image4.png',
                image_height=100,
                image_width=100
            )
        )
        ImageAttachment.objects.bulk_create(image_attachments)

    def test_name(self):
        params = {'name': ['Image Attachment 1', 'Image Attachment 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type(self):
        params = {'content_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type_id_and_object_id(self):
        params = {
            'content_type_id': ContentType.objects.get(app_label='dcim', model='site').pk,
            'object_id': [Site.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class JournalEntryTestCase(TestCase, BaseFilterSetTests):
    queryset = JournalEntry.objects.all()
    filterset = JournalEntryFilterSet

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        users = (
            User(username='Alice'),
            User(username='Bob'),
            User(username='Charlie'),
        )
        User.objects.bulk_create(users)

        journal_entries = (
            JournalEntry(
                assigned_object=sites[0],
                created_by=users[0],
                kind=JournalEntryKindChoices.KIND_INFO,
                comments='New journal entry'
            ),
            JournalEntry(
                assigned_object=sites[0],
                created_by=users[1],
                kind=JournalEntryKindChoices.KIND_SUCCESS,
                comments='New journal entry'
            ),
            JournalEntry(
                assigned_object=sites[1],
                created_by=users[2],
                kind=JournalEntryKindChoices.KIND_WARNING,
                comments='New journal entry'
            ),
            JournalEntry(
                assigned_object=racks[0],
                created_by=users[0],
                kind=JournalEntryKindChoices.KIND_INFO,
                comments='New journal entry'
            ),
            JournalEntry(
                assigned_object=racks[0],
                created_by=users[1],
                kind=JournalEntryKindChoices.KIND_SUCCESS,
                comments='New journal entry'
            ),
            JournalEntry(
                assigned_object=racks[1],
                created_by=users[2],
                kind=JournalEntryKindChoices.KIND_WARNING,
                comments='New journal entry'
            ),
        )
        JournalEntry.objects.bulk_create(journal_entries)

    def test_created_by(self):
        users = User.objects.filter(username__in=['Alice', 'Bob'])
        params = {'created_by': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'created_by_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_assigned_object_type(self):
        params = {'assigned_object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'assigned_object_type_id': ContentType.objects.get(app_label='dcim', model='site').pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_assigned_object(self):
        params = {
            'assigned_object_type': 'dcim.site',
            'assigned_object_id': [Site.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_kind(self):
        params = {'kind': [JournalEntryKindChoices.KIND_INFO, JournalEntryKindChoices.KIND_SUCCESS]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class ConfigContextTestCase(TestCase, BaseFilterSetTests):
    queryset = ConfigContext.objects.all()
    filterset = ConfigContextFilterSet

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
            Site(name='Test Site 1', slug='test-site-1'),
            Site(name='Test Site 2', slug='test-site-2'),
            Site(name='Test Site 3', slug='test-site-3'),
        )
        Site.objects.bulk_create(sites)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-3'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-4'),
        )
        DeviceType.objects.bulk_create(device_types)

        device_roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(device_roles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        clusters = (
            Cluster(name='Cluster 1', type=cluster_type),
            Cluster(name='Cluster 2', type=cluster_type),
            Cluster(name='Cluster 3', type=cluster_type),
        )
        Cluster.objects.bulk_create(clusters)

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        for i in range(0, 3):
            is_active = bool(i % 2)
            c = ConfigContext.objects.create(
                name='Config Context {}'.format(i + 1),
                is_active=is_active,
                data='{"foo": 123}'
            )
            c.regions.set([regions[i]])
            c.site_groups.set([site_groups[i]])
            c.sites.set([sites[i]])
            c.device_types.set([device_types[i]])
            c.roles.set([device_roles[i]])
            c.platforms.set([platforms[i]])
            c.cluster_groups.set([cluster_groups[i]])
            c.clusters.set([clusters[i]])
            c.tenant_groups.set([tenant_groups[i]])
            c.tenants.set([tenants[i]])

    def test_name(self):
        params = {'name': ['Config Context 1', 'Config Context 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_active(self):
        params = {'is_active': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'is_active': False}
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

    def test_device_type(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        device_roles = DeviceRole.objects.all()[:2]
        params = {'role_id': [device_roles[0].pk, device_roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [device_roles[0].slug, device_roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        platforms = Platform.objects.all()[:2]
        params = {'platform_id': [platforms[0].pk, platforms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'platform': [platforms[0].slug, platforms[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_group(self):
        cluster_groups = ClusterGroup.objects.all()[:2]
        params = {'cluster_group_id': [cluster_groups[0].pk, cluster_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_group': [cluster_groups[0].slug, cluster_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster(self):
        clusters = Cluster.objects.all()[:2]
        params = {'cluster_id': [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TagTestCase(TestCase, BaseFilterSetTests):
    queryset = Tag.objects.all()
    filterset = TagFilterSet

    @classmethod
    def setUpTestData(cls):

        tags = (
            Tag(name='Tag 1', slug='tag-1', color='ff0000'),
            Tag(name='Tag 2', slug='tag-2', color='00ff00'),
            Tag(name='Tag 3', slug='tag-3', color='0000ff'),
        )
        Tag.objects.bulk_create(tags)

    def test_name(self):
        params = {'name': ['Tag 1', 'Tag 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tag-1', 'tag-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ObjectChangeTestCase(TestCase, BaseFilterSetTests):
    queryset = ObjectChange.objects.all()
    filterset = ObjectChangeFilterSet

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='user1'),
            User(username='user2'),
            User(username='user3'),
        )
        User.objects.bulk_create(users)

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        ipaddress = IPAddress.objects.create(address='192.0.2.1/24')

        object_changes = (
            ObjectChange(
                user=users[0],
                user_name=users[0].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_CREATE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[0],
                user_name=users[0].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[1],
                user_name=users[1].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_DELETE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[1],
                user_name=users[1].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_CREATE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
            ObjectChange(
                user=users[2],
                user_name=users[2].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
            ObjectChange(
                user=users[2],
                user_name=users[2].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_DELETE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
        )
        ObjectChange.objects.bulk_create(object_changes)

    def test_user(self):
        params = {'user_id': User.objects.filter(username__in=['user1', 'user2']).values_list('pk', flat=True)}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'user': ['user1', 'user2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_user_name(self):
        params = {'user_name': ['user1', 'user2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_changed_object_type(self):
        params = {'changed_object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_changed_object_type_id(self):
        params = {'changed_object_type_id': ContentType.objects.get(app_label='dcim', model='site').pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
