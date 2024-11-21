VMINTERFACE_BUTTONS = """
{% if perms.virtualization.change_vminterface %}
  <span class="dropdown">
    <button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Add">
      <span class="mdi mdi-plus-thick" aria-hidden="true"></span>
    </button>
    <ul class="dropdown-menu dropdown-menu-end">
      {% if perms.ipam.add_ipaddress %}
        <li><a class="dropdown-item" href="{% url 'ipam:ipaddress_add' %}?vminterface={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}">IP Address</a></li>
      {% endif %}
      {% if perms.dcim.add_macaddress %}
        <li><a class="dropdown-item" href="{% url 'dcim:macaddress_add' %}?vminterface={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}">MAC Address</a></li>
      {% endif %}
      {% if perms.vpn.add_l2vpntermination %}
        <li><a class="dropdown-item" href="{% url 'vpn:l2vpntermination_add' %}?virtual_machine={{ object.pk }}&vminterface={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}">L2VPN Termination</a></li>
      {% endif %}
      {% if perms.ipam.add_fhrpgroupassignment %}
        <li><a class="dropdown-item" href="{% url 'ipam:fhrpgroupassignment_add' %}?interface_type={{ record|content_type_id }}&interface_id={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}">Assign FHRP Group</a></li>
      {% endif %}
    </ul>
  </span>
{% endif %}
{% if perms.vpn.add_tunnel and not record.tunnel_termination %}
  <a href="{% url 'vpn:tunnel_add' %}?termination1_type=virtualization.virtualmachine&termination1_parent={{ record.virtual_machine.pk }}&termination1_termination={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}" title="Create a tunnel" class="btn btn-success btn-sm">
    <i class="mdi mdi-tunnel-outline" aria-hidden="true"></i>
  </a>
{% elif perms.vpn.delete_tunneltermination and record.tunnel_termination %}
  <a href="{% url 'vpn:tunneltermination_delete' pk=record.tunnel_termination.pk %}?return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}" title="Remove tunnel" class="btn btn-danger btn-sm">
    <i class="mdi mdi-tunnel-outline" aria-hidden="true"></i>
  </a>
{% endif %}
"""
