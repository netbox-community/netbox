import json

from django.urls import reverse
from rest_framework import status

from core.events import OBJECT_CREATED
from core.models import ObjectType
from dcim.models import Site
from extras.choices import EventRuleActionChoices
from extras.graphql.enums import EventRuleActionEnum
from extras.models import EventRule, Webhook
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
