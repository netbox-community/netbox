from django.db.models import Q, QuerySet


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

        :param queryset: Base QuerySet to be restricted
        :param user: User instance
        :param action: The action which must be permitted (e.g. "view" for "dcim.view_site")
        """
        # Resolve the full name of the required permission
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission_required = f'{app_label}.{action}_{model_name}'

        # TODO: Handle anonymous users
        if not user.is_authenticated:
            return self

        # Determine what constraints (if any) have been placed on this user for this action and model
        # TODO: Find a better way to ensure permissions are cached
        if not hasattr(user, '_object_perm_cache'):
            user.get_all_permissions()

        # User has not been granted any permission
        if permission_required not in user._object_perm_cache:
            return self.none()

        # Filter the queryset to include only objects with allowed attributes
        attrs = Q()
        for perm_attrs in user._object_perm_cache[permission_required]:
            if perm_attrs:
                attrs |= Q(**perm_attrs)

        return self.filter(attrs)
