from django.core.validators import RegexValidator


DNSValidator = RegexValidator(
    regex='^[0-9A-Za-z.-]+$',
    message='Only alphanumeric characters, hyphens, and periods are allowed in DNS names',
    code='invalid'
)
