import logging

import requests
import sys
from django.conf import settings
from django_rq import job
from jinja2.exceptions import TemplateError

from .conditions import ConditionSet
from .choices import EventRuleActionChoices
from .constants import WEBHOOK_EVENT_TYPES
from .scripts_worker import process_script
from .webhooks import generate_signature
from .webhooks_worker import process_webhook

logger = logging.getLogger('netbox.events_worker')


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


def import_module(name):
    __import__(name)
    return sys.modules[name]


def module_member(name):
    mod, member = name.rsplit(".", 1)
    module = import_module(mod)
    return getattr(module, member)


def process_event_rules(event_rule, model_name, event, data, timestamp, username, request_id, snapshots):
    if event_rule.action_type == EventRuleActionChoices.WEBHOOK:
        process_webhook(event_rule, model_name, event, data, timestamp, username, request_id, snapshots)
    elif event_rule.action_type == EventRuleActionChoices.SCRIPT:
        process_script(event_rule, model_name, event, data, timestamp, username, request_id, snapshots)


@job('default')
def process_event(event_rule, model_name, event, data, timestamp, username, request_id=None, snapshots=None):
    """
    Make a POST request to the defined Webhook
    """
    # Evaluate event rule conditions (if any)
    if not eval_conditions(event_rule, data):
        return

    # process the events pipeline
    for name in settings.NETBOX_EVENTS_PIPELINE:
        func = module_member(name)
        func(event_rule, model_name, event, data, timestamp, username, request_id, snapshots)
