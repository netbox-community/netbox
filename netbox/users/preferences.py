class UserPreference:
    """
    Represents a configurable user preference.
    """
    def __init__(self, label, choices, default=None, description='', coerce=lambda x: x, experimental=False):
        self.label = label
        self.choices = choices
        self.default = default if default is not None else choices[0]
        self.description = description
        self.coerce = coerce
        self.experimental = experimental
