from django.test import TestCase

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Site, Region
from extras.models import ConfigContext, Tag
from tenancy.models import Tenant, TenantGroup
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class TagTest(TestCase):

    def test_create_tag_unicode(self):
        tag = Tag(name='Testing Unicode: 台灣')
        tag.save()

        self.assertEqual(tag.slug, 'testing-unicode-台灣')


class ConfigContextTest(TestCase):
    """
    These test cases deal with the weighting, ordering, and deep merge logic of config context data.

    It also ensures the various config context querysets are consistent.
    """

    def setUp(self):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        self.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        self.devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        self.region = Region.objects.create(name="Region")
        self.site = Site.objects.create(name='Site-1', slug='site-1', region=self.region)
        self.platform = Platform.objects.create(name="Platform")
        self.tenantgroup = TenantGroup.objects.create(name="Tenant Group")
        self.tenant = Tenant.objects.create(name="Tenant", group=self.tenantgroup)
        self.tag = Tag.objects.create(name="Tag", slug="tag")
        self.tag2 = Tag.objects.create(name="Tag2", slug="tag2")

        self.device = Device.objects.create(
            name='Device 1',
            device_type=self.devicetype,
            device_role=self.devicerole,
            site=self.site
        )

    def test_higher_weight_wins(self):

        context1 = ConfigContext(
            name="context 1",
            weight=101,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        ConfigContext.objects.bulk_create([context1, context2])

        expected_data = {
            "a": 123,
            "b": 456,
            "c": 777
        }
        self.assertEqual(self.device.get_config_context(), expected_data)

    def test_name_ordering_after_weight(self):

        context1 = ConfigContext(
            name="context 1",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        ConfigContext.objects.bulk_create([context1, context2])

        expected_data = {
            "a": 123,
            "b": 456,
            "c": 789
        }
        self.assertEqual(self.device.get_config_context(), expected_data)

    def test_annotation_same_as_get_for_object(self):
        """
        This test incorperates features from all of the above tests cases to ensure
        the annotate_config_context_data() and get_for_object() queryset methods are the same.
        """
        context1 = ConfigContext(
            name="context 1",
            weight=101,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        context3 = ConfigContext(
            name="context 3",
            weight=99,
            data={
                "d": 1
            }
        )
        context4 = ConfigContext(
            name="context 4",
            weight=99,
            data={
                "d": 2
            }
        )
        ConfigContext.objects.bulk_create([context1, context2, context3, context4])

        annotated_queryset = Device.objects.filter(name=self.device.name).annotate_config_context_data()
        self.assertEqual(self.device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_annotation_same_as_get_for_object_device_relations(self):

        site_context = ConfigContext.objects.create(
            name="site",
            weight=100,
            data={
                "site": 1
            }
        )
        site_context.sites.add(self.site)
        region_context = ConfigContext.objects.create(
            name="region",
            weight=100,
            data={
                "region": 1
            }
        )
        region_context.regions.add(self.region)
        platform_context = ConfigContext.objects.create(
            name="platform",
            weight=100,
            data={
                "platform": 1
            }
        )
        platform_context.platforms.add(self.platform)
        tenant_group_context = ConfigContext.objects.create(
            name="tenant group",
            weight=100,
            data={
                "tenant_group": 1
            }
        )
        tenant_group_context.tenant_groups.add(self.tenantgroup)
        tenant_context = ConfigContext.objects.create(
            name="tenant",
            weight=100,
            data={
                "tenant": 1
            }
        )
        tenant_context.tenants.add(self.tenant)
        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context.tags.add(self.tag)

        device = Device.objects.create(
            name="Device 2",
            site=self.site,
            tenant=self.tenant,
            platform=self.platform,
            device_role=self.devicerole,
            device_type=self.devicetype
        )
        device.tags.add(self.tag)

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_annotation_same_as_get_for_object_virtualmachine_relations(self):

        site_context = ConfigContext.objects.create(
            name="site",
            weight=100,
            data={
                "site": 1
            }
        )
        site_context.sites.add(self.site)
        region_context = ConfigContext.objects.create(
            name="region",
            weight=100,
            data={
                "region": 1
            }
        )
        region_context.regions.add(self.region)
        platform_context = ConfigContext.objects.create(
            name="platform",
            weight=100,
            data={
                "platform": 1
            }
        )
        platform_context.platforms.add(self.platform)
        tenant_group_context = ConfigContext.objects.create(
            name="tenant group",
            weight=100,
            data={
                "tenant_group": 1
            }
        )
        tenant_group_context.tenant_groups.add(self.tenantgroup)
        tenant_context = ConfigContext.objects.create(
            name="tenant",
            weight=100,
            data={
                "tenant": 1
            }
        )
        tenant_context.tenants.add(self.tenant)
        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context.tags.add(self.tag)
        cluster_group = ClusterGroup.objects.create(name="Cluster Group")
        cluster_group_context = ConfigContext.objects.create(
            name="cluster group",
            weight=100,
            data={
                "cluster_group": 1
            }
        )
        cluster_group_context.cluster_groups.add(cluster_group)
        cluster_type = ClusterType.objects.create(name="Cluster Type 1")
        cluster = Cluster.objects.create(name="Cluster", group=cluster_group, type=cluster_type)
        cluster_context = ConfigContext.objects.create(
            name="cluster",
            weight=100,
            data={
                "cluster": 1
            }
        )
        cluster_context.clusters.add(cluster)

        virtual_machine = VirtualMachine.objects.create(
            name="VM 1",
            cluster=cluster,
            tenant=self.tenant,
            platform=self.platform,
            role=self.devicerole
        )
        virtual_machine.tags.add(self.tag)

        annotated_queryset = VirtualMachine.objects.filter(name=virtual_machine.name).annotate_config_context_data()
        self.assertEqual(virtual_machine.get_config_context(), annotated_queryset[0].get_config_context())

    def test_multiple_tags_return_distinct_objects(self):
        """
        Tagged items use a generic relationship, which results in duplicate rows being returned when queried.
        This is combatted by by appending distinct() to the config context querysets. This test creates a config
        context assigned to two tags and ensures objects related by those same two tags result in only a single
        config context record being returned.

        See https://github.com/netbox-community/netbox/issues/5314
        """
        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context.tags.add(self.tag)
        tag_context.tags.add(self.tag2)

        device = Device.objects.create(
            name="Device 3",
            site=self.site,
            tenant=self.tenant,
            platform=self.platform,
            device_role=self.devicerole,
            device_type=self.devicetype
        )
        device.tags.add(self.tag)
        device.tags.add(self.tag2)

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(ConfigContext.objects.get_for_object(device).count(), 1)
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())
