OBJECTCHANGE_FULL_NAME = """
{% load helpers %}
{{ value.get_full_name|placeholder }}
"""

OBJECTCHANGE_OBJECT = """
{% if value and value.get_absolute_url %}
    <a href="{{ value.get_absolute_url }}">{{ record.object_repr }}</a>
{% else %}
    {{ record.object_repr }}
{% endif %}
"""

OBJECTCHANGE_REQUEST_ID = """
<a href="{% url 'core:objectchange_list' %}?request_id={{ value }}">{{ value }}</a>
"""

PLUGIN_IS_INSTALLED = """
{% if record.is_local %}
    {% if record.is_loaded %}
        <span class="text-success"><i class="mdi mdi-check-bold"></i></span>
    {% else %}
        <span class="text-danger"><i class="mdi mdi-alert" data-bs-toggle="tooltip" title="Could not load plugin. Version may be incompatible. Min version: {{ record.netbox_min_version }}, max version: {{ record.netbox_max_version }}"></i></span>
    {% endif %}
{% else %}
    <span class="text-muted">&mdash;</span>
{% endif %}
"""
