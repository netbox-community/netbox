from django.conf import settings
from django.db.models import Q
from social_core.storage import NO_ASCII_REGEX, NO_SPECIAL_REGEX

__all__ = (
    'clean_username',
    'get_current_pepper',
    'user_may_grant_token',
)


def user_may_grant_token(requesting_user, token_user):
    """
    Return True if *requesting_user* has permission to create a token for *token_user*,
    respecting ObjectPermission constraints on the users.grant_token permission.

    ``has_perm('users.grant_token', obj=None)`` always short-circuits to True when the
    permission is present in the cache (obj=None bypasses constraint evaluation in
    ObjectPermissionMixin.has_perm).  Since the new token does not yet exist in the
    database we cannot pass an existing Token as obj.  Instead we extract the raw
    constraint list, remap Token-field paths to User-field paths, and evaluate them
    directly against the target User record — the only variable in a new token creation.

    Field remapping rules:
      ``user__<field>`` → ``<field>``  (FK traversal into User)
      ``user``          → ``pk``       (Token.user FK becomes User.pk)

    Constraints referencing other Token fields cannot be evaluated for an unsaved
    token; the function returns False (deny) for those.
    """
    from users.models import User

    # Mirrors ObjectPermissionMixin.has_perm: superusers implicitly have all permissions.
    if requesting_user.is_active and requesting_user.is_superuser:
        return True

    perm = 'users.grant_token'

    # get_all_permissions() populates _object_perm_cache as a side effect.
    # Guard against missing cache key in case a non-standard backend is in use.
    if perm not in requesting_user.get_all_permissions():
        return False

    constraints = getattr(requesting_user, '_object_perm_cache', {}).get(perm, [])

    # An empty/null constraint means "no restriction" — allow any target.
    if any(not c for c in constraints):
        return True

    # Substitute the $user token so {"user": "$user"} resolves to the requesting user.
    resolved_user_id = requesting_user.pk

    q = Q()
    for constraint in constraints:
        user_constraint = {}
        for key, raw_val in constraint.items():
            val = resolved_user_id if raw_val == '$user' else raw_val
            if key == 'user':
                user_constraint['pk'] = val
            elif key.startswith('user__'):
                user_constraint[key.removeprefix('user__')] = val
            else:
                # Non-user Token field — cannot evaluate for a new (unsaved) token.
                # Fail closed.
                return False
        q |= Q(**user_constraint)

    return User.objects.filter(q, pk=token_user.pk).exists()


def clean_username(value):
    """Clean username removing any unsupported character"""
    value = NO_ASCII_REGEX.sub('', value)
    value = NO_SPECIAL_REGEX.sub('', value)
    value = value.replace(':', '')
    return value


def get_current_pepper():
    """
    Return the ID and value of the newest (highest ID) cryptographic pepper.
    """
    if not settings.API_TOKEN_PEPPERS:
        raise ValueError("API_TOKEN_PEPPERS is not defined")
    newest_id = sorted(settings.API_TOKEN_PEPPERS.keys())[-1]
    return newest_id, settings.API_TOKEN_PEPPERS[newest_id]
