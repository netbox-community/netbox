from django.core.validators import RegexValidator


DNSValidator = RegexValidator(
    regex='^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$',
    message='Only alphanumeric characters, hyphens, and periods are allowed in DNS names',
    code='invalid'
)
