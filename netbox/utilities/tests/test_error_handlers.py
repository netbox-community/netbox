import json
from unittest.mock import patch

from django.db.models import ProtectedError
from django.test import RequestFactory, TestCase

from dcim.models import Site
from users.models import User
from utilities.error_handlers import handle_protectederror, handle_rest_api_exception


class HandleProtectedErrorTestCase(TestCase):
    """
    Test handle_protectederror() message formatting.
    """

    def test_dependent_objects_truncated(self):
        request = RequestFactory().get('/')
        request.user = User(username='superuser', is_superuser=True)
        sites = {Site(pk=i, name=f'Site {i}', slug=f'site-{i}') for i in range(1, 53)}

        with patch('utilities.error_handlers.messages') as messages:
            handle_protectederror([Site(name='Site 0')], request, ProtectedError('', sites))

        message = messages.error.call_args.args[1]
        self.assertIn('52 dependent objects were found', message)
        self.assertEqual(message.count('<a href='), 50)
        self.assertTrue(message.endswith(', 2 more objects'))


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
