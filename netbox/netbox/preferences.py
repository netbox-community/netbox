from django.conf import settings
from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from users.preferences import UserPreference
from utilities.constants import CSV_DELIMITERS
from utilities.paginator import EnhancedPaginator


def get_page_lengths():
    return [
        (v, str(v)) for v in EnhancedPaginator.default_page_lengths
    ]


def get_csv_delimiters():
    choices = []
    for k, v in CSV_DELIMITERS.items():
        label = _(k.title())
        if v.strip():
            label = f'{label} ({v})'
        choices.append((k, label))
    return choices


PREFERENCES = {

    # User interface
    'ui.htmx_navigation': UserPreference(
        label=_('HTMX Navigation'),
        choices=(
            ('', _('Disabled')),
            ('true', _('Enabled')),
        ),
        description=_('Enable dynamic UI navigation'),
        default=False,
        warning=_('Experimental feature')
    ),
    'locale.language': UserPreference(
        label=_('Language'),
        choices=(
            ('', _('Auto')),
            *settings.LANGUAGES,
        ),
        description=_('Forces UI translation to the specified language'),
        warning=(
            _("Support for translation has been disabled locally")
            if not settings.TRANSLATION_ENABLED
            else ''
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
        default='bottom',
        description=_('Where the paginator controls will be displayed relative to a table')
    ),
    'ui.tables.striping': UserPreference(
        label=_('Striped table rows'),
        choices=(
            ('', _('Disabled')),
            ('true', _('Enabled')),
        ),
        description=_('Render table rows with alternating colors to increase readability'),
    ),

    # Miscellaneous
    'data_format': UserPreference(
        label=_('Data format'),
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML'),
        ),
        description=_('The preferred syntax for displaying generic data within the UI')
    ),
    'csv_delimiter': UserPreference(
        label=_('CSV delimiter'),
        choices=get_csv_delimiters(),
        default='comma',
        description=_('The character used to separate fields in CSV data')
    ),

}

# Register plugin preferences
if registry['plugins']['preferences']:
    plugin_preferences = {}

    for plugin_name, preferences in registry['plugins']['preferences'].items():
        for name, userpreference in preferences.items():
            PREFERENCES[f'plugins.{plugin_name}.{name}'] = userpreference

    PREFERENCES.update(plugin_preferences)
