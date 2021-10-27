from django import forms
from django.contrib.postgres.forms import SimpleArrayField


class ConfigParam:

    def __init__(self, name, label, default, description='', field=None, field_kwargs=None):
        self.name = name
        self.label = label
        self.default = default
        self.field = field or forms.CharField
        self.description = description
        self.field_kwargs = field_kwargs or {}


PARAMS = (

    # Banners
    ConfigParam(
        name='BANNER_LOGIN',
        label='Login banner',
        default='',
        description="Additional content to display on the login page"
    ),
    ConfigParam(
        name='BANNER_TOP',
        label='Top banner',
        default='',
        description="Additional content to display at the top of every page"
    ),
    ConfigParam(
        name='BANNER_BOTTOM',
        label='Bottom banner',
        default='',
        description="Additional content to display at the bottom of every page"
    ),

    # IPAM
    ConfigParam(
        name='ENFORCE_GLOBAL_UNIQUE',
        label='Globally unique IP space',
        default=False,
        description="Enforce unique IP addressing within the global table",
        field=forms.BooleanField
    ),
    ConfigParam(
        name='PREFER_IPV4',
        label='Prefer IPv4',
        default=False,
        description="Prefer IPv4 addresses over IPv6",
        field=forms.BooleanField
    ),

    # Racks
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_HEIGHT',
        label='Rack unit height',
        default=22,
        description="Default unit height for rendered rack elevations",
        field=forms.IntegerField
    ),
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_WIDTH',
        label='Rack unit width',
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

    # Pagination
    ConfigParam(
        name='PAGINATE_COUNT',
        label='Default page size',
        default=50,
        field=forms.IntegerField
    ),
    ConfigParam(
        name='MAX_PAGE_SIZE',
        label='Maximum page size',
        default=1000,
        field=forms.IntegerField
    ),

    # NAPALM
    ConfigParam(
        name='NAPALM_USERNAME',
        label='NAPALM username',
        default='',
        description="Username to use when connecting to devices via NAPALM"
    ),
    ConfigParam(
        name='NAPALM_PASSWORD',
        label='NAPALM password',
        default='',
        description="Password to use when connecting to devices via NAPALM"
    ),
    ConfigParam(
        name='NAPALM_TIMEOUT',
        label='NAPALM timeout',
        default=30,
        description="NAPALM connection timeout (in seconds)",
        field=forms.IntegerField
    ),
    ConfigParam(
        name='NAPALM_ARGS',
        label='NAPALM arguments',
        default={},
        description="Additional arguments to pass when invoking a NAPALM driver (as JSON data)",
        field=forms.JSONField
    ),

    # Miscellaneous
    ConfigParam(
        name='MAINTENANCE_MODE',
        label='Maintenance mode',
        default=False,
        description="Enable maintenance mode",
        field=forms.BooleanField
    ),
    ConfigParam(
        name='MAPS_URL',
        label='Maps URL',
        default='https://maps.google.com/?q=',
        description="Base URL for mapping geographic locations"
    ),

)
