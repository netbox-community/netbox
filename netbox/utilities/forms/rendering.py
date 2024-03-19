import random
import string
from functools import cached_property

__all__ = (
    'FieldSet',
    'InlineFields',
    'ObjectAttribute',
    'TabbedGroups',
)


class FieldSet:
    """
    A generic grouping of fields, with an optional name. Each item will be rendered
    on its own row under the provided heading (name), if any. The following types
    may be passed as items:

      * Field name (string)
      * InlineFields instance
      * TabbedGroups instance
      * ObjectAttribute instance

    Parameters:
        items: An iterable of items to be rendered (one per row)
        name: The fieldset's name, displayed as a heading (optional)
    """
    def __init__(self, *items, name=None):
        self.items = items
        self.name = name


class InlineFields:
    """
    A set of fields rendered inline (side-by-side) with a shared label.

    Parameters:
        fields: An iterable of form field names
        label: The label text to render for the row (optional)
    """
    def __init__(self, *fields, label=None):
        self.fields = fields
        self.label = label


class TabbedGroups:
    """
    Two or more groups of fields (FieldSets) arranged under tabs among which the user can toggle.

    Parameters:
        fieldsets: An iterable of FieldSet instances, one per tab. Each FieldSet *must* have a
            name assigned, which will be employed as the tab's label.
    """
    def __init__(self, *fieldsets):
        for fs in fieldsets:
            if not fs.name:
                raise ValueError(f"Grouped fieldset {fs} must have a name.")
        self.groups = fieldsets

        # Initialize a random ID for the group (for tab selection)
        self.id = ''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )

    @cached_property
    def tabs(self):
        return [
            {
                'id': f'{self.id}_{i}',
                'title': group.name,
                'fields': group.items,
            } for i, group in enumerate(self.groups, start=1)
        ]


class ObjectAttribute:
    """
    Renders the value for a specific attribute on the form's instance. This may be used to
    display a read-only value and convey additional context to the user. If the attribute has
    a `get_absolute_url()` method, it will be rendered as a hyperlink.

    Parameters:
        name: The name of the attribute to be displayed
    """
    def __init__(self, name):
        self.name = name
