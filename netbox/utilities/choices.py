from django.conf import settings
from django.utils.translation import gettext_lazy as _

__all__ = (
    'ChoiceSet',
    'unpack_grouped_choices',
)


class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __new__(mcs, name, bases, attrs):

        # Extend static choices with any configured choices
        if key := attrs.get('key'):
            assert type(attrs['CHOICES']) is list, _(
                "{name} has a key defined but CHOICES is not a list"
            ).format(name=name)
            app = attrs['__module__'].split('.', 1)[0]
            replace_key = f'{app}.{key}'
            extend_key = f'{replace_key}+' if replace_key else None
            if replace_key and replace_key in settings.FIELD_CHOICES:
                # Replace the stock choices
                attrs['CHOICES'] = settings.FIELD_CHOICES[replace_key]
            elif extend_key and extend_key in settings.FIELD_CHOICES:
                # Extend the stock choices
                attrs['CHOICES'].extend(settings.FIELD_CHOICES[extend_key])

        # Define choice tuples and color maps
        attrs['_choices'] = []
        attrs['colors'] = {}
        for choice in attrs['CHOICES']:
            if isinstance(choice[1], (list, tuple)):
                grouped_choices = []
                for c in choice[1]:
                    grouped_choices.append((c[0], c[1]))
                    if len(c) == 3:
                        attrs['colors'][c[0]] = c[2]
                attrs['_choices'].append((choice[0], grouped_choices))
            else:
                attrs['_choices'].append((choice[0], choice[1]))
                if len(choice) == 3:
                    attrs['colors'][choice[0]] = choice[2]

        return super().__new__(mcs, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        # django-filters will check if a 'choices' value is callable, and if so assume that it returns an iterable
        return getattr(cls, '_choices', ())

    def __iter__(cls):
        return iter(getattr(cls, '_choices', ()))


class ChoiceSet(metaclass=ChoiceSetMeta):
    """
    Holds an iterable of choice tuples suitable for passing to a Django model or form field. Choices can be defined
    statically within the class as CHOICES and/or gleaned from the FIELD_CHOICES configuration parameter.
    """
    CHOICES = list()

    @classmethod
    def values(cls):
        return [c[0] for c in unpack_grouped_choices(cls._choices)]


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
