from django.db.models import QuerySet

from users.constants import CONSTRAINT_TOKEN_USER
from utilities.permissions import permission_is_exempt, qs_filter_from_constraints


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
