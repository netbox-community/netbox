import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as _RemoteUserBackend
from django.contrib.auth.models import Group
from django.db.models import Q

from users.models import ObjectPermission
from utilities.permissions import permission_is_exempt, resolve_permission, resolve_permission_ct


class ObjectPermissionBackend(ModelBackend):

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return dict()
        if not hasattr(user_obj, '_object_perm_cache'):
            user_obj._object_perm_cache = self.get_object_permissions(user_obj)
        return user_obj._object_perm_cache

    def get_object_permissions(self, user_obj):
        """
        Return all permissions granted to the user by an ObjectPermission.
        """
        # Retrieve all assigned ObjectPermissions
        object_permissions = ObjectPermission.objects.filter(
            Q(users=user_obj) |
            Q(groups__user=user_obj)
        ).prefetch_related('content_types')

        # Create a dictionary mapping permissions to their attributes
        perms = dict()
        for obj_perm in object_permissions:
            for content_type in obj_perm.content_types.all():
                for action in obj_perm.actions:
                    perm_name = f"{content_type.app_label}.{action}_{content_type.model}"
                    if perm_name in perms:
                        perms[perm_name].append(obj_perm.attrs)
                    else:
                        perms[perm_name] = [obj_perm.attrs]

        return perms

    def has_perm(self, user_obj, perm, obj=None):
        app_label, action, model_name = resolve_permission(perm)

        # Superusers implicitly have all permissions
        if user_obj.is_active and user_obj.is_superuser:
            return True

        # Permission is exempt from enforcement (i.e. listed in EXEMPT_VIEW_PERMISSIONS)
        if permission_is_exempt(perm):
            return True

        # Handle inactive/anonymous users
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        # If no applicable ObjectPermissions have been created for this user/permission, deny permission
        if perm not in self.get_all_permissions(user_obj):
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
        obj_perm_attrs = self.get_all_permissions(user_obj)[perm]
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
        for permission_name, attrs in settings.REMOTE_AUTH_DEFAULT_PERMISSIONS.items():
            try:
                content_type, action = resolve_permission_ct(permission_name)
                # TODO: Merge multiple actions into a single ObjectPermission per content type
                obj_perm = ObjectPermission(actions=[action], attrs=attrs)
                obj_perm.save()
                obj_perm.users.add(user)
                obj_perm.content_types.add(content_type)
                permissions_list.append(permission_name)
            except ValueError:
                logging.error(
                    f"Invalid permission name: '{permission_name}'. Permissions must be in the form "
                    "<app>.<action>_<model>. (Example: dcim.add_site)"
                )
        if permissions_list:
            logger.debug(f"Assigned permissions to remotely-authenticated user {user}: {permissions_list}")

        return user

    def has_perm(self, user_obj, perm, obj=None):
        return False
