from django import forms

from utilities.choices import Choice
from utilities.forms import widgets

__all__ = (
    'ChoiceField',
    'MultipleChoiceField',
    'TypedChoiceField',
)


def _map_choice_attr(choices, attr):
    """
    Build a {value: attr_value} mapping from the Choice objects among an iterable of choices (descending into
    optgroups), for the given Choice attribute (e.g. 'description' or 'color'). Values of None are omitted.

    Django flattens choices to plain (value, label) tuples before they reach the widget, so this is collected from
    the field's original choices, where the Choice objects are still intact. A ChoiceSet is iterable (yielding its
    Choice objects); a plain callable (lazy choices) is not, and yields an empty mapping.
    """
    mapping = {}
    try:
        entries = iter(choices)
    except TypeError:
        return mapping
    for choice in entries:
        # Descend into an optgroup's members; a Choice is always a flat choice
        members = [choice]
        if not isinstance(choice, Choice) and isinstance(choice[1], (list, tuple)):
            members = choice[1]
        for member in members:
            if isinstance(member, Choice) and (value := getattr(member, attr)) is not None:
                mapping[member.value] = value
    return mapping


def _parent_choices_property(cls):
    """
    Return the `choices` property inherited from the first class after AttrChoiceMixin in cls's MRO (i.e. the
    Django field's own property). Used to delegate to the parent getter/setter without hardcoding a specific base
    class, so a setter override on a future Django subclass (e.g. TypedChoiceField/MultipleChoiceField) isn't
    bypassed.
    """
    mro = cls.__mro__
    for klass in mro[mro.index(AttrChoiceMixin) + 1:]:
        if isinstance(prop := klass.__dict__.get('choices'), property):
            return prop
    raise AttributeError(f"No parent 'choices' property found for {cls.__name__}")  # pragma: no cover


class AttrChoiceMixin:
    """
    Reads option descriptions from the Choice objects among a field's choices and passes them to a
    description-aware Select widget for rendering as option subtitles. Set `show_descriptions=False` to suppress.
    """
    def __init__(self, *, choices=(), show_descriptions=True, **kwargs):
        self.show_descriptions = show_descriptions
        super().__init__(choices=choices, **kwargs)

    def _get_choices(self):
        return _parent_choices_property(type(self)).fget(self)

    def _set_choices(self, value):
        # Delegate to the parent setter (updates self._choices and self.widget.choices), then refresh the widget's
        # description map from the same choices. Collecting descriptions here (rather than once in __init__) keeps
        # them in sync should the field's choices be reassigned after construction. Descriptions are read from the
        # raw choices, where the Choice objects are still intact, before Django normalizes them to (value, label).
        _parent_choices_property(type(self)).fset(self, value)
        if getattr(self, 'show_descriptions', True):
            self.widget.descriptions = _map_choice_attr(value, 'description')

    choices = property(_get_choices, _set_choices)


class ChoiceField(AttrChoiceMixin, forms.ChoiceField):
    """
    Extends Django's ChoiceField to render the description defined on each Choice as an option subtitle.
    """
    widget = widgets.Select


class TypedChoiceField(AttrChoiceMixin, forms.TypedChoiceField):
    """
    A description-aware ChoiceField for use on nullable model choice fields. Like Django's TypedChoiceField, an empty
    selection is coerced to `empty_value` (which defaults to None here) so that a blank submission is stored as NULL
    rather than an empty string. This mirrors the form field Django generates automatically for a nullable choice
    field, while also rendering the description defined on each Choice as an option subtitle.
    """
    widget = widgets.Select

    def __init__(self, *, empty_value=None, **kwargs):
        super().__init__(empty_value=empty_value, **kwargs)


class MultipleChoiceField(AttrChoiceMixin, forms.MultipleChoiceField):
    """
    Extends Django's MultipleChoiceField to render the description defined on each Choice as an option subtitle.
    """
    widget = widgets.SelectMultiple
