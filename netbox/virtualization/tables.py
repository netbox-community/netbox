from __future__ import unicode_literals

import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Interface
from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable, ToggleColumn
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

CLUSTERTYPE_ACTIONS = """
<a href="{% url 'virtualization:clustertype_changelog' slug=record.slug %}" class="btn btn-default btn-xs" title="Changelog">
    <i class="fa fa-history"></i>
</a>
{% if perms.virtualization.change_clustertype %}
    <a href="{% url 'virtualization:clustertype_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

CLUSTERGROUP_ACTIONS = """
<a href="{% url 'virtualization:clustergroup_changelog' slug=record.slug %}" class="btn btn-default btn-xs" title="Changelog">
    <i class="fa fa-history"></i>
</a>
{% if perms.virtualization.change_clustergroup %}
    <a href="{% url 'virtualization:clustergroup_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

VIRTUALMACHINE_STATUS = """
<span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
"""

VIRTUALMACHINE_ROLE = """
{% if record.role %}<label class="label" style="background-color: #{{ record.role.color }}">{{ value }}</label>{% else %}&mdash;{% endif %}
"""

VIRTUALMACHINE_PRIMARY_IP = """
{{ record.primary_ip6.address.ip|default:"" }}
{% if record.primary_ip6 and record.primary_ip4 %}<br />{% endif %}
{{ record.primary_ip4.address.ip|default:"" }}
"""


#
# Cluster types
#

class ClusterTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = tables.Column(verbose_name='Clusters')
    actions = tables.TemplateColumn(
        template_code=CLUSTERTYPE_ACTIONS,
        attrs={'td': {'class': 'text-right'}},
        verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = ClusterType
        fields = ('pk', 'name', 'cluster_count', 'actions')


#
# Cluster groups
#

class ClusterGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = tables.Column(verbose_name='Clusters')
    actions = tables.TemplateColumn(
        template_code=CLUSTERGROUP_ACTIONS,
        attrs={'td': {'class': 'text-right'}},
        verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = ClusterGroup
        fields = ('pk', 'name', 'cluster_count', 'actions')


#
# Clusters
#

class ClusterTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')])
    device_count = tables.Column(accessor=Accessor('devices.count'), orderable=False, verbose_name='Devices')
    vm_count = tables.Column(accessor=Accessor('virtual_machines.count'), orderable=False, verbose_name='VMs')

    class Meta(BaseTable.Meta):
        model = Cluster
        fields = ('pk', 'name', 'type', 'group', 'site', 'device_count', 'vm_count')


#
# Virtual machines
#

class VirtualMachineTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    status = tables.TemplateColumn(template_code=VIRTUALMACHINE_STATUS)
    cluster = tables.LinkColumn('virtualization:cluster', args=[Accessor('cluster.pk')])
    role = tables.TemplateColumn(VIRTUALMACHINE_ROLE)
    tenant = tables.TemplateColumn(template_code=COL_TENANT)

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = ('pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk')


class VirtualMachineDetailTable(VirtualMachineTable):
    primary_ip = tables.TemplateColumn(
        orderable=False, verbose_name='IP Address', template_code=VIRTUALMACHINE_PRIMARY_IP
    )

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = ('pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk', 'primary_ip')


#
# VM components
#

class InterfaceTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('name', 'enabled', 'description')
