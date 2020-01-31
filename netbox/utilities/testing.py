import logging
from contextlib import contextmanager

from django.contrib.auth.models import Permission, User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict as _model_to_dict
from django.test import Client, TestCase as _TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import Token


class TestCase(_TestCase):
    user_permissions = ()

    def setUp(self):

        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.add_permissions(*self.user_permissions)

        # Initialize the test client
        self.client = Client()
        self.client.force_login(self.user)

    #
    # Permissions management
    #

    def add_permissions(self, *names):
        """
        Assign a set of permissions to the test user. Accepts permission names in the form <app>.<action>_<model>.
        """
        for name in names:
            app, codename = name.split('.')
            perm = Permission.objects.get(content_type__app_label=app, codename=codename)
            self.user.user_permissions.add(perm)

    def remove_permissions(self, *names):
        """
        Remove a set of permissions from the test user, if assigned.
        """
        for name in names:
            app, codename = name.split('.')
            perm = Permission.objects.get(content_type__app_label=app, codename=codename)
            self.user.user_permissions.remove(perm)

    #
    # Convenience methods
    #

    def assertHttpStatus(self, response, expected_status):
        """
        TestCase method. Provide more detail in the event of an unexpected HTTP response.
        """
        err_message = "Expected HTTP status {}; received {}: {}"
        self.assertEqual(response.status_code, expected_status, err_message.format(
            expected_status, response.status_code, getattr(response, 'data', 'No data')
        ))


class APITestCase(TestCase):
    client_class = APIClient

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}


# TODO: Omit this from tests
class ViewTestCase(TestCase):
    """
    Stock TestCase suitable for testing all standard View functions:
        - List objects
        - View single object
        - Create new object
        - Modify existing object
        - Delete existing object
        - Import multiple new objects
    """
    model = None
    form_data = {}
    csv_data = {}

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.base_url_name = '{}:{}_{{}}'.format(self.model._meta.app_label, self.model._meta.model_name)

    def test_list_objects(self):
        response = self.client.get(reverse(self.base_url_name.format('list')))
        self.assertHttpStatus(response, 200)

    def test_get_object(self):
        instance = self.model.objects.first()
        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_create_object(self):
        initial_count = self.model.objects.count()
        request = {
            'path': reverse(self.base_url_name.format('add')),
            'data': post_data(self.form_data),
            'follow': True,
        }
        print(request['data'])

        # Attempt to make the request without required permissions
        with disable_warnings('django.request'):
            self.assertHttpStatus(self.client.post(**request), 403)

        # Assign the required permission and submit again
        self.add_permissions('{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)

        self.assertEqual(initial_count, self.model.objects.count() + 1)
        instance = self.model.objects.order_by('-pk').first()
        self.assertDictEqual(model_to_dict(instance), self.form_data)

    def test_edit_object(self):
        instance = self.model.objects.first()

        # Determine the proper kwargs to pass to the edit URL
        if hasattr(instance, 'slug'):
            kwargs = {'slug': instance.slug}
        else:
            kwargs = {'pk': instance.pk}

        request = {
            'path': reverse(self.base_url_name.format('edit'), kwargs=kwargs),
            'data': post_data(self.form_data),
            'follow': True,
        }

        # Attempt to make the request without required permissions
        with disable_warnings('django.request'):
            self.assertHttpStatus(self.client.post(**request), 403)

        # Assign the required permission and submit again
        self.add_permissions('{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)

        instance = self.model.objects.get(pk=instance.pk)
        self.assertDictEqual(model_to_dict(instance), self.form_data)

    def test_delete_object(self):
        instance = self.model.objects.first()

        # Determine the proper kwargs to pass to the deletion URL
        if hasattr(instance, 'slug'):
            kwargs = {'slug': instance.slug}
        else:
            kwargs = {'pk': instance.pk}

        request = {
            'path': reverse(self.base_url_name.format('delete'), kwargs=kwargs),
            'data': {'confirm': True},
            'follow': True,
        }

        # Attempt to make the request without required permissions
        with disable_warnings('django.request'):
            self.assertHttpStatus(self.client.post(**request), 403)

        # Assign the required permission and submit again
        self.add_permissions('{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)

        with self.assertRaises(ObjectDoesNotExist):
            self.model.objects.get(pk=instance.pk)

    def test_import_objects(self):
        request = {
            'path': reverse(self.base_url_name.format('import')),
            'data': {
                'csv': '\n'.join(self.csv_data)
            }
        }
        initial_count = self.model.objects.count()

        # Attempt to make the request without required permissions
        with disable_warnings('django.request'):
            self.assertHttpStatus(self.client.post(**request), 403)

        # Assign the required permission and submit again
        self.add_permissions('{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)

        self.assertEqual(self.model.objects.count(), initial_count + len(self.csv_data) - 1)


def model_to_dict(instance, fields=None, exclude=None):
    """
    Customized wrapper for Django's built-in model_to_dict(). Does the following:
      - Excludes the instance ID field
      - Convert any assigned tags to a comma-separated string
    """
    _exclude = ['id']
    if exclude is not None:
        _exclude += exclude

    model_dict = _model_to_dict(instance, fields=fields, exclude=_exclude)

    if 'tags' in model_dict:
        model_dict['tags'] = ','.join(sorted([tag.name for tag in model_dict['tags']]))

    return model_dict


def post_data(data):
    """
    Take a dictionary of test data (suitable for comparison to an instance) and return a dict suitable for POSTing.
    """
    ret = {}

    for key, value in data.items():
        if value is None:
            ret[key] = ''
        elif hasattr(value, 'pk'):
            ret[key] = getattr(value, 'pk')
        else:
            ret[key] = str(value)

    return ret


def create_test_user(username='testuser', permissions=list()):
    """
    Create a User with the given permissions.
    """
    user = User.objects.create_user(username=username)
    for perm_name in permissions:
        app, codename = perm_name.split('.')
        perm = Permission.objects.get(content_type__app_label=app, codename=codename)
        user.user_permissions.add(perm)

    return user


def choices_to_dict(choices_list):
    """
    Convert a list of field choices to a dictionary suitable for direct comparison with a ChoiceSet. For example:

        [
            {
                "value": "choice-1",
                "label": "First Choice"
            },
            {
                "value": "choice-2",
                "label": "Second Choice"
            }
        ]

    Becomes:

        {
            "choice-1": "First Choice",
            "choice-2": "Second Choice
        }
    """
    return {
        choice['value']: choice['label'] for choice in choices_list
    }


@contextmanager
def disable_warnings(logger_name):
    """
    Temporarily suppress expected warning messages to keep the test output clean.
    """
    logger = logging.getLogger(logger_name)
    current_level = logger.level
    logger.setLevel(logging.ERROR)
    yield
    logger.setLevel(current_level)
