from unittest.mock import patch

from django.test import TestCase

from core.data_backends import GitBackend


class GitBackendCredentialTests(TestCase):

    def _get_clone_kwargs(self, url, **params):
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
