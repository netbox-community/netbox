from contextvars import ContextVar

__all__ = (
    'current_request',
    'webhooks_queue',
)


current_request = ContextVar('current_request', default=None)
webhooks_queue = ContextVar('webhooks_queue', default=[])
