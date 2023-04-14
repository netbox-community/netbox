from django.dispatch import Signal, receiver

__all__ = (
    'post_sync',
    'pre_sync',
)

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
