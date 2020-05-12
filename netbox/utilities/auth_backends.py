import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as RemoteUserBackend_
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from users.models import ObjectPermission


class ViewExemptModelBackend(ModelBackend):
    """
    Custom implementation of Django's stock ModelBackend which allows for the exemption of arbitrary models from view
    permission enforcement.
    """
    def has_perm(self, user_obj, perm, obj=None):

        # If this is a view permission, check whether the model has been exempted from enforcement
        try:
            app, codename = perm.split('.')
            action, model = codename.split('_')
            if action == 'view':
                if (
                    # All models are exempt from view permission enforcement
                    '*' in settings.EXEMPT_VIEW_PERMISSIONS
                ) or (
                    # This specific model is exempt from view permission enforcement
                    '.'.join((app, model)) in settings.EXEMPT_VIEW_PERMISSIONS
                ):
                    return True
        except ValueError:
            pass

        # Fall back to ModelBackend's default behavior, with one exception: Set obj to None. Model-level permissions
        # override object-level permissions, so if a user has the model-level permission we can ignore any specified
        # object. (By default, ModelBackend will return False if an object is specified.)
        return super().has_perm(user_obj, perm, None)


class ObjectPermissionBackend(ModelBackend):
    """
    Evaluates permission of a user to access or modify a specific object based on the assignment of ObjectPermissions
    either to the user directly or to a group of which the user is a member. Model-level permissions supersede this
    check: For example, if a user has the dcim.view_site model-level permission assigned, the ViewExemptModelBackend
    will grant permission before this backend is evaluated for permission to view a specific site.
    """
    def _get_all_permissions(self, user_obj):
        """
        Retrieve all ObjectPermissions assigned to this User (either directly or through a Group) and return the model-
        level equivalent codenames.
        """
        perm_names = set()
        for obj_perm in ObjectPermission.objects.filter(
            Q(users=user_obj) | Q(groups__user=user_obj)
        ).prefetch_related('model'):
            for action in ['view', 'add', 'change', 'delete']:
                if getattr(obj_perm, f"can_{action}"):
                    perm_names.add(f"{obj_perm.model.app_label}.{action}_{obj_perm.model.model}")
        return perm_names

    def get_all_permissions(self, user_obj, obj=None):
        """
        Get all model-level permissions assigned by this backend. Permissions are cached on the User instance.
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if not hasattr(user_obj, '_obj_perm_cache'):
            user_obj._obj_perm_cache = self._get_all_permissions(user_obj)
        return user_obj._obj_perm_cache

    def has_perm(self, user_obj, perm, obj=None):

        # If no object is specified, look for any matching ObjectPermissions. If one or more are found, this indicates
        # that the user has permission to perform the requested action on at least *some* objects, but not necessarily
        # on all of them.
        if obj is None:
            return perm in self.get_all_permissions(user_obj)

        attrs = ObjectPermission.objects.get_attr_constraints(user_obj, perm)

        # No ObjectPermissions found for this combination of user, model, and action
        if not attrs:
            return

        model = obj._meta.model

        # Check that the requested permission applies to the specified object
        app_label, codename = perm.split('.')
        action, model_name = codename.split('_')
        if model._meta.label_lower != '.'.join((app_label, model_name)):
            raise ValueError(f"Invalid permission {perm} for model {model}")

        # Attempt to retrieve the model from the database using the attributes defined in the
        # ObjectPermission. If we have a match, assert that the user has permission.
        if model.objects.filter(pk=obj.pk, **attrs).exists():
            return True


class RemoteUserBackend(ViewExemptModelBackend, RemoteUserBackend_):
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
