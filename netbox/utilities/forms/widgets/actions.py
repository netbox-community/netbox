from django import forms

from utilities.permissions import get_action_model_map

__all__ = (
    'RegisteredActionsWidget',
)


class RegisteredActionsWidget(forms.CheckboxSelectMultiple):
    """
    Widget for registered model actions. Renders each action as an individual checkbox
    row styled identically to the CRUD checkboxes, with a data-models attribute so JS
    can enable/disable based on the currently selected object types.
    """
    template_name = 'widgets/registered_actions.html'

    def __init__(self, *args, model_actions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_actions = model_actions or {}
        self._action_model_keys = {}
        self._action_help_text = {}
        self._build_maps()

    def _build_maps(self):
        self._action_model_keys = get_action_model_map(self.model_actions)
        self._action_help_text = {}
        for actions in self.model_actions.values():
            for action in actions:
                if action.name not in self._action_help_text:
                    self._action_help_text[action.name] = action.help_text

    def set_model_actions(self, model_actions):
        self.model_actions = model_actions
        self._build_maps()

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        """
        Inject model_keys (comma-separated model keys that support this action) and
        help_text into the option dict. The template uses model_keys for the data-models
        attribute, which JS reads to enable/disable checkboxes based on selected object types.
        """
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        action_name = str(value)
        option['model_keys'] = ','.join(self._action_model_keys.get(action_name, set()))
        option['help_text'] = self._action_help_text.get(action_name, '')
        return option
