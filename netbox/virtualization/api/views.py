from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST

from dcim.models import Device
from extras.api.mixins import ConfigContextQuerySetMixin, ConfigTemplateRenderMixin
from netbox.api.renderers import TextRenderer
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from virtualization import filtersets
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from . import serializers


class VirtualizationRootView(APIRootView):
    """
    Virtualization API root view
    """
    def get_view_name(self):
        return 'Virtualization'


#
# Clusters
#

class ClusterTypeViewSet(NetBoxModelViewSet):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    ).prefetch_related('tags')
    serializer_class = serializers.ClusterTypeSerializer
    filterset_class = filtersets.ClusterTypeFilterSet


class ClusterGroupViewSet(NetBoxModelViewSet):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    ).prefetch_related('tags')
    serializer_class = serializers.ClusterGroupSerializer
    filterset_class = filtersets.ClusterGroupFilterSet


class ClusterViewSet(NetBoxModelViewSet):
    queryset = Cluster.objects.prefetch_related(
        'type', 'group', 'tenant', 'site', 'tags'
    ).annotate(
        device_count=count_related(Device, 'cluster'),
        virtualmachine_count=count_related(VirtualMachine, 'cluster')
    )
    serializer_class = serializers.ClusterSerializer
    filterset_class = filtersets.ClusterFilterSet


#
# Virtual machines
#

class VirtualMachineViewSet(ConfigContextQuerySetMixin, ConfigTemplateRenderMixin, NetBoxModelViewSet):
    queryset = VirtualMachine.objects.prefetch_related(
        'site', 'cluster', 'device', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'config_template', 'tags'
    )
    filterset_class = filtersets.VirtualMachineFilterSet

    def get_serializer_class(self):
        """
        Select the specific serializer based on the request context.

        If the `brief` query param equates to True, return the NestedVirtualMachineSerializer

        If the `exclude` query param includes `config_context` as a value, return the VirtualMachineSerializer

        Else, return the VirtualMachineWithConfigContextSerializer
        """

        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            return serializers.NestedVirtualMachineSerializer

        elif 'config_context' in request.query_params.get('exclude', []):
            return serializers.VirtualMachineSerializer

        return serializers.VirtualMachineWithConfigContextSerializer

    @action(detail=True, methods=['post'], url_path='render-config', renderer_classes=[JSONRenderer, TextRenderer])
    def render_config(self, request, pk):
        """
        Resolve and render the preferred ConfigTemplate for this Device.
        """
        instance = self.get_object()
        configtemplate = instance.get_config_template()
        if not configtemplate:
            return Response({'error': 'No config template found for this virtual machine.'}, status=HTTP_400_BAD_REQUEST)

        # Compile context data
        context_data = instance.get_config_context()
        context_data.update(request.data)
        context_data.update({'virtualmachine': instance})

        return self.render_configtemplate(request, configtemplate, context_data)


class VMInterfaceViewSet(NetBoxModelViewSet):
    queryset = VMInterface.objects.prefetch_related(
        'virtual_machine', 'parent', 'tags', 'untagged_vlan', 'tagged_vlans', 'vrf', 'ip_addresses',
        'fhrp_group_assignments',
    )
    serializer_class = serializers.VMInterfaceSerializer
    filterset_class = filtersets.VMInterfaceFilterSet
    brief_prefetch_fields = ['virtual_machine']
