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

        # If not, check for an object-level permission
        app, codename = self.permission_required.split('.')
        action, model_name = codename.split('_')
        model = self.queryset.model
        obj_permissions = ObjectPermission.objects.filter(
            Q(users=self.request.user) | Q(groups__user=self.request.user),
            model=ContentType.objects.get_for_model(model),
            **{f'can_{action}': True}
        )
        if obj_permissions:

            # Update the view's QuerySet to filter only the permitted objects
            # TODO: Do this more efficiently
            for perm in obj_permissions:
                self.queryset = self.queryset.filter(**perm.attrs)

            return True

        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
