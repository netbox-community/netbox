from django.test import TestCase

from core.models import ObjectType
from dcim.models import Device, VirtualChassis
from extras.models import CachedValue
from utilities.testing import create_test_device


class VirtualChassisSearchCacheTestCase(TestCase):

    def setUp(self):
        # Object creation triggers deferred (post-commit) search caching. With no RQ worker
        # running in tests the flush falls back to synchronous indexing; execute the on_commit
        # callbacks so the member Device's cache is populated before each test runs.
        with self.captureOnCommitCallbacks(execute=True):
            self.vc = VirtualChassis.objects.create(name='VC1')
            self.device = create_test_device('Switch-1', virtual_chassis=self.vc, vc_position=1)
        self.object_type = ObjectType.objects.get_for_model(Device)

    def test_renaming_virtual_chassis_refreshes_member_search_cache(self):
        """
        Renaming a VirtualChassis updates the cached virtual_chassis value for its member Devices.
        """
        # The member device is initially cached under the original VC name
        self.assertTrue(
            CachedValue.objects.filter(
                object_type=self.object_type,
                object_id=self.device.pk,
                field='virtual_chassis',
                value='VC1',
            ).exists()
        )

        # Rename the VirtualChassis
        self.vc.name = 'VC-test'
        self.vc.save()

        # The stale entry is gone and a fresh one reflects the new name
        self.assertFalse(
            CachedValue.objects.filter(
                object_type=self.object_type,
                object_id=self.device.pk,
                field='virtual_chassis',
                value='VC1',
            ).exists()
        )
        self.assertTrue(
            CachedValue.objects.filter(
                object_type=self.object_type,
                object_id=self.device.pk,
                field='virtual_chassis',
                value='VC-test',
            ).exists()
        )

    def test_updating_virtual_chassis_without_name_change_keeps_member_cache(self):
        """
        A targeted save excluding 'name' leaves the member Device search cache untouched.
        """
        self.vc.domain = 'example'
        self.vc.save(update_fields=['domain'])

        self.assertTrue(
            CachedValue.objects.filter(
                object_type=self.object_type,
                object_id=self.device.pk,
                field='virtual_chassis',
                value='VC1',
            ).exists()
        )
