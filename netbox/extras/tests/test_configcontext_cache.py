from unittest import mock

from django.db import connection, router
from django.db.models import F, Q
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from core.models import Job
from dcim.models import Device, DeviceRole, DeviceType, Location, Manufacturer, Platform, Region, Site, SiteGroup
from extras.cache import (
    invalidate_config_context_for_configcontext,
    invalidate_config_context_for_objects,
    invalidate_for_scope_delta,
)
from extras.jobs import RenderConfigContextJob
from extras.models import ConfigContext, Tag
from extras.signals import _make_direct_upstream_handler, _make_reparent_handler
from tenancy.models import Tenant, TenantGroup
from utilities.testing import PinnedConnectionRouter
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


def _set_cache(device, value):
    """Manually set the cache field and refresh the in-memory instance so subsequent save()
    calls don't overwrite the DB value with stale in-memory state."""
    type(device).objects.filter(pk=device.pk).update(_config_context_data=value)
    device.refresh_from_db()


def _get_cache(device):
    device.refresh_from_db()
    return device._config_context_data


class ConfigContextCacheReadPathTest(TestCase):
    """
    get_config_context() must return the cached `_config_context_data` blob when present, and
    fall back to the on-demand render path when it is NULL.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')
        cls.site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(
            name='Device', device_type=cls.devicetype, role=cls.role, site=cls.site
        )

    def test_cached_value_is_returned(self):
        cached = {'cached': True, 'value': 42}
        _set_cache(self.device, cached)
        device = Device.objects.get(pk=self.device.pk)
        self.assertEqual(device.get_config_context(), cached)

    def test_null_cache_falls_back_to_render(self):
        ConfigContext.objects.create(name='CC', weight=100, data={'rendered': True})
        device = Device.objects.get(pk=self.device.pk)
        self.assertIsNone(device._config_context_data)
        self.assertEqual(device.get_config_context(), {'rendered': True})

    def test_render_matches_legacy_path(self):
        ConfigContext.objects.create(name='A', weight=100, data={'a': 1})
        ConfigContext.objects.create(name='B', weight=200, data={'a': 2, 'b': 3})

        device = Device.objects.get(pk=self.device.pk)
        on_demand = device.render_config_context()
        _set_cache(device, on_demand)
        self.assertEqual(device.get_config_context(), on_demand)


class ConfigContextInvalidationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')
        cls.role2 = DeviceRole.objects.create(name='Role 2', slug='role-2')
        cls.site1 = Site.objects.create(name='Site 1', slug='site-1')
        cls.site2 = Site.objects.create(name='Site 2', slug='site-2')
        cls.device_in_scope = Device.objects.create(
            name='In scope', device_type=cls.devicetype, role=cls.role, site=cls.site1,
        )
        cls.device_out_of_scope = Device.objects.create(
            name='Out of scope', device_type=cls.devicetype, role=cls.role, site=cls.site2,
        )

    def setUp(self):
        # Pre-populate caches for both devices.
        _set_cache(self.device_in_scope, {'cached': True})
        _set_cache(self.device_out_of_scope, {'cached': True})

    def test_configcontext_save_invalidates_in_scope_only(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.sites.add(self.site1)
        # Re-populate caches (the create + m2m add above already triggered invalidations).
        _set_cache(self.device_in_scope, {'cached': True})
        _set_cache(self.device_out_of_scope, {'cached': True})

        cc.data = {'x': 2}
        cc.save()

        self.assertIsNone(_get_cache(self.device_in_scope))
        self.assertEqual(_get_cache(self.device_out_of_scope), {'cached': True})

    def test_configcontext_delete_invalidates_in_scope(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.sites.add(self.site1)
        _set_cache(self.device_in_scope, {'cached': True})
        _set_cache(self.device_out_of_scope, {'cached': True})

        cc.delete()

        self.assertIsNone(_get_cache(self.device_in_scope))
        self.assertEqual(_get_cache(self.device_out_of_scope), {'cached': True})

    def test_m2m_post_add_invalidates_newly_in_scope(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        _set_cache(self.device_in_scope, {'cached': True})

        cc.sites.add(self.site1)

        self.assertIsNone(_get_cache(self.device_in_scope))

    def test_m2m_post_remove_invalidates_previously_in_scope(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.sites.add(self.site1)
        _set_cache(self.device_in_scope, {'cached': True})

        cc.sites.remove(self.site1)

        self.assertIsNone(_get_cache(self.device_in_scope))

    def test_device_role_change_invalidates(self):
        self.device_in_scope.snapshot()
        self.device_in_scope.role = self.role2
        self.device_in_scope.save()

        self.assertIsNone(_get_cache(self.device_in_scope))

    def test_device_serial_change_does_not_invalidate(self):
        # Refresh first so the in-memory instance has the cached value (avoids save() writing
        # stale NULL back to the DB).
        self.device_in_scope.refresh_from_db()
        self.device_in_scope.snapshot()
        self.device_in_scope.serial = 'ABC123'
        self.device_in_scope.save()

        self.assertEqual(_get_cache(self.device_in_scope), {'cached': True})

    def test_device_tag_add_invalidates(self):
        tag = Tag.objects.create(name='Tag', slug='tag')
        self.device_in_scope.tags.add(tag)

        self.assertIsNone(_get_cache(self.device_in_scope))


class ConfigContextUpstreamDeleteInvalidationTest(TestCase):
    """
    Deleting an upstream object referenced by a Device/VM via a SET_NULL FK nulls that FK with a
    bulk UPDATE that emits no post_save signal. The pre_delete handlers must invalidate the
    affected caches before the references are cleared.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')

    def test_platform_delete_invalidates(self):
        platform = Platform.objects.create(name='Platform', slug='platform')
        site = Site.objects.create(name='Site', slug='site')
        device = Device.objects.create(
            name='Device', device_type=self.devicetype, role=self.role, site=site, platform=platform,
        )
        _set_cache(device, {'cached': True})

        platform.delete()

        self.assertIsNone(_get_cache(device))

    def test_region_delete_invalidates(self):
        region = Region.objects.create(name='Region', slug='region')
        site = Site.objects.create(name='Site', slug='site', region=region)
        device = Device.objects.create(
            name='Device', device_type=self.devicetype, role=self.role, site=site,
        )
        _set_cache(device, {'cached': True})

        region.delete()

        self.assertIsNone(_get_cache(device))

    def test_site_group_delete_invalidates(self):
        group = SiteGroup.objects.create(name='Group', slug='group')
        site = Site.objects.create(name='Site', slug='site', group=group)
        device = Device.objects.create(
            name='Device', device_type=self.devicetype, role=self.role, site=site,
        )
        _set_cache(device, {'cached': True})

        group.delete()

        self.assertIsNone(_get_cache(device))


class RenderConfigContextJobTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(
            name='Device', device_type=devicetype, role=role, site=site,
        )
        ConfigContext.objects.create(name='CC', weight=100, data={'foo': 'bar'})

    def _make_runner(self):
        runner = RenderConfigContextJob.__new__(RenderConfigContextJob)
        runner.job = mock.Mock()
        runner.logger = mock.Mock()
        return runner

    def test_job_populates_cache(self):
        Device.objects.filter(pk=self.device.pk).update(_config_context_data=None)
        self._make_runner()._render_for_model('dcim.device', pks=[self.device.pk])

        self.device.refresh_from_db()
        self.assertEqual(self.device._config_context_data, {'foo': 'bar'})

    def test_job_idempotent_on_repopulated_cache(self):
        runner = self._make_runner()
        runner._render_for_model('dcim.device', pks=[self.device.pk])
        self.device.refresh_from_db()
        first = self.device._config_context_data

        Device.objects.filter(pk=self.device.pk).update(_config_context_data=None)
        runner._render_for_model('dcim.device', pks=[self.device.pk])
        self.device.refresh_from_db()
        self.assertEqual(self.device._config_context_data, first)

    def test_job_skips_stale_write_on_concurrent_invalidation(self):
        """
        If an invalidation bumps the generation counter after the renderer captured it but before
        the result is written, the compare-and-set write must be rejected so a stale value is never
        persisted (the row stays NULL for the follow-up job to re-render).
        """
        Device.objects.filter(pk=self.device.pk).update(
            _config_context_data=None, _config_context_generation=1
        )
        runner = self._make_runner()

        def racing_render(device_self):
            # Simulate a concurrent invalidation committing mid-render.
            Device.objects.filter(pk=device_self.pk).update(
                _config_context_generation=F('_config_context_generation') + 1
            )
            return {'stale': True}

        with mock.patch.object(Device, 'render_config_context', autospec=True, side_effect=racing_render):
            runner._render_for_model('dcim.device', pks=[self.device.pk])

        self.device.refresh_from_db()
        self.assertIsNone(self.device._config_context_data)
        self.assertEqual(self.device._config_context_generation, 2)

        # A subsequent render against the current generation succeeds.
        runner._render_for_model('dcim.device', pks=[self.device.pk])
        self.device.refresh_from_db()
        self.assertEqual(self.device._config_context_data, {'foo': 'bar'})

    def test_run_rescans_for_caches_nulled_mid_sweep(self):
        """
        An invalidation that commits while this job is already RUNNING coalesces into it (rather
        than enqueuing a follow-up), so run() must re-scan after each pass. Otherwise a cache that
        is NULLed after its row has been passed over would be stranded on the on-demand read path
        with no job left to repopulate it.
        """
        device_b = Device.objects.create(
            name='Device B', device_type=self.device.device_type, role=self.device.role,
            site=self.device.site,
        )
        # Device A needs rendering; Device B starts populated, so the first scan skips it.
        Device.objects.filter(pk=self.device.pk).update(_config_context_data=None)
        Device.objects.filter(pk=device_b.pk).update(_config_context_data={'old': True})

        runner = self._make_runner()
        real_render = Device.render_config_context
        nulled = []

        def render_then_null_b(device_self):
            # While rendering Device A (the first pass), simulate a concurrent invalidation NULLing
            # Device B's cache after B has already been passed over.
            if device_self.pk == self.device.pk and not nulled:
                nulled.append(True)
                Device.objects.filter(pk=device_b.pk).update(_config_context_data=None)
            return real_render(device_self)

        with mock.patch.object(Device, 'render_config_context', autospec=True, side_effect=render_then_null_b):
            runner.run(model_label='dcim.device')

        # Both caches must be populated: A on the first pass, B on the re-scan.
        self.device.refresh_from_db()
        device_b.refresh_from_db()
        self.assertEqual(self.device._config_context_data, {'foo': 'bar'})
        self.assertEqual(device_b._config_context_data, {'foo': 'bar'})


