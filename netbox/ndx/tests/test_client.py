from unittest.mock import MagicMock, patch

import requests
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from ndx.client import (
    DISABLED,
    FORBIDDEN,
    NOT_FOUND,
    RATE_LIMITED,
    UNAUTHORIZED,
    UNAVAILABLE,
    NDXClient,
    NDXImage,
    NDXResponse,
    error_of,
)

API_URL = 'https://ndx.example.com/ndx/api/v1'


def mock_response(status=200, data=None, content=b'', content_type='application/json'):
    response = MagicMock()
    response.__enter__.return_value = response
    response.status_code = status
    response.headers = {'Content-Type': content_type}
    response.json.return_value = data if data is not None else {}
    response.iter_content.return_value = [content[i:i + 4] for i in range(0, len(content), 4)]
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
    return response


@override_settings(NDX_API_TOKEN='secret-token', NDX_API_URL=API_URL, ISOLATED_DEPLOYMENT=False)
class NDXClientTestCase(SimpleTestCase):

    def setUp(self):
        cache.clear()
        self.client = NDXClient()

    def assertRequested(self, mock_get, path, params=None):
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], f'{API_URL}/{path}')
        self.assertEqual(kwargs['params'], params)

    @patch('ndx.client.requests.get')
    def test_headers(self, mock_get):
        mock_get.return_value = mock_response(data={'tier': 'paid'})
        self.client.verify_auth()

        headers = mock_get.call_args.kwargs['headers']
        self.assertEqual(headers['Authorization'], 'Bearer secret-token')
        self.assertEqual(headers['Accept'], 'application/json')
        self.assertTrue(headers['User-Agent'].startswith('NetBox/'))
        self.assertIn('timeout', mock_get.call_args.kwargs)

    @override_settings(HTTP_PROXIES={'https': 'http://proxy.example.com:3128'})
    @patch('ndx.client.requests.get')
    def test_proxies(self, mock_get):
        mock_get.return_value = mock_response(data={})
        self.client.get_manifest()
        self.assertEqual(mock_get.call_args.kwargs['proxies'], {'https': 'http://proxy.example.com:3128'})

    @patch('ndx.client.requests.get')
    def test_endpoints(self, mock_get):
        mock_get.return_value = mock_response(data={'results': []})

        self.client.verify_auth()
        self.assertRequested(mock_get, 'auth/verify')

        self.client.get_vendors(limit=200, cursor='abc')
        self.assertRequested(mock_get, 'vendors', {'limit': 200, 'cursor': 'abc'})

        self.client.search(q='9300', vendor='cisco', entry_type='module-type', offset=50, limit=25, has_thermal='true')
        self.assertRequested(mock_get, 'device-types', {
            'limit': 25, 'q': '9300', 'vendor': 'cisco', 'type': 'module-type', 'offset': 50, 'has_thermal': 'true',
        })

        self.client.get_entry('cisco', 'catalyst-9300')
        self.assertRequested(mock_get, 'device-types/cisco/catalyst-9300')

        self.client.check_sync(since='2026-01-01T00:00:00')
        self.assertRequested(mock_get, 'sync/check', {'since': '2026-01-01T00:00:00'})

        self.client.get_manifest()
        self.assertRequested(mock_get, 'sync/manifest')

    @patch('ndx.client.requests.get')
    def test_get_all_vendors(self, mock_get):
        mock_get.side_effect = [
            mock_response(data={'results': [{'slug': 'a10'}], 'next_cursor': 'abc'}),
            mock_response(data={'results': [{'slug': 'cisco'}], 'next_cursor': None}),
        ]
        self.assertEqual(self.client.get_all_vendors(), [{'slug': 'a10'}, {'slug': 'cisco'}])
        self.assertEqual(mock_get.call_args.kwargs['params'], {'limit': 200, 'cursor': 'abc'})

    @patch('ndx.client.requests.get')
    def test_search_limit_capped(self, mock_get):
        mock_get.return_value = mock_response(data={})
        self.client.search(limit=1000)
        self.assertEqual(mock_get.call_args.kwargs['params']['limit'], 200)

    @patch('ndx.client.requests.get')
    def test_get_image(self, mock_get):
        mock_get.return_value = mock_response(content=b'JPEG data', content_type='image/jpeg; charset=binary')
        self.assertEqual(
            self.client.get_image('cisco', 'catalyst-9300', 'front'),
            NDXImage(content=b'JPEG data', extension='.jpg'),
        )
        self.assertEqual(mock_get.call_args.args[0], f'{API_URL}/device-types/cisco/catalyst-9300/image/front')
        self.assertTrue(mock_get.call_args.kwargs['stream'])

        mock_get.return_value = mock_response(status=404)
        self.assertIsNone(self.client.get_image('cisco', 'catalyst-9300', 'rear'))

    @patch('ndx.client.requests.get')
    def test_get_image_rejected(self, mock_get):
        # Not an accepted image type
        mock_get.return_value = mock_response(content=b'<svg/>', content_type='image/svg+xml')
        self.assertIsNone(self.client.get_image('cisco', 'catalyst-9300', 'front'))

        # Exceeds the maximum size
        mock_get.return_value = mock_response(content=b'PNG data', content_type='image/png')
        with patch('ndx.client.IMAGE_MAX_SIZE', 6):
            self.assertIsNone(self.client.get_image('cisco', 'catalyst-9300', 'front'))

    @patch('ndx.client.requests.get')
    def test_path_segments_encoded(self, mock_get):
        mock_get.return_value = mock_response(data={})
        self.client.get_entry('cisco', 'a?b#c')
        self.assertRequested(mock_get, 'device-types/cisco/a%3Fb%23c')

        # Relative path references are never requested
        mock_get.reset_mock()
        for vendor_slug, slug in (('..', 'x'), ('cisco', '..'), ('cisco', '.'), ('cisco', 'a/b'), ('', 'x')):
            self.assertEqual(error_of(self.client.get_entry(vendor_slug, slug)).kind, NOT_FOUND)
            self.assertIsNone(self.client.get_image(vendor_slug, slug, 'front'))
        mock_get.assert_not_called()

    @patch('ndx.client.requests.get')
    def test_error_classification(self, mock_get):
        for status, kind in ((401, UNAUTHORIZED), (403, FORBIDDEN), (404, NOT_FOUND), (429, RATE_LIMITED),
                             (500, UNAVAILABLE)):
            with self.subTest(status=status):
                mock_get.return_value = mock_response(status=status)
                response = self.client.get_entry('cisco', 'catalyst-9300')
                self.assertIsInstance(response, NDXResponse)
                self.assertFalse(response)
                self.assertEqual(error_of(response).kind, kind)
                self.assertEqual(error_of(response).status, status)

    @patch('ndx.client.requests.get')
    def test_verify_auth_not_authenticated(self, mock_get):
        mock_get.return_value = mock_response(data={'authenticated': False, 'tier': ''})
        self.assertEqual(error_of(self.client.verify_auth()).kind, UNAUTHORIZED)

        mock_get.return_value = mock_response(data={'authenticated': True, 'tier': 'free'})
        response = self.client.verify_auth()
        self.assertIsNone(error_of(response))
        self.assertEqual(response['tier'], 'free')

    @patch('ndx.client.requests.get')
    def test_connection_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError('unreachable')
        response = self.client.get_manifest()
        self.assertEqual(error_of(response).kind, UNAVAILABLE)
        self.assertIsNone(error_of(response).status)

    @patch('ndx.client.requests.get')
    def test_invalid_json(self, mock_get):
        response = mock_response()
        response.json.side_effect = ValueError('invalid JSON')
        mock_get.return_value = response
        self.assertEqual(error_of(self.client.get_manifest()).kind, UNAVAILABLE)

    @patch('ndx.client.requests.get')
    def test_non_object_json(self, mock_get):
        mock_get.return_value = mock_response(data=['unexpected'])
        response = self.client.get_manifest()
        self.assertEqual(error_of(response).kind, UNAVAILABLE)
        self.assertEqual(dict(response), {})

    @patch('ndx.client.requests.get')
    def test_response_caching(self, mock_get):
        mock_get.return_value = mock_response(data={'results': [{'slug': 'cisco'}]})
        self.assertEqual(self.client.get_vendors(), {'results': [{'slug': 'cisco'}]})
        self.assertEqual(self.client.get_vendors(), {'results': [{'slug': 'cisco'}]})
        self.assertEqual(mock_get.call_count, 1)

        # Entries are never cached
        self.client.get_entry('cisco', 'catalyst-9300')
        self.client.get_entry('cisco', 'catalyst-9300')
        self.assertEqual(mock_get.call_count, 3)

    @patch('ndx.client.requests.get')
    def test_error_caching(self, mock_get):
        mock_get.return_value = mock_response(status=401)
        self.assertEqual(error_of(self.client.search(q='foo')).kind, UNAUTHORIZED)
        self.assertEqual(error_of(self.client.search(q='foo')).kind, UNAUTHORIZED)
        self.assertEqual(mock_get.call_count, 1)

    @override_settings(NDX_API_TOKEN=None)
    @patch('ndx.client.requests.get')
    def test_disabled_without_token(self, mock_get):
        self.assertEqual(error_of(NDXClient().get_manifest()).kind, DISABLED)
        self.assertIsNone(NDXClient().get_image('cisco', 'catalyst-9300', 'front'))
        mock_get.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=True)
    @patch('ndx.client.requests.get')
    def test_disabled_when_isolated(self, mock_get):
        self.assertEqual(error_of(self.client.search()).kind, DISABLED)
        mock_get.assert_not_called()
