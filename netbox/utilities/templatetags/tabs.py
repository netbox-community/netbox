from django import template
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from extras.registry import registry

register = template.Library()


#
# Object detail view tabs
#

@register.inclusion_tag('tabs/model_view_tabs.html', takes_context=True)
def model_view_tabs(context, instance):
    app_label = instance._meta.app_label
    model_name = instance._meta.model_name
    user = context['request'].user
    tabs = []

    # Retrieve registered views for this model
    try:
        views = registry['views'][app_label][model_name]
    except KeyError:
        # No views have been registered for this model
        views = []

    # Compile a list of tabs to be displayed in the UI
    for view in views:
        if view['tab_label'] and (not view['tab_permission'] or user.has_perm(view['tab_permission'])):

            # Determine the value of the tab's badge (if any)
            if view['tab_badge'] and callable(view['tab_badge']):
                badge_value = view['tab_badge'](instance)
            elif view['tab_badge']:
                badge_value = view['tab_badge']
            else:
                badge_value = None

            tabs.append({
                'name': view['name'],
                'url': reverse(f"{app_label}:{model_name}_{view['name']}", args=[instance.pk]),
                'label': view['tab_label'],
                'badge_value': badge_value,
                'is_active': context.get('active_tab') == view['name'],
            })

    return {
        'tabs': tabs,
    }
