import logging

import requests
from core.models import Job
from django.conf import settings
from django_rq import job
from jinja2.exceptions import TemplateError
from utilities.rqworker import get_workers_for_queue

from extras.conditions import ConditionSet
from extras.constants import WEBHOOK_EVENT_TYPES
from extras.models import ScriptModule
from extras.scripts import run_script
from extras.utils import eval_conditions
from extras.webhooks import generate_signature

logger = logging.getLogger('netbox.webhooks_worker')


@job('default')
def process_script(event_rule, model_name, event, data, timestamp, username, request_id=None, snapshots=None):
    """
    Run the requested script
    """
    if not eval_conditions(event_rule, data):
        return

    module_id = event_rule.action_object_identifier.split(":")[0]
    script_name = event_rule.action_object_identifier.split(":")[1]

    try:
        module = ScriptModule.objects.get(pk=module_id)
    except ScriptModule.DoesNotExist:
        return

    script = module.scripts[script_name]()

    job = Job.enqueue(
        run_script,
        instance=module,
        name=script.class_name,
        user=None,
        schedule_at=None,
        interval=None,
        data=event_rule.parameters,
    )
