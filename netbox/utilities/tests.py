from __future__ import unicode_literals


class HttpStatusMixin(object):
    """
    Custom mixin to provide more detail in the event of an unexpected HTTP response.
    """

    def assertHttpStatus(self, response, expected_status):
        err_message = "Expected HTTP status {}; received {}: {}"
        self.assertEqual(response.status_code, expected_status, err_message.format(
            expected_status, response.status_code, response.data
        ))
