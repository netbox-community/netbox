import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, RangeField
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ManyToManyField, ManyToManyRel, JSONField
from django.forms.models import model_to_dict
from django.test import Client, TestCase as _TestCase
from netaddr import IPNetwork
from taggit.managers import TaggableManager

from core.models import ObjectType
from users.models import ObjectPermission
from utilities.data import ranges_to_string
from utilities.object_types import object_type_identifier
from utilities.permissions import resolve_permission_type
from .utils import DUMMY_CF_DATA, extract_form_failures

__all__ = (
    'ModelTestCase',
    'TestCase',
)


class TestCase(_TestCase):
    user_permissions = ()

    def setUp(self):

        # Create the test user and assign permissions
        self.user = get_user_model().objects.create_user(username='testuser')
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
            object_type, action = resolve_permission_type(name)
            obj_perm = ObjectPermission(name=name, actions=[action])
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(object_type)

    #
    # Custom assertions
    #

    def assertHttpStatus(self, response, expected_status):
        """
        TestCase method. Provide more detail in the event of an unexpected HTTP response.
        """
        err_message = None
        # Construct an error message only if we know the test is going to fail
        if response.status_code != expected_status:
            if hasattr(response, 'data'):
                # REST API response; pass the response data through directly
                err = response.data
            else:
                # Attempt to extract form validation errors from the response HTML
                form_errors = extract_form_failures(response.content)
                err = form_errors or response.content or 'No data'
            err_message = f"Expected HTTP status {expected_status}; received {response.status_code}: {err}"
        self.assertEqual(response.status_code, expected_status, err_message)


class ModelTestCase(TestCase):
    """
    Parent class for TestCases which deal with models.
    """
    model = None

    def _get_queryset(self):
        """
        Return a base queryset suitable for use in test methods.
        """
        return self.model.objects.all()

    def prepare_instance(self, instance):
        """
        Test cases can override this method to perform any necessary manipulation of an instance prior to its evaluation
        against test data. For example, it can be used to decrypt a Secret's plaintext attribute.
        """
        return instance

    def model_to_dict(self, instance, fields, api=False):
        """
        Return a dictionary representation of an instance.
        """
        # Prepare the instance and call Django's model_to_dict() to extract all fields
        model_dict = model_to_dict(self.prepare_instance(instance), fields=fields)

        # Map any additional (non-field) instance attributes that were specified
        for attr in fields:
            if hasattr(instance, attr) and attr not in model_dict:
                model_dict[attr] = getattr(instance, attr)

        for key, value in list(model_dict.items()):
            try:
                field = instance._meta.get_field(key)
            except FieldDoesNotExist:
                # Attribute is not a model field
                continue

            # Handle ManyToManyFields
            if value and type(field) in (ManyToManyField, ManyToManyRel, TaggableManager):
                # Resolve reverse M2M relationships
                if isinstance(field, ManyToManyRel):
                    value = getattr(instance, field.related_name).all()
                if field.related_model in (ContentType, ObjectType) and api:
                    model_dict[key] = sorted([object_type_identifier(ot) for ot in value])
                else:
                    model_dict[key] = sorted([obj.pk for obj in value])

            elif api:

                # Replace ContentType numeric IDs with <app_label>.<model>
                if type(getattr(instance, key)) in (ContentType, ObjectType):
                    object_type = ObjectType.objects.get(pk=value)
                    model_dict[key] = object_type_identifier(object_type)

                # Convert IPNetwork instances to strings
                elif type(value) is IPNetwork:
                    model_dict[key] = str(value)

            else:
                field = instance._meta.get_field(key)

                # Convert ArrayFields to CSV strings
                if type(field) is ArrayField:
                    if type(field.base_field) is ArrayField:
                        # Handle nested arrays (e.g. choice sets)
                        model_dict[key] = '\n'.join([f'{k},{v}' for k, v in value])
                    elif issubclass(type(field.base_field), RangeField):
                        # Handle arrays of numeric ranges (e.g. VLANGroup VLAN ID ranges)
                        model_dict[key] = ranges_to_string(value)
                    else:
                        model_dict[key] = ','.join([str(v) for v in value])

                # JSON
                if type(field) is JSONField and value is not None:
                    model_dict[key] = json.dumps(value)

        return model_dict

    #
    # Custom assertions
    #

    def assertInstanceEqual(self, instance, data, exclude=None, api=False):
        """
        Compare a model instance to a dictionary, checking that its attribute values match those specified
        in the dictionary.

        :param instance: Python object instance
        :param data: Dictionary of test data used to define the instance
        :param exclude: List of fields to exclude from comparison (e.g. passwords, which get hashed)
        :param api: Set to True is the data is a JSON representation of the instance
        """
        if exclude is None:
            exclude = []

        fields = [k for k in data.keys() if k not in exclude]
        model_dict = self.model_to_dict(instance, fields=fields, api=api)

        # Omit any dictionary keys which are not instance attributes or have been excluded
        model_data = {
            k: v for k, v in data.items() if hasattr(instance, k) and k not in exclude
        }

        self.assertDictEqual(model_dict, model_data)

        # Validate any custom field data, if present
        if getattr(instance, 'custom_field_data', None):
            self.assertDictEqual(instance.custom_field_data, DUMMY_CF_DATA)
