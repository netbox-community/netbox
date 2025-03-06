from netbox.api.serializers import WritableNestedSerializer
from virtualization import models

__all__ = (
    'NestedVirtualMachineSerializer',
    'NestedVMInterfaceSerializer',
)


class NestedVirtualMachineSerializer(WritableNestedSerializer):

    class Meta:
        model = models.VirtualMachine
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedVMInterfaceSerializer(WritableNestedSerializer):
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
        model = models.VMInterface
        fields = ['id', 'url', 'display_url', 'display', 'virtual_machine', 'name']
