from __future__ import unicode_literals

from rest_framework.exceptions import APIException


class MissingFilterException(APIException):
    status_code = 400
    default_detail = "One or more required filters is missing from the request."
