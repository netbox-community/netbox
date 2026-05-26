from unittest import mock

from django.test import TestCase

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Region, Site, SiteGroup
from extras.cache import invalidate_config_context_for_objects
from extras.jobs import RenderConfigContextJob
from extras.models import ConfigContext, Tag


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

    def test_invalidate_with_empty_args_is_noop(self):
        invalidate_config_context_for_objects('dcim.device', [])
