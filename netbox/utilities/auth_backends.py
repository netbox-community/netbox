import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as RemoteUserBackend_
from django.contrib.auth.models import Group, Permission


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


class RemoteUserBackend(ViewExemptModelBackend, RemoteUserBackend_):
    """
    Custom implementation of Django's RemoteUserBackend which provides configuration hooks for basic customization.
    """
    @property
    def create_unknown_user(self):
        return bool(settings.REMOTE_AUTH_AUTO_CREATE_USER)

    def configure_user(self, request, user):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')

        # Assign default groups to the user
        group_list = []
        for name in settings.REMOTE_AUTH_DEFAULT_GROUPS:
            try:
                group_list.append(Group.objects.get(name=name))
            except Group.DoesNotExist:
                logging.error("Could not assign group {name} to remotely-authenticated user {user}: Group not found")
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
