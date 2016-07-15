import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from .models import Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VLANGroup, VRF


RIR_EDIT_LINK = """
{% if perms.ipam.change_rir %}<a href="{% url 'ipam:rir_edit' slug=record.slug %}">Edit</a>{% endif %}
"""

UTILIZATION_GRAPH = """
{% with record.get_utilization as percentage %}
<div class="progress text-center">
    {% if percentage < 15 %}<span style="font-size: 12px;">{{ percentage }}%</span>{% endif %}
    <div class="progress-bar progress-bar-{% if percentage >= 90 %}danger{% elif percentage >= 75 %}warning{% else %}success{% endif %}"
        role="progressbar" aria-valuenow="{{ percentage }}" aria-valuemin="0" aria-valuemax="100" style="width: {{ percentage }}%">
        {% if percentage >= 15 %}{{ percentage }}%{% endif %}
    </div>
</div>
{% endwith %}
"""

ROLE_EDIT_LINK = """
{% if perms.ipam.change_role %}<a href="{% url 'ipam:role_edit' slug=record.slug %}">Edit</a>{% endif %}
"""

PREFIX_LINK = """
{% if record.has_children %}
    <span style="padding-left: {{ record.depth }}0px "><i class="fa fa-caret-right"></i></a>
{% else %}
    <span style="padding-left: {{ record.depth }}9px">
{% endif %}
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

PREFIX_LINK_BRIEF = """
<span style="padding-left: {{ record.depth }}0px">
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

STATUS_LABEL = """
{% if record.pk %}
    <span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
{% else %}
    <span class="label label-success">Available</span>
{% endif %}
"""

VLANGROUP_EDIT_LINK = """
{% if perms.ipam.change_vlangroup %}
    <a href="{% url 'ipam:vlangroup_edit' pk=record.pk %}">Edit</a>
{% endif %}
"""


#
# VRFs
#

class VRFTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('ipam:vrf', args=[Accessor('pk')], verbose_name='Name')
    rd = tables.Column(verbose_name='RD')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = VRF
        fields = ('pk', 'name', 'rd', 'description')


#
# RIRs
#

class RIRTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    aggregate_count = tables.Column(verbose_name='Aggregates')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=RIR_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = RIR
        fields = ('pk', 'name', 'aggregate_count', 'slug', 'edit')


#
# Aggregates
#

class AggregateTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.LinkColumn('ipam:aggregate', args=[Accessor('pk')], verbose_name='Aggregate')
    rir = tables.Column(verbose_name='RIR')
    child_count = tables.Column(verbose_name='Prefixes')
    utilization = tables.TemplateColumn(UTILIZATION_GRAPH, orderable=False, verbose_name='Utilization')
    date_added = tables.DateColumn(format="Y-m-d", verbose_name='Added')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = Aggregate
        fields = ('pk', 'prefix', 'rir', 'child_count', 'utilization', 'date_added', 'description')


#
# Roles
#

class RoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(verbose_name='Name')
    prefix_count = tables.Column(accessor=Accessor('count_prefixes'), orderable=False, verbose_name='Prefixes')
    vlan_count = tables.Column(accessor=Accessor('count_vlans'), orderable=False, verbose_name='VLANs')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=ROLE_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = Role
        fields = ('pk', 'name', 'prefix_count', 'vlan_count', 'slug', 'edit')


#
# Prefixes
#

class PrefixTable(BaseTable):
    pk = ToggleColumn()
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    prefix = tables.TemplateColumn(PREFIX_LINK, verbose_name='Prefix')
    vrf = tables.Column(orderable=False, default='Global', verbose_name='VRF')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    role = tables.Column(verbose_name='Role')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = ('pk', 'prefix', 'status', 'vrf', 'site', 'role', 'description')


class PrefixBriefTable(BaseTable):
    prefix = tables.TemplateColumn(PREFIX_LINK_BRIEF, verbose_name='Prefix')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    role = tables.Column(verbose_name='Role')

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = ('prefix', 'status', 'site', 'role')


#
# IPAddresses
#

class IPAddressTable(BaseTable):
    pk = ToggleColumn()
    address = tables.LinkColumn('ipam:ipaddress', args=[Accessor('pk')], verbose_name='IP Address')
    vrf = tables.Column(orderable=False, default='Global', verbose_name='VRF')
    device = tables.LinkColumn('dcim:device', args=[Accessor('interface.device.pk')], orderable=False,
                               verbose_name='Device')
    interface = tables.Column(orderable=False, verbose_name='Interface')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('pk', 'address', 'vrf', 'device', 'interface', 'description')


class IPAddressBriefTable(BaseTable):
    address = tables.LinkColumn('ipam:ipaddress', args=[Accessor('pk')], verbose_name='IP Address')
    device = tables.LinkColumn('dcim:device', args=[Accessor('interface.device.pk')], orderable=False,
                               verbose_name='Device')
    interface = tables.Column(orderable=False, verbose_name='Interface')
    nat_inside = tables.LinkColumn('ipam:ipaddress', args=[Accessor('nat_inside.pk')], orderable=False,
                                   verbose_name='NAT (Inside)')

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('address', 'device', 'interface', 'nat_inside')


#
# VLAN groups
#

class VLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    vlan_count = tables.Column(verbose_name='VLANs')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=VLANGROUP_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = VLANGroup
        fields = ('pk', 'name', 'site', 'vlan_count', 'slug', 'edit')


#
# VLANs
#

class VLANTable(BaseTable):
    pk = ToggleColumn()
    vid = tables.LinkColumn('ipam:vlan', args=[Accessor('pk')], verbose_name='ID')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    group = tables.Column(accessor=Accessor('group.name'), verbose_name='Group')
    name = tables.Column(verbose_name='Name')
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    role = tables.Column(verbose_name='Role')

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('pk', 'vid', 'site', 'group', 'name', 'status', 'role')
