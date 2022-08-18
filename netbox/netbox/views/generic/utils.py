def get_prerequisite_model(queryset):
    model = queryset.model

    if not queryset.count():
        if hasattr(model, 'get_prerequisite_models'):
            prerequisites = model.get_prerequisite_models()
            if prerequisites:
                for prereq in prerequisites:
                    if not prereq.objects.count():
                        return prereq

    return None
