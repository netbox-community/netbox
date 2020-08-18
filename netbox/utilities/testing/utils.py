import logging
import re
from contextlib import contextmanager

from django.contrib.auth.models import Permission, User


def post_data(data):
    """
    Take a dictionary of test data (suitable for comparison to an instance) and return a dict suitable for POSTing.
    """
    ret = {}

    for key, value in data.items():
        if value is None:
            ret[key] = ''
        elif type(value) in (list, tuple):
            if value and hasattr(value[0], 'pk'):
                # Value is a list of instances
                ret[key] = [v.pk for v in value]
            else:
                ret[key] = value
        elif hasattr(value, 'pk'):
            # Value is an instance
            ret[key] = value.pk
        else:
            ret[key] = str(value)

    return ret


def create_test_user(username='testuser', permissions=None):
    """
    Create a User with the given permissions.
    """
    user = User.objects.create_user(username=username)
    if permissions is None:
        permissions = ()
    for perm_name in permissions:
        app, codename = perm_name.split('.')
        perm = Permission.objects.get(content_type__app_label=app, codename=codename)
        user.user_permissions.add(perm)

    return user


def extract_form_failures(content):
    """
    Given raw HTML content from an HTTP response, return a list of form errors.
    """
    FORM_ERROR_REGEX = r'<!-- FORM-ERROR (.*) -->'
    return re.findall(FORM_ERROR_REGEX, str(content))


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
