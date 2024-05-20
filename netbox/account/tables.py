from django.utils.translation import gettext as _

from account.models import UserToken
from netbox.tables import NetBoxTable, columns

__all__ = (
    'UserTokenTable',
)


TOKEN = """<samp><span id="token_{{ record.pk }}">{{ record }}</span></samp>"""

ALLOWED_IPS = """{{ value|join:", " }}"""

COPY_BUTTON = """
{% if settings.ALLOW_TOKEN_RETRIEVAL %}
  {% copy_content record.pk prefix="token_" color="success" %}
{% endif %}
"""


class UserTokenTable(NetBoxTable):
    """
    Table for users to manager their own API tokens under account views.
    """
    key = columns.TemplateColumn(
        verbose_name=_('Key'),
        template_code=TOKEN,
    )
    write_enabled = columns.BooleanColumn(
        verbose_name=_('Write Enabled')
    )
    created = columns.DateTimeColumn(
        timespec='minutes',
        verbose_name=_('Created'),
    )
    expires = columns.DateTimeColumn(
        timespec='minutes',
        verbose_name=_('Expires'),
    )
    last_used = columns.DateTimeColumn(
        verbose_name=_('Last Used'),
    )
    allowed_ips = columns.TemplateColumn(
        verbose_name=_('Allowed IPs'),
        template_code=ALLOWED_IPS
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = UserToken
        fields = (
            'pk', 'id', 'key', 'description', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        )
