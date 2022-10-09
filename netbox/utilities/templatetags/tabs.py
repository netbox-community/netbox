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

            if attrs := tab.render(instance):
                viewname = f"{app_label}:{model_name}_{config['name']}"
                active_tab = context.get('tab')
                tabs.append({
                    'name': config['name'],
                    'url': reverse(viewname, args=[instance.pk]),
                    'label': attrs['label'],
                    'badge': attrs['badge'],
                    'is_active': active_tab and active_tab == tab,
                })

    return {
        'tabs': tabs,
    }