class ConfigContextCacheJobEnqueueTest(TestCase):
    """
    Invalidation NULLs the cache synchronously and enqueues the render job on transaction commit.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(
            name='Device', device_type=devicetype, role=role, site=site,
        )

    def test_invalidation_enqueues_render_job_on_commit(self):
        _set_cache(self.device, {'x': 1})
        self.assertFalse(Job.objects.filter(name=RenderConfigContextJob.name).exists())

        with self.captureOnCommitCallbacks(execute=True):
            invalidate_config_context_for_objects('dcim.device', [self.device.pk])

        self.assertTrue(Job.objects.filter(name=RenderConfigContextJob.name).exists())


class CacheHelperTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(
            name='Device', device_type=devicetype, role=role, site=site,
        )

    def test_invalidate_for_objects_nulls_cache(self):
        _set_cache(self.device, {'x': 1})
        invalidate_config_context_for_objects('dcim.device', [self.device.pk])
        self.assertIsNone(_get_cache(self.device))

    def test_invalidate_for_objects_bumps_generation(self):
        _set_cache(self.device, {'x': 1})
        self.device.refresh_from_db()
        before = self.device._config_context_generation
        invalidate_config_context_for_objects('dcim.device', [self.device.pk])
        self.device.refresh_from_db()
        self.assertEqual(self.device._config_context_generation, before + 1)

    def test_invalidate_with_empty_args_is_noop(self):
        invalidate_config_context_for_objects('dcim.device', [])


class VirtualMachineInvalidationTest(TestCase):
    """
    The invalidation signals must cover VirtualMachine, not just Device.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site1 = Site.objects.create(name='Site 1', slug='site-1')
        cls.site2 = Site.objects.create(name='Site 2', slug='site-2')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')
        cls.role2 = DeviceRole.objects.create(name='Role 2', slug='role-2')
        clustertype = ClusterType.objects.create(name='CT', slug='ct')
        cls.cluster = Cluster.objects.create(name='Cluster', type=clustertype)
        cls.vm_in_scope = VirtualMachine.objects.create(name='In scope', site=cls.site1, role=cls.role)
        cls.vm_out_of_scope = VirtualMachine.objects.create(name='Out of scope', site=cls.site2, role=cls.role)

    def setUp(self):
        _set_cache(self.vm_in_scope, {'cached': True})
        _set_cache(self.vm_out_of_scope, {'cached': True})

    def test_configcontext_save_invalidates_in_scope_vm_only(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.sites.add(self.site1)
        _set_cache(self.vm_in_scope, {'cached': True})
        _set_cache(self.vm_out_of_scope, {'cached': True})

        cc.data = {'x': 2}
        cc.save()

        self.assertIsNone(_get_cache(self.vm_in_scope))
        self.assertEqual(_get_cache(self.vm_out_of_scope), {'cached': True})

    def test_vm_role_change_invalidates(self):
        self.vm_in_scope.refresh_from_db()
        self.vm_in_scope.snapshot()
        self.vm_in_scope.role = self.role2
        self.vm_in_scope.save()
        self.assertIsNone(_get_cache(self.vm_in_scope))

    def test_vm_tag_add_invalidates(self):
        tag = Tag.objects.create(name='Tag', slug='tag')
        self.vm_in_scope.tags.add(tag)
        self.assertIsNone(_get_cache(self.vm_in_scope))

    def test_device_only_scope_does_not_invalidate_vm(self):
        # A context scoped by device_type can never apply to a VM, so its changes must not touch
        # VM caches.
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.device_types.add(devicetype)
        _set_cache(self.vm_in_scope, {'cached': True})

        cc.data = {'x': 2}
        cc.save()

        self.assertEqual(_get_cache(self.vm_in_scope), {'cached': True})


class ConfigContextUpstreamChangeInvalidationTest(TestCase):
    """
    Changes to intermediate/hierarchical objects (not the Device/VM itself) must invalidate the
    affected caches: direct FK changes on an intermediate model, and ltree reparents.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')

    def _make_device(self, site):
        device = Device.objects.create(
            name=f'Device {site.slug}', device_type=self.devicetype, role=self.role, site=site,
        )
        _set_cache(device, {'cached': True})
        return device

    def test_direct_upstream_site_region_change_invalidates(self):
        region1 = Region.objects.create(name='R1', slug='r1')
        region2 = Region.objects.create(name='R2', slug='r2')
        site = Site.objects.create(name='Site', slug='site', region=region1)
        device = self._make_device(site)

        site.snapshot()
        site.region = region2
        site.save()

        self.assertIsNone(_get_cache(device))

    def test_region_reparent_invalidates(self):
        region_a = Region.objects.create(name='A', slug='a')
        region_b = Region.objects.create(name='B', slug='b')
        site = Site.objects.create(name='Site', slug='site', region=region_b)
        device = self._make_device(site)

        region_b.snapshot()
        region_b.parent = region_a
        region_b.save()

        self.assertIsNone(_get_cache(device))

    def test_direct_upstream_cluster_type_change_invalidates_vm(self):
        ct1 = ClusterType.objects.create(name='CT1', slug='ct1')
        ct2 = ClusterType.objects.create(name='CT2', slug='ct2')
        cluster = Cluster.objects.create(name='Cluster', type=ct1)
        site = Site.objects.create(name='Site', slug='site')
        vm = VirtualMachine.objects.create(name='VM', site=site, role=self.role, cluster=cluster)
        _set_cache(vm, {'cached': True})

        cluster.snapshot()
        cluster.type = ct2
        cluster.save()

        self.assertIsNone(_get_cache(vm))

    def test_direct_upstream_cluster_group_change_invalidates_vm(self):
        ct = ClusterType.objects.create(name='CT', slug='ct')
        cg1 = ClusterGroup.objects.create(name='CG1', slug='cg1')
        cg2 = ClusterGroup.objects.create(name='CG2', slug='cg2')
        cluster = Cluster.objects.create(name='Cluster', type=ct, group=cg1)
        site = Site.objects.create(name='Site', slug='site')
        vm = VirtualMachine.objects.create(name='VM', site=site, role=self.role, cluster=cluster)
        _set_cache(vm, {'cached': True})

        cluster.snapshot()
        cluster.group = cg2
        cluster.save()

        self.assertIsNone(_get_cache(vm))

    def test_direct_upstream_cluster_scope_change_invalidates_vm(self):
        # A Cluster's effective site lives in the cached `_site_id`, which virtualization.signals
        # propagates onto every VM in the cluster with a bulk UPDATE emitting no post_save. The
        # VMs' site-based matching shifts with it, so the Cluster save must invalidate them.
        ct = ClusterType.objects.create(name='CT', slug='ct')
        site1 = Site.objects.create(name='Site 1', slug='site-1')
        site2 = Site.objects.create(name='Site 2', slug='site-2')
        cluster = Cluster.objects.create(name='Cluster', type=ct, scope=site1)
        vm = VirtualMachine.objects.create(name='VM', role=self.role, cluster=cluster)
        self.assertEqual(vm.site, site1)
        _set_cache(vm, {'cached': True})

        cluster.snapshot()
        cluster.scope = site2
        cluster.save()

        self.assertIsNone(_get_cache(vm))

    def test_direct_upstream_tenant_group_change_invalidates_device(self):
        tg1 = TenantGroup.objects.create(name='TG1', slug='tg1')
        tg2 = TenantGroup.objects.create(name='TG2', slug='tg2')
        tenant = Tenant.objects.create(name='Tenant', slug='tenant', group=tg1)
        site = Site.objects.create(name='Site', slug='site')
        device = Device.objects.create(
            name='Device', device_type=self.devicetype, role=self.role, site=site, tenant=tenant,
        )
        _set_cache(device, {'cached': True})

        tenant.snapshot()
        tenant.group = tg2
        tenant.save()

        self.assertIsNone(_get_cache(device))

    def test_direct_upstream_tenant_group_change_invalidates_vm(self):
        tg1 = TenantGroup.objects.create(name='TG1', slug='tg1')
        tg2 = TenantGroup.objects.create(name='TG2', slug='tg2')
        tenant = Tenant.objects.create(name='Tenant', slug='tenant', group=tg1)
        site = Site.objects.create(name='Site', slug='site')
        vm = VirtualMachine.objects.create(name='VM', site=site, role=self.role, tenant=tenant)
        _set_cache(vm, {'cached': True})

        tenant.snapshot()
        tenant.group = tg2
        tenant.save()

        self.assertIsNone(_get_cache(vm))

    def test_m2m_post_clear_invalidates(self):
        site = Site.objects.create(name='Site', slug='site')
        device = self._make_device(site)
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'x': 1})
        cc.sites.add(site)
        _set_cache(device, {'cached': True})

        cc.sites.clear()

        self.assertIsNone(_get_cache(device))


class ConfigContextScopeParityTest(TestCase):
    """
    The inverse matcher (ConfigContext.get_affected_objects()) must agree exactly with the forward
    matcher (ConfigContextQuerySet.get_for_object()) across every scope dimension, including
    hierarchy expansion and device-only dimensions.
    """

    @classmethod
    def setUpTestData(cls):
        # Hierarchies
        cls.region_parent = Region.objects.create(name='Region Parent', slug='region-parent')
        cls.region_child = Region.objects.create(name='Region Child', slug='region-child', parent=cls.region_parent)
        cls.sg_parent = SiteGroup.objects.create(name='SG Parent', slug='sg-parent')
        cls.sg_child = SiteGroup.objects.create(name='SG Child', slug='sg-child', parent=cls.sg_parent)
        cls.role_parent = DeviceRole.objects.create(name='Role Parent', slug='role-parent')
        cls.role_child = DeviceRole.objects.create(name='Role Child', slug='role-child', parent=cls.role_parent)
        cls.plat_parent = Platform.objects.create(name='Plat Parent', slug='plat-parent')
        cls.plat_child = Platform.objects.create(name='Plat Child', slug='plat-child', parent=cls.plat_parent)
        cls.tg = TenantGroup.objects.create(name='TG', slug='tg')
        cls.tenant = Tenant.objects.create(name='Tenant', slug='tenant', group=cls.tg)

        cls.site_a = Site.objects.create(
            name='Site A', slug='site-a', region=cls.region_child, group=cls.sg_child
        )
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.loc_parent = Location.objects.create(name='Loc Parent', slug='loc-parent', site=cls.site_a)
        cls.loc_child = Location.objects.create(
            name='Loc Child', slug='loc-child', site=cls.site_a, parent=cls.loc_parent
        )

        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        clustertype = ClusterType.objects.create(name='CT', slug='ct')
        clustergroup = ClusterGroup.objects.create(name='CG', slug='cg')
        cls.cluster = Cluster.objects.create(name='Cluster', type=clustertype, group=clustergroup)
        cls.tag = Tag.objects.create(name='Tag', slug='tag')

        cls.d_full = Device.objects.create(
            name='d-full', device_type=cls.devicetype, role=cls.role_child, site=cls.site_a,
            location=cls.loc_child, platform=cls.plat_child, tenant=cls.tenant, cluster=cls.cluster,
        )
        cls.d_full.tags.add(cls.tag)
        cls.d_min = Device.objects.create(
            name='d-min', device_type=cls.devicetype, role=cls.role_parent, site=cls.site_b,
        )
        cls.vm_full = VirtualMachine.objects.create(
            name='vm-full', site=cls.site_a, role=cls.role_child, platform=cls.plat_child,
            tenant=cls.tenant, cluster=cls.cluster,
        )
        cls.vm_full.tags.add(cls.tag)
        cls.vm_min = VirtualMachine.objects.create(name='vm-min', site=cls.site_b, role=cls.role_parent)

    def _assert_parity(self, cc):
        device_qs, vm_qs = cc.get_affected_objects()
        inverse_devices = set(device_qs.values_list('pk', flat=True))
        inverse_vms = set(vm_qs.values_list('pk', flat=True))

        forward_devices = {
            d.pk for d in Device.objects.all()
            if ConfigContext.objects.get_for_object(d).filter(pk=cc.pk).exists()
        }
        forward_vms = {
            v.pk for v in VirtualMachine.objects.all()
            if ConfigContext.objects.get_for_object(v).filter(pk=cc.pk).exists()
        }
        self.assertEqual(inverse_devices, forward_devices, f"device mismatch for {cc.name}")
        self.assertEqual(inverse_vms, forward_vms, f"VM mismatch for {cc.name}")

    def test_scope_parity_across_dimensions(self):
        scopes = {
            'regions': [self.region_parent],         # hierarchy: matches descendant region_child
            'site_groups': [self.sg_parent],         # hierarchy
            'sites': [self.site_a],
            'locations': [self.loc_parent],          # device-only, hierarchy
            'device_types': [self.devicetype],       # device-only
            'roles': [self.role_parent],             # hierarchy
            'platforms': [self.plat_parent],         # hierarchy
            'cluster_types': [self.cluster.type],
            'cluster_groups': [self.cluster.group],
            'clusters': [self.cluster],
            'tenant_groups': [self.tg],              # direct (immediate group only)
            'tenants': [self.tenant],
            'tags': [self.tag],
        }
        for i, (field, items) in enumerate(scopes.items()):
            cc = ConfigContext.objects.create(name=f'cc-{field}', weight=100 + i, data={field: True})
            getattr(cc, field).set(items)
            self._assert_parity(cc)

        # A context with no scope matches every object.
        cc_all = ConfigContext.objects.create(name='cc-all', weight=999, data={'all': True})
        self._assert_parity(cc_all)


class ConfigContextCacheQueryCountTest(TestCase):
    """
    Proves the optimization: when caches are warm, get_config_context() issues no per-object
    queries, whereas the cold fallback path scales with the number of objects.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        for i in range(4):
            Device.objects.create(name=f'Device {i}', device_type=devicetype, role=role, site=site)
        ConfigContext.objects.create(name='A', weight=100, data={'a': 1})
        ConfigContext.objects.create(name='B', weight=200, data={'b': 2})

    def test_warm_cache_avoids_per_object_queries(self):
        # Cold: caches are NULL, so each object renders on demand.
        Device.objects.update(_config_context_data=None)
        cold_devices = list(Device.objects.all())
        with CaptureQueriesContext(connection) as cold:
            for device in cold_devices:
                device.get_config_context()

        # Warm the caches.
        for device in Device.objects.all():
            Device.objects.filter(pk=device.pk).update(_config_context_data=device.render_config_context())

        warm_devices = list(Device.objects.all())
        with CaptureQueriesContext(connection) as warm:
            for device in warm_devices:
                device.get_config_context()

        self.assertEqual(len(warm.captured_queries), 0)
        self.assertGreaterEqual(len(cold.captured_queries), len(cold_devices))


class ConditionalConfigContextAnnotationTest(TestCase):
    """
    annotate_config_context_data(only_invalidated=True) is the list/detail read-path optimization:
    it must compute the aggregation only for rows whose cache is NULL and leave it NULL for warm
    rows, while a single query still serves a mix of warm and cold objects correctly via
    get_config_context().
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        cls.warm = Device.objects.create(name='Warm', device_type=devicetype, role=role, site=site)
        cls.cold = Device.objects.create(name='Cold', device_type=devicetype, role=role, site=site)
        ConfigContext.objects.create(name='A', weight=100, data={'a': 1})
        ConfigContext.objects.create(name='B', weight=200, data={'b': 2})

    def setUp(self):
        # Warm one device with a sentinel cache, leave the other invalidated.
        _set_cache(self.warm, {'sentinel': True})
        Device.objects.filter(pk=self.cold.pk).update(_config_context_data=None)

    def test_annotation_skips_warm_rows(self):
        rows = {
            d.pk: d
            for d in Device.objects.annotate_config_context_data(only_invalidated=True)
        }
        # Warm row: the aggregation must not have run; the annotated value is NULL.
        self.assertIsNone(rows[self.warm.pk].config_context_data)
        # Cold row: the aggregation ran and produced the ordered list of context data.
        self.assertEqual(rows[self.cold.pk].config_context_data, [{'a': 1}, {'b': 2}])

    def test_single_query_serves_mixed_warm_and_cold(self):
        qs = Device.objects.annotate_config_context_data(only_invalidated=True)
        with CaptureQueriesContext(connection) as ctx:
            rows = {d.pk: d.get_config_context() for d in qs}
        # The warm row returns its cached sentinel; the cold row is rendered from the annotation.
        self.assertEqual(rows[self.warm.pk], {'sentinel': True})
        self.assertEqual(rows[self.cold.pk], {'a': 1, 'b': 2})
        # A single query backs the whole page — no per-object fallback to get_for_object().
        self.assertEqual(len(ctx.captured_queries), 1)


# Resolving a ConfigContext's affected object set reads every dimension of its scope, whether or
# not that dimension is populated (see ConfigContext._get_affected_object_filters). A router which
# named only Device and VirtualMachine would therefore leave those scope lookups unchecked, so the
# ConfigContext-driven tests below name them all.
CC_SCOPE_MODELS = (
    Cluster,
    ClusterGroup,
    ClusterType,
    DeviceRole,
    DeviceType,
    Location,
    Platform,
    Region,
    Site,
    SiteGroup,
    Tag,
    Tenant,
    TenantGroup,
)


class ConfigContextInvalidationRoutingTest(TestCase):
    """
    Every query the invalidation makes must be issued against the connection the triggering object
    was saved on — the alias the signal supplies as `using` — rather than being resolved anew by
    DATABASE_ROUTERS. A router which resolved them elsewhere would read the affected PKs from, and
    NULL the cache in, a database other than the one holding the triggering change.

    PinnedConnectionRouter raises on any unpinned read or write of the models it is given. Each
    test omits the model being saved or deleted, as Django routes that operation itself.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Mfr', slug='mfr')
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='DT', slug='dt')
        cls.role = DeviceRole.objects.create(name='Role', slug='role')
        cls.region = Region.objects.create(name='Region', slug='region')
        cls.site_a = Site.objects.create(name='Site A', slug='site-a', region=cls.region)
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.platform = Platform.objects.create(name='Platform', slug='platform')
        cls.location = Location.objects.create(name='Location', slug='location', site=cls.site_a)
        cls.device = Device.objects.create(
            name='Device',
            device_type=cls.devicetype,
            role=cls.role,
            site=cls.site_a,
            location=cls.location,
            platform=cls.platform,
        )
        cls.cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')
        cls.cluster = Cluster.objects.create(name='Cluster', type=cls.cluster_type, scope=cls.site_a)
        cls.vm = VirtualMachine.objects.create(
            name='VM', cluster=cls.cluster, role=cls.role, platform=cls.platform
        )

    def test_helper_pins_update_to_given_connection(self):
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine)]):
            invalidate_config_context_for_objects('dcim.device', [self.device.pk], using='default')

    def test_helper_resolves_one_alias_for_update_and_enqueue(self):
        # Called without an alias, the UPDATE falls to the router but transaction.on_commit()
        # would fall to 'default', which need not be the same database: the callback would then
        # be attached to a connection other than the one being written, and could fire before
        # the UPDATE it waits on. Both must be bound to the alias the router chooses.
        with mock.patch('extras.cache.transaction.on_commit') as on_commit:
            invalidate_config_context_for_objects('dcim.device', [self.device.pk])

        self.assertEqual(on_commit.call_args.kwargs['using'], router.db_for_write(Device))

    def test_location_site_change_pins_device_query(self):
        location = Location.objects.get(pk=self.location.pk)
        location.site_id = self.site_b.pk
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device)]):
            location.save()

    def test_cluster_scope_change_pins_vm_query(self):
        # Snapshotted, so that the handler's watched-field check runs for real: absent a
        # snapshot _changed_fields() returns True conservatively, and the query under test would
        # be issued even if the trigger named a field the model does not have. Asserting the
        # cache is cleared confirms the change was actually recognized as scope-relevant.
        cluster = Cluster.objects.get(pk=self.cluster.pk)
        _set_cache(self.vm, {'cached': True})
        cluster.snapshot()
        cluster.scope = self.site_b
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(VirtualMachine)]):
            cluster.save()

        self.assertIsNone(_get_cache(self.vm))

    def test_region_reparent_pins_device_and_vm_queries(self):
        parent = Region.objects.create(name='Parent', slug='parent')
        region = Region.objects.get(pk=self.region.pk)
        region.parent = parent
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine)]):
            region.save()

    def test_reparent_handler_pins_subtree_queries_to_given_connection(self):
        # The reparent handler resolves the moved node's post-move path and the PKs of its
        # subtree before it can name the affected objects, and both reads must follow the
        # saving connection. The handler is invoked directly so that the reparented model can
        # be named in the router: saving the Region under it would trip on the unpinned cycle
        # check in the ltree base save, which this handler does not control.
        parent = Region.objects.create(name='Parent', slug='parent')
        region = Region.objects.get(pk=self.region.pk)
        region.parent = parent
        region.save()

        handler = _make_reparent_handler('site__region__in', 'site__region__in')
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, Region)]):
            handler(sender=Region, instance=region, created=False, using='default')

    def test_configcontext_save_pins_device_and_vm_queries(self):
        # Both a nested (ltree) and a direct scope dimension are populated, so that the path
        # lookup and the PK lookup which resolve them are each exercised.
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'a': 1})
        cc.sites.add(self.site_a)
        cc.regions.add(self.region)
        cc.data = {'a': 2}
        with override_settings(
            DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, *CC_SCOPE_MODELS)]
        ):
            cc.save()

    def test_configcontext_delete_pins_device_and_vm_queries(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'a': 1})
        cc.sites.add(self.site_a)
        cc.regions.add(self.region)
        with override_settings(
            DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, *CC_SCOPE_MODELS)]
        ):
            cc.delete()

    def test_configcontext_m2m_add_pins_device_and_vm_queries(self):
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'a': 1})
        with override_settings(
            DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, *CC_SCOPE_MODELS)]
        ):
            cc.sites.add(self.site_a)

    def test_configcontext_m2m_remove_pins_device_and_vm_queries(self):
        # post_remove additionally resolves the removed scope items via
        # invalidate_for_scope_delta(), which must be pinned too.
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'a': 1})
        cc.sites.add(self.site_a)
        with override_settings(
            DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, *CC_SCOPE_MODELS)]
        ):
            cc.sites.remove(self.site_a)

    def test_configcontext_nested_m2m_remove_pins_scope_delta_queries(self):
        # A nested (ltree) scope dimension resolves the removed items' paths as well. Region is
        # named so that read is checked rather than merely performed.
        cc = ConfigContext.objects.create(name='CC', weight=100, data={'a': 1})
        cc.regions.add(self.region)
        with override_settings(
            DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine, *CC_SCOPE_MODELS)]
        ):
            cc.regions.remove(self.region)

    def test_upstream_delete_pins_device_and_vm_queries(self):
        # Platform is a SET_NULL feeder on both Device and VirtualMachine.
        platform = Platform.objects.create(name='Spare', slug='spare')
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device, VirtualMachine)]):
            platform.delete()

    def test_device_tag_change_pins_device_query(self):
        tag = Tag.objects.create(name='Tag', slug='tag')
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device)]):
            self.device.tags.add(tag)


