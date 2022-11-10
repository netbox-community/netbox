import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import pre_delete, post_save

from extras.choices import ChangeActionChoices
from extras.models import Change
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


class checkout:

    def __init__(self, branch):
        self.branch = branch
        self.queue = {}

    def __enter__(self):

        # Disable autocommit to effect a new transaction
        logger.debug(f"Entering transaction for {self.branch}")
        self._autocommit = transaction.get_autocommit()

        transaction.set_autocommit(False)

        # Apply any existing Changes assigned to this Branch
        changes = self.branch.changes.all()
        if changes.exists():
            logger.debug(f"Applying {changes.count()} pre-staged changes...")
            for change in changes:
                change.apply()
        else:
            logger.debug("No pre-staged changes found")

        # Connect signal handlers
        logger.debug("Connecting signal handlers")
        post_save.connect(self.post_save_handler)
        pre_delete.connect(self.pre_delete_handler)

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Roll back the transaction to return the database to its original state
        logger.debug("Rolling back transaction")
        transaction.rollback()
        logger.debug(f"Restoring autocommit state {self._autocommit}")
        transaction.set_autocommit(self._autocommit)

        # Disconnect signal handlers
        logger.debug("Disconnecting signal handlers")
        post_save.disconnect(self.post_save_handler)
        pre_delete.disconnect(self.pre_delete_handler)

        # Process queued changes
        changes = []
        logger.debug(f"Processing {len(self.queue)} queued changes:")
        for key, change in self.queue.items():
            logger.debug(f'  {key}: {change}')
            object_type, pk = key
            action, instance = change
            if action in (ChangeActionChoices.ACTION_CREATE, ChangeActionChoices.ACTION_UPDATE):
                data = serialize_object(instance)
            else:
                data = None

            change = Change(
                branch=self.branch,
                action=action,
                object_type=object_type,
                object_id=pk,
                data=data
            )
            changes.append(change)

        Change.objects.bulk_create(changes)

    def post_save_handler(self, sender, instance, created, **kwargs):
        key = get_key_for_instance(instance)
        object_type = instance._meta.verbose_name

        if created:
            # Creating a new object
            logger.debug(f"[{self.branch}] Staging creation of {object_type} {instance}")
            self.queue[key] = (ChangeActionChoices.ACTION_CREATE, instance)
        elif key in self.queue:
            # Object has already been created/updated at least once
            logger.debug(f"[{self.branch}] Updating staged value for {object_type} {instance}")
            self.queue[key] = (self.queue[key][0], instance)
        else:
            # Modifying an existing object
            logger.debug(f"[{self.branch}] Staging changes to {object_type} {instance} (PK: {instance.pk})")
            self.queue[key] = (ChangeActionChoices.ACTION_UPDATE, instance)

    def pre_delete_handler(self, sender, instance, **kwargs):
        key = get_key_for_instance(instance)
        if key in self.queue and self.queue[key][0] == 'create':
            # Cancel the creation of a new object
            logger.debug(f"[{self.branch}] Removing staged deletion of {instance} (PK: {instance.pk})")
            del self.queue[key]
        else:
            # Delete an existing object
            logger.debug(f"[{self.branch}] Staging deletion of {instance} (PK: {instance.pk})")
            self.queue[key] = (ChangeActionChoices.ACTION_DELETE, instance)
