import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_rq import job

from core.models import Job
from extras.models import ScriptModule
from extras.scripts import run_script

logger = logging.getLogger('netbox.scripts_worker')


@job('default')
def process_script(event_rule, data, username, **kwargs):
    """
    Run the requested script
    """
    if not event_rule.eval_conditions(data):
        return

    script_choice = None
    if event_rule.action_parameters and 'script_choice' in event_rule_action_parameters:
        script_choice = event_rule.action_parameters['script_choice']

    if script_choice:
        module_id = script_choice.split(":")[0]
        script_name = script_choice.split(":")[1]
    else:
        logger.warning(f"event run script - event_rule: {event_rule.id} no script_choice selected")
        return

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
