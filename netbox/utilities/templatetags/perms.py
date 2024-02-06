from django import template

from utilities.permissions import get_permission_for_model

__all__ = (
    'can_add',
    'can_change',
    'can_delete',
    'can_sync',
    'can_view',
)

register = template.Library()


def _check_permission(user, instance, action):
    permission = get_permission_for_model(instance, action)
    return user.has_perm(perm=permission, obj=instance)


@register.filter()
def can_view(user, instance):
    return _check_permission(user, instance, 'view')


@register.filter()
def can_add(user, model):
    permission = get_permission_for_model(model, 'add')
    return user.has_perm(perm=permission)


@register.filter()
def can_change(user, instance):
    return _check_permission(user, instance, 'change')


@register.filter()
def can_delete(user, instance):
    return _check_permission(user, instance, 'delete')


@register.filter()
def can_sync(user, instance):
    return _check_permission(user, instance, 'sync')
