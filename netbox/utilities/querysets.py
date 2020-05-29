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

    def restrict(self, user, permission_required):
        """
        Filter the QuerySet to return only objects on which the specified user has been granted the specified
        permission.

        :param queryset: Base QuerySet to be restricted
        :param user: User instance
        :param permission_required: Name of the required permission (e.g. "dcim.view_site")
        """

        # Determine what constraints (if any) have been placed on this user for this action and model
        # TODO: Find a better way to ensure permissions are cached
        if not hasattr(user, '_object_perm_cache'):
            user.get_all_permissions()
        obj_perm_attrs = user._object_perm_cache[permission_required]

        # Filter the queryset to include only objects with allowed attributes
        attrs = Q()
        for perm_attrs in obj_perm_attrs:
            if perm_attrs:
                attrs |= Q(**perm_attrs)

        return self.filter(attrs)
