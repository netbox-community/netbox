LINKTERMINATION = """
{% for termination in value %}
  {% if termination.parent_object %}
    <a href="{{ termination.parent_object.get_absolute_url }}">{{ termination.parent_object }}</a>
    <i class="mdi mdi-chevron-right"></i>
  {% endif %}
  <a href="{{ termination.get_absolute_url }}">{{ termination }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
  {{ ''|placeholder }}
{% endfor %}
"""

CABLE_LENGTH = """
{% load helpers %}
{% if record.length %}{{ record.length|floatformat:"-2" }} {{ record.length_unit }}{% endif %}
"""

WEIGHT = """
{% load helpers %}
{% if value %}{{ value|floatformat:"-2" }} {{ record.weight_unit }}{% endif %}
"""

DEVICE_LINK = """
{{ value|default:'<span class="badge text-bg-info">Unnamed device</span>' }}
"""

DEVICEBAY_STATUS = """
{% if record.installed_device_id %}
    <span class="badge text-bg-{{ record.installed_device.get_status_color }}">
        {{ record.installed_device.get_status_display }}
    </span>
{% else %}
    <span class="badge text-bg-secondary">Vacant</span>
{% endif %}
"""

INTERFACE_IPADDRESSES = """
  {% if value.count > 3 %}
    <a href="{% url 'ipam:ipaddress_list' %}?{{ record|meta:"model_name" }}_id={{ record.pk }}">{{ value.count }}</a>
  {% else %}
    {% for ip in value.all %}
      {% if ip.status != 'active' %}
        <a href="{{ ip.get_absolute_url }}" class="badge text-bg-{{ ip.get_status_color }}" data-bs-toggle="tooltip" data-bs-placement="left" title="{{ ip.get_status_display }}">{{ ip }}</a>
      {% else %}
        <a href="{{ ip.get_absolute_url }}">{{ ip }}</a>
      {% endif %}
    {% endfor %}
  {% endif %}
"""

INTERFACE_FHRPGROUPS = """
  {% for assignment in value.all %}
    <a href="{{ assignment.group.get_absolute_url }}">{{ assignment.group.get_protocol_display }}: {{ assignment.group.group_id }}</a>
  {% endfor %}
"""

INTERFACE_TAGGED_VLANS = """
{% if record.mode == 'tagged' %}
  {% if value.count > 3 %}
    <a href="{% url 'ipam:vlan_list' %}?{{ record|meta:"model_name" }}_id={{ record.pk }}">{{ value.count }} VLANs</a>
  {% else %}
    {% for vlan in value.all %}
        <a href="{{ vlan.get_absolute_url }}">{{ vlan }}</a><br />
    {% endfor %}
  {% endif %}
{% elif record.mode == 'tagged-all' %}
  All
{% endif %}
"""

INTERFACE_WIRELESS_LANS = """
{% for wlan in value.all %}
  <a href="{{ wlan.get_absolute_url }}">{{ wlan }}</a><br />
{% endfor %}
"""

POWERFEED_CABLE = """
<a href="{{ value.get_absolute_url }}">{{ value }}</a>
<a href="{% url 'dcim:powerfeed_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace">
    <i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i>
</a>
"""

POWERFEED_CABLETERMINATION = """
<a href="{{ value.parent_object.get_absolute_url }}">{{ value.parent_object }}</a>
<i class="mdi mdi-chevron-right"></i>
<a href="{{ value.get_absolute_url }}">{{ value }}</a>
"""

LOCATION_BUTTONS = """
<a href="{% url 'dcim:rack_elevation_list' %}?site={{ record.site.slug }}&location_id={{ record.pk }}" class="btn btn-sm btn-primary" title="View elevations">
    <i class="mdi mdi-server"></i>
</a>
"""

#
# Device component templatebuttons
#

