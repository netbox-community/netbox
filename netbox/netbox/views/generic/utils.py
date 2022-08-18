def get_prerequisite_model(queryset):
    requirement = None
    model = queryset.model

    if not queryset.count():
        prerequisites = model.get_prerequisite_models()
        if prerequisites:
            for prereq in prerequisites:
                if not prereq.objects.count():
                    requirement = prereq

    return requirement
