from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured

from users.models import ObjectPermission


class ObjectPermissionRequiredMixin(AccessMixin):
    """
    Similar to Django's built-in PermissionRequiredMixin, but extended to check for both model-level and object-level
    permission assignments. If the user has only object-level permissions assigned, the view's queryset is filtered
    to return only those objects on which the user is permitted to perform the specified action.
    """
    permission_required = None

    def has_permission(self):
        # First, check whether the user is granted the requested permissions from any backend.
        if not self.request.user.has_perm(self.permission_required):
            return False

        # Next, determine whether the permission is model-level or object-level. Model-level permissions grant the
        # specified action to *all* objects, so no further action is needed.
        if self.request.user.is_superuser or self.permission_required in self.request.user._perm_cache:
            return True

        # If the permission is granted only at the object level, filter the view's queryset to return only objects
        # on which the user is permitted to perform the specified action.
        if self.permission_required in self.request.user._obj_perm_cache:
            attrs = ObjectPermission.objects.get_attr_constraints(self.request.user, self.permission_required)
            if attrs:
                # Update the view's QuerySet to filter only the permitted objects
                self.queryset = self.queryset.filter(attrs)
                return True

    def dispatch(self, request, *args, **kwargs):
        if self.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )

        if not hasattr(self, 'queryset'):
            raise ImproperlyConfigured(
                '{} has no queryset defined. ObjectPermissionRequiredMixin may only be used on views which define '
                'a base queryset'.format(self.__class__.__name__)
            )

        if not self.has_permission():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
