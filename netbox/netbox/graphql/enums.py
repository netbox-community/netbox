from enum import Enum
import strawberry

__all__ = [
    'ColorEnum',
    'ButtonColorEnum',
    'ImportMethodEnumEnum',
    'ImportFormatEnum',
    'DistanceUnitEnum',
    'WeightUnitEnum',
]

#
# Generic color choices
#


@strawberry.enum
class ColorEnum(Enum):
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


#
# Button color choices
#


@strawberry.enum
class ButtonColorEnum(Enum):
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


#
# Import
#


@strawberry.enum
class ImportMethodEnumEnum(Enum):
    DIRECT = 'direct'
    UPLOAD = 'upload'
    DATA_FILE = 'datafile'


@strawberry.enum
class ImportFormatEnum(Enum):
    AUTO = 'auto'
    CSV = 'csv'
    JSON = 'json'
    YAML = 'yaml'


# @strawberry.enum
# class CSVDelimiterEnum(Enum):
#     AUTO = 'auto'
#     COMMA = CSV_DELIMITERS['comma']
#     SEMICOLON = CSV_DELIMITERS['semicolon']
#     TAB = CSV_DELIMITERS['tab']


@strawberry.enum
class DistanceUnitEnum(Enum):
    # Metric
    UNIT_KILOMETER = 'km'
    UNIT_METER = 'm'

    # Imperial
    UNIT_MILE = 'mi'
    UNIT_FOOT = 'ft'


@strawberry.enum
class WeightUnitEnum(Enum):
    # Metric
    UNIT_KILOGRAM = 'kg'
    UNIT_GRAM = 'g'

    # Imperial
    UNIT_POUND = 'lb'
    UNIT_OUNCE = 'oz'
