import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import m2m_changed, pre_delete, post_save

from extras.choices import ChangeActionChoices
from extras.models import StagedChange
from utilities.serialization import serialize_object

logger = logging.getLogger('netbox.staging')


class checkout:
    """
    Context manager for staging changes to NetBox objects. Staged changes are saved out-of-band
    (as Change instances) for application at a later time, without modifying the production
    database.

        branch = Branch.objects.create(name='my-branch')
        with checkout(branch):
            # All changes made herein will be rolled back and stored for later

    Note that invoking the context disabled transaction autocommit to facilitate manual rollbacks,
    and restores its original value upon exit.
    """
    def __init__(self, branch):
        self.branch = branch
        self.queue = {}

    def __enter__(self):

        # Disable autocommit to effect a new transaction
        logger.debug(f"Entering transaction for {self.branch}")
        self._autocommit = transaction.get_autocommit()
        transaction.set_autocommit(False)

        # Apply any existing Changes assigned to this Branch
        staged_changes = self.branch.staged_changes.all()
        if change_count := staged_changes.count():
            logger.debug(f"Applying {change_count} pre-staged changes...")
            for change in staged_changes:
                change.apply()
        else:
            logger.debug("No pre-staged changes found")

        # Connect signal handlers
        logger.debug("Connecting signal handlers")
        post_save.connect(self.post_save_handler)
        m2m_changed.connect(self.post_save_handler)
        pre_delete.connect(self.pre_delete_handler)

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Disconnect signal handlers
        logger.debug("Disconnecting signal handlers")
        post_save.disconnect(self.post_save_handler)
        m2m_changed.disconnect(self.post_save_handler)
        pre_delete.disconnect(self.pre_delete_handler)

        # Roll back the transaction to return the database to its original state
        logger.debug("Rolling back database transaction")
        transaction.rollback()
        logger.debug(f"Restoring autocommit state ({self._autocommit})")
        transaction.set_autocommit(self._autocommit)

        # Process queued changes
        self.process_queue()

    #
    # Queuing
    #

    @staticmethod
    def get_key_for_instance(instance):
        return ContentType.objects.get_for_model(instance), instance.pk

    def process_queue(self):
        """
        Create Change instances for all actions stored in the queue.
        """
        if not self.queue:
            logger.debug(f"No queued changes; aborting")
            return
        logger.debug(f"Processing {len(self.queue)} queued changes")

        # Iterate through the in-memory queue, creating Change instances
        changes = []
        for key, change in self.queue.items():
            logger.debug(f'  {key}: {change}')
            object_type, pk = key
            action, data = change

            changes.append(StagedChange(
                branch=self.branch,
                action=action,
                object_type=object_type,
                object_id=pk,
                data=data
            ))

        # Save all Change instances to the database
        StagedChange.objects.bulk_create(changes)

    #
    # Signal handlers
    #

    def post_save_handler(self, sender, instance, **kwargs):
        """
        Hooks to the post_save signal when a branch is active to queue create and update actions.
        """
        key = self.get_key_for_instance(instance)
        object_type = instance._meta.verbose_name

        # Creating a new object
        if kwargs.get('created'):
            logger.debug(f"[{self.branch}] Staging creation of {object_type} {instance} (PK: {instance.pk})")
            data = serialize_object(instance, resolve_tags=False)
            self.queue[key] = (ChangeActionChoices.ACTION_CREATE, data)
            return

        # Ignore pre_* many-to-many actions
        if 'action' in kwargs and kwargs['action'] not in ('post_add', 'post_remove', 'post_clear'):
            return

        # Object has already been created/updated in the queue; update its queued representation
        if key in self.queue:
            logger.debug(f"[{self.branch}] Updating staged value for {object_type} {instance} (PK: {instance.pk})")
            data = serialize_object(instance, resolve_tags=False)
            self.queue[key] = (self.queue[key][0], data)
            return

        # Modifying an existing object for the first time
        logger.debug(f"[{self.branch}] Staging changes to {object_type} {instance} (PK: {instance.pk})")
        data = serialize_object(instance, resolve_tags=False)
        self.queue[key] = (ChangeActionChoices.ACTION_UPDATE, data)

    def pre_delete_handler(self, sender, instance, **kwargs):
        """
        Hooks to the pre_delete signal when a branch is active to queue delete actions.
        """
        key = self.get_key_for_instance(instance)
        object_type = instance._meta.verbose_name

        # Delete an existing object
        logger.debug(f"[{self.branch}] Staging deletion of {object_type} {instance} (PK: {instance.pk})")
        self.queue[key] = (ChangeActionChoices.ACTION_DELETE, None)
