from django.db.models import Q, QuerySet

from utilities.permissions import permission_is_exempt


class DummyQuerySet:
    """
    A fake QuerySet that can be used to cache relationships to objects that have been deleted.
    """
    def __init__(self, queryset):
        self._cache = [obj for obj in queryset.all()]

    def all(self):
        return self._cache


class RestrictedQuerySet(QuerySet):

    def restrict(self, user, action):
        """
        Filter the QuerySet to return only objects on which the specified user has been granted the specified
        permission.

        :param user: User instance
        :param action: The action which must be permitted (e.g. "view" for "dcim.view_site")
        """
        # Resolve the full name of the required permission
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission_required = f'{app_label}.{action}_{model_name}'

        # Bypass restriction for superusers and exempt views
        if user.is_superuser or permission_is_exempt(permission_required):
            return self

        # User is anonymous or has not been granted the requisite permission
        if not user.is_authenticated or permission_required not in user.get_all_permissions():
            return self.none()

        # Filter the queryset to include only objects with allowed attributes
        attrs = Q()
        for perm_attrs in user._object_perm_cache[permission_required]:
            if perm_attrs:
                attrs |= Q(**perm_attrs)

        return self.filter(attrs)
