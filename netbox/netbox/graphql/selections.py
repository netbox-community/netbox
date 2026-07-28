from strawberry.types import Info
from strawberry.types.nodes import FragmentSpread, InlineFragment, SelectedField, Selection

__all__ = (
    'get_selected_field_names',
)


def get_selected_field_names(info: Info) -> set[str]:
    """
    Return the field names selected on the current GraphQL type.

    Recursively traverses inline fragments and fragment spreads.
    """
    return _collect_field_names(info.selected_fields[0].selections)


def _collect_field_names(selections: list[Selection]) -> set[str]:
    names = set()
    for selection in selections:
        if isinstance(selection, SelectedField):
            names.add(selection.name)
        elif isinstance(selection, (InlineFragment, FragmentSpread)):
            names.update(_collect_field_names(selection.selections))
    return names
