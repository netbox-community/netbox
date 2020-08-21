from django.db.models import Q, QuerySet

from utilities.permissions import permission_is_exempt


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
            attrs = Q()
            for perm_attrs in user._object_perm_cache[permission_required]:
                if type(perm_attrs) is list:
                    for p in perm_attrs:
                        attrs |= Q(**p)
                elif perm_attrs:
                    attrs |= Q(**perm_attrs)
                else:
                    # Any permission with null constraints grants access to _all_ instances
                    attrs = Q()
                    break
            qs = self.filter(attrs)

        return qs
