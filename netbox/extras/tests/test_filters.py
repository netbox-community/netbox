from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import DeviceRole, Platform, Region, Site
from extras.filters import *
from extras.models import ConfigContext, ExportTemplate, Tag
from tenancy.models import Tenant, TenantGroup
from virtualization.models import Cluster, ClusterGroup, ClusterType


class ExportTemplateTestCase(TestCase):
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

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Export Template 1', 'Export Template 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type(self):
        params = {'content_type': ContentType.objects.get(model='site').pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ConfigContextTestCase(TestCase):
    queryset = ConfigContext.objects.all()
    filterset = ConfigContextFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        # Can't use bulk_create for models with MPTT fields
        for r in regions:
            r.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1'),
            Site(name='Test Site 2', slug='test-site-2'),
            Site(name='Test Site 3', slug='test-site-3'),
        )
        Site.objects.bulk_create(sites)

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
            c.sites.set([sites[i]])
            c.roles.set([device_roles[i]])
            c.platforms.set([platforms[i]])
            c.cluster_groups.set([cluster_groups[i]])
            c.clusters.set([clusters[i]])
            c.tenant_groups.set([tenant_groups[i]])
            c.tenants.set([tenants[i]])

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

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

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
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


class TagTestCase(TestCase):
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

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Tag 1', 'Tag 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tag-1', 'tag-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


# TODO: ObjectChangeFilter test
