import logging
import re
from contextlib import contextmanager

from django.contrib.auth.models import Permission, User
from django.utils.text import slugify

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.models import Tag
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


def create_test_device(name):
    """
    Convenience method for creating a Device (e.g. for component testing).
    """
    site, _ = Site.objects.get_or_create(name='Site 1', slug='site-1')
    manufacturer, _ = Manufacturer.objects.get_or_create(name='Manufacturer 1', slug='manufacturer-1')
    devicetype, _ = DeviceType.objects.get_or_create(model='Device Type 1', manufacturer=manufacturer)
    devicerole, _ = DeviceRole.objects.get_or_create(name='Device Role 1', slug='device-role-1')
    device = Device.objects.create(name=name, site=site, device_type=devicetype, device_role=devicerole)

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
    user = User.objects.create_user(username=username)
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
