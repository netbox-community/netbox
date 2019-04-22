from django.core.validators import RegexValidator


DNSValidator = RegexValidator(
    regex='^[a-z]+$',
    message='Only alphanumeric characters, hyphens, and periods are allowed in DNS names',
    code='invalid'
)
