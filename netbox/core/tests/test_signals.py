import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.signals import request_finished
from django.db import transaction
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from core import signals
from core.choices import DataSourceStatusChoices, JobStatusChoices, ObjectChangeActionChoices
from core.models import ConfigRevision, DataSource, ObjectChange, ObjectType
from core.signals import _signals_received, clear_events, post_sync
from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site, SiteGroup
from extras.models import Tag
from extras.validators import CustomValidator
from netbox.context import events_queue
from netbox.context_managers import event_tracking
from users.models import User
from utilities.exceptions import AbortRequest


def _build_request(user):
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = user
    return request


class UpdateObjectTypesSignalTestCase(TestCase):
    """
    Verify core.signals.update_object_types has registered an ObjectType for known
    models, with the expected public flag and feature set.
    """

    def test_public_model_object_type_is_registered(self):
        ot = ObjectType.objects.get(app_label='dcim', model='site')
        self.assertTrue(ot.public)
        # Site supports several features — verify a couple representative ones.
        self.assertIn('custom_fields', ot.features)
        self.assertIn('tags', ot.features)

    def test_private_model_object_type_is_registered_as_non_public(self):
        ot = ObjectType.objects.get(app_label='dcim', model='cablepath')
        self.assertFalse(ot.public)


class HandleChangedObjectSignalTestCase(TestCase):
    """
    Verify core.signals.handle_changed_object writes an ObjectChange and increments
    metric counters whenever a tracked object is created or updated within a request.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_create_records_an_objectchange(self):
        request = _build_request(self.user)
        with event_tracking(request):
            site = Site.objects.create(name='Site 1', slug='site-1')

        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk,
        )
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(oc.user, self.user)
        self.assertEqual(oc.request_id, request.id)

    def test_update_records_an_objectchange(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        request = _build_request(self.user)

        with event_tracking(request):
            site.description = 'updated'
            site.save()

        ocs = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk,
        ).order_by('-pk')
        self.assertEqual(ocs.first().action, ObjectChangeActionChoices.ACTION_UPDATE)

    def test_no_request_skips_objectchange(self):
        # Saving outside a request context (no event_tracking) should not record any
        # ObjectChange entries.
        Site.objects.create(name='Site 1', slug='site-1')
        self.assertEqual(ObjectChange.objects.count(), 0)

    def test_m2m_tag_change_records_objectchange_with_postchange_tags(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        tag = Tag.objects.create(name='Important', slug='important')
        request = _build_request(self.user)

        with event_tracking(request):
            site.tags.add(tag)

        oc = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk,
        ).first()
        self.assertEqual(oc.postchange_data['tags'], ['Important'])


class HandleDeletedObjectSignalTestCase(TestCase):
    """
    Verify core.signals.handle_deleted_object writes a delete-type ObjectChange and
    respects PROTECTION_RULES.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def setUp(self):
        # Reset the in-memory pre_delete bookkeeping; the signal's de-dup set lives in a
        # threading.local that is not rolled back between TestCase methods.
        _signals_received.pre_delete = set()

    def test_delete_records_an_objectchange(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_pk = site.pk
        site_type = ContentType.objects.get_for_model(Site)
        request = _build_request(self.user)

        with event_tracking(request):
            site.delete()

        oc = ObjectChange.objects.get(changed_object_type=site_type, changed_object_id=site_pk)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertIsNone(oc.postchange_data)

    @override_settings(PROTECTION_RULES={'dcim.site': [CustomValidator({'name': {'neq': 'protected'}})]})
    def test_protection_rule_violation_aborts_deletion(self):
        site = Site.objects.create(name='protected', slug='protected')
        request = _build_request(self.user)

        with event_tracking(request):
            # The signal raises AbortRequest from a pre_delete handler, which can poison
            # the surrounding transaction; isolate the delete in its own atomic block.
            with self.assertRaises((AbortRequest, ValidationError)):
                with transaction.atomic():
                    site.delete()

        self.assertTrue(Site.objects.filter(pk=site.pk).exists())

    def test_delete_records_single_objectchange(self):
        # A delete should record exactly one ObjectChange for the deleted object.
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_pk = site.pk
        site_type = ContentType.objects.get_for_model(Site)
        request = _build_request(self.user)

        with event_tracking(request):
            site.delete()

        ocs = ObjectChange.objects.filter(changed_object_type=site_type, changed_object_id=site_pk)
        self.assertEqual(ocs.count(), 1)

    def test_duplicate_pre_delete_for_same_instance_is_ignored(self):
        # Exercise the dedup short-circuit by invoking the handler twice for the
        # same instance, mirroring what happens when a parent and its child are
        # deleted simultaneously and the same pre_delete fires more than once.
        # Only the first invocation should record an ObjectChange.
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_pk = site.pk
        site_type = ContentType.objects.get_for_model(Site)
        request = _build_request(self.user)

        with event_tracking(request):
            signals.handle_deleted_object(sender=Site, instance=site)
            signals.handle_deleted_object(sender=Site, instance=site)

        ocs = ObjectChange.objects.filter(
            changed_object_type=site_type,
            changed_object_id=site_pk,
            action=ObjectChangeActionChoices.ACTION_DELETE,
        )
        self.assertEqual(ocs.count(), 1)

    def test_delete_records_change_for_objects_with_nulled_fk(self):
        # When a parent is deleted, related objects with on_delete=SET_NULL have
        # their FK cleared by the signal *and* receive a change-log entry via
        # snapshot()+save(). Without the signal, Django's SET_NULL would clear
        # the FK silently with no ObjectChange.
        group = SiteGroup.objects.create(name='Group', slug='group')
        group_pk = group.pk
        site = Site.objects.create(name='Site', slug='site', group=group)
        site_type = ContentType.objects.get_for_model(Site)
        request = _build_request(self.user)

        with event_tracking(request):
            group.delete()

        site.refresh_from_db()
        self.assertIsNone(site.group)
        oc = ObjectChange.objects.get(
            changed_object_type=site_type,
            changed_object_id=site.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertEqual(oc.prechange_data['group'], group_pk)
        self.assertIsNone(oc.postchange_data['group'])

    def test_cascade_delete_does_not_record_update_after_delete(self):
        # Regression test for #22270. Deleting a device cascades to all of its interfaces.
        # When the LAG interface's pre_delete fires, it clears the `lag` FK (SET_NULL) on its
        # member interfaces and records a change. If a member is itself being deleted in the
        # same cascade, that update must not be written *after* the member's delete record —
        # an UPDATE-after-DELETE corrupts the changelog and breaks branch replay.
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type', slug='device-type')
        role = DeviceRole.objects.create(name='Role', slug='role')
        site = Site.objects.create(name='Site', slug='site')
        device = Device.objects.create(name='Device', site=site, device_type=device_type, role=role)
        # Members are created before the LAG so their PKs are lower; the cascade fires their
        # pre_delete (and records their DELETE) before the LAG's pre_delete runs.
        member1 = Interface.objects.create(device=device, name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        member2 = Interface.objects.create(device=device, name='eth1', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        lag = Interface.objects.create(device=device, name='lag0', type=InterfaceTypeChoices.TYPE_LAG)
        member1.lag = lag
        member1.save()
        member2.lag = lag
        member2.save()
        member_pks = (member1.pk, member2.pk)
        interface_type = ContentType.objects.get_for_model(Interface)

        request = _build_request(self.user)
        with event_tracking(request):
            device.delete()

        for member_pk in member_pks:
            actions = list(
                ObjectChange.objects.filter(
                    request_id=request.id,
                    changed_object_type=interface_type,
                    changed_object_id=member_pk,
                ).order_by('time', 'pk').values_list('action', flat=True)
            )
            # In this ordering the member's pre_delete fires before the LAG's, so the LAG
            # skips it: the member's only change record for the request is its own deletion.
            # Pre-fix, a spurious UPDATE was appended *after* this DELETE — assert the exact
            # sequence so any trailing (or leading) update fails the test.
            self.assertEqual(actions, [ObjectChangeActionChoices.ACTION_DELETE])


class ClearSignalHistorySignalTestCase(TestCase):
    """
    Verify core.signals.clear_signal_history resets the pre_delete bookkeeping at the
    end of every request.
    """

    def test_request_finished_clears_history(self):
        _signals_received.pre_delete = {('a', 1), ('b', 2)}

        request_finished.send(sender=self.__class__)

        self.assertEqual(_signals_received.pre_delete, set())


class ClearEventsQueueSignalTestCase(TestCase):
    """
    Verify core.signals.clear_events_queue empties the in-flight events queue when the
    clear_events signal fires (e.g. during a rolled-back bulk transaction).
    """

    def test_clear_events_signal_empties_the_queue(self):
        events_queue.set({'event-1': object(), 'event-2': object()})

        clear_events.send(sender='test-suite')

        self.assertEqual(events_queue.get(), {})


class EnqueueSyncJobSignalTestCase(TestCase):
    """
    Verify core.signals.enqueue_sync_job schedules a recurring sync job when a
    DataSource is saved with a sync_interval, and removes any existing schedule
    otherwise.
    """

    def test_saving_datasource_with_interval_enqueues_sync_job(self):
        with patch('core.jobs.SyncDataSourceJob') as sync_job:
            DataSource.objects.create(
                name='DS 1',
                type='local',
                source_url='/tmp/ds1',
                enabled=True,
                sync_interval=60,
            )

        sync_job.enqueue_once.assert_called_once()
        _, kwargs = sync_job.enqueue_once.call_args
        self.assertEqual(kwargs.get('interval'), 60)

    def test_disabled_datasource_clears_scheduled_jobs(self):
        class ScheduledJobQueryset:
            def __init__(self, jobs):
                self.jobs = jobs
                self.defer = Mock(return_value=self)
                self.filter = Mock(return_value=self)

            def __iter__(self):
                return iter(self.jobs)

        with patch('core.jobs.SyncDataSourceJob') as sync_job:
            ds = DataSource.objects.create(
                name='DS 1',
                type='local',
                source_url='/tmp/ds1',
                enabled=True,
                sync_interval=60,
            )
            sync_job.reset_mock()

            scheduled_job = Mock()
            scheduled_jobs = ScheduledJobQueryset([scheduled_job])
            sync_job.get_jobs.return_value = scheduled_jobs
            ds.enabled = False
            ds.sync_interval = None
            ds.save()

        sync_job.get_jobs.assert_called_once_with(ds)
        scheduled_jobs.defer.assert_called_once_with('data')
        scheduled_jobs.filter.assert_called_once_with(interval__isnull=False, status=JobStatusChoices.STATUS_SCHEDULED)
        scheduled_job.delete.assert_called_once_with()

    def test_creating_disabled_datasource_does_not_enqueue(self):
        with patch('core.jobs.SyncDataSourceJob') as sync_job:
            DataSource.objects.create(
                name='DS 1',
                type='local',
                source_url='/tmp/ds1',
                enabled=False,
                sync_interval=None,
            )

        sync_job.enqueue_once.assert_not_called()
        sync_job.get_jobs.assert_not_called()


class AutoSyncSignalTestCase(TestCase):
    """
    Verify core.signals.auto_sync re-syncs every AutoSyncRecord linked to the
    DataSource when post_sync fires.
    """

    def test_post_sync_resyncs_dependent_records(self):
        ds = DataSource.objects.create(
            name='DS 1',
            type='local',
            source_url='/tmp/ds1',
            status=DataSourceStatusChoices.COMPLETED,
        )
        record_a = SimpleNamespace(object=SimpleNamespace(synced=False))
        record_a.object.sync = lambda save: setattr(record_a.object, 'synced', save)
        record_b = SimpleNamespace(object=SimpleNamespace(synced=False))
        record_b.object.sync = lambda save: setattr(record_b.object, 'synced', save)

        with patch('core.models.AutoSyncRecord') as autosync_model:
            autosync_model.objects.filter.return_value.prefetch_related.return_value = [
                record_a,
                record_b,
            ]
            post_sync.send(sender=ds.__class__, instance=ds)

        self.assertTrue(record_a.object.synced)
        self.assertTrue(record_b.object.synced)


class UpdateConfigSignalTestCase(TestCase):
    """
    Verify core.signals.update_config invokes activate() on a newly-saved
    ConfigRevision.
    """

    def test_saving_config_revision_activates_it(self):
        with patch.object(ConfigRevision, 'activate') as activate:
            ConfigRevision.objects.create(data={'foo': 1}, comment='test')

        activate.assert_called_once()


class HandleChangedObjectDirectHandlerTestCase(SimpleTestCase):
    """
    Direct-call tests for handle_changed_object branches that are not naturally
    reachable through ORM operations (a real .save() always produces changes, and
    Django collapses every m2m_changed action into a single dispatch the handler
    cannot fully simulate via real m2m operations).
    """

    def _instance(self):
        objectchange = MagicMock()
        objectchange.has_changes = True
        objectchange.postchange_data = {'name': 'Device 1'}
        instance = SimpleNamespace(
            pk=123,
            _meta=SimpleNamespace(model_name='device'),
            refresh_from_db=MagicMock(),
        )
        instance.to_objectchange = MagicMock(return_value=objectchange)
        return instance, objectchange

    def test_unhandled_m2m_action_returns_without_recording(self):
        request = SimpleNamespace(id='request-id', user='alice')
        instance, _ = self._instance()
        current_request = MagicMock()
        current_request.get.return_value = request

        with patch.object(signals, 'current_request', current_request):
            signals.handle_changed_object(
                sender=None,
                instance=instance,
                action='pre_add',
                pk_set={1},
            )

        instance.to_objectchange.assert_not_called()

    def test_objectchange_without_changes_is_not_saved(self):
        request = SimpleNamespace(id='request-id', user='alice')
        instance, objectchange = self._instance()
        objectchange.has_changes = False
        current_request = MagicMock()
        current_request.get.return_value = request
        events_queue_mock = MagicMock()
        events_queue_mock.get.return_value = {}
        update_metric = MagicMock()

        with (
            patch.object(signals, 'current_request', current_request),
            patch.object(signals, 'events_queue', events_queue_mock),
            patch.object(signals, 'enqueue_event') as enqueue_event,
            patch.object(signals.model_updates, 'labels', return_value=update_metric),
        ):
            signals.handle_changed_object(sender=None, instance=instance, created=False)

        instance.to_objectchange.assert_called_once_with(ObjectChangeActionChoices.ACTION_UPDATE)
        # has_changes is False, so the ObjectChange should never be saved …
        objectchange.save.assert_not_called()
        # … but metric counters and event enqueueing still run.
        update_metric.inc.assert_called_once_with()
        enqueue_event.assert_called_once()

    def test_m2m_change_updates_existing_objectchange_in_same_request(self):
        request = SimpleNamespace(id='request-id', user='alice')
        instance, objectchange = self._instance()
        previous_change = MagicMock()
        current_request = MagicMock()
        current_request.get.return_value = request
        events_queue_mock = MagicMock()
        events_queue_mock.get.return_value = {}
        objectchange_model = MagicMock()
        objectchange_model.objects.filter.return_value.first.return_value = previous_change
        content_type_model = MagicMock()
        content_type_model.objects.get_for_model.return_value = object()

        with (
            patch.object(signals, 'current_request', current_request),
            patch.object(signals, 'events_queue', events_queue_mock),
            patch.object(signals, 'ObjectChange', objectchange_model),
            patch.object(signals, 'ContentType', content_type_model),
            patch.object(signals, 'enqueue_event'),
            patch.object(signals.model_updates, 'labels', return_value=MagicMock()),
        ):
            signals.handle_changed_object(
                sender=None,
                instance=instance,
                action='post_add',
                pk_set={1},
            )

        # The handler should update the existing ObjectChange instead of creating a new one.
        self.assertEqual(previous_change.postchange_data, objectchange.postchange_data)
        previous_change.save.assert_called_once_with()
        objectchange.save.assert_not_called()
        instance.refresh_from_db.assert_called_once_with()


class HandleDeletedObjectDirectHandlerTestCase(SimpleTestCase):
    """
    Direct-call tests for handle_deleted_object branches that are hard to construct
    via real model operations (notably _netbox_private skip, which requires a
    private-model instance with reverse relations the test can introspect).
    """

    def setUp(self):
        _signals_received.pre_delete = set()

    def test_private_model_skips_reverse_relation_processing(self):
        # Build a relation the handler would normally process — a ManyToOneRel-typed
        # instance pointing at a ChangeLoggingMixin subclass. The handler narrows by
        # exact type (`type(relation) is ManyToOneRel`), so do not use
        # MagicMock(spec=ManyToOneRel): it would be skipped before reaching the
        # _netbox_private branch. Patching ManyToOneRel to this fake class keeps the
        # exact-type check meaningful, so related_model.objects.filter() would be
        # called if the private-model skip failed.
        class FakeManyToOneRel:
            pass

        class FakeChangeLoggingMixin:
            pass

        class FakeRelatedModel(FakeChangeLoggingMixin):
            pass

        FakeRelatedModel.objects = MagicMock()

        fake_relation = FakeManyToOneRel()
        fake_relation.related_model = FakeRelatedModel
        fake_relation.remote_field = SimpleNamespace(name='parent')
        fake_relation.null = True
        fake_relation.on_delete = object()

        sender = SimpleNamespace(_meta=SimpleNamespace(app_label='dcim', model_name='cablepath'))
        request = SimpleNamespace(id='request-id', user='alice')
        instance = SimpleNamespace(
            pk=1,
            _meta=SimpleNamespace(model_name='cablepath', related_objects=[fake_relation]),
            _netbox_private=True,
        )
        # Private models typically don't have to_objectchange, so skip change-log too.
        config = SimpleNamespace(PROTECTION_RULES={})
        current_request = MagicMock()
        current_request.get.return_value = request
        events_queue_mock = MagicMock()
        events_queue_mock.get.return_value = {}

        with (
            patch.object(signals, 'ManyToOneRel', FakeManyToOneRel),
            patch.object(signals, 'get_config', return_value=config),
            patch.object(signals, 'get_config_value_ci', return_value=[]),
            patch.object(signals, 'run_validators'),
            patch.object(signals, 'current_request', current_request),
            patch.object(signals, 'events_queue', events_queue_mock),
            patch.object(signals, 'ContentType') as content_type_model,
            patch.object(signals, 'ChangeLoggingMixin', FakeChangeLoggingMixin),
            patch.object(signals, 'enqueue_event'),
            patch.object(signals.model_deletes, 'labels', return_value=MagicMock()),
        ):
            content_type_model.objects.get_for_model.return_value = object()
            signals.handle_deleted_object(sender=sender, instance=instance)

        FakeRelatedModel.objects.filter.assert_not_called()
