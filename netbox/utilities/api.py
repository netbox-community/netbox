from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework import authentication, exceptions
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission, DjangoModelPermissions, SAFE_METHODS
from rest_framework.serializers import Field, ModelSerializer, ValidationError
from rest_framework.views import get_view_name as drf_get_view_name

from users.models import Token


WRITE_OPERATIONS = ['create', 'update', 'partial_update', 'delete']


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


#
# Authentication
#

class TokenAuthentication(authentication.TokenAuthentication):
    """
    A custom authentication scheme which enforces Token expiration times.
    """
    model = Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")

        # Enforce the Token's expiration time, if one has been set.
        if token.is_expired:
            raise exceptions.AuthenticationFailed("Token expired")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")

        return token.user, token


class TokenPermissions(DjangoModelPermissions):
    """
    Custom permissions handler which extends the built-in DjangoModelPermissions to validate a Token's write ability
    for unsafe requests (POST/PUT/PATCH/DELETE).
    """
    def __init__(self):
        # LOGIN_REQUIRED determines whether read-only access is provided to anonymous users.
        self.authenticated_users_only = settings.LOGIN_REQUIRED
        super(TokenPermissions, self).__init__()

    def has_permission(self, request, view):
        # If token authentication is in use, verify that the token allows write operations (for unsafe methods).
        if request.method not in SAFE_METHODS and isinstance(request.auth, Token):
            if not request.auth.write_enabled:
                return False
        return super(TokenPermissions, self).has_permission(request, view)


class IsAuthenticatedOrLoginNotRequired(BasePermission):
    """
    Returns True if the user is authenticated or LOGIN_REQUIRED is False.
    """
    def has_permission(self, request, view):
        if not settings.LOGIN_REQUIRED:
            return True
        return request.user and is_authenticated(request.user)


#
# Serializers
#

class ValidatedModelSerializer(ModelSerializer):
    """
    Extends the built-in ModelSerializer to enforce calling clean() on the associated model during validation.
    """
    def validate(self, data):

        # Remove custom field data (if any) prior to model validation
        attrs = data.copy()
        attrs.pop('custom_fields', None)

        # Run clean() on an instance of the model
        if self.instance is None:
            instance = self.Meta.model(**attrs)
        else:
            instance = self.instance
            for k, v in attrs.items():
                setattr(instance, k, v)
        instance.clean()

        return data


class ChoiceFieldSerializer(Field):
    """
    Represent a ChoiceField as {'value': <DB value>, 'label': <string>}.
    """
    def __init__(self, choices, **kwargs):
        self._choices = dict()
        for k, v in choices:
            # Unpack grouped choices
            if type(v) in [list, tuple]:
                for k2, v2 in v:
                    self._choices[k2] = v2
            else:
                self._choices[k] = v
        super(ChoiceFieldSerializer, self).__init__(**kwargs)

    def to_representation(self, obj):
        return {'value': obj, 'label': self._choices[obj]}

    def to_internal_value(self, data):
        return self._choices.get(data)


class ContentTypeFieldSerializer(Field):
    """
    Represent a ContentType as '<app_label>.<model>'
    """
    def to_representation(self, obj):
        return "{}.{}".format(obj.app_label, obj.model)

    def to_internal_value(self, data):
        app_label, model = data.split('.')
        try:
            return ContentType.objects.get_by_natural_key(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            raise ValidationError("Invalid content type")


#
# Mixins
#

class WritableSerializerMixin(object):
    """
    Allow for the use of an alternate, writable serializer class for write operations (e.g. POST, PUT).
    """
    def get_serializer_class(self):
        if self.action in WRITE_OPERATIONS and hasattr(self, 'write_serializer_class'):
            return self.write_serializer_class
        return self.serializer_class


#
# Pagination
#

class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Override the stock paginator to allow setting limit=0 to disable pagination for a request. This returns all objects
    matching a query, but retains the same format as a paginated request. The limit can only be disabled if
    MAX_PAGE_SIZE has been set to 0 or None.
    """

    def paginate_queryset(self, queryset, request, view=None):

        try:
            self.count = queryset.count()
        except (AttributeError, TypeError):
            self.count = len(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request

        if self.limit and self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return list()

        if self.limit:
            return list(queryset[self.offset:self.offset + self.limit])
        else:
            return list(queryset[self.offset:])

    def get_limit(self, request):

        if self.limit_query_param:
            try:
                limit = int(request.query_params[self.limit_query_param])
                if limit < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
                if settings.MAX_PAGE_SIZE:
                    if limit == 0:
                        return settings.MAX_PAGE_SIZE
                    else:
                        return min(limit, settings.MAX_PAGE_SIZE)
                return limit
            except (KeyError, ValueError):
                pass

        return self.default_limit


#
# Miscellaneous
#

def get_view_name(view_cls, suffix=None):
    """
    Derive the view name from its associated model, if it has one. Fall back to DRF's built-in `get_view_name`.
    """
    if hasattr(view_cls, 'queryset'):
        name = view_cls.queryset.model._meta.verbose_name
        name = ' '.join([w[0].upper() + w[1:] for w in name.split()])  # Capitalize each word
        if suffix:
            name = "{} {}".format(name, suffix)
        return name

    return drf_get_view_name(view_cls, suffix)
