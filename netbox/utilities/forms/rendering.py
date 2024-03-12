__all__ = (
    'InlineFields',
)


class InlineFields:

    def __init__(self, *field_names, label=None):
        self.field_names = field_names
        self.label = label
