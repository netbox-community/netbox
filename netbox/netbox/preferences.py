from django.conf import settings
from django.utils.translation import gettext as _

from netbox.registry import registry
from users.preferences import UserPreference
from utilities.paginator import EnhancedPaginator


def get_page_lengths():
    return [
        (v, str(v)) for v in EnhancedPaginator.default_page_lengths
    ]


PREFERENCES = {

    # User interface
    'ui.colormode': UserPreference(
        label=_('Color mode'),
        choices=(
            ('light', _('Light')),
            ('dark', _('Dark')),
        ),
        default='light',
    ),
    'locale.language': UserPreference(
        label=_('Language'),
        choices=(
            ('', _('Auto')),
            *settings.LANGUAGES,
        )
    ),
    'pagination.per_page': UserPreference(
        label=_('Page length'),
        choices=get_page_lengths(),
        description=_('The default number of objects to display per page'),
        coerce=lambda x: int(x)
    ),
    'pagination.placement': UserPreference(
        label=_('Paginator placement'),
        choices=(
            ('bottom', _('Bottom')),
            ('top', _('Top')),
            ('both', _('Both')),
        ),
        description=_('Where the paginator controls will be displayed relative to a table'),
        default='bottom'
    ),

    # Miscellaneous
    'data_format': UserPreference(
        label=_('Data format'),
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML'),
        ),
    ),

}

# Register plugin preferences
if registry['plugins']['preferences']:
    plugin_preferences = {}

    for plugin_name, preferences in registry['plugins']['preferences'].items():
        for name, userpreference in preferences.items():
            PREFERENCES[f'plugins.{plugin_name}.{name}'] = userpreference

    PREFERENCES.update(plugin_preferences)
