from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet
from utilities.constants import CSV_DELIMITERS

__all__ = (
    'ButtonColorChoices',
    'CSVDelimiterChoices',
    'ColorChoices',
    'DiameterUnitChoices',
    'DistanceUnitChoices',
    'FlowRateUnitChoices',
    'ImportFormatChoices',
    'ImportMethodChoices',
    'WeightUnitChoices',
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
        Choice(COLOR_DARK_RED, _('Dark Red')),
        Choice(COLOR_RED, _('Red')),
        Choice(COLOR_PINK, _('Pink')),
        Choice(COLOR_ROSE, _('Rose')),
        Choice(COLOR_FUCHSIA, _('Fuchsia')),
        Choice(COLOR_PURPLE, _('Purple')),
        Choice(COLOR_DARK_PURPLE, _('Dark Purple')),
        Choice(COLOR_INDIGO, _('Indigo')),
        Choice(COLOR_BLUE, _('Blue')),
        Choice(COLOR_LIGHT_BLUE, _('Light Blue')),
        Choice(COLOR_CYAN, _('Cyan')),
        Choice(COLOR_TEAL, _('Teal')),
        Choice(COLOR_AQUA, _('Aqua')),
        Choice(COLOR_DARK_GREEN, _('Dark Green')),
        Choice(COLOR_GREEN, _('Green')),
        Choice(COLOR_LIGHT_GREEN, _('Light Green')),
        Choice(COLOR_LIME, _('Lime')),
        Choice(COLOR_YELLOW, _('Yellow')),
        Choice(COLOR_AMBER, _('Amber')),
        Choice(COLOR_ORANGE, _('Orange')),
        Choice(COLOR_DARK_ORANGE, _('Dark Orange')),
        Choice(COLOR_BROWN, _('Brown')),
        Choice(COLOR_LIGHT_GREY, _('Light Grey')),
        Choice(COLOR_GREY, _('Grey')),
        Choice(COLOR_DARK_GREY, _('Dark Grey')),
        Choice(COLOR_BLACK, _('Black')),
        Choice(COLOR_WHITE, _('White')),
    )


#
# Button color choices
#

class ButtonColorChoices(ChoiceSet):
    DEFAULT = 'default'
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
        Choice(DEFAULT, _('Default')),
        Choice(BLUE, _('Blue')),
        Choice(INDIGO, _('Indigo')),
        Choice(PURPLE, _('Purple')),
        Choice(PINK, _('Pink')),
        Choice(RED, _('Red')),
        Choice(ORANGE, _('Orange')),
        Choice(YELLOW, _('Yellow')),
        Choice(GREEN, _('Green')),
        Choice(TEAL, _('Teal')),
        Choice(CYAN, _('Cyan')),
        Choice(GRAY, _('Gray')),
        Choice(BLACK, _('Black')),
        Choice(WHITE, _('White')),
    )


#
# Import Choices
#

class ImportMethodChoices(ChoiceSet):
    DIRECT = 'direct'
    UPLOAD = 'upload'
    DATA_FILE = 'datafile'

    CHOICES = [
        Choice(DIRECT, _('Direct'), description=_('Enter data directly into a form field')),
        Choice(UPLOAD, _('Upload'), description=_('Upload a file from the local filesystem')),
        Choice(DATA_FILE, _('Data file'), description=_('Reference a file from a synced data source')),
    ]


class ImportFormatChoices(ChoiceSet):
    AUTO = 'auto'
    CSV = 'csv'
    JSON = 'json'
    YAML = 'yaml'

    CHOICES = [
        Choice(AUTO, _('Auto-detect')),
        Choice(CSV, 'CSV'),
        Choice(JSON, 'JSON'),
        Choice(YAML, 'YAML'),
    ]


class CSVDelimiterChoices(ChoiceSet):
    AUTO = 'auto'
    COMMA = CSV_DELIMITERS['comma']
    SEMICOLON = CSV_DELIMITERS['semicolon']
    PIPE = CSV_DELIMITERS['pipe']
    TAB = CSV_DELIMITERS['tab']

    CHOICES = [
        Choice(AUTO, _('Auto-detect')),
        Choice(COMMA, _('Comma')),
        Choice(SEMICOLON, _('Semicolon')),
        Choice(PIPE, _('Pipe')),
        Choice(TAB, _('Tab')),
    ]


class DistanceUnitChoices(ChoiceSet):

    # Metric
    UNIT_KILOMETER = 'km'
    UNIT_METER = 'm'

    # Imperial
    UNIT_MILE = 'mi'
    UNIT_FOOT = 'ft'

    CHOICES = (
        Choice(UNIT_KILOMETER, _('Kilometers')),
        Choice(UNIT_METER, _('Meters')),
        Choice(UNIT_MILE, _('Miles')),
        Choice(UNIT_FOOT, _('Feet')),
    )


class WeightUnitChoices(ChoiceSet):

    # Metric
    UNIT_KILOGRAM = 'kg'
    UNIT_GRAM = 'g'

    # Imperial
    UNIT_POUND = 'lb'
    UNIT_OUNCE = 'oz'

    CHOICES = (
        Choice(UNIT_KILOGRAM, _('Kilograms')),
        Choice(UNIT_GRAM, _('Grams')),
        Choice(UNIT_POUND, _('Pounds')),
        Choice(UNIT_OUNCE, _('Ounces')),
    )


class DiameterUnitChoices(ChoiceSet):

    # Metric
    UNIT_MILLIMETER = 'mm'
    UNIT_CENTIMETER = 'cm'

    # Imperial
    UNIT_INCH = 'in'

    CHOICES = (
        (UNIT_MILLIMETER, _('Millimeters')),
        (UNIT_CENTIMETER, _('Centimeters')),
        (UNIT_INCH, _('Inches')),
    )


class FlowRateUnitChoices(ChoiceSet):

    # Metric
    UNIT_LITERS_PER_MINUTE = 'lpm'
    UNIT_CUBIC_METERS_PER_HOUR = 'm3ph'

    # Imperial
    UNIT_GALLONS_PER_MINUTE = 'gpm'

    CHOICES = (
        (UNIT_LITERS_PER_MINUTE, _('Liters per minute (L/min)')),
        (UNIT_CUBIC_METERS_PER_HOUR, _('Cubic meters per hour (m³/h)')),
        (UNIT_GALLONS_PER_MINUTE, _('Gallons per minute (GPM)')),
    )
