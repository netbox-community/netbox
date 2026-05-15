import uuid
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings

from core.events import JOB_COMPLETED, JOB_STARTED, OBJECT_DELETED, OBJECT_UPDATED
from core.models import Job, ObjectType
from core.signals import job_end, job_start
from dcim.choices import SiteStatusChoices
from dcim.models import Region, Site
from extras import signals
from extras.choices import CustomFieldTypeChoices, EventRuleActionChoices
from extras.models import CustomField, EventRule, Notification, Subscription, Tag, Webhook
from extras.validators import CustomValidator
from netbox.context_managers import event_tracking
from users.models import User
from utilities.exceptions import AbortRequest


def _build_request(user=None):
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = user
    return request


class CustomFieldRenameSignalTestCase(TestCase):
    """
    Verify extras.signals.handle_cf_renamed migrates stored custom-field data when a
    CustomField is renamed.
    """

    def test_renaming_custom_field_moves_object_data(self):
        site_type = ContentType.objects.get_for_model(Site)
        cf = CustomField.objects.create(
            name='asset_tag',
            type=CustomFieldTypeChoices.TYPE_TEXT,
        )
        cf.object_types.set([site_type])
        site = Site.objects.create(name='Site 1', slug='site-1', custom_field_data={'asset_tag': 'A123'})

        cf.name = 'inventory_id'
        cf.save()

        site.refresh_from_db()
        self.assertNotIn('asset_tag', site.custom_field_data)
        self.assertEqual(site.custom_field_data['inventory_id'], 'A123')

    def test_creating_custom_field_does_not_attempt_rename(self):
        # Should not raise — newly-created custom fields have no prior name to migrate.
        site_type = ContentType.objects.get_for_model(Site)
        cf = CustomField.objects.create(
            name='cf1',
            type=CustomFieldTypeChoices.TYPE_TEXT,
        )
        cf.object_types.set([site_type])


class CustomFieldDeletedSignalTestCase(TestCase):
    """
    Verify extras.signals.handle_cf_deleted strips stale data from associated objects
    when a CustomField is deleted.
    """

    def test_deleting_custom_field_clears_object_data(self):
        site_type = ContentType.objects.get_for_model(Site)
        cf = CustomField.objects.create(
            name='asset_tag',
            type=CustomFieldTypeChoices.TYPE_TEXT,
        )
        cf.object_types.set([site_type])
        site = Site.objects.create(name='Site 1', slug='site-1', custom_field_data={'asset_tag': 'A123'})

        cf.delete()

        site.refresh_from_db()
        self.assertNotIn('asset_tag', site.custom_field_data)


class CustomFieldObjectTypeSignalTestCase(TestCase):
    """
    Verify extras.signals.handle_cf_added_obj_types and handle_cf_removed_obj_types
    populate or strip default values when a CustomField's object_types m2m changes.
    """

    def test_adding_object_type_populates_default_value(self):
        site_type = ContentType.objects.get_for_model(Site)
        Site.objects.create(name='Site 1', slug='site-1')
        cf = CustomField.objects.create(
            name='asset_tag',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            default='UNTAGGED',
        )

        cf.object_types.set([site_type])

        site = Site.objects.get(slug='site-1')
        self.assertEqual(site.custom_field_data.get('asset_tag'), 'UNTAGGED')

    def test_removing_object_type_clears_stored_data(self):
        site_type = ContentType.objects.get_for_model(Site)
        cf = CustomField.objects.create(
            name='asset_tag',
            type=CustomFieldTypeChoices.TYPE_TEXT,
        )
        cf.object_types.set([site_type])
        site = Site.objects.create(name='Site 1', slug='site-1', custom_field_data={'asset_tag': 'A123'})

        cf.object_types.remove(site_type)

        site.refresh_from_db()
        self.assertNotIn('asset_tag', site.custom_field_data)


class RunSaveValidatorsSignalTestCase(TestCase):
    """
    Verify extras.signals.run_save_validators invokes any configured CUSTOM_VALIDATORS
    when a model emits the post_clean signal.
    """

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [CustomValidator({'name': {'eq': 'allowed'}})]})
    def test_validation_failure_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            Site(name='blocked', slug='blocked', status=SiteStatusChoices.STATUS_ACTIVE).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [CustomValidator({'name': {'eq': 'allowed'}})]})
    def test_validation_success_does_not_raise(self):
        Site(name='allowed', slug='allowed', status=SiteStatusChoices.STATUS_ACTIVE).clean()


