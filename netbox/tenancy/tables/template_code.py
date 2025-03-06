TENANT_COLUMN = """
{% if record.tenant %}
    <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
{% elif record.vrf.tenant %}
    <a href="{{ record.vrf.tenant.get_absolute_url }}" title="{{ record.vrf.tenant.description }}">{{ record.vrf.tenant }}</a>*
{% else %}
    &mdash;
{% endif %}
"""

TENANT_GROUP_COLUMN = """
{% if record.tenant and record.tenant.group %}
    <a href="{{ record.tenant.group.get_absolute_url }}" title="{{ record.tenant.group.description }}">{{ record.tenant.group }}</a>
{% elif record.vrf.tenant and record.vrf.tenant.group %}
    <a href="{{ record.vrf.tenant.group.get_absolute_url }}" title="{{ record.vrf.tenant.group.description }}">{{ record.vrf.tenant.group }}</a>*
{% else %}
    &mdash;
{% endif %}
"""
