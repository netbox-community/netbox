import logging

from django.db.models import Q, QuerySet

from utilities.permissions import permission_is_exempt


class DummyQuerySet:
    """
    A fake QuerySet that can be used to cache relationships to objects that have been deleted.
    """
    def __init__(self, queryset):
        self._cache = [obj for obj in queryset.all()]

    def __iter__(self):
        return iter(self._cache)

    def all(self):
        return self._cache


class RestrictedQuerySet(QuerySet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize the allow_evaluation flag to False. This indicates that the QuerySet has not yet been restricted.
        self.allow_evaluation = False

    def _check_restriction(self):
        # Raise a warning if the QuerySet is evaluated without first calling restrict() or unrestricted().
        if not getattr(self, 'allow_evaluation', False):
            logger = logging.getLogger('netbox.RestrictedQuerySet')
            logger.warning(
                f'Evaluation of RestrictedQuerySet prior to calling restrict() or unrestricted(): {self.model}'
            )

    def _clone(self):

        # Persist the allow_evaluation flag when cloning the QuerySet.
        c = super()._clone()
        c.allow_evaluation = self.allow_evaluation

        return c

    def _fetch_all(self):
        self._check_restriction()
        return super()._fetch_all()

    def count(self):
        self._check_restriction()
        return super().count()

    def unrestricted(self):
        """
        Bypass restriction for the QuerySet. This is necessary in cases where we are not interacting with the objects
        directly (e.g. when filtering by related object).
        """
        self.allow_evaluation = True
        return self

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
                if perm_attrs:
                    attrs |= Q(**perm_attrs)
            qs = self.filter(attrs)

        # Allow QuerySet evaluation
        qs.allow_evaluation = True

        return qs
