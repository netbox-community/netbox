import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as _RemoteUserBackend
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from users.models import ObjectPermission


class ObjectPermissionBackend(ModelBackend):

    def get_object_permissions(self, user_obj):
        """
        Return all permissions granted to the user by an ObjectPermission.
        """
        if not hasattr(user_obj, '_object_perm_cache'):

            # Retrieve all assigned ObjectPermissions
            object_permissions = ObjectPermission.objects.filter(
                Q(users=user_obj) |
                Q(groups__user=user_obj)
            ).prefetch_related('model')

            # Create a dictionary mapping permissions to their attributes
            perms = dict()
            for obj_perm in object_permissions:
                for action in ['view', 'add', 'change', 'delete']:
                    if getattr(obj_perm, f"can_{action}"):
                        perm_name = f"{obj_perm.model.app_label}.{action}_{obj_perm.model.model}"
                        if perm_name in perms:
                            perms[perm_name].append(obj_perm.attrs)
                        else:
                            perms[perm_name] = [obj_perm.attrs]

            # Cache resolved permissions on the User instance
            setattr(user_obj, '_object_perm_cache', perms)

        return user_obj._object_perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        # print(f'has_perm({perm})')
        app_label, codename = perm.split('.')
        action, model_name = codename.split('_')

        # Superusers implicitly have all permissions
        if user_obj.is_active and user_obj.is_superuser:
            return True

        # If this is a view permission, check whether the model has been exempted from enforcement
        if action == 'view':
            if (
                # All models are exempt from view permission enforcement
                '*' in settings.EXEMPT_VIEW_PERMISSIONS
            ) or (
                # This specific model is exempt from view permission enforcement
                '{}.{}'.format(app_label, model_name) in settings.EXEMPT_VIEW_PERMISSIONS
            ):
                return True

        # Handle inactive/anonymous users
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        # If no applicable ObjectPermissions have been created for this user/permission, deny permission
        if perm not in self.get_object_permissions(user_obj):
            return False

        # If no object has been specified, grant permission. (The presence of a permission in this set tells
        # us that the user has permission for *some* objects, but not necessarily a specific object.)
        if obj is None:
            return True

        # Sanity check: Ensure that the requested permission applies to the specified object
        model = obj._meta.model
        if model._meta.label_lower != '.'.join((app_label, model_name)):
            raise ValueError(f"Invalid permission {perm} for model {model}")

        # Compile a query filter that matches all instances of the specified model
        obj_perm_attrs = self.get_object_permissions(user_obj)[perm]
        attrs = Q()
        for perm_attrs in obj_perm_attrs:
            if perm_attrs:
                attrs |= Q(**perm_attrs)
            else:
                # Found ObjectPermission with null attrs; allow model-level access
                attrs = Q()
                break

        # Permission to perform the requested action on the object depends on whether the specified object matches
        # the specified attributes. Note that this check is made against the *database* record representing the object,
        # not the instance itself.
        return model.objects.filter(attrs, pk=obj.pk).exists()


class RemoteUserBackend(_RemoteUserBackend):
    """
    Custom implementation of Django's RemoteUserBackend which provides configuration hooks for basic customization.
    """
    @property
    def create_unknown_user(self):
        return settings.REMOTE_AUTH_AUTO_CREATE_USER

    def configure_user(self, request, user):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')

        # Assign default groups to the user
        group_list = []
        for name in settings.REMOTE_AUTH_DEFAULT_GROUPS:
            try:
                group_list.append(Group.objects.get(name=name))
            except Group.DoesNotExist:
                logging.error(f"Could not assign group {name} to remotely-authenticated user {user}: Group not found")
        if group_list:
            user.groups.add(*group_list)
            logger.debug(f"Assigned groups to remotely-authenticated user {user}: {group_list}")

        # Assign default object permissions to the user
        permissions_list = []
        for permission_name in settings.REMOTE_AUTH_DEFAULT_PERMISSIONS:
            try:
                app_label, codename = permission_name.split('.')
                action, model_name = codename.split('_')

                kwargs = {
                    'model': ContentType.objects.get(app_label=app_label, model=model_name),
                    f'can_{action}': True
                }
                obj_perm = ObjectPermission(**kwargs)
                obj_perm.save()
                obj_perm.users.add(user)
                permissions_list.append(permission_name)
            except ValueError:
                logging.error(
                    "Invalid permission name: '{permission_name}'. Permissions must be in the form "
                    "<app>.<action>_<model>. (Example: dcim.add_site)"
                )
        if permissions_list:
            logger.debug(f"Assigned permissions to remotely-authenticated user {user}: {permissions_list}")

        return user

    def has_perm(self, user_obj, perm, obj=None):
        return False
