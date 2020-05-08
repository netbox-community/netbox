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
                    '{}.{}'.format(app, model) in settings.EXEMPT_VIEW_PERMISSIONS
                ):
                    return True
        except ValueError:
            pass

        return super().has_perm(user_obj, perm, obj)


class ObjectPermissionBackend(ModelBackend):
    """
    Evaluates permission of a user to access or modify a specific object based on the assignment of ObjectPermissions
    either to the user directly or to a group of which the user is a member. Model-level permissions supersede this
    check: For example, if a user has the dcim.view_site model-level permission assigned, the ViewExemptModelBackend
    will grant permission before this backend is evaluated for permission to view a specific site.
    """
    def has_perm(self, user_obj, perm, obj=None):

        # This backend only checks for permissions on specific objects
        if obj is None:
            return

        app, codename = perm.split('.')
        action, model_name = codename.split('_')
        model = obj._meta.model

        # Check that the requested permission applies to the specified object
        if model._meta.model_name != model_name:
            raise ValueError(f"Invalid permission {perm} for model {model}")

        # Retrieve user's permissions for this model
        # This can probably be cached
        obj_permissions = ObjectPermission.objects.filter(
            Q(users=user_obj) | Q(groups__user=user_obj),
            model=ContentType.objects.get_for_model(obj),
            **{f'can_{action}': True}
        )

        for perm in obj_permissions:

            # Attempt to retrieve the model from the database using the
            # attributes defined in the ObjectPermission. If we have a
            # match, assert that the user has permission.
            if model.objects.filter(pk=obj.pk, **perm.attrs).exists():
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