class ValidateAssignedTagsSignalTestCase(TestCase):
    """
    Verify extras.signals.validate_assigned_tags rejects Tags that are restricted to
    object types incompatible with the target object.
    """

    def test_restricted_tag_blocks_incompatible_object(self):
        region_type = ContentType.objects.get_for_model(Region)
        tag = Tag.objects.create(name='RegionOnly', slug='regiononly')
        tag.object_types.set([region_type])
        site = Site.objects.create(name='Site 1', slug='site-1')

        with self.assertRaises(AbortRequest):
            site.tags.add(tag)

    def test_restricted_tag_allows_compatible_object(self):
        site_type = ContentType.objects.get_for_model(Site)
        tag = Tag.objects.create(name='SiteOnly', slug='siteonly')
        tag.object_types.set([site_type])
        site = Site.objects.create(name='Site 1', slug='site-1')

        site.tags.add(tag)
        self.assertEqual(list(site.tags.all()), [tag])

    def test_unrestricted_tag_is_always_permitted(self):
        tag = Tag.objects.create(name='Anywhere', slug='anywhere')
        site = Site.objects.create(name='Site 1', slug='site-1')

        site.tags.add(tag)
        self.assertEqual(list(site.tags.all()), [tag])


class JobEventRulesSignalTestCase(TestCase):
    """
    Verify extras.signals.process_job_start_event_rules and process_job_end_event_rules
    invoke any EventRule registered for JOB_STARTED / JOB_COMPLETED on the sender's
    object_type.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.create(
            name='Webhook',
            payload_url='http://localhost/',
            secret='secret',
        )
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        cls.start_rule = EventRule.objects.create(
            name='Job Start Rule',
            event_types=[JOB_STARTED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        cls.start_rule.object_types.set([cls.site_type])
        cls.end_rule = EventRule.objects.create(
            name='Job End Rule',
            event_types=[JOB_COMPLETED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        cls.end_rule.object_types.set([cls.site_type])

    def _create_job(self):
        return Job.objects.create(
            object_type=self.site_type,
            name='test-job',
            job_id=uuid.uuid4(),
            data={'foo': 1},
        )

    def test_job_start_filters_to_matching_event_rules(self):
        sender = self._create_job()

        with patch('extras.signals.process_event_rules') as process_event_rules:
            job_start.send(sender=sender)

        process_event_rules.assert_called_once()
        rules_qs = process_event_rules.call_args.args[0]
        self.assertEqual(list(rules_qs.values_list('pk', flat=True)), [self.start_rule.pk])

    def test_job_end_filters_to_matching_event_rules(self):
        sender = self._create_job()

        with patch('extras.signals.process_event_rules') as process_event_rules:
            job_end.send(sender=sender)

        process_event_rules.assert_called_once()
        rules_qs = process_event_rules.call_args.args[0]
        self.assertEqual(list(rules_qs.values_list('pk', flat=True)), [self.end_rule.pk])


class NotifyObjectChangedSignalTestCase(TestCase):
    """
    Verify extras.signals.notify_object_changed creates Notifications for subscribed
    users on object update and deletion, and skips creation otherwise.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_creating_object_does_not_create_notifications(self):
        # Subscribe a user to the object BEFORE invoking the handler so the
        # discriminating branch (created=True early return) is genuinely
        # exercised. Without the subscription this assertion passes trivially.
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_type = ContentType.objects.get_for_model(Site)
        Subscription.objects.create(user=self.user, object_type=site_type, object_id=site.pk)
        Notification.objects.all().delete()

        signals.notify_object_changed(sender=Site, instance=site, created=True)

        self.assertFalse(Notification.objects.exists())

    def test_updating_subscribed_object_creates_update_notification(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_type = ContentType.objects.get_for_model(Site)
        Subscription.objects.create(user=self.user, object_type=site_type, object_id=site.pk)

        site.description = 'updated'
        site.save()

        notification = Notification.objects.get(user=self.user)
        self.assertEqual(notification.object_type, site_type)
        self.assertEqual(notification.object_id, site.pk)
        self.assertEqual(notification.event_type, OBJECT_UPDATED)

    def test_deleting_subscribed_object_creates_delete_notification(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_type = ContentType.objects.get_for_model(Site)
        Subscription.objects.create(user=self.user, object_type=site_type, object_id=site.pk)

        site.delete()

        notification = Notification.objects.get(user=self.user)
        self.assertEqual(notification.event_type, OBJECT_DELETED)

    def test_updating_unsubscribed_object_creates_no_notification(self):
        site = Site.objects.create(name='Site 1', slug='site-1')

        site.description = 'updated'
        site.save()

        self.assertEqual(Notification.objects.count(), 0)

    def test_updating_object_replaces_existing_notification(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site_type = ContentType.objects.get_for_model(Site)
        Subscription.objects.create(user=self.user, object_type=site_type, object_id=site.pk)

        # Trigger two updates within a single request; only one Notification should remain.
        request = _build_request(user=self.user)
        with event_tracking(request):
            site.description = 'first'
            site.save()
            site.description = 'second'
            site.save()

        self.assertEqual(
            Notification.objects.filter(user=self.user, object_type=site_type, object_id=site.pk).count(),
            1,
        )
