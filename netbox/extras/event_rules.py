import logging

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_rq import get_queue

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.event_rules import EventRuleAction
from utilities.request import copy_safe_request
from utilities.rqworker import get_rq_retry

from .choices import EventRuleActionChoices
from .models import NotificationGroup, Script, Webhook

__all__ = (
    'NotificationAction',
    'ScriptAction',
    'WebhookAction',
)

logger = logging.getLogger('netbox.events_processor')


class WebhookAction(EventRuleAction):
    slug = EventRuleActionChoices.WEBHOOK
    label = _('Webhook')
    description = _('Send an outgoing HTTP request to a remote endpoint')
    object_model = Webhook
    object_required = True

    def enqueue(self, *, event_rule, event_context, action_object, action_data):
        # Select the appropriate RQ queue
        queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
        rq_queue = get_queue(queue_name)

        # Compile the task parameters
        params = {
            'event_rule': event_rule,
            'object_type': event_context['object_type'],
            'event_type': event_context['event_type'],
            'data': action_data,
            'snapshots': event_context.get('snapshots'),
            'timestamp': timezone.now().isoformat(),
            'retry': get_rq_retry(),
        }
        if 'request' in event_context:
            # Exclude FILES - webhooks don't need uploaded files,
            # which can cause pickle errors with Pillow.
            params['request'] = copy_safe_request(event_context['request'], include_files=False)

        # Enqueue the task
        rq_queue.enqueue('extras.webhooks.send_webhook', **params)

    def resolve_import_object(self, value):
        return Webhook.objects.get(name=value)


class ScriptAction(EventRuleAction):
    slug = EventRuleActionChoices.SCRIPT
    label = _('Script')
    description = _('Execute a custom script')
    object_model = Script
    object_required = True

    def enqueue(self, *, event_rule, event_context, action_object, action_data):
        # Resolve the script from action parameters
        script = action_object.python_class()

        # Enqueue a Job to record the script's execution
        from extras.jobs import ScriptJob

        params = {
            'instance': action_object,
            'name': script.name,
            'user': event_context['user'],
            'data': action_data,
            'notifications': script.notifications_default,
            'job_timeout': script.job_timeout,
        }
        if 'snapshots' in event_context:
            params['snapshots'] = event_context['snapshots']
        if 'request' in event_context:
            params['request'] = copy_safe_request(event_context['request'], include_files=False)

        # Enqueue the job. If the script's Meta configuration is invalid (see #22872), log the error and skip this
        # action rather than allowing the exception to abort the event pipeline (and, since events are processed
        # in-request, the originating object change). Note this is intentionally asymmetric with the webhook
        # action, which lets enqueue failures propagate: script Meta is validated eagerly at enqueue and a
        # misconfigured script must not take down an unrelated object change.
        try:
            ScriptJob.enqueue(**params)
        except ValidationError as e:
            logger.error(
                "Skipping script action for event rule %s: invalid script configuration: %s",
                event_rule, '; '.join(e.messages)
            )

    def resolve_import_object(self, value):
        from extras.scripts import get_module_and_script
        module_name, script_name = value.split('.', 1)
        return get_module_and_script(module_name, script_name)[1]


class NotificationAction(EventRuleAction):
    slug = EventRuleActionChoices.NOTIFICATION
    label = _('Notification')
    description = _('Generate a notification for one or more users or groups')
    object_model = NotificationGroup
    object_required = True

    def enqueue(self, *, event_rule, event_context, action_object, action_data):
        # Bulk-create notifications for all members of the notification group
        action_object.notify(
            object_type=event_context['object_type'],
            object_id=action_data['id'],
            object_repr=action_data.get('display'),
            event_type=event_context['event_type'],
        )

    def resolve_import_object(self, value):
        return NotificationGroup.objects.get(name=value)
