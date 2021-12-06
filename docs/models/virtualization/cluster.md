# Clusters

A cluster is a logical grouping of physical resources within which virtual machines run. A cluster must be assigned a type (technological classification), and may optionally be assigned to a cluster group, site, and/or tenant. Each cluster must have a unique name within its assigned group and/or site, if any.

Physical devices may be associated with clusters as hosts. This allows users to track on which host(s) a particular virtual machine may reside. However, NetBox does not support pinning a specific VM within a cluster to a particular host device.