# An alias which is deliberately absent from DATABASES. Every query issued against it would raise
# ConnectionDoesNotExist, so the tests below stop at the boundary where the alias is handed off
# (the queryset's `_db`, or the `using` kwarg) rather than executing anything.
OTHER_ALIAS = 'other'


class ConfigContextInvalidationAliasThreadingTest(TestCase):
    """
    ConfigContextInvalidationRoutingTest establishes that no query in the invalidation path is left
    for DATABASE_ROUTERS to resolve. That is only half of the requirement: a query pinned to the
    wrong alias consults no router either. These tests close the other half by handing each entry
    point an alias of their own choosing and asserting that *that* alias is what reaches the
    queryset and the enqueue — which a hardcoded `.using('default')` would fail.

    The alias names no real connection, so nothing here may execute a query against it. Each test
    patches the boundary immediately below the code under test, leaving the querysets unevaluated.
    """
    def test_helper_pins_update_and_enqueue_to_supplied_alias(self):
        with (
            mock.patch('extras.cache.chunked_update', return_value=1) as chunked,
            mock.patch('extras.cache.transaction.on_commit') as on_commit,
        ):
            invalidate_config_context_for_objects('dcim.device', [1], using=OTHER_ALIAS)

        self.assertEqual(chunked.call_args.args[0]._db, OTHER_ALIAS)
        self.assertEqual(on_commit.call_args.kwargs['using'], OTHER_ALIAS)

    def test_helper_pins_update_to_the_alias_it_resolves(self):
        # Called without an alias, the UPDATE and the enqueue must still agree: the alias the
        # helper resolves for on_commit() (asserted by the routing test above) is the one the
        # UPDATE has to carry, or the callback waits on a connection other than the one written.
        with (
            mock.patch('extras.cache.chunked_update', return_value=1) as chunked,
            mock.patch('extras.cache.transaction.on_commit') as on_commit,
        ):
            invalidate_config_context_for_objects('dcim.device', [1])

        self.assertEqual(chunked.call_args.args[0]._db, router.db_for_write(Device))
        self.assertEqual(chunked.call_args.args[0]._db, on_commit.call_args.kwargs['using'])

    def test_configcontext_helper_forwards_alias(self):
        cc = ConfigContext(name='CC', weight=100, data={})
        affected = (Device.objects.using(OTHER_ALIAS), VirtualMachine.objects.using(OTHER_ALIAS))
        with (
            mock.patch.object(ConfigContext, 'get_affected_objects', return_value=affected) as get_affected,
            mock.patch('extras.cache.invalidate_config_context_for_objects') as invalidate,
        ):
            invalidate_config_context_for_configcontext(cc, using=OTHER_ALIAS)

        self.assertEqual(get_affected.call_args.kwargs['using'], OTHER_ALIAS)
        self.assertEqual([c.kwargs['using'] for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])
        self.assertEqual([c.args[1]._db for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])

    def test_scope_delta_pins_pk_selects_to_supplied_alias(self):
        # 'sites' is a direct (non-nested, non-tag) scope dimension, so the function resolves it
        # without a query of its own and the Device/VM PK selects are the only reads to check.
        with mock.patch('extras.cache.invalidate_config_context_for_objects') as invalidate:
            invalidate_for_scope_delta('sites', [1], using=OTHER_ALIAS)

        self.assertEqual([c.kwargs['using'] for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])
        self.assertEqual([c.args[1]._db for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])

    def test_get_affected_objects_binds_querysets_to_supplied_alias(self):
        cc = ConfigContext(name='CC', weight=100, data={})
        with mock.patch.object(
            ConfigContext, '_get_affected_object_filters', return_value=(Q(), Q())
        ) as get_filters:
            device_qs, vm_qs = cc.get_affected_objects(using=OTHER_ALIAS)

        self.assertEqual(get_filters.call_args.kwargs['using'], OTHER_ALIAS)
        self.assertEqual(device_qs._db, OTHER_ALIAS)
        self.assertEqual(vm_qs._db, OTHER_ALIAS)

    def test_upstream_handler_forwards_alias_to_helper(self):
        # The receivers take their alias from the signal; the handler is invoked directly so that
        # an alias other than the one the test connection would supply can be threaded through it.
        handler = _make_direct_upstream_handler(('name',), 'platform_id', 'platform_id')
        with mock.patch('extras.signals.invalidate_config_context_for_objects') as invalidate:
            handler(sender=Platform, instance=Platform(pk=1, name='Platform'), created=False, using=OTHER_ALIAS)

        self.assertEqual([c.kwargs['using'] for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])
        self.assertEqual([c.args[1]._db for c in invalidate.call_args_list], [OTHER_ALIAS, OTHER_ALIAS])
