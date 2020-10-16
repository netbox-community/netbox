CABLE_LENGTH = """
{% if record.length %}{{ record.length }} {{ record.get_length_unit_display }}{% else %}&mdash;{% endif %}
"""

CABLE_TERMINATION_PARENT = """
{% if value.device %}
    <a href="{{ value.device.get_absolute_url }}">{{ value.device }}</a>
{% elif value.circuit %}
    <a href="{{ value.circuit.get_absolute_url }}">{{ value.circuit }}</a>
{% elif value.power_panel %}
    <a href="{{ value.power_panel.get_absolute_url }}">{{ value.power_panel }}</a>
{% endif %}
"""

DEVICE_LINK = """
<a href="{% url 'dcim:device' pk=record.pk %}">
    {{ record.name|default:'<span class="label label-info">Unnamed device</span>' }}
</a>
"""

INTERFACE_IPADDRESSES = """
{% for ip in record.ip_addresses.unrestricted %}
    <a href="{{ ip.get_absolute_url }}">{{ ip }}</a><br />
{% endfor %}
"""

INTERFACE_TAGGED_VLANS = """
{% for vlan in record.tagged_vlans.unrestricted %}
    <a href="{{ vlan.get_absolute_url }}">{{ vlan }}</a><br />
{% endfor %}
"""

MPTT_LINK = """
{% if record.get_children %}
    <span style="padding-left: {{ record.get_ancestors|length }}0px "><i class="fa fa-caret-right"></i>
{% else %}
    <span style="padding-left: {{ record.get_ancestors|length }}9px">
{% endif %}
    <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
</span>
"""

POWERFEED_CABLE = """
<a href="{{ value.get_absolute_url }}">{{ value }}</a>
<a href="{% url 'dcim:powerfeed_trace' pk=record.pk %}" class="btn btn-primary btn-xs" title="Trace">
    <i class="fa fa-share-alt" aria-hidden="true"></i>
</a>
"""

POWERFEED_CABLETERMINATION = """
<a href="{{ value.parent.get_absolute_url }}">{{ value.parent }}</a>
<i class="fa fa-caret-right"></i>
<a href="{{ value.get_absolute_url }}">{{ value }}</a>
"""

RACKGROUP_ELEVATIONS = """
<a href="{% url 'dcim:rack_elevation_list' %}?site={{ record.site.slug }}&group_id={{ record.pk }}" class="btn btn-xs btn-primary" title="View elevations">
    <i class="fa fa-eye"></i>
</a>
"""

UTILIZATION_GRAPH = """
{% load helpers %}
{% utilization_graph value %}
"""
