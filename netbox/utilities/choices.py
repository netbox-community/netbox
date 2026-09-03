import enum
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _

from utilities.data import get_config_value_ci
from utilities.string import enum_key

__all__ = (
    'Choice',
    'ChoiceSet',
    'unpack_grouped_choices',
)


class Choice(tuple):
    """
    A single choice within a ChoiceSet. Carries the choice's label, and optionally a color and a description, in a
    single object. A Choice **is** a `(value, label)` two-tuple for backward compatibility with the plain-tuple choice
    format (so it satisfies `isinstance(choice, tuple)` checks in Django, DRF, etc.); its `color` and `description`
    are exposed only as attributes.
    """
    value: Any
    label: str | Promise
    color: str | None
    description: str | Promise | None

    def __new__(cls, value, label, color=None, description=None):
        instance = super().__new__(cls, (value, label))
        instance.value = value
        instance.label = label
        instance.color = color
        instance.description = description
        return instance

    def __getnewargs__(self):
        # tuple's default reconstructor would call Choice((value, label)) with a single argument, which fails
        # __new__'s (value, label, ...) signature. Supply the real constructor args so copy/deepcopy/pickle work.
        return self.value, self.label, self.color, self.description

    def __repr__(self):
        return f'Choice(value={self.value!r}, label={self.label!r})'


class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __new__(mcs, name, bases, attrs):

        # Extend static choices with any configured choices
        if key := attrs.get('key'):
            if type(attrs['CHOICES']) is not list:
                raise ImproperlyConfigured(
                    _("{name} has a key defined but CHOICES is not a list").format(name=name)
                )
            app = attrs['__module__'].split('.', 1)[0]
            replace_key = f'{app}.{key}'
            replace_choices = get_config_value_ci(settings.FIELD_CHOICES, replace_key)
            if replace_choices is not None:
                attrs['CHOICES'] = replace_choices
            else:
                extend_key = f'{replace_key}+'
                extend_choices = get_config_value_ci(settings.FIELD_CHOICES, extend_key)
                if extend_choices is not None:
                    attrs['CHOICES'].extend(extend_choices)

        # Build the normalized choice list and the derived color map. Each choice may be defined as a Choice object
        # (which is preserved as-is so consumers can reference its color/description) or as a plain (value, label) or
        # (value, label, color) tuple. The colors map is kept for model-level consumers (e.g. get_FOO_color()).
        attrs['_choices'] = []
        attrs['colors'] = {}

        def register(entry):
            # A choice may be given as a dict (e.g. from FIELD_CHOICES config, to avoid importing Choice), a Choice
            # object, or a legacy (value, label[, color]) tuple. Dicts and Choices are preserved as Choice objects so
            # consumers can reference their color/description; legacy tuples are reduced to (value, label). Any color
            # is also recorded on the colors map for model-level consumers.
            if isinstance(entry, dict):
                entry = Choice(**entry)
            if isinstance(entry, Choice):
                if entry.color is not None:
                    attrs['colors'][entry.value] = entry.color
                return entry
            value, label = entry[0], entry[1]
            if len(entry) >= 3:
                attrs['colors'][value] = entry[2]
            return value, label

        for choice in attrs['CHOICES']:
            # A grouped choice is a (group_label, [members]) tuple; Choice and dict entries are always flat choices
            if not isinstance(choice, (Choice, dict)) and isinstance(choice[1], (list, tuple)):
                grouped_choices = [register(c) for c in choice[1]]
                attrs['_choices'].append((choice[0], grouped_choices))
            else:
                attrs['_choices'].append(register(choice))

        return super().__new__(mcs, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        # django-filters will check if a 'choices' value is callable, and if so assume that it returns an iterable
        return getattr(cls, '_choices', ())

    def __iter__(cls):
        return iter(getattr(cls, '_choices', ()))


class ChoiceSet(metaclass=ChoiceSetMeta):
    """
    Holds an iterable of choices suitable for passing to a Django model or form field. Choices can be defined
    statically within the class as CHOICES and/or gleaned from the FIELD_CHOICES configuration parameter. Each
    choice may be defined as a Choice object (to carry a color and/or description) or as a plain (value, label) or
    (value, label, color) tuple.
    """
    CHOICES = list()

    @classmethod
    def values(cls):
        return [c[0] for c in unpack_grouped_choices(cls._choices)]

    @classmethod
    def as_enum(cls, name=None, prefix=''):
        """
        Return the ChoiceSet as an Enum. If no name is provided, "Choices" will be stripped from the class name (if
        present) and "Enum" will be appended. For example, "CircuitStatusChoices" will become "CircuitStatusEnum".
        """
        name = name or f"{cls.__name__.split('Choices')[0]}Enum"
        prefix = f'{prefix}_' if prefix else ''
        data = {f'{prefix}{enum_key(v)}'.upper(): v for v in cls.values()}
        return enum.Enum(name, data)


def unpack_grouped_choices(choices):
    """
    Unpack a grouped choices hierarchy into a flat list of two-tuples. For example:

    choices = (
        ('Foo', (
            (1, 'A'),
            (2, 'B')
        )),
        ('Bar', (
            (3, 'C'),
            (4, 'D')
        ))
    )

    becomes:

    choices = (
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D')
    )
    """
    unpacked_choices = []
    for key, value in choices:
        if isinstance(value, (list, tuple)):
            # Entered an optgroup
            for optgroup_key, optgroup_value in value:
                unpacked_choices.append((optgroup_key, optgroup_value))
        else:
            unpacked_choices.append((key, value))
    return unpacked_choices
