from django.db.models import TextField


class CachedValueField(TextField):
    """
    Currently a dummy field to prevent custom lookups being applied globally to TextField.
    """
    pass
