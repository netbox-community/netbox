import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as RemoteUserBackend_
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from users.models import ObjectPermission


class ObjectPermissionBackend(ModelBackend):

    def get_object_permissions(self, user_obj):
        """
        Return all model-level permissions granted to the user by an ObjectPermission.
        """
        if not hasattr(user_obj, '_object_perm_cache'):

            # Cache all assigned ObjectPermissions on the User instance
            perms = set()
            for obj_perm in ObjectPermission.objects.filter(
                Q(users=user_obj) |
                Q(groups__user=user_obj)
            ).prefetch_related('model'):
                for action in ['view', 'add', 'change', 'delete']:
                    if getattr(obj_perm, f"can_{action}"):
                        perms.add(f"{obj_perm.model.app_label}.{action}_{obj_perm.model.model}")
            setattr(user_obj, '_object_perm_cache', perms)

        return user_obj._object_perm_cache

    def get_all_permissions(self, user_obj, obj=None):

        # Handle inactive/anonymous users
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        # Cache model-level permissions on the User instance
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = {
                *self.get_user_permissions(user_obj, obj=obj),
                *self.get_group_permissions(user_obj, obj=obj),
                *self.get_object_permissions(user_obj)
            }

        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        app_label, codename = perm.split('.')
        action, model_name = codename.split('_')

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

        # If no object is specified, evaluate model-level permissions. The presence of a permission in this set tells
        # us that the user has permission for *some* objects, but not necessarily a specific object.
        if obj is None:
            return perm in self.get_all_permissions(user_obj)

        # Sanity check: Ensure that the requested permission applies to the specified object
        model = obj._meta.model
        if model._meta.label_lower != '.'.join((app_label, model_name)):
            raise ValueError(f"Invalid permission {perm} for model {model}")

        # If the user has been granted model-level permission for the object, return True
        model_perms = {
            *self.get_user_permissions(user_obj),
            *self.get_group_permissions(user_obj),
        }
        if perm in model_perms:
            return True

        # Gather all ObjectPermissions pertinent to the requested permission. If none are found, the User has no
        # applicable permissions.
        attrs = ObjectPermission.objects.get_attr_constraints(user_obj, perm)
        if not attrs:
            return False

        # Permission to perform the requested action on the object depends on whether the specified object matches
        # the specified attributes. Note that this check is made against the *database* record representing the object,
        # not the instance itself.
        return model.objects.filter(attrs, pk=obj.pk).exists()


class RemoteUserBackend(RemoteUserBackend_):
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

        # Assign default permissions to the user
        permissions_list = []
        for permission_name in settings.REMOTE_AUTH_DEFAULT_PERMISSIONS:
            try:
                app_label, codename = permission_name.split('.')
                permissions_list.append(
                    Permission.objects.get(content_type__app_label=app_label, codename=codename)
                )
            except (ValueError, Permission.DoesNotExist):
                logging.error(
                    "Invalid permission name: '{permission_name}'. Permissions must be in the form "
                    "<app>.<action>_<model>. (Example: dcim.add_site)"
                )
        if permissions_list:
            user.user_permissions.add(*permissions_list)
            logger.debug(f"Assigned permissions to remotely-authenticated user {user}: {permissions_list}")

        return user
