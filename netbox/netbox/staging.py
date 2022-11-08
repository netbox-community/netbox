import logging
from contextlib import contextmanager

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import pre_delete, post_save

from extras.choices import ChangeActionChoices
from extras.models import Change
from utilities.exceptions import AbortTransaction
from utilities.utils import serialize_object, shallow_compare_dict

logger = logging.getLogger('netbox.staging')


def get_changed_fields(instance):
    model = instance._meta.model
    original = model.objects.get(pk=instance.pk)
    return shallow_compare_dict(
        serialize_object(original),
        serialize_object(instance),
        exclude=('last_updated',)
    )


def get_key_for_instance(instance):
    object_type = ContentType.objects.get_for_model(instance)
    return object_type, instance.pk


@contextmanager
def checkout(branch):

    queue = {}

    def save_handler(sender, instance, **kwargs):
        return post_save_handler(sender, instance, branch=branch, queue=queue, **kwargs)

    def delete_handler(sender, instance, **kwargs):
        return pre_delete_handler(sender, instance, branch=branch, queue=queue, **kwargs)

    # Connect signal handlers
    post_save.connect(save_handler)
    pre_delete.connect(delete_handler)

    try:
        with transaction.atomic():
            yield
            raise AbortTransaction()

    # Roll back the transaction
    except AbortTransaction:
        pass

    finally:

        # Disconnect signal handlers
        post_save.disconnect(save_handler)
        pre_delete.disconnect(delete_handler)

        # Process queued changes
        logger.debug("Processing queued changes:")
        for key, change in queue.items():
            logger.debug(f'  {key}: {change}')

        # TODO: Optimize the creation of new Changes
        changes = []
        for key, change in queue.items():
            object_type, pk = key
            action, instance = change
            if action in (ChangeActionChoices.ACTION_CREATE, ChangeActionChoices.ACTION_UPDATE):
                data = serialize_object(instance)
            else:
                data = None

            change = Change(
                branch=branch,
                action=action,
                object_type=object_type,
                object_id=pk,
                data=data
            )
            changes.append(change)

        Change.objects.bulk_create(changes)


def post_save_handler(sender, instance, branch, queue, created, **kwargs):
    key = get_key_for_instance(instance)
    if created:
        # Creating a new object
        logger.debug(f"Staging creation of {instance} under branch {branch}")
        queue[key] = (ChangeActionChoices.ACTION_CREATE, instance)
    elif key in queue:
        # Object has already been created/updated at least once
        logger.debug(f"Updating staged value for {instance} under branch {branch}")
        queue[key] = (queue[key][0], instance)
    else:
        # Modifying an existing object
        logger.debug(f"Staging changes to {instance} (PK: {instance.pk}) under branch {branch}")
        queue[key] = (ChangeActionChoices.ACTION_UPDATE, instance)


def pre_delete_handler(sender, instance, branch, queue, **kwargs):
    key = get_key_for_instance(instance)
    if key in queue and queue[key][0] == 'create':
        # Cancel the creation of a new object
        logger.debug(f"Removing staged deletion of {instance} (PK: {instance.pk}) under branch {branch}")
        del queue[key]
    else:
        # Delete an existing object
        logger.debug(f"Staging deletion of {instance} (PK: {instance.pk}) under branch {branch}")
        queue[key] = (ChangeActionChoices.ACTION_DELETE, instance)
