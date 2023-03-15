from django import template
from django.urls import NoReverseMatch, reverse
from utilities.utils import get_viewname


register = template.Library()


def _check_permission(user, instance, action):
    return user.has_perm(
        perm=f'{instance._meta.app_label}.{action}_{instance._meta.model_name}',
        obj=instance
    )


def _check_view_exists(instance):
    try:
        viewname = get_viewname(instance, 'suggest')
        reverse(viewname, kwargs={'pk': instance.pk})
        return True
    except NoReverseMatch:
        return False


@register.filter()
def can_view(user, instance):
    return _check_permission(user, instance, 'view')


@register.filter()
def can_add(user, instance):
    return _check_permission(user, instance, 'add')


@register.filter()
def can_change(user, instance):
    return _check_permission(user, instance, 'change')


@register.filter()
def can_suggest(user, instance):
    # TODO: View check is temporary until we impl. this everywhere.
    return _check_view_exists(instance) and _check_permission(user, instance, 'suggest')


@register.filter()
def is_owner(user, instance):
    return instance.owner.id == user.id


@register.filter()
def is_reviewer(user, instance):
    return instance.reviewer.id == user.id


@register.filter()
def can_delete(user, instance):
    return _check_permission(user, instance, 'delete')
