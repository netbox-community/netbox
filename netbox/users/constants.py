from django.db.models import Q


OBJECTPERMISSION_OBJECT_TYPES = Q(
    ~Q(app_label__in=['account', 'admin', 'auth', 'contenttypes', 'sessions', 'taggit', 'users']) |
    Q(app_label='users', model__in=['objectpermission', 'token', 'group', 'user'])
)

CONSTRAINT_TOKEN_USER = '$user'
