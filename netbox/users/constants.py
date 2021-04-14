from django.db.models import Q


OBJECTPERMISSION_OBJECT_TYPES = Q(
    ~Q(app_label__in=['admin', 'auth', 'contenttypes', 'sessions', 'taggit', 'users']) |
    Q(app_label='auth', model__in=['group', 'user']) |
    Q(app_label='users', model__in=['objectpermission', 'token'])
)
