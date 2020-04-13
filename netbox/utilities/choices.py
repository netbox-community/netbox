class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __call__(cls, *args, **kwargs):
        # Django will check if a 'choices' value is callable, and if so assume that it returns an iterable
        return getattr(cls, 'CHOICES', ())

    def __iter__(cls):
        choices = getattr(cls, 'CHOICES', ())
        return iter(choices)


class ChoiceSet(metaclass=ChoiceSetMeta):

    CHOICES = list()
    LEGACY_MAP = dict()

    @classmethod
    def values(cls):
        return [c[0] for c in unpack_grouped_choices(cls.CHOICES)]

    @classmethod
    def as_dict(cls):
        # Unpack grouped choices before casting as a dict
        return dict(unpack_grouped_choices(cls.CHOICES))

    @classmethod
    def slug_to_id(cls, slug):
        """
        Return the legacy integer value corresponding to a slug.
        """
        return cls.LEGACY_MAP.get(slug)

    @classmethod
    def id_to_slug(cls, legacy_id):
        """
        Return the slug value corresponding to a legacy integer value.
        """
        if legacy_id in cls.LEGACY_MAP.values():
            # Invert the legacy map to allow lookup by integer
            legacy_map = dict([
                (id, slug) for slug, id in cls.LEGACY_MAP.items()
            ])
            return legacy_map.get(legacy_id)


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


#
# Button color choices
#

class ButtonColorChoices(ChoiceSet):
    """
    Map standard button color choices to Bootstrap color classes
    """
    DEFAULT = 'default'
    BLUE = 'primary'
    GREY = 'secondary'
    GREEN = 'success'
    RED = 'danger'
    YELLOW = 'warning'
    BLACK = 'dark'

    CHOICES = (
        (DEFAULT, 'Default'),
        (BLUE, 'Blue'),
        (GREY, 'Grey'),
        (GREEN, 'Green'),
        (RED, 'Red'),
        (YELLOW, 'Yellow'),
        (BLACK, 'Black')
    )
