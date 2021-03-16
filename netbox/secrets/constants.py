from django.db.models import Q


#
# Secrets
#

SECRET_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='device') |
    Q(app_label='virtualization', model='virtualmachine')
)

SECRET_PLAINTEXT_MAX_LENGTH = 65535
