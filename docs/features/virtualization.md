# Virtualization

Virtual machines and clusters can be modeled in NetBox alongside physical infrastructure. IP addresses and other resources are assigned to these objects just like physical objects, providing a seamless integration between physical and virtual networks.

```mermaid
flowchart TD
    ClusterGroup & ClusterType --> Cluster
    Cluster --> VirtualMachine
    Platform --> VirtualMachine
    VirtualMachine --> VMInterface

click Cluster "../../models/virtualization/cluster/"
click ClusterGroup "../../models/virtualization/clustergroup/"
click ClusterType "../../models/virtualization/clustertype/"
click Platform "../../models/dcim/platform/"
click VirtualMachine "../../models/virtualization/virtualmachine/"
click VMInterface "../../models/virtualization/vminterface/"
```

## Clusters

A cluster is one or more physical host devices on which virtual machines can run. Each cluster must have a type and operational status, and may be assigned to a group. (Both types and groups are user-defined.) Each cluster may designate one or more devices as hosts, however this is optional.

## Virtual Machines

A virtual machine is a virtualized compute instance. These behave in NetBox very similarly to device objects, but without any physical attributes. For example, a VM may have interfaces assigned to it with IP addresses and VLANs, however its interfaces cannot be connected via cables (because they are virtual). Each VM may also define its compute, memory, and storage resources as well.
