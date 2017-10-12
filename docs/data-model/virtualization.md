NetBox supports the definition of virtual machines arranged in clusters. A cluster can optionally have physical host devices associated with it.

# Clusters

A cluster is a logical grouping of physical resources within which virtual machines run. A cluster must be assigned a type, and may optionally be assigned an organizational group.

Physical devices (from NetBox's DCIM component) may be associated with clusters as hosts. This allows users to track on which host(s) a particular VM may reside. However, NetBox does not support pinning a specific VM within a cluster to a particular host device.

### Cluster Types

A cluster type represents a technology or mechanism by which a cluster is formed. For example, you might create a cluster type named "VMware vSphere" for a locally hosted cluster or "DigitalOcean NYC3" for one hosted by a cloud provider.

### Cluster Groups

Cluster groups may be created for the purpose of organizing clusters.

---

# Virtual Machines

A virtual machine represents a virtual compute instance hosted within a cluster. Each VM must be associated with exactly one cluster.

Like devices, each VM can have interfaces created on it. These behave similarly to device interfaces, and can be assigned IP addresses, however given their virtual nature they cannot be connected to other interfaces. VMs can also be assigned layer four services. Unlike physical devices, VMs cannot be assigned console or power ports, or device bays.

The following resources can be defined for each VM:

* vCPU count
* Memory (MB)
* Disk space (GB)
