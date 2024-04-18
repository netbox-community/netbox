from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.translation import gettext_lazy as _


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
        label=_('Login banner'),
        default='',
        description=_("Additional content to display on the login page"),
        field_kwargs={
            'widget': forms.Textarea(
                attrs={'class': 'vLargeTextField'}
            ),
        },
    ),
    ConfigParam(
        name='BANNER_MAINTENANCE',
        label=_('Maintenance banner'),
        default='NetBox is currently in maintenance mode. Functionality may be limited.',
        description=_('Additional content to display when in maintenance mode'),
        field_kwargs={
            'widget': forms.Textarea(
                attrs={'class': 'vLargeTextField'}
            ),
        },
    ),
    ConfigParam(
        name='BANNER_TOP',
        label=_('Top banner'),
        default='',
        description=_("Additional content to display at the top of every page"),
        field_kwargs={
            'widget': forms.Textarea(
                attrs={'class': 'vLargeTextField'}
            ),
        },
    ),
    ConfigParam(
        name='BANNER_BOTTOM',
        label=_('Bottom banner'),
        default='',
        description=_("Additional content to display at the bottom of every page"),
        field_kwargs={
            'widget': forms.Textarea(
                attrs={'class': 'vLargeTextField'}
            ),
        },
    ),

    # IPAM
    ConfigParam(
        name='ENFORCE_GLOBAL_UNIQUE',
        label=_('Globally unique IP space'),
        default=True,
        description=_("Enforce unique IP addressing within the global table"),
        field=forms.BooleanField
    ),
    ConfigParam(
        name='PREFER_IPV4',
        label=_('Prefer IPv4'),
        default=False,
        description=_("Prefer IPv4 addresses over IPv6"),
        field=forms.BooleanField
    ),

    # Racks
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_HEIGHT',
        label=_('Rack unit height'),
        default=22,
        description=_("Default unit height for rendered rack elevations"),
        field=forms.IntegerField
    ),
    ConfigParam(
        name='RACK_ELEVATION_DEFAULT_UNIT_WIDTH',
        label=_('Rack unit width'),
        default=220,
        description=_("Default unit width for rendered rack elevations"),
        field=forms.IntegerField
    ),

    # Power
    ConfigParam(
        name='POWERFEED_DEFAULT_VOLTAGE',
        label=_('Powerfeed voltage'),
        default=120,
        description=_("Default voltage for powerfeeds"),
        field=forms.IntegerField
    ),
    ConfigParam(
        name='POWERFEED_DEFAULT_AMPERAGE',
        label=_('Powerfeed amperage'),
        default=15,
        description=_("Default amperage for powerfeeds"),
        field=forms.IntegerField
    ),
    ConfigParam(
        name='POWERFEED_DEFAULT_MAX_UTILIZATION',
        label=_('Powerfeed max utilization'),
        default=80,
        description=_("Default max utilization for powerfeeds"),
        field=forms.IntegerField
    ),

    # Security
    ConfigParam(
        name='ALLOWED_URL_SCHEMES',
        label=_('Allowed URL schemes'),
        default=(
            'file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc',
            'xmpp',
        ),
        description=_("Permitted schemes for URLs in user-provided content"),
        field=SimpleArrayField,
        field_kwargs={'base_field': forms.CharField()}
    ),

    # Pagination
    ConfigParam(
        name='PAGINATE_COUNT',
        label=_('Default page size'),
        default=50,
        field=forms.IntegerField
    ),
    ConfigParam(
        name='MAX_PAGE_SIZE',
        label=_('Maximum page size'),
        default=1000,
        field=forms.IntegerField
    ),

    # Validation
    ConfigParam(
        name='CUSTOM_VALIDATORS',
        label=_('Custom validators'),
        default={},
        description=_("Custom validation rules (JSON)"),
        field=forms.JSONField,
        field_kwargs={
            'widget': forms.Textarea(),
        },
    ),
    ConfigParam(
        name='PROTECTION_RULES',
        label=_('Protection rules'),
        default={},
        description=_("Deletion protection rules (JSON)"),
        field=forms.JSONField,
        field_kwargs={
            'widget': forms.Textarea(),
        },
    ),

    # User preferences
    ConfigParam(
        name='DEFAULT_USER_PREFERENCES',
        label=_('Default preferences'),
        default={},
        description=_("Default preferences for new users"),
        field=forms.JSONField
    ),

    # Miscellaneous
    ConfigParam(
        name='MAINTENANCE_MODE',
        label=_('Maintenance mode'),
        default=False,
        description=_("Enable maintenance mode"),
        field=forms.BooleanField
    ),
    ConfigParam(
        name='GRAPHQL_ENABLED',
        label=_('GraphQL enabled'),
        default=True,
        description=_("Enable the GraphQL API"),
        field=forms.BooleanField
    ),
    ConfigParam(
        name='CHANGELOG_RETENTION',
        label=_('Changelog retention'),
        default=90,
        description=_("Days to retain changelog history (set to zero for unlimited)"),
        field=forms.IntegerField
    ),
    ConfigParam(
        name='JOB_RETENTION',
        label=_('Job result retention'),
        default=90,
        description=_("Days to retain job result history (set to zero for unlimited)"),
        field=forms.IntegerField
    ),
    ConfigParam(
        name='MAPS_URL',
        label=_('Maps URL'),
        default='https://maps.google.com/?q=',
        description=_("Base URL for mapping geographic locations")
    ),

)
