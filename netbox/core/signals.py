import django.dispatch

__all__ = (
    'post_sync',
    'pre_sync',
)

# DataSource signals
pre_sync = django.dispatch.Signal()
post_sync = django.dispatch.Signal()
