from django import forms
from django.apps import apps

__all__ = (
    'RegisteredActionsWidget',
)


class RegisteredActionsWidget(forms.CheckboxSelectMultiple):
    """
    Widget rendering checkboxes for registered model actions.
    Groups actions by model with data attributes for JS show/hide.
    """
    template_name = 'widgets/registered_actions.html'

    def __init__(self, *args, model_actions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_actions = model_actions or {}

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        model_actions_with_labels = {}
        for model_key, actions in self.model_actions.items():
            app_label, model_name = model_key.split('.')
            try:
                model = apps.get_model(app_label, model_name)
                app_config = apps.get_app_config(app_label)
                label = f"{app_config.verbose_name} | {model._meta.verbose_name.title()}"
            except LookupError:
                label = model_key
            model_actions_with_labels[model_key] = {
                'label': label,
                'actions': actions,
            }

        context['widget']['model_actions'] = model_actions_with_labels
        context['widget']['value'] = value or []
        return context
