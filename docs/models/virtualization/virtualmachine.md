# Virtual Machines

A virtual machine represents a virtual compute instance hosted within a cluster. Each VM must be associated with exactly one cluster.

Like devices, each VM can be assigned a platform and have interfaces created on it. VM interfaces behave similarly to device interfaces, and can be assigned IP addresses, VLANs, and services. However, given their virtual nature, they cannot be connected to other interfaces. Unlike physical devices, VMs cannot be assigned console or power ports, device bays, or inventory items.

The following resources can be defined for each VM:

* vCPU count
* Memory (MB)
* Disk space (GB)
