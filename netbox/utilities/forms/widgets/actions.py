from django import forms

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
        context['widget']['model_actions'] = self.model_actions
        context['widget']['value'] = value or []
        return context
