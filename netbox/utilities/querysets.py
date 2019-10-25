class DummyQuerySet:
    """
    A fake QuerySet that can be used to cache relationships to objects that have been deleted.
    """
    def __init__(self, queryset):
        self._cache = [obj for obj in queryset.all()]

    def all(self):
        return self._cache
