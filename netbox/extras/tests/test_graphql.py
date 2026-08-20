import json

from django.urls import reverse
from rest_framework import status

from core.events import OBJECT_CREATED
from core.models import ObjectType
from dcim.models import Site
from extras.choices import CustomFieldStatusChoices, CustomFieldTypeChoices, EventRuleActionChoices
from extras.graphql.enums import EventRuleActionEnum
from extras.models import CustomField, EventRule, Webhook
from utilities.testing import APITestCase


class EventRuleActionEnumTestCase(APITestCase):
    """EventRuleActionEnum must reflect the live action registry, and the filter must use it."""

    def test_enum_contains_core_actions(self):
        # A subset check, since an installed plugin may register actions of its own
        values = {member.value for member in EventRuleActionEnum}
        core_slugs = {
            EventRuleActionChoices.WEBHOOK, EventRuleActionChoices.SCRIPT, EventRuleActionChoices.NOTIFICATION,
        }
        self.assertLessEqual(core_slugs, values)

    def test_filter_event_rules_by_action_type(self):
        webhook = Webhook.objects.create(name='GraphQL Enum Test Webhook', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        site_type = ObjectType.objects.get_for_model(Site)

        webhook_rule = EventRule.objects.create(
            name='GraphQL Enum Webhook Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        webhook_rule.object_types.set([site_type])

        script_rule = EventRule.objects.create(
            name='GraphQL Enum Script Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.SCRIPT,
        )
        script_rule.object_types.set([site_type])

        self.add_permissions('extras.view_eventrule')
        url = reverse('graphql')
        query = '{event_rule_list(filters: {action_type: {exact: WEBHOOK}}) {name action_type}}'
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        names = {rule['name'] for rule in data['data']['event_rule_list']}
        self.assertEqual(names, {'GraphQL Enum Webhook Rule'})


class CustomFieldStatusFilterTestCase(APITestCase):
    """A field which is not live is invisible everywhere else, so its status must be queryable."""

    def test_filter_custom_fields_by_status(self):
        site_type = ObjectType.objects.get_for_model(Site)
        for name, status_ in (
            ('graphql_active_field', CustomFieldStatusChoices.STATUS_ACTIVE),
            ('graphql_provisioning_field', CustomFieldStatusChoices.STATUS_PROVISIONING),
        ):
            custom_field = CustomField.objects.create(type=CustomFieldTypeChoices.TYPE_TEXT, name=name)
            custom_field.object_types.set([site_type])
            # Applied via the queryset, as CustomField.status is not directly writable
            CustomField.objects.filter(pk=custom_field.pk).update(status=status_)

        self.add_permissions('extras.view_customfield')
        url = reverse('graphql')
        query = '{custom_field_list(filters: {status: {exact: STATUS_PROVISIONING}}) {name status}}'
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(
            [(cf['name'], cf['status']) for cf in data['data']['custom_field_list']],
            [('graphql_provisioning_field', CustomFieldStatusChoices.STATUS_PROVISIONING)]
        )
