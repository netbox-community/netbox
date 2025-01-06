AGGREGATE_COPY_BUTTON = """
{% copy_content record.pk prefix="aggregate_" %}
"""

PREFIX_LINK = """
{% if record.pk %}
  <a href="{{ record.get_absolute_url }}" id="prefix_{{ record.pk }}">{{ record.prefix }}</a>
{% else %}
  <a href="{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}{% if object.site %}&site={{ object.site.pk }}{% endif %}{% if object.tenant %}&tenant_group={{ object.tenant.group.pk }}&tenant={{ object.tenant.pk }}{% endif %}">{{ record.prefix }}</a>
{% endif %}
"""

PREFIX_COPY_BUTTON = """
{% copy_content record.pk prefix="prefix_" %}
"""

PREFIX_LINK_WITH_DEPTH = """
{% load helpers %}
{% if record.depth %}
    <div class="record-depth">
        {% for i in record.depth|as_range %}
            <span>•</span>
        {% endfor %}
    </div>
{% endif %}
""" + PREFIX_LINK

IPADDRESS_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}" id="ipaddress_{{ record.pk }}">{{ record.address }}</a>
{% elif perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?address={{ record.1 }}{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}{% if object.tenant %}&tenant={{ object.tenant.pk }}{% endif %}&return_url={% url 'ipam:prefix_ipaddresses' pk=object.pk %}" class="btn btn-sm btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available
{% endif %}
"""

IPADDRESS_COPY_BUTTON = """
{% copy_content record.pk prefix="ipaddress_" %}
"""

IPADDRESS_ASSIGN_LINK = """
<a href="{% url 'ipam:ipaddress_edit' pk=record.pk %}?{% if request.GET.interface %}interface={{ request.GET.interface }}{% elif request.GET.vminterface %}vminterface={{ request.GET.vminterface }}{% endif %}&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""

VRF_LINK = """
{% if value %}
    <a href="{{ record.vrf.get_absolute_url }}">{{ record.vrf }}</a>
{% elif object.vrf %}
    <a href="{{ object.vrf.get_absolute_url }}">{{ object.vrf }}</a>
{% else %}
    Global
{% endif %}
"""

VLAN_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.vid }}</a>
{% elif perms.ipam.add_vlan %}
    <a href="{% url 'ipam:vlan_add' %}?vid={{ record.vid }}{% if record.vlan_group %}&group={{ record.vlan_group.pk }}{% endif %}" class="btn btn-sm btn-success">{{ record.available }} VLAN{{ record.available|pluralize }} available</a>
{% else %}
    {{ record.available }} VLAN{{ record.available|pluralize }} available
{% endif %}
"""

VLAN_PREFIXES = """
{% for prefix in value.all %}
    <a href="{% url 'ipam:prefix' pk=prefix.pk %}">{{ prefix }}</a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""

VLANGROUP_BUTTONS = """
{% with next_vid=record.get_next_available_vid %}
    {% if next_vid and perms.ipam.add_vlan %}
        <a href="{% url 'ipam:vlan_add' %}?group={{ record.pk }}&vid={{ next_vid }}" title="Add VLAN" class="btn btn-sm btn-success">
            <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
        </a>
    {% endif %}
{% endwith %}
"""

VLAN_MEMBER_TAGGED = """
{% if record.untagged_vlan_id == object.pk %}
    <span class="text-danger"><i class="mdi mdi-close-thick"></i></span>
{% else %}
    <span class="text-success"><i class="mdi mdi-check-bold"></i></span>
{% endif %}
"""
