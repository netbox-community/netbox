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

PLUGIN_NAME_TEMPLATE = """
{% load static %}
{% if record.icon_url %}
    <img class="plugin-icon" src="{{ record.icon_url }}">
{% else %}
    <img class="plugin-icon" src="{% static 'plugin-default.svg' %}">
{% endif %}
<a href="{% url 'core:plugin' record.config_name %}">{{ record.title_long }}</a>
"""

DATA_SOURCE_SYNC_BUTTON = """
{% load helpers %}
{% load i18n %}
{% if perms.core.sync_datasource %}
    {% if record.ready_for_sync %}
        <button class="btn btn-primary btn-sm" type="submit" formaction="{% url 'core:datasource_sync' pk=record.pk %}?return_url={{ request.get_full_path|urlencode }}" formmethod="post">
            <i class="mdi mdi-sync" aria-hidden="true"></i> {% trans "Sync" %}
        </button>
    {% else %}
        <button class="btn btn-primary btn-sm" disabled>
            <i class="mdi mdi-sync" aria-hidden="true"></i> {% trans "Sync" %}
        </button>
    {% endif %}
{% endif %}
"""
