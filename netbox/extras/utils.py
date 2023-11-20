import logging
from django.db.models import Q
from django_rq import get_queue
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from taggit.managers import _TaggableManager

from extras.conditions import ConditionSet
from netbox.constants import RQ_QUEUE_DEFAULT
from extras.choices import EventRuleActionChoices
from netbox.config import get_config
from netbox.registry import registry
from utilities.rqworker import get_rq_retry

logger = logging.getLogger('netbox.extras.utils')


def is_taggable(obj):
    """
    Return True if the instance can have Tags assigned to it; False otherwise.
    """
    if hasattr(obj, 'tags'):
        if issubclass(obj.tags.__class__, _TaggableManager):
            return True
    return False


def image_upload(instance, filename):
    """
    Return a path for uploading image attachments.
    """
    path = 'image-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name and extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png']:
        filename = '.'.join([instance.name, extension])
    elif instance.name:
        filename = instance.name

    return '{}{}_{}_{}'.format(path, instance.content_type.name, instance.object_id, filename)


def register_features(model, features):
    """
    Register model features in the application registry.
    """
    app_label, model_name = model._meta.label_lower.split('.')
    for feature in features:
        try:
            registry['model_features'][feature][app_label].add(model_name)
        except KeyError:
            raise KeyError(
                f"{feature} is not a valid model feature! Valid keys are: {registry['model_features'].keys()}"
            )

    # Register public models
    if not getattr(model, '_netbox_private', False):
        registry['models'][app_label].add(model_name)


def is_script(obj):
    """
    Returns True if the object is a Script.
    """
    from .scripts import Script
    try:
        return issubclass(obj, Script) and obj != Script
    except TypeError:
        return False


def is_report(obj):
    """
    Returns True if the given object is a Report.
    """
    from .reports import Report
    try:
        return issubclass(obj, Report) and obj != Report
    except TypeError:
        return False


def eval_conditions(event_rule, data):
    """
    Test whether the given data meets the conditions of the event rule (if any). Return True
    if met or no conditions are specified.
    """
    if not event_rule.conditions:
        return True

    logger.debug(f'Evaluating event rule conditions: {event_rule.conditions}')
    if ConditionSet(event_rule.conditions).eval(data):
        return True

    return False


def process_event_rules(event_rules, model_name, event, data, username, snapshots=None, request_id=None):
    rq_queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
    rq_queue = get_queue(rq_queue_name)

    for event_rule in event_rules:
        if event_rule.action_type == EventRuleActionChoices.WEBHOOK:
            processor = "extras.webhooks_worker.process_webhook"
        elif event_rule.action_type == EventRuleActionChoices.SCRIPT:
            processor = "extras.scripts_worker.process_script"
        else:
            raise ValueError(f"Unknown action type for an event rule: {event_rule.action_type}")

        params = {
            "event_rule": event_rule,
            "model_name": model_name,
            "event": event,
            "data": data,
            "snapshots": snapshots,
            "timestamp": str(timezone.now()),
            "username": username,
            "retry": get_rq_retry()
        }

        if snapshots:
            params["snapshots"] = snapshots
        if request_id:
            params["request_id"] = request_id

        rq_queue.enqueue(
            processor,
            **params
        )
