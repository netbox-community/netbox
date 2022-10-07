from django import template
from django.urls import reverse
from django.utils.module_loading import import_string

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
    for config in views:
        view = import_string(config['view']) if type(config['view']) is str else config['view']
        if tab := getattr(view, 'tab', None):
            if tab.permission and not user.has_perm(tab.permission):
                continue

            # Determine the value of the tab's badge (if any)
            if tab.badge and callable(tab.badge):
                badge_value = tab.badge(instance)
            else:
                badge_value = tab.badge

            if not tab.always_display and not badge_value:
                continue

            tabs.append({
                'name': config['name'],
                'url': reverse(f"{app_label}:{model_name}_{config['name']}", args=[instance.pk]),
                'label': tab.label,
                'badge_value': badge_value,
                'is_active': context.get('active_tab') == config['name'],
            })

    return {
        'tabs': tabs,
    }
