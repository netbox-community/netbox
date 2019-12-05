from utilities.choices import ChoiceSet


#
# CustomFields
#

class CustomFieldTypeChoices(ChoiceSet):

    TYPE_TEXT = 'text'
    TYPE_INTEGER = 'integer'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_URL = 'url'
    TYPE_SELECT = 'select'

    CHOICES = (
        (TYPE_TEXT, 'Text'),
        (TYPE_INTEGER, 'Integer'),
        (TYPE_BOOLEAN, 'Boolean (true/false)'),
        (TYPE_DATE, 'Date'),
        (TYPE_URL, 'URL'),
        (TYPE_SELECT, 'Selection'),
    )

    LEGACY_MAP = {
        TYPE_TEXT: 100,
        TYPE_INTEGER: 200,
        TYPE_BOOLEAN: 300,
        TYPE_DATE: 400,
        TYPE_URL: 500,
        TYPE_SELECT: 600,
    }


class CustomFieldFilterLogicChoices(ChoiceSet):

    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'

    CHOICES = (
        (FILTER_DISABLED, 'Disabled'),
        (FILTER_LOOSE, 'Loose'),
        (FILTER_EXACT, 'Exact'),
    )

    LEGACY_MAP = {
        FILTER_DISABLED: 0,
        FILTER_LOOSE: 1,
        FILTER_EXACT: 2,
    }
