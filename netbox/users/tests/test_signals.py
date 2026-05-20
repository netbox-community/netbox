from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.test import RequestFactory, TestCase, override_settings

from users.models import User, UserConfig
from users.signals import create_userconfig


class LogUserLoginFailedSignalTestCase(TestCase):
    """
    Verify users.signals.log_user_login_failed emits the expected log records when the
    user_login_failed signal fires.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_log_includes_client_ip_when_available(self):
        request = self.factory.post('/login/', REMOTE_ADDR='192.0.2.100')

        with self.assertLogs('netbox.auth.login', level='INFO') as cm:
            user_login_failed.send(
                sender=self.__class__,
                credentials={'username': 'alice'},
                request=request,
            )

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].levelname, 'INFO')
        self.assertIn('alice', cm.records[0].getMessage())
        self.assertIn('192.0.2.100', cm.records[0].getMessage())

    def test_log_warns_when_client_ip_missing(self):
        request = self.factory.post('/login/')
        # RequestFactory sets REMOTE_ADDR by default; strip it to simulate missing IP.
        request.META.pop('REMOTE_ADDR', None)

        with self.assertLogs('netbox.auth.login', level='INFO') as cm:
            user_login_failed.send(
                sender=self.__class__,
                credentials={'username': 'alice'},
                request=request,
            )

        levels = [record.levelname for record in cm.records]
        self.assertIn('WARNING', levels)
        self.assertIn('INFO', levels)
        info_message = next(r.getMessage() for r in cm.records if r.levelname == 'INFO')
        self.assertEqual(info_message, 'Failed login attempt for username: alice')


class SetLanguageOnLoginSignalTestCase(TestCase):
    """
    Verify users.signals.set_language_on_login stores the user's preferred language on the
    request when the user logs in.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='alice', password='pw')

    def test_language_cookie_is_set_from_user_config(self):
        # Assign a fresh dict to avoid mutating the shared DEFAULT_USER_PREFERENCES reference.
        self.user.config.data = {'locale': {'language': 'de'}}
        self.user.config.save()
        request = self.factory.post('/login/')

        user_logged_in.send(sender=self.__class__, user=self.user, request=request)

        self.assertEqual(request._language_cookie, 'de')

    def test_missing_language_preference_leaves_request_untouched(self):
        self.user.config.data = {}
        self.user.config.save()
        request = self.factory.post('/login/')

        user_logged_in.send(sender=self.__class__, user=self.user, request=request)

        self.assertFalse(hasattr(request, '_language_cookie'))

    def test_user_without_config_leaves_request_untouched(self):
        request = self.factory.post('/login/')
        # Drop the UserConfig that was auto-created so `hasattr(user, 'config')` returns False.
        self.user.config.delete()
        # Reload the user instance from the DB so the cached 'config' related attribute is gone.
        user = User.objects.get(pk=self.user.pk)

        user_logged_in.send(sender=self.__class__, user=user, request=request)

        self.assertFalse(hasattr(request, '_language_cookie'))


class CreateUserConfigSignalTestCase(TestCase):
    """
    Verify users.signals.create_userconfig creates a default UserConfig for new users only.
    """

    @override_settings(DEFAULT_USER_PREFERENCES={'pagination.per_page': 42})
    def test_userconfig_is_created_with_default_preferences(self):
        user = User.objects.create_user(username='alice', password='pw')

        config = UserConfig.objects.get(user=user)
        self.assertEqual(config.data, {'pagination.per_page': 42})

    def test_userconfig_is_not_created_for_existing_user(self):
        user = User.objects.create_user(username='alice', password='pw')
        UserConfig.objects.filter(user=user).delete()

        user.email = 'alice@example.com'
        user.save()

        self.assertFalse(UserConfig.objects.filter(user=user).exists())

    def test_userconfig_is_not_created_for_raw_imports(self):
        """
        When loading a fixture (`raw=True`), the signal must skip UserConfig creation.
        """
        user = User(username='bob')
        # Simulate the post_save signal Django emits during loaddata with raw=True.
        post_save.disconnect(create_userconfig, sender=User)
        try:
            user.save()
            UserConfig.objects.filter(user=user).delete()
            create_userconfig(instance=user, created=True, raw=True)
        finally:
            post_save.connect(create_userconfig, sender=User)

        self.assertFalse(UserConfig.objects.filter(user=user).exists())
