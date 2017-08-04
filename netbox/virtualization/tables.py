from __future__ import unicode_literals

import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


CLUSTERTYPE_ACTIONS = """
{% if perms.virtualization.change_clustertype %}
    <a href="{% url 'virtualization:clustertype_edit' pk=record.pk %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

CLUSTERGROUP_ACTIONS = """
{% if perms.virtualization.change_clustergroup %}
    <a href="{% url 'virtualization:clustergroup_edit' pk=record.pk %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""


#
# Cluster types
#

class ClusterTypeTable(BaseTable):
    pk = ToggleColumn()
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
    vm_count = tables.Column(verbose_name='VMs')

    class Meta(BaseTable.Meta):
        model = Cluster
        fields = ('pk', 'name', 'type', 'group', 'vm_count')


#
# Virtual machines
#

class VirtualMachineTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')])

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = ('pk', 'name', 'tenant')
