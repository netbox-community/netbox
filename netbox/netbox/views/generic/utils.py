from django.apps import apps


def get_prerequisite_model(queryset):
    """
    Return any prerequisite model that must be created prior to creating
    an instance of the current model.
    """
    if not queryset.exists():
        for prereq in getattr(queryset.model, 'prerequisite_models', []):
            model = apps.get_model(prereq)
            if not model.objects.exists():
                return model
