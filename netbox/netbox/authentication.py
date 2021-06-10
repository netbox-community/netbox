import logging
from collections import defaultdict

from django.conf import settings
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as _RemoteUserBackend
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from users.models import ObjectPermission
from utilities.permissions import permission_is_exempt, resolve_permission, resolve_permission_ct


class ObjectPermissionMixin():

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return dict()
        if not hasattr(user_obj, '_object_perm_cache'):
            user_obj._object_perm_cache = self.get_object_permissions(user_obj)
        return user_obj._object_perm_cache

    def get_permission_filter(self, user_obj):
        return Q(users=user_obj) | Q(groups__user=user_obj)

    def get_object_permissions(self, user_obj):
        """
        Return all permissions granted to the user by an ObjectPermission.
        """
        # Retrieve all assigned and enabled ObjectPermissions
        object_permissions = ObjectPermission.objects.filter(
            self.get_permission_filter(user_obj),
            enabled=True
        ).prefetch_related('object_types')

        # Create a dictionary mapping permissions to their constraints
        perms = defaultdict(list)
        for obj_perm in object_permissions:
            for object_type in obj_perm.object_types.all():
                for action in obj_perm.actions:
                    perm_name = f"{object_type.app_label}.{action}_{object_type.model}"
                    perms[perm_name].extend(obj_perm.list_constraints())

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
        obj_perm_constraints = self.get_all_permissions(user_obj)[perm]
        constraints = Q()
        for perm_constraints in obj_perm_constraints:
            if perm_constraints:
                constraints |= Q(**perm_constraints)
            else:
                # Found ObjectPermission with null constraints; allow model-level access
                constraints = Q()
                break

        # Permission to perform the requested action on the object depends on whether the specified object matches
        # the specified constraints. Note that this check is made against the *database* record representing the object,
        # not the instance itself.
        return model.objects.filter(constraints, pk=obj.pk).exists()


class ObjectPermissionBackend(ObjectPermissionMixin, ModelBackend):
    pass


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
        for permission_name, constraints in settings.REMOTE_AUTH_DEFAULT_PERMISSIONS.items():
            try:
                object_type, action = resolve_permission_ct(permission_name)
                # TODO: Merge multiple actions into a single ObjectPermission per content type
                obj_perm = ObjectPermission(actions=[action], constraints=constraints)
                obj_perm.save()
                obj_perm.users.add(user)
                obj_perm.object_types.add(object_type)
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


class LDAPBackend:

    def __new__(cls, *args, **kwargs):
        try:
            from django_auth_ldap.backend import LDAPBackend as LDAPBackend_, LDAPSettings
            import ldap
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'django_auth_ldap':
                raise ImproperlyConfigured(
                    "LDAP authentication has been configured, but django-auth-ldap is not installed."
                )
            raise e

        try:
            from netbox import ldap_config
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'ldap_config':
                raise ImproperlyConfigured(
                    "LDAP configuration file not found: Check that ldap_config.py has been created alongside "
                    "configuration.py."
                )
            raise e

        try:
            getattr(ldap_config, 'AUTH_LDAP_SERVER_URI')
        except AttributeError:
            raise ImproperlyConfigured(
                "Required parameter AUTH_LDAP_SERVER_URI is missing from ldap_config.py."
            )

        # Create a new instance of django-auth-ldap's LDAPBackend with our own ObjectPermissions
        class NBLDAPBackend(ObjectPermissionMixin, LDAPBackend_):
            def get_permission_filter(self, user_obj):
                permission_filter = Q(users=user_obj) | Q(groups__user=user_obj)
                if self.settings.FIND_GROUP_PERMS:
                    permission_filter = permission_filter | Q(groups__name__in=user_obj.ldap_user.group_names)
                return permission_filter

        obj = NBLDAPBackend()

        # Read LDAP configuration parameters from ldap_config.py instead of settings.py
        settings = LDAPSettings()
        for param in dir(ldap_config):
            if param.startswith(settings._prefix):
                setattr(settings, param[10:], getattr(ldap_config, param))
        obj.settings = settings

        # Optionally disable strict certificate checking
        if getattr(ldap_config, 'LDAP_IGNORE_CERT_ERRORS', False):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        return obj
