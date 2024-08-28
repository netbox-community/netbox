import json
import logging
import re
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.text import slugify

from core.models import ObjectType
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField, Tag
from virtualization.models import Cluster, ClusterType, VirtualMachine


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


def create_test_device(name, site=None, **attrs):
    """
    Convenience method for creating a Device (e.g. for component testing).
    """
    if site is None:
        site, _ = Site.objects.get_or_create(name='Site 1', slug='site-1')
    manufacturer, _ = Manufacturer.objects.get_or_create(name='Manufacturer 1', slug='manufacturer-1')
    devicetype, _ = DeviceType.objects.get_or_create(model='Device Type 1', manufacturer=manufacturer)
    devicerole, _ = DeviceRole.objects.get_or_create(name='Device Role 1', slug='device-role-1')
    device = Device.objects.create(name=name, site=site, device_type=devicetype, role=devicerole, **attrs)

    return device


def create_test_virtualmachine(name):
    """
    Convenience method for creating a VirtualMachine.
    """
    cluster_type, _ = ClusterType.objects.get_or_create(name='Cluster Type 1', slug='cluster-type-1')
    cluster, _ = Cluster.objects.get_or_create(name='Cluster 1', type=cluster_type)
    virtual_machine = VirtualMachine.objects.create(name=name, cluster=cluster)

    return virtual_machine


def create_test_user(username='testuser', permissions=None):
    """
    Create a User with the given permissions.
    """
    user = get_user_model().objects.create_user(username=username)
    if permissions is None:
        permissions = ()
    for perm_name in permissions:
        app, codename = perm_name.split('.')
        perm = Permission.objects.get(content_type__app_label=app, codename=codename)
        user.user_permissions.add(perm)

    return user


def create_tags(*names):
    """
    Create and return a Tag instance for each name given.
    """
    tags = [Tag(name=name, slug=slugify(name)) for name in names]
    Tag.objects.bulk_create(tags)
    return tags


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


@contextmanager
def disable_logging(level=logging.CRITICAL):
    """
    Temporarily suppress log messages at or below the specified level (default: critical).
    """
    logging.disable(level)
    yield
    logging.disable(logging.NOTSET)


#
# Custom field testing
#

DUMMY_CF_DATA = {
    'text_field': 'foo123',
    'integer_field': 456,
    'decimal_field': 456.12,
    'boolean_field': True,
    'json_field': {'abc': 123},
}


def add_custom_field_data(form_data, model):
    """
    Create some custom fields for the model and add a value for each to the form data.

    Args:
        form_data: The dictionary of form data to be updated
        model: The model of the object the form seeks to create or modify
    """
    object_type = ObjectType.objects.get_for_model(model)
    custom_fields = (
        CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo'),
        CustomField(type=CustomFieldTypeChoices.TYPE_INTEGER, name='integer_field', default=123),
        CustomField(type=CustomFieldTypeChoices.TYPE_DECIMAL, name='decimal_field', default=123.45),
        CustomField(type=CustomFieldTypeChoices.TYPE_BOOLEAN, name='boolean_field', default=False),
        CustomField(type=CustomFieldTypeChoices.TYPE_JSON, name='json_field', default='{"x": "y"}'),
    )
    CustomField.objects.bulk_create(custom_fields)
    for cf in custom_fields:
        cf.object_types.set([object_type])

    form_data.update({
        f'cf_{k}': v if type(v) is str else json.dumps(v)
        for k, v in DUMMY_CF_DATA.items()
    })
