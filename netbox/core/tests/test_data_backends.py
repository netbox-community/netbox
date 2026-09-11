import tempfile
from pathlib import Path
from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase

from core.data_backends import S3Backend, url_has_embedded_credentials
from core.exceptions import SyncError

try:
    import dulwich  # noqa: F401
    DULWICH_AVAILABLE = True
except ImportError:
    DULWICH_AVAILABLE = False


class URLEmbeddedCredentialsTestCase(TestCase):
    def test_url_with_embedded_username(self):
        self.assertTrue(url_has_embedded_credentials('https://myuser@bitbucket.org/workspace/repo.git'))

    def test_url_without_embedded_username(self):
        self.assertFalse(url_has_embedded_credentials('https://bitbucket.org/workspace/repo.git'))

    def test_url_with_username_and_password(self):
        self.assertTrue(url_has_embedded_credentials('https://user:pass@bitbucket.org/workspace/repo.git'))

    def test_various_providers_with_embedded_username(self):
        urls = [
            'https://user@bitbucket.org/workspace/repo.git',
            'https://user@github.com/owner/repo.git',
            'https://deploy-key@gitlab.com/group/project.git',
            'http://user@internal-git.example.com/repo.git',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(url_has_embedded_credentials(url))

    def test_various_providers_without_embedded_username(self):
        """Various Git providers without embedded usernames."""
        urls = [
            'https://bitbucket.org/workspace/repo.git',
            'https://github.com/owner/repo.git',
            'https://gitlab.com/group/project.git',
            'http://internal-git.example.com/repo.git',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(url_has_embedded_credentials(url))

    def test_ssh_url(self):
        # git@host:path format doesn't parse as having a username in the traditional sense
        self.assertFalse(url_has_embedded_credentials('git@github.com:owner/repo.git'))

    def test_file_url(self):
        self.assertFalse(url_has_embedded_credentials('file:///path/to/repo'))


@skipIf(not DULWICH_AVAILABLE, "dulwich is not installed")
class GitBackendCredentialIntegrationTestCase(TestCase):
    """
    Integration tests that verify GitBackend correctly applies credential logic.

    These tests require dulwich to be installed and verify the full integration
    of the credential handling in GitBackend.fetch().
    """

    def _get_clone_kwargs(self, url, **params):
        from core.data_backends import GitBackend

        backend = GitBackend(url=url, **params)

        with patch('dulwich.porcelain.clone') as mock_clone, \
             patch('dulwich.porcelain.NoneStream'):
            try:
                with backend.fetch():
                    pass
            except Exception:
                pass

            if mock_clone.called:
                return mock_clone.call_args.kwargs
            return {}

    def test_url_with_embedded_username_skips_explicit_credentials(self):
        kwargs = self._get_clone_kwargs(
            url='https://myuser@bitbucket.org/workspace/repo.git',
            username='myuser',
            password='my-api-key'
        )

        self.assertEqual(kwargs.get('username'), None)
        self.assertEqual(kwargs.get('password'), None)

    def test_url_without_embedded_username_passes_explicit_credentials(self):
        kwargs = self._get_clone_kwargs(
            url='https://bitbucket.org/workspace/repo.git',
            username='myuser',
            password='my-api-key'
        )

        self.assertEqual(kwargs.get('username'), 'myuser')
        self.assertEqual(kwargs.get('password'), 'my-api-key')

    def test_url_with_embedded_username_no_explicit_credentials(self):
        kwargs = self._get_clone_kwargs(
            url='https://myuser@bitbucket.org/workspace/repo.git'
        )

        self.assertEqual(kwargs.get('username'), None)
        self.assertEqual(kwargs.get('password'), None)

    def test_public_repo_no_credentials(self):
        kwargs = self._get_clone_kwargs(
            url='https://github.com/public/repo.git'
        )

        self.assertEqual(kwargs.get('username'), None)
        self.assertEqual(kwargs.get('password'), None)


class S3BackendKeyResolutionTestCase(TestCase):
    """
    Verify that S3Backend resolves object keys to local paths safely, rejecting any
    key that would write outside of the local temporary directory.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.local_root = Path(self._tmp.name).resolve()

    def test_simple_key_resolves_under_root(self):
        result = S3Backend._resolve_local_path(self.local_root, 'data/file.yaml')
        self.assertEqual(result, self.local_root / 'data' / 'file.yaml')

    def test_nested_key_resolves_under_root(self):
        result = S3Backend._resolve_local_path(self.local_root, 'a/b/c/d.txt')
        self.assertEqual(result, self.local_root / 'a' / 'b' / 'c' / 'd.txt')

    def test_absolute_key_is_contained(self):
        # A key beginning with '/' must not escape the local root
        result = S3Backend._resolve_local_path(self.local_root, '/etc/passwd')
        self.assertEqual(result, self.local_root / 'etc' / 'passwd')
        self.assertTrue(result.is_relative_to(self.local_root))

    def test_parent_traversal_is_rejected(self):
        with self.assertRaises(SyncError):
            S3Backend._resolve_local_path(self.local_root, '../escape.txt')

    def test_nested_parent_traversal_is_rejected(self):
        with self.assertRaises(SyncError):
            S3Backend._resolve_local_path(self.local_root, 'foo/../../escape.txt')

    def test_absolute_parent_traversal_is_rejected(self):
        with self.assertRaises(SyncError):
            S3Backend._resolve_local_path(self.local_root, '/../escape.txt')

    def test_empty_key_is_rejected(self):
        with self.assertRaises(SyncError):
            S3Backend._resolve_local_path(self.local_root, '')

    def test_root_key_is_rejected(self):
        with self.assertRaises(SyncError):
            S3Backend._resolve_local_path(self.local_root, '/')
