# Clusters

A cluster is a logical grouping of physical resources within which virtual machines run. A cluster must be assigned a type, and may optionally be assigned to a group and/or site.

Physical devices may be associated with clusters as hosts. This allows users to track on which host(s) a particular VM may reside. However, NetBox does not support pinning a specific VM within a cluster to a particular host device.

## Cluster Types

A cluster type represents a technology or mechanism by which a cluster is formed. For example, you might create a cluster type named "VMware vSphere" for a locally hosted cluster or "DigitalOcean NYC3" for one hosted by a cloud provider.

## Cluster Groups

Cluster groups may be created for the purpose of organizing clusters. The assignment of clusters to groups is optional.

---

# Virtual Machines

A virtual machine represents a virtual compute instance hosted within a cluster. Each VM must be associated with exactly one cluster.

Like devices, each VM can be assigned a platform and have interfaces created on it. VM interfaces behave similarly to device interfaces, and can be assigned IP addresses, VLANs, and services. However, given their virtual nature, they cannot be connected to other interfaces. Unlike physical devices, VMs cannot be assigned console or power ports, device bays, or inventory items.

The following resources can be defined for each VM:

* vCPU count
* Memory (MB)
* Disk space (GB)
