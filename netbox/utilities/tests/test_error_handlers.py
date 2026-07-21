import json

from django.test import RequestFactory, TestCase

from utilities.error_handlers import handle_rest_api_exception


class HandleRestApiExceptionTestCase(TestCase):
    """
    Test handle_rest_api_exception() response formatting.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/api/test/')

    def test_error_kwarg_used_when_provided(self):
        """
        When an error kwarg is passed, it should appear in the response body.
        """
        try:
            raise ValueError("raw exception message")
        except ValueError:
            response = handle_rest_api_exception(self.request, error="custom error message")

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "custom error message")

    def test_fallback_to_exc_info_when_no_kwarg(self):
        """
        When no error kwarg is passed, sys.exc_info() should be used.
        """
        try:
            raise ValueError("raw exception message")
        except ValueError:
            response = handle_rest_api_exception(self.request)

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "raw exception message")
        self.assertEqual(data['exception'], "ValueError")
