from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import ConfigRevision

__all__ = (
    'job_end',
    'job_start',
    'post_sync',
    'pre_sync',
)

# Job signals
job_start = Signal()
job_end = Signal()

# DataSource signals
pre_sync = Signal()
post_sync = Signal()


@receiver(post_sync)
def auto_sync(instance, **kwargs):
    """
    Automatically synchronize any DataFiles with AutoSyncRecords after synchronizing a DataSource.
    """
    from .models import AutoSyncRecord

    for autosync in AutoSyncRecord.objects.filter(datafile__source=instance).prefetch_related('object'):
        autosync.object.sync(save=True)


@receiver(post_save, sender=ConfigRevision)
def update_config(sender, instance, **kwargs):
    """
    Update the cached NetBox configuration when a new ConfigRevision is created.
    """
    instance.activate()
