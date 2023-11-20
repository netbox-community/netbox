import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_rq import job

from core.models import Job
from extras.models import ScriptModule
from extras.scripts import run_script
from extras.utils import eval_conditions

logger = logging.getLogger('netbox.scripts_worker')


@job('default')
def process_script(event_rule, model_name, event, data, timestamp, username, request_id=None, snapshots=None):
    """
    Run the requested script
    """
    if not eval_conditions(event_rule, data):
        return

    module_id = event_rule.action_parameters.split(":")[0]
    script_name = event_rule.action_parameters.split(":")[1]

    try:
        module = ScriptModule.objects.get(pk=module_id)
    except ScriptModule.DoesNotExist:
        logger.warning(f"event run script - script module_id: {module_id} script_name: {script_name}")
        return

    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        logger.warning(f"event run script - user does not exist username: {username} script_name: {script_name}")
        return

    script = module.scripts[script_name]()

    Job.enqueue(
        run_script,
        instance=module,
        name=script.class_name,
        user=user,
        schedule_at=None,
        interval=None,
        data=event_rule.action_data,
    )
