import random
import string
from functools import cached_property

__all__ = (
    'InlineFields',
    'ObjectAttribute',
    'TabbedFieldGroups',
)


class FieldGroup:

    def __init__(self, label, *field_names):
        self.field_names = field_names
        self.label = label


class InlineFields(FieldGroup):
    pass


class TabbedFieldGroups:

    def __init__(self, *groups):
        self.groups = [
            FieldGroup(*group) for group in groups
        ]

        # Initialize a random ID for the group (for tab selection)
        self.id = ''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )

    @cached_property
    def tabs(self):
        return [
            {
                'id': f'{self.id}_{i}',
                'title': group.label,
                'fields': group.field_names,
            } for i, group in enumerate(self.groups, start=1)
        ]


class ObjectAttribute:

    def __init__(self, name):
        self.name = name
