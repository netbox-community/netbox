import string

from django.db.models import Q


OBJECTPERMISSION_OBJECT_TYPES = Q(
    ~Q(app_label__in=['account', 'admin', 'auth', 'contenttypes', 'sessions', 'taggit', 'users']) |
    Q(app_label='users', model__in=['objectpermission', 'token', 'group', 'user'])
)

CONSTRAINT_TOKEN_USER = '$user'

# API tokens
TOKEN_KEY_LENGTH = 16
TOKEN_DEFAULT_LENGTH = 40
TOKEN_CHARSET = string.ascii_letters + string.digits
