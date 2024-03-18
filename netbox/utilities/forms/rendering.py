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
    A generic grouping of fields, with an optional name. Each field will be rendered
    on its own row under the heading (name).
    """
    def __init__(self, *fields, name=None):
        self.fields = fields
        self.name = name


class InlineFields:
    """
    A set of fields rendered inline (side-by-side) with a shared label; typically nested within a FieldSet.
    """
    def __init__(self, *fields, label=None):
        self.fields = fields
        self.label = label


class TabbedGroups:
    """
    Two or more groups of fields (FieldSets) arranged under tabs among which the user can navigate.
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
                'fields': group.fields,
            } for i, group in enumerate(self.groups, start=1)
        ]


class ObjectAttribute:
    """
    Renders the value for a specific attribute on the form's instance.
    """
    def __init__(self, name):
        self.name = name
