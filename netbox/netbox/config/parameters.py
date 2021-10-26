from django import forms
from django.contrib.postgres.forms import SimpleArrayField


class OptionalBooleanSelect(forms.Select):
    """
    An optional boolean field (yes/no/default).
    """
    def __init__(self, attrs=None):
        choices = (
            ('', 'Default'),
            (True, 'Yes'),
            (False, 'No'),
        )
        super().__init__(attrs, choices)


class OptionalBooleanField(forms.NullBooleanField):
    widget = OptionalBooleanSelect


class ConfigParam:

    def __init__(self, name, label, default, description=None, field=None, field_kwargs=None):
        self.name = name
        self.label = label
        self.default = default
        self.field = field or forms.CharField
        self.description = description
        self.field_kwargs = field_kwargs or {}


PARAMS = (

    # Banners
    ConfigParam('BANNER_LOGIN', 'Login banner', ''),
    ConfigParam('BANNER_TOP', 'Top banner', ''),
    ConfigParam('BANNER_BOTTOM', 'Bottom banner', ''),

    # IPAM
    ConfigParam(
        name='ENFORCE_GLOBAL_UNIQUE',
        label='Globally unique IP space',
        default=False,
        description="Enforce unique IP addressing within the global table",
        field=OptionalBooleanField
    ),
    ConfigParam(
        name='PREFER_IPV4',
        label='Prefer IPv4',
        default=False,
        description="Prefer IPv4 addresses over IPv6",
        field=OptionalBooleanField
    ),

    # Racks
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_HEIGHT',
        label='Rack Unit Height',
        default=22,
        description="Default unit height for rendered rack elevations",
        field=forms.IntegerField
    ),
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_WIDTH',
        label='Rack Unit Width',
        default=220,
        description="Default unit width for rendered rack elevations",
        field=forms.IntegerField
    ),

    # Security
    ConfigParam(
        name='ALLOWED_URL_SCHEMES',
        label='Allowed URL schemes',
        default=(
            'file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc',
            'xmpp',
        ),
        description="Permitted schemes for URLs in user-provided content",
        field=SimpleArrayField,
        field_kwargs={'base_field': forms.CharField()}
    ),

)
