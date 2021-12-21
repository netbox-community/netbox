from utilities.paginator import EnhancedPaginator


def get_page_lengths():
    return [
        (v, str(v)) for v in EnhancedPaginator.default_page_lengths
    ]


class UserPreference:

    def __init__(self, label, choices, default=None, description='', coerce=lambda x: x):
        self.label = label
        self.choices = choices
        self.default = default if default is not None else choices[0]
        self.description = description
        self.coerce = coerce


PREFERENCES = {

    # User interface
    'ui.colormode': UserPreference(
        label='Color mode',
        choices=(
            ('light', 'Light'),
            ('dark', 'Dark'),
        ),
        default='light',
    ),
    'pagination.per_page': UserPreference(
        label='Page length',
        choices=get_page_lengths(),
        coerce=lambda x: int(x)
    ),

    # Miscellaneous
    'data_format': UserPreference(
        label='Data format',
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML'),
        ),
    ),

}
