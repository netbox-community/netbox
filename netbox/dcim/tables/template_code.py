CABLETERMINATION = """
{% if value %}
    <a href="{{ value.parent.get_absolute_url }}">{{ value.parent }}</a>
    <i class="fa fa-caret-right"></i>
    <a href="{{ value.get_absolute_url }}">{{ value }}</a>
{% else %}
    &mdash;
{% endif %}
"""

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

#
# Device component buttons
#

CONSOLEPORT_BUTTONS = """
{% if record.cable %}
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
{% elif perms.dcim.add_cable %}
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="glyphicon glyphicon-resize-small" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-right">
            <li><a href="{% url 'dcim:consoleport_connect' termination_a_id=record.pk termination_b_type='console-server-port' %}?return_url={{ device.get_absolute_url }}">Console Server Port</a></li>
            <li><a href="{% url 'dcim:consoleport_connect' termination_a_id=record.pk termination_b_type='front-port' %}?return_url={{ device.get_absolute_url }}">Front Port</a></li>
            <li><a href="{% url 'dcim:consoleport_connect' termination_a_id=record.pk termination_b_type='rear-port' %}?return_url={{ device.get_absolute_url }}">Rear Port</a></li>
        </ul>
    </span>
{% endif %}
"""

CONSOLESERVERPORT_BUTTONS = """
{% if record.cable %}
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
{% elif perms.dcim.add_cable %}
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="glyphicon glyphicon-resize-small" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-right">
            <li><a href="{% url 'dcim:consoleserverport_connect' termination_a_id=record.pk termination_b_type='console-port' %}?return_url={{ device.get_absolute_url }}">Console Port</a></li>
            <li><a href="{% url 'dcim:consoleserverport_connect' termination_a_id=record.pk termination_b_type='front-port' %}?return_url={{ device.get_absolute_url }}">Front Port</a></li>
            <li><a href="{% url 'dcim:consoleserverport_connect' termination_a_id=record.pk termination_b_type='rear-port' %}?return_url={{ device.get_absolute_url }}">Rear Port</a></li>
        </ul>
    </span>
{% endif %}
"""

POWERPORT_BUTTONS = """
{% if record.cable %}
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
{% elif perms.dcim.add_cable %}
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="glyphicon glyphicon-resize-small" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-right">
            <li><a href="{% url 'dcim:powerport_connect' termination_a_id=record.pk termination_b_type='power-outlet' %}?return_url={{ device.get_absolute_url }}">Power Outlet</a></li>
            <li><a href="{% url 'dcim:powerport_connect' termination_a_id=record.pk termination_b_type='power-feed' %}?return_url={{ device.get_absolute_url }}">Power Feed</a></li>
        </ul>
    </span>
{% endif %}
"""
