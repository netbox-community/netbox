from __future__ import unicode_literals

from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import DjangoModelPermissions, SAFE_METHODS
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.utils import formatting

from users.models import Token


#
# Renderers
#

class FormlessBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Override the built-in BrowsableAPIRenderer to disable HTML forms.
    """
    def show_form_for_method(self, *args, **kwargs):
        return False

    def get_filter_form(self, data, view, request):
        return None


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
        from django.conf import settings
        self.authenticated_users_only = settings.LOGIN_REQUIRED
        super(TokenPermissions, self).__init__()

    def has_permission(self, request, view):
        # If token authentication is in use, verify that the token allows write operations (for unsafe methods).
        if request.method not in SAFE_METHODS and isinstance(request.auth, Token):
            if not request.auth.write_enabled:
                return False
        return super(TokenPermissions, self).has_permission(request, view)


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

    def get_next_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        return super(OptionalLimitOffsetPagination, self).get_next_link()

    def get_previous_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        return super(OptionalLimitOffsetPagination, self).get_previous_link()


#
# Miscellaneous
#

def get_view_name(view_cls, suffix=None):
    """
    Derive the view name from its associated model, if it has one. Fall back to DRF's built-in `get_view_name`.
    """
    if hasattr(view_cls, 'queryset'):
        # Determine the model name from the queryset.
        name = view_cls.queryset.model._meta.verbose_name
        name = ' '.join([w[0].upper() + w[1:] for w in name.split()])  # Capitalize each word

    else:
        # Replicate DRF's built-in behavior.
        name = view_cls.__name__
        name = formatting.remove_trailing_string(name, 'View')
        name = formatting.remove_trailing_string(name, 'ViewSet')
        name = formatting.camelcase_to_spaces(name)

    if suffix:
        name += ' ' + suffix

    return name
