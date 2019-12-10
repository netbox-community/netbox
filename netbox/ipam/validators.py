from django.core.validators import RegexValidator


DNSValidator = RegexValidator(
    regex='^[0-9A-Za-z._-]+$',
    message='Only alphanumeric characters, hyphens, periods, and underscores are allowed in DNS names',
    code='invalid'
)
