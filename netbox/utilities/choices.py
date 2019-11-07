class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __call__(cls, *args, **kwargs):
        # Django will check if a choices value is callable, and if so assume that it returns an iterable
        return getattr(cls, 'CHOICES', ())

    def __iter__(cls):
        choices = getattr(cls, 'CHOICES', ())
        return iter(choices)


class ChoiceSet(metaclass=ChoiceSetMeta):

    CHOICES = list()
    LEGACY_MAP = dict()

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
