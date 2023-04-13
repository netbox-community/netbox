from django.db.models import Prefetch, QuerySet

from users.constants import CONSTRAINT_TOKEN_USER
from utilities.permissions import permission_is_exempt, qs_filter_from_constraints

__all__ = (
    'RestrictedPrefetch',
    'RestrictedQuerySet',
)


class RestrictedPrefetch(Prefetch):
    """
    Extend Django's Prefetch to accept a user and action to be passed to the
    `restrict()` method of the related object's queryset.
    """
    def __init__(self, lookup, user, action='view', queryset=None, to_attr=None):
        self.restrict_user = user
        self.restrict_action = action

        super().__init__(lookup, queryset=queryset, to_attr=to_attr)

    def get_current_queryset(self, level):
        params = {
            'user': self.restrict_user,
            'action': self.restrict_action,
        }

        if qs := super().get_current_queryset(level):
            return qs.restrict(**params)

        # Bit of a hack. If no queryset is defined, pass through the dict of restrict()
        # kwargs to be handled by the field. This is necessary e.g. for GenericForeignKey
        # fields, which do not permit setting a queryset on a Prefetch object.
        return params


class RestrictedQuerySet(QuerySet):

    def restrict(self, user, action='view'):
        """
        Filter the QuerySet to return only objects on which the specified user has been granted the specified
        permission.

        :param user: User instance
        :param action: The action which must be permitted (e.g. "view" for "dcim.view_site"); default is 'view'
        """
        # Resolve the full name of the required permission
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission_required = f'{app_label}.{action}_{model_name}'

        # Bypass restriction for superusers and exempt views
        if user.is_superuser or permission_is_exempt(permission_required):
            qs = self

        # User is anonymous or has not been granted the requisite permission
        elif not user.is_authenticated or permission_required not in user.get_all_permissions():
            qs = self.none()

        # Filter the queryset to include only objects with allowed attributes
        else:
            tokens = {
                CONSTRAINT_TOKEN_USER: user,
            }
            attrs = qs_filter_from_constraints(user._object_perm_cache[permission_required], tokens)
            # #8715: Avoid duplicates when JOIN on many-to-many fields without using DISTINCT.
            # DISTINCT acts globally on the entire request, which may not be desirable.
            allowed_objects = self.model.objects.filter(attrs)
            qs = self.filter(pk__in=allowed_objects)

        return qs
