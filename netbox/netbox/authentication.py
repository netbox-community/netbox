import logging
from collections import defaultdict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend as _RemoteUserBackend
from django.contrib.auth.models import Group, AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from users.models import ObjectPermission
from utilities.permissions import permission_is_exempt, resolve_permission, resolve_permission_ct

UserModel = get_user_model()


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

    def configure_groups(self, user, remote_groups):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')

        # Assign default groups to the user
        group_list = []
        for name in remote_groups:
            try:
                group_list.append(Group.objects.get(name=name))
            except Group.DoesNotExist:
                logging.error(
                    f"Could not assign group {name} to remotely-authenticated user {user}: Group not found")
        if group_list:
            user.groups.set(group_list)
            logger.debug(
                f"Assigned groups to remotely-authenticated user {user}: {group_list}")
        else:
            user.groups.clear()
            logger.debug(f"Stripping user {user} from Groups")
        user.is_superuser = self._is_superuser(user)
        logger.debug(f"User {user} is Superuser: {user.is_superuser}")
        logger.debug(
            f"User {user} should be Superuser: {self._is_superuser(user)}")

        user.is_staff = self._is_staff(user)
        logger.debug(f"User {user} is Staff: {user.is_staff}")
        logger.debug(f"User {user} should be Staff: {self._is_staff(user)}")
        user.save()
        return user

    def authenticate(self, request, remote_user, remote_groups=None):
        """
        The username passed as ``remote_user`` is considered trusted. Return
        the ``User`` object with the given username. Create a new ``User``
        object if ``create_unknown_user`` is ``True``.
        Return None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')
        logger.debug(
            f"trying to authenticate {remote_user} with groups {remote_groups}")
        if not remote_user:
            return
        user = None
        username = self.clean_username(remote_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = UserModel._default_manager.get_or_create(**{
                UserModel.USERNAME_FIELD: username
            })
            if created:
                user = self.configure_user(request, user)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                pass
        if self.user_can_authenticate(user):
            if settings.REMOTE_AUTH_GROUP_SYNC_ENABLED:
                if user is not None and not isinstance(user, AnonymousUser):
                    return self.configure_groups(user, remote_groups)
            else:
                return user
        else:
            return None

    def _is_superuser(self, user):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')
        superuser_groups = settings.REMOTE_AUTH_SUPERUSER_GROUPS
        logger.debug(f"Superuser Groups: {superuser_groups}")
        superusers = settings.REMOTE_AUTH_SUPERUSERS
        logger.debug(f"Superuser Users: {superusers}")
        user_groups = set()
        for g in user.groups.all():
            user_groups.add(g.name)
        logger.debug(f"User {user.username} is in Groups:{user_groups}")

        result = user.username in superusers or (
            set(user_groups) & set(superuser_groups))
        logger.debug(f"User {user.username} in Superuser Users :{result}")
        return bool(result)

    def _is_staff(self, user):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')
        staff_groups = settings.REMOTE_AUTH_STAFF_GROUPS
        logger.debug(f"Superuser Groups: {staff_groups}")
        staff_users = settings.REMOTE_AUTH_STAFF_USERS
        logger.debug(f"Staff Users :{staff_users}")
        user_groups = set()
        for g in user.groups.all():
            user_groups.add(g.name)
        logger.debug(f"User {user.username} is in Groups:{user_groups}")
        result = user.username in staff_users or (
            set(user_groups) & set(staff_groups))
        logger.debug(f"User {user.username} in Staff Users :{result}")
        return bool(result)

    def configure_user(self, request, user):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')
        if not settings.REMOTE_AUTH_GROUP_SYNC_ENABLED:
            # Assign default groups to the user
            group_list = []
            for name in settings.REMOTE_AUTH_DEFAULT_GROUPS:
                try:
                    group_list.append(Group.objects.get(name=name))
                except Group.DoesNotExist:
                    logging.error(
                        f"Could not assign group {name} to remotely-authenticated user {user}: Group not found")
            if group_list:
                user.groups.add(*group_list)
                logger.debug(
                    f"Assigned groups to remotely-authenticated user {user}: {group_list}")

            # Assign default object permissions to the user
            permissions_list = []
            for permission_name, constraints in settings.REMOTE_AUTH_DEFAULT_PERMISSIONS.items():
                try:
                    object_type, action = resolve_permission_ct(
                        permission_name)
                    # TODO: Merge multiple actions into a single ObjectPermission per content type
                    obj_perm = ObjectPermission(
                        actions=[action], constraints=constraints)
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
                logger.debug(
                    f"Assigned permissions to remotely-authenticated user {user}: {permissions_list}")
        else:
            logger.debug(
                f"Skipped initial assignment of permissions and groups to remotely-authenticated user {user} as Group sync is enabled")

        return user

    def has_perm(self, user_obj, perm, obj=None):
        return False


# Create a new instance of django-auth-ldap's LDAPBackend with our own ObjectPermissions
try:
    from django_auth_ldap.backend import LDAPBackend as LDAPBackend_

    class NBLDAPBackend(ObjectPermissionMixin, LDAPBackend_):
        def get_permission_filter(self, user_obj):
            permission_filter = super().get_permission_filter(user_obj)
            if (self.settings.FIND_GROUP_PERMS and
                    hasattr(user_obj, "ldap_user") and
                    hasattr(user_obj.ldap_user, "group_names")):
                permission_filter = permission_filter | Q(groups__name__in=user_obj.ldap_user.group_names)
            return permission_filter
except ModuleNotFoundError:
    pass


class LDAPBackend:

    def __new__(cls, *args, **kwargs):
        try:
            from django_auth_ldap.backend import LDAPSettings
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
