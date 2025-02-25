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
{% if record.failed_to_load %}
    <span class="text-danger"><i class="mdi mdi-alert" data-bs-toggle="tooltip" title="Could not load due to NetBox version incompatibility. Min version: {{ record.netbox_min_version }}, max version: {{ record.netbox_max_version }}"></i></span>
{% elif value is True %}
    <span class="text-success"><i class="mdi mdi-check-bold"></i></span>
{% else %}
    <span class="text-danger"><i class="mdi mdi-close-thick"></i></span>
{% endif %}
"""
