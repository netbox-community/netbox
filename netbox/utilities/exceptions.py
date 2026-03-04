from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = (
    'AbortRequest',
    'AbortScript',
    'AbortTransaction',
    'PermissionsViolation',
    'PreconditionFailed',
    'RQWorkerNotRunningException',
)


class AbortTransaction(Exception):
    """
    A dummy exception used to trigger a database transaction rollback.
    """
    pass


class AbortRequest(Exception):
    """
    Raised to cleanly abort a request (for example, by a pre_save signal receiver).
    """
    def __init__(self, message):
        self.message = message


class AbortScript(Exception):
    """
    Raised to cleanly abort a script.
    """
    pass


class PermissionsViolation(Exception):
    """
    Raised when an operation was prevented because it would violate the
    allowed permissions.
    """
    message = "Operation failed due to object-level permissions violation"


class PreconditionFailed(APIException):
    """
    Raised when an If-Match precondition is not satisfied (HTTP 412).
    """
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = 'Precondition failed.'
    default_code = 'precondition_failed'


class RQWorkerNotRunningException(APIException):
    """
    Indicates the temporary inability to enqueue a new task (e.g. custom script execution) because no RQ worker
    processes are currently running.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Unable to process request: RQ worker process not running.'
    default_code = 'rq_worker_not_running'
