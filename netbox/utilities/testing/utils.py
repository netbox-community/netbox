import logging
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
            ret[key] = value
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