MODULAR_COMPONENT_TEMPLATE_BUTTONS = """
{% load helpers %}
{% if perms.dcim.add_inventoryitemtemplate and record.device_type_id %}
<a href="{% url 'dcim:inventoryitemtemplate_add' %}?device_type={{ record.device_type_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={{ request.path }}" title="Add inventory item" class="btn btn-primary btn-sm">
  <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
</a>
{% endif %}
"""

#
# Device component buttons
#

CONSOLEPORT_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_consoleports' pk=object.pk %}" class="btn btn-sm btn-success" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:consoleport_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_consoleports' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_consoleports' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleserverport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleports' pk=object.pk %}">Console Server Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleport&a_terminations={{ record.pk }}&b_terminations_type=dcim.frontport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleports' pk=object.pk %}">Front Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleport&a_terminations={{ record.pk }}&b_terminations_type=dcim.rearport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleports' pk=object.pk %}">Rear Port</a></li>
        </ul>
    </span>
{% else %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
{% endif %}
"""

CONSOLESERVERPORT_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}" class="btn btn-sm btn-success" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:consoleserverport_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleserverport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}">Console Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleserverport&a_terminations={{ record.pk }}&b_terminations_type=dcim.frontport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}">Front Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.consoleserverport&a_terminations={{ record.pk }}&b_terminations_type=dcim.rearport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_consoleserverports' pk=object.pk %}">Rear Port</a></li>
        </ul>
    </span>
{% else %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
{% endif %}
"""

POWERPORT_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_powerports' pk=object.pk %}" class="btn btn-sm btn-primary" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:powerport_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_powerports' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_powerports' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.powerport&a_terminations={{ record.pk }}&b_terminations_type=dcim.poweroutlet&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_powerports' pk=object.pk %}">Power Outlet</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.powerport&a_terminations={{ record.pk }}&b_terminations_type=dcim.powerfeed&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_powerports' pk=object.pk %}">Power Feed</a></li>
        </ul>
    </span>
{% else %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
{% endif %}
"""

POWEROUTLET_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_poweroutlets' pk=object.pk %}" class="btn btn-sm btn-primary" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:poweroutlet_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_poweroutlets' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_poweroutlets' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    {% if not record.mark_connected %}
        <a href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.poweroutlet&a_terminations={{ record.pk }}&b_terminations_type=dcim.powerport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_poweroutlets' pk=object.pk %}" title="Connect" class="btn btn-success btn-sm">
            <i class="mdi mdi-ethernet-cable" aria-hidden="true"></i>
        </a>
    {% else %}
        <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
    {% endif %}
{% endif %}
"""

INTERFACE_BUTTONS = """
{% if perms.dcim.change_interface %}
  <span class="dropdown">
    <button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Add">
      <span class="mdi mdi-plus-thick" aria-hidden="true"></span>
    </button>
    <ul class="dropdown-menu dropdown-menu-end">
      {% if perms.ipam.add_ipaddress %}
        <li><a class="dropdown-item" href="{% url 'ipam:ipaddress_add' %}?interface={{ record.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">IP Address</a></li>
      {% endif %}
      {% if perms.dcim.add_inventoryitem %}
        <li><a class="dropdown-item" href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Inventory Item</a></li>
      {% endif %}
      {% if perms.dcim.add_interface %}
        <li><a class="dropdown-item" href="{% url 'dcim:interface_add' %}?device={{ record.device_id }}&parent={{ record.pk }}&name={{ record.name }}.&type=virtual&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Child Interface</a></li>
      {% endif %}
      {% if perms.vpn.add_l2vpntermination %}
        <li><a class="dropdown-item" href="{% url 'vpn:l2vpntermination_add' %}?device={{ object.pk }}&interface={{ record.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">L2VPN Termination</a></li>
      {% endif %}
      {% if perms.ipam.add_fhrpgroupassignment %}
        <li><a class="dropdown-item" href="{% url 'ipam:fhrpgroupassignment_add' %}?interface_type={{ record|content_type_id }}&interface_id={{ record.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Assign FHRP Group</a></li>
      {% endif %}
    </ul>
  </span>
{% endif %}
{% if record.link %}
    <a href="{% url 'dcim:interface_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
{% endif %}
{% if record.cable %}
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_interfaces' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_interfaces' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif record.wireless_link %}
    {% if perms.wireless.delete_wirelesslink %}
        <a href="{% url 'wireless:wirelesslink_delete' pk=record.wireless_link.pk %}?return_url={% url 'dcim:device_interfaces' pk=object.pk %}" title="Delete wireless link" class="btn btn-danger btn-sm">
            <i class="mdi mdi-wifi-off" aria-hidden="true"></i>
        </a>
    {% endif %}
{% elif record.type == 'virtual' %}
    {% if perms.vpn.add_tunnel and not record.tunnel_termination %}
        <a href="{% url 'vpn:tunnel_add' %}?termination1_type=dcim.device&termination1_parent={{ record.device.pk }}&termination1_termination={{ record.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}" title="Create a tunnel" class="btn btn-success btn-sm">
            <i class="mdi mdi-tunnel-outline" aria-hidden="true"></i>
        </a>
    {% elif perms.vpn.delete_tunneltermination and record.tunnel_termination %}
        <a href="{% url 'vpn:tunneltermination_delete' pk=record.tunnel_termination.pk %}?return_url={% url 'dcim:device_interfaces' pk=object.pk %}" title="Remove tunnel" class="btn btn-danger btn-sm">
            <i class="mdi mdi-tunnel-outline" aria-hidden="true"></i>
        </a>
    {% endif %}
{% elif record.is_wired and perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    {% if not record.mark_connected %}
    <span class="dropdown">
        <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Connect cable">
            <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.interface&a_terminations={{ record.pk }}&b_terminations_type=dcim.interface&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Interface</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.interface&a_terminations={{ record.pk }}&b_terminations_type=dcim.frontport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Front Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.interface&a_terminations={{ record.pk }}&b_terminations_type=dcim.rearport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Rear Port</a></li>
            <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.interface&a_terminations={{ record.pk }}&b_terminations_type=circuits.circuittermination&termination_b_site={{ object.site.pk }}&return_url={% url 'dcim:device_interfaces' pk=object.pk %}">Circuit Termination</a></li>
        </ul>
    </span>
    {% else %}
        <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
    {% endif %}
{% elif record.is_wireless and perms.wireless.add_wirelesslink %}
    <a href="{% url 'wireless:wirelesslink_add' %}?site_a={{ record.device.site.pk }}&location_a={{ record.device.location.pk }}&device_a={{ record.device_id }}&interface_a={{ record.pk }}&site_b={{ record.device.site.pk }}&location_b={{ record.device.location.pk }}" class="btn btn-success btn-sm">
        <span class="mdi mdi-wifi-plus" aria-hidden="true"></span>
    </a>
{% endif %}
"""

FRONTPORT_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}" class="btn btn-sm btn-primary" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:frontport_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_frontports' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_frontports' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    {% if not record.mark_connected %}
        <span class="dropdown">
            <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=dcim.interface&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Interface</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleserverport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Console Server Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Console Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=dcim.frontport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Front Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=dcim.rearport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Rear Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.frontport&a_terminations={{ record.pk }}&b_terminations_type=circuits.circuittermination&termination_b_site={{ object.site.pk }}&return_url={% url 'dcim:device_frontports' pk=object.pk %}">Circuit Termination</a></li>
            </ul>
        </span>
    {% else %}
        <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
    {% endif %}
{% endif %}
"""

REARPORT_BUTTONS = """
{% if perms.dcim.add_inventoryitem %}
  <a href="{% url 'dcim:inventoryitem_add' %}?device={{ record.device_id }}&component_type={{ record|content_type_id }}&component_id={{ record.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}" class="btn btn-sm btn-primary" title="Add inventory item">
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
  </a>
{% endif %}
{% if record.cable %}
    <a href="{% url 'dcim:rearport_trace' pk=record.pk %}" class="btn btn-primary btn-sm" title="Trace"><i class="mdi mdi-transit-connection-variant"></i></a>
    {% include 'dcim/inc/cable_toggle_buttons.html' with cable=record.cable %}
    {% if perms.dcim.change_cable or perms.dcim.delete_cable %}
        <span class="dropdown">
            <button type="button" class="btn btn-warning btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
            {% if perms.dcim.change_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_edit' pk=record.cable.pk %}?return_url={% url 'dcim:device_rearports' pk=object.pk %}">
                    <i class="mdi mdi-pencil-outline"></i>
                    Edit cable
                    </a>
                </li>
            {% endif %}
            {% if perms.dcim.delete_cable %}
                <li><a class="dropdown-item" href="{% url 'dcim:cable_delete' pk=record.cable.pk %}?return_url={% url 'dcim:device_rearports' pk=object.pk %}">
                    <i class="mdi mdi-trash-can-outline"></i>
                    Delete cable
                    </a>
                </li>
            {% endif %}
            </ul>
        </span>
    {% endif %}
{% elif perms.dcim.add_cable %}
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-transit-connection-variant" aria-hidden="true"></i></a>
    <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-lan-connect" aria-hidden="true"></i></a>
    {% if not record.mark_connected %}
        <span class="dropdown">
            <button type="button" class="btn btn-success btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="mdi mdi-ethernet-cable" aria-hidden="true"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=dcim.interface&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Interface</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleserverport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Console Server Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=dcim.consoleport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Console Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=dcim.frontport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Front Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=dcim.rearport&termination_b_site={{ object.site.pk }}&termination_b_rack={{ object.rack.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Rear Port</a></li>
                <li><a class="dropdown-item" href="{% url 'dcim:cable_add' %}?a_terminations_type=dcim.rearport&a_terminations={{ record.pk }}&b_terminations_type=circuits.circuittermination&termination_b_site={{ object.site.pk }}&return_url={% url 'dcim:device_rearports' pk=object.pk %}">Circuit Termination</a></li>
            </ul>
        </span>
    {% else %}
        <a href="#" class="btn btn-outline-dark btn-sm disabled"><i class="mdi mdi-ethernet-cable" aria-hidden="true"></i></a>
    {% endif %}
{% endif %}
"""

DEVICEBAY_BUTTONS = """
{% if perms.dcim.change_devicebay %}
    {% if record.installed_device %}
        <a href="{% url 'dcim:devicebay_depopulate' pk=record.pk %}?return_url={% url 'dcim:device_devicebays' pk=object.pk %}" class="btn btn-danger btn-sm">
            <i class="mdi mdi-server-minus" aria-hidden="true" title="Remove device"></i>
        </a>
    {% else %}
        <a href="{% url 'dcim:devicebay_populate' pk=record.pk %}?return_url={% url 'dcim:device_devicebays' pk=object.pk %}" class="btn btn-success btn-sm">
            <i class="mdi mdi-server-plus" aria-hidden="true" title="Install device"></i>
        </a>
    {% endif %}
{% endif %}
"""

MODULEBAY_BUTTONS = """
{% if perms.dcim.add_module %}
    {% if record.installed_module %}
        <a href="{% url 'dcim:module_delete' pk=record.installed_module.pk %}?return_url={% url 'dcim:device_modulebays' pk=object.pk %}" class="btn btn-danger btn-sm">
            <i class="mdi mdi-server-minus" aria-hidden="true" title="Remove module"></i>
        </a>
    {% else %}
        <a href="{% url 'dcim:module_add' %}?device={{ record.device_id }}&module_bay={{ record.pk }}&manufacturer={{ object.device_type.manufacturer_id }}&return_url={% url 'dcim:device_modulebays' pk=object.pk %}" class="btn btn-success btn-sm">
            <i class="mdi mdi-server-plus" aria-hidden="true" title="Install module"></i>
        </a>
    {% endif %}
{% endif %}
"""
