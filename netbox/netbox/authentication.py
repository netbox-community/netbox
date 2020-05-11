from django.contrib.auth.mixins import AccessMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from users.models import ObjectPermission


class ObjectPermissionRequiredMixin(AccessMixin):
    permission_required = None

    def has_permission(self):

        # First, check whether the user has a model-level permission assigned
        if self.request.user.has_perm(self.permission_required):
            return True

        # If not, check for object-level permissions
        app, codename = self.permission_required.split('.')
        action, model_name = codename.split('_')
        model = self.queryset.model
        attrs = ObjectPermission.objects.get_attr_constraints(self.request.user, model, action)
        if attrs:
            # Update the view's QuerySet to filter only the permitted objects
            self.queryset = self.queryset.filter(**attrs)
            return True

        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
