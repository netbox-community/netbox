import logging
from contextlib import contextmanager

from django.contrib.auth.models import Permission, User
from django.forms.models import model_to_dict as _model_to_dict


def model_to_dict(instance, fields=None, exclude=None):
    """
    Customized wrapper for Django's built-in model_to_dict(). Does the following:
      - Excludes the instance ID field
      - Exclude any fields prepended with an underscore
      - Convert any assigned tags to a comma-separated string
    """
    _exclude = ['id']
    if exclude is not None:
        _exclude += exclude

    model_dict = _model_to_dict(instance, fields=fields, exclude=_exclude)

    for key in list(model_dict.keys()):
        if key.startswith('_'):
            del model_dict[key]

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
