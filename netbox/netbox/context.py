from contextvars import ContextVar

__all__ = (
    'current_request',
    'events_queue',
    'object_types_cache',
)


current_request = ContextVar('current_request', default=None)
events_queue = ContextVar('events_queue', default=dict())
object_types_cache = ContextVar('object_types_cache', default=None)
