from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet
from utilities.constants import CSV_DELIMITERS

__all__ = (
    'ButtonColorChoices',
    'ColorChoices',
    'CSVDelimiterChoices',
    'ImportFormatChoices',
    'ImportMethodChoices',
)


#
# Generic color choices
#

class ColorChoices(ChoiceSet):
    COLOR_DARK_RED = 'aa1409'
    COLOR_RED = 'f44336'
    COLOR_PINK = 'e91e63'
    COLOR_ROSE = 'ffe4e1'
    COLOR_FUCHSIA = 'ff66ff'
    COLOR_PURPLE = '9c27b0'
    COLOR_DARK_PURPLE = '673ab7'
    COLOR_INDIGO = '3f51b5'
    COLOR_BLUE = '2196f3'
    COLOR_LIGHT_BLUE = '03a9f4'
    COLOR_CYAN = '00bcd4'
    COLOR_TEAL = '009688'
    COLOR_AQUA = '00ffff'
    COLOR_DARK_GREEN = '2f6a31'
    COLOR_GREEN = '4caf50'
    COLOR_LIGHT_GREEN = '8bc34a'
    COLOR_LIME = 'cddc39'
    COLOR_YELLOW = 'ffeb3b'
    COLOR_AMBER = 'ffc107'
    COLOR_ORANGE = 'ff9800'
    COLOR_DARK_ORANGE = 'ff5722'
    COLOR_BROWN = '795548'
    COLOR_LIGHT_GREY = 'c0c0c0'
    COLOR_GREY = '9e9e9e'
    COLOR_DARK_GREY = '607d8b'
    COLOR_BLACK = '111111'
    COLOR_WHITE = 'ffffff'

    CHOICES = (
        (COLOR_DARK_RED, _('Dark Red')),
        (COLOR_RED, _('Red')),
        (COLOR_PINK, _('Pink')),
        (COLOR_ROSE, _('Rose')),
        (COLOR_FUCHSIA, _('Fuchsia')),
        (COLOR_PURPLE, _('Purple')),
        (COLOR_DARK_PURPLE, _('Dark Purple')),
        (COLOR_INDIGO, _('Indigo')),
        (COLOR_BLUE, _('Blue')),
        (COLOR_LIGHT_BLUE, _('Light Blue')),
        (COLOR_CYAN, _('Cyan')),
        (COLOR_TEAL, _('Teal')),
        (COLOR_AQUA, _('Aqua')),
        (COLOR_DARK_GREEN, _('Dark Green')),
        (COLOR_GREEN, _('Green')),
        (COLOR_LIGHT_GREEN, _('Light Green')),
        (COLOR_LIME, _('Lime')),
        (COLOR_YELLOW, _('Yellow')),
        (COLOR_AMBER, _('Amber')),
        (COLOR_ORANGE, _('Orange')),
        (COLOR_DARK_ORANGE, _('Dark Orange')),
        (COLOR_BROWN, _('Brown')),
        (COLOR_LIGHT_GREY, _('Light Grey')),
        (COLOR_GREY, _('Grey')),
        (COLOR_DARK_GREY, _('Dark Grey')),
        (COLOR_BLACK, _('Black')),
        (COLOR_WHITE, _('White')),
    )


#
# Button color choices
#

class ButtonColorChoices(ChoiceSet):
    """
    Map standard button color choices to Bootstrap 3 button classes
    """
    DEFAULT = 'outline-dark'
    BLUE = 'blue'
    INDIGO = 'indigo'
    PURPLE = 'purple'
    PINK = 'pink'
    RED = 'red'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    GREEN = 'green'
    TEAL = 'teal'
    CYAN = 'cyan'
    GRAY = 'gray'
    GREY = 'gray'  # Backward compatability for <3.2
    BLACK = 'black'
    WHITE = 'white'

    CHOICES = (
        (DEFAULT, _('Default')),
        (BLUE, _('Blue')),
        (INDIGO, _('Indigo')),
        (PURPLE, _('Purple')),
        (PINK, _('Pink')),
        (RED, _('Red')),
        (ORANGE, _('Orange')),
        (YELLOW, _('Yellow')),
        (GREEN, _('Green')),
        (TEAL, _('Teal')),
        (CYAN, _('Cyan')),
        (GRAY, _('Gray')),
        (BLACK, _('Black')),
        (WHITE, _('White')),
    )


#
# Import Choices
#

class ImportMethodChoices(ChoiceSet):
    DIRECT = 'direct'
    UPLOAD = 'upload'
    DATA_FILE = 'datafile'

    CHOICES = [
        (DIRECT, _('Direct')),
        (UPLOAD, _('Upload')),
        (DATA_FILE, _('Data file')),
    ]


class ImportFormatChoices(ChoiceSet):
    AUTO = 'auto'
    CSV = 'csv'
    JSON = 'json'
    YAML = 'yaml'

    CHOICES = [
        (AUTO, _('Auto-detect')),
        (CSV, 'CSV'),
        (JSON, 'JSON'),
        (YAML, 'YAML'),
    ]


class CSVDelimiterChoices(ChoiceSet):
    AUTO = 'auto'
    COMMA = CSV_DELIMITERS['comma']
    SEMICOLON = CSV_DELIMITERS['semicolon']
    TAB = CSV_DELIMITERS['tab']

    CHOICES = [
        (AUTO, _('Auto-detect')),
        (COMMA, _('Comma')),
        (SEMICOLON, _('Semicolon')),
        (TAB, _('Tab')),
    ]
