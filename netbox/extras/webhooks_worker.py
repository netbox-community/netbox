import warnings

from .webhooks import send_webhook as process_webhook


# TODO: Remove in v4.0
warnings.warn(
    f"webhooks_worker.process_webhook has been moved to webhooks.send_webhook.",
    DeprecationWarning
)
